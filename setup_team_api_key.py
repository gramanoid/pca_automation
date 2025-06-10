#!/usr/bin/env python3
"""
Setup script for configuring team API key
This will encrypt your API key and show you how to add it to the code
"""

import os
import sys
from pathlib import Path

# Add production workflow to path
sys.path.insert(0, str(Path(__file__).parent))

from production_workflow.utils.secure_api_key import SecureAPIKeyManager

def main():
    print("=" * 60)
    print("PCA AUTOMATION - TEAM API KEY SETUP")
    print("=" * 60)
    print("\nThis script will help you set up a hardcoded API key")
    print("that your team can use without configuration.\n")
    
    # Create manager instance
    manager = SecureAPIKeyManager()
    
    # Get API key from user
    print("Which API provider do you want to configure?")
    print("1. Anthropic (Claude)")
    print("2. OpenAI (GPT)")
    print("3. Google (Gemini)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    provider_map = {
        '1': 'anthropic',
        '2': 'openai',
        '3': 'google'
    }
    
    provider = provider_map.get(choice)
    if not provider:
        print("Invalid choice!")
        return
    
    api_key = input(f"\nEnter your {provider.upper()} API key: ").strip()
    
    if not api_key:
        print("No API key provided!")
        return
    
    # Encrypt the key
    encrypted = manager.update_encrypted_key(provider, api_key)
    
    # Show instructions
    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1. Open the file:")
    print("   production_workflow/utils/secure_api_key.py")
    
    print("\n2. Find the ENCRYPTED_KEYS dictionary (around line 24)")
    
    print("\n3. Update it with your encrypted key:")
    print(f"\n    ENCRYPTED_KEYS = {{")
    print(f"        'anthropic': {'"{}"'.format(encrypted) if provider == 'anthropic' else 'None'},")
    print(f"        'openai': {'"{}"'.format(encrypted) if provider == 'openai' else 'None'},")
    print(f"        'google': {'"{}"'.format(encrypted) if provider == 'google' else 'None'}")
    print(f"    }}")
    
    print("\n4. Save the file and commit to your repository")
    
    print("\n5. Your team can now use the app without entering API keys!")
    
    print("\n" + "=" * 60)
    print("SECURITY NOTES")
    print("=" * 60)
    print("- The key is encrypted with AES-256 encryption")
    print("- The encryption passphrase is derived from multiple factors")
    print("- This provides reasonable security for team use")
    print("- For production deployments, consider using environment variables")
    print("- Never commit unencrypted API keys to version control")
    
    print("\n✅ Setup complete!")

if __name__ == "__main__":
    main()