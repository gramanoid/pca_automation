#!/usr/bin/env python3
"""Test if the API key is working"""

from production_workflow.utils.secure_api_key import get_api_key, get_default_model_config

# Get the configuration
config = get_default_model_config()

print("=" * 60)
print("API KEY TEST")
print("=" * 60)
print(f"\nProvider: {config['provider']}")
print(f"Model: {config['model']}")

if config['api_key']:
    # Mask the key for security
    key = config['api_key']
    masked = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
    print(f"API Key: {masked}")
    print("\n✅ API key is configured and ready!")
    print("Everyone who uses your Streamlit app will automatically use this key.")
else:
    print("\n❌ No API key found!")
    print("\nTo fix this:")
    print("1. Run: python encrypt_my_key.py")
    print("2. Follow the instructions to add your encrypted key")
    print("3. Commit and push to GitHub")