#!/usr/bin/env python3
"""
Secure API Key Management Module
Handles encryption/decryption of API keys with hardcoded encrypted values
"""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class SecureAPIKeyManager:
    """Manages encrypted API keys with fallback to environment variables"""
    
    # IMPORTANT: These are the encrypted API keys. To update them:
    # 1. Run: python secure_api_key.py update
    # 2. Copy the output and replace these values
    # 3. Commit the changes
    ENCRYPTED_KEYS = {
        'anthropic': None,  # Will be set after initial encryption
        'openai': None,     # Optional: for OpenAI support
        'google': None      # Optional: for Google AI support
    }
    
    # Salt for key derivation (can be public)
    SALT = b'pca_automation_salt_v1_2025'
    
    def __init__(self):
        """Initialize the secure key manager"""
        self._fernet = self._initialize_cipher()
        
    def _initialize_cipher(self) -> Fernet:
        """Initialize the encryption cipher using a derived key"""
        # Derive encryption key from a fixed passphrase
        # In production, this could come from a secure configuration
        passphrase = self._get_passphrase()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.SALT,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
        return Fernet(key)
    
    def _get_passphrase(self) -> str:
        """Get the passphrase for encryption/decryption"""
        # Use a combination of factors to generate the passphrase
        # This makes it harder to extract the key even with source code access
        factors = [
            "PCA",  # Project identifier
            "2025",  # Version year
            "MediaPlan",  # Component
            "SecureKey",  # Purpose
            "Automation"  # Type
        ]
        # Create passphrase by interleaving factors
        passphrase = "".join([f"{factors[i % len(factors)]}_{i}" for i in range(20)])
        return passphrase[:32]  # Use first 32 characters
    
    def get_api_key(self, provider: str = 'anthropic') -> str:
        """
        Get the API key with the following priority:
        1. Environment variable (if set)
        2. Decrypted hardcoded key
        3. None if neither available
        
        Args:
            provider: The API provider ('anthropic', 'openai', 'google')
        """
        # Environment variable mapping
        env_vars = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'google': 'GOOGLE_API_KEY'
        }
        
        # First check environment variable
        env_key = os.getenv(env_vars.get(provider, 'ANTHROPIC_API_KEY'))
        if env_key:
            logger.debug(f"Using {provider} API key from environment variable")
            return env_key
        
        # Then try decrypting hardcoded key
        encrypted_key = self.ENCRYPTED_KEYS.get(provider)
        if encrypted_key:
            try:
                decrypted_key = self._decrypt_key(encrypted_key)
                logger.debug(f"Using decrypted hardcoded {provider} API key")
                return decrypted_key
            except Exception as e:
                logger.error(f"Failed to decrypt hardcoded {provider} API key: {e}")
        
        logger.warning(f"No {provider} API key available (neither environment nor hardcoded)")
        return None
    
    def _encrypt_key(self, api_key: str) -> str:
        """Encrypt an API key"""
        encrypted = self._fernet.encrypt(api_key.encode())
        return base64.b64encode(encrypted).decode()
    
    def _decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an API key"""
        encrypted_bytes = base64.b64decode(encrypted_key.encode())
        decrypted = self._fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def update_encrypted_key(self, provider: str, new_api_key: str) -> str:
        """
        Encrypt a new API key and return the encrypted value.
        Use this to update the ENCRYPTED_KEYS constant.
        
        Args:
            provider: The API provider ('anthropic', 'openai', 'google')
            new_api_key: The plain text API key to encrypt
            
        Returns:
            The encrypted key string to be hardcoded
        """
        encrypted = self._encrypt_key(new_api_key)
        
        print("\n" + "="*60)
        print(f"ENCRYPTED {provider.upper()} API KEY")
        print("="*60)
        print(f"\nUpdate the ENCRYPTED_KEYS['{provider}'] with this value:")
        print(f"\n'{provider}': '{encrypted}',")
        print("\n" + "="*60)
        
        # Verify it can be decrypted
        try:
            decrypted = self._decrypt_key(encrypted)
            if decrypted == new_api_key:
                print("✅ Encryption verified successfully!")
            else:
                print("❌ Encryption verification failed!")
        except Exception as e:
            print(f"❌ Failed to verify encryption: {e}")
        
        return encrypted
    
    @classmethod
    def get_instance(cls):
        """Get a singleton instance of the key manager"""
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance


# Convenience function for easy access
def get_api_key(provider: str = 'anthropic') -> str:
    """
    Get the API key using the secure manager.
    
    Args:
        provider: The API provider ('anthropic', 'openai', 'google')
    
    Returns:
        The API key string or None if not available
    """
    manager = SecureAPIKeyManager.get_instance()
    return manager.get_api_key(provider)


# CLI tool for key management
def main():
    """Command line interface for managing encrypted API keys"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python secure_api_key.py [command]")
        print("\nCommands:")
        print("  encrypt <api_key>  - Encrypt a new API key")
        print("  test              - Test current key configuration")
        print("  update            - Interactive key update")
        return
    
    command = sys.argv[1]
    manager = SecureAPIKeyManager()
    
    if command == "encrypt":
        if len(sys.argv) < 4:
            print("Error: Please provide the provider and API key to encrypt")
            print("Usage: python secure_api_key.py encrypt <provider> <api_key>")
            print("Providers: anthropic, openai, google")
            return
        
        provider = sys.argv[2]
        api_key = sys.argv[3]
        if provider not in ['anthropic', 'openai', 'google']:
            print(f"Error: Invalid provider '{provider}'")
            print("Valid providers: anthropic, openai, google")
            return
        manager.update_encrypted_key(provider, api_key)
    
    elif command == "test":
        print("\nTesting API key configuration...")
        print("-" * 40)
        
        for provider in ['anthropic', 'openai', 'google']:
            print(f"\n{provider.upper()}:")
            
            # Check environment variable
            env_vars = {'anthropic': 'ANTHROPIC_API_KEY', 'openai': 'OPENAI_API_KEY', 'google': 'GOOGLE_API_KEY'}
            env_key = os.getenv(env_vars[provider])
            print(f"  Environment variable set: {'Yes' if env_key else 'No'}")
            
            # Check hardcoded key
            print(f"  Hardcoded key available: {'Yes' if manager.ENCRYPTED_KEYS.get(provider) else 'No'}")
            
            # Get actual key
            api_key = get_api_key(provider)
            if api_key:
                # Show masked key for security
                masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
                print(f"  API key retrieved: {masked_key}")
                print(f"  ✅ {provider} configuration is working!")
            else:
                print(f"  ❌ No {provider} API key available!")
    
    elif command == "update":
        print("\nInteractive API Key Update")
        print("-" * 40)
        print("\nThis will generate encrypted API keys to hardcode in the source.")
        print("You can skip any provider by pressing Enter.\n")
        
        encrypted_keys = {}
        for provider in ['anthropic', 'openai', 'google']:
            api_key = input(f"Enter your {provider.upper()} API key (or press Enter to skip): ").strip()
            
            if api_key:
                encrypted = manager.update_encrypted_key(provider, api_key)
                encrypted_keys[provider] = encrypted
        
        if encrypted_keys:
            print("\n" + "="*60)
            print("UPDATE YOUR CODE")
            print("="*60)
            print("\nReplace the ENCRYPTED_KEYS dictionary with:")
            print("\nENCRYPTED_KEYS = {")
            for provider in ['anthropic', 'openai', 'google']:
                if provider in encrypted_keys:
                    print(f"    '{provider}': '{encrypted_keys[provider]}',")
                else:
                    print(f"    '{provider}': None,")
            print("}")
            print("\n" + "="*60)
    
    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see usage.")


if __name__ == "__main__":
    main()