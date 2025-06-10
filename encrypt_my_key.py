#!/usr/bin/env python3
"""
Quick script to encrypt your OpenRouter API key
"""

from production_workflow.utils.secure_api_key import SecureAPIKeyManager

# Initialize the manager
manager = SecureAPIKeyManager()

# Get your API key
print("=" * 60)
print("OPENROUTER API KEY ENCRYPTION")
print("=" * 60)
print("\nThis will encrypt your OpenRouter API key for team use.")
print("Get your key from: https://openrouter.ai/keys\n")

api_key = input("Enter your OpenRouter API key: ").strip()

if api_key:
    # Encrypt the key
    encrypted = manager.update_encrypted_key('openrouter', api_key)
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("\n1. Copy this encrypted key:")
    print(f"\n'{encrypted}'")
    print("\n2. Open the file:")
    print("   production_workflow/utils/secure_api_key.py")
    print("\n3. Find line ~28 where ENCRYPTED_KEYS is defined")
    print("\n4. Replace the 'openrouter' value with your encrypted key:")
    print(f"\n    'openrouter': '{encrypted}'")
    print("\n5. Save, commit, and push to GitHub")
    print("\n✅ Then everyone can use your app without needing an API key!")
else:
    print("\nNo API key provided. Exiting.")