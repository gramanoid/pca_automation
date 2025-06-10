# Team API Key Setup Guide

This guide explains how to set up a hardcoded, encrypted API key that your entire team can use without individual configuration.

## 🎯 Benefits

- **Zero Configuration**: Team members can use the app immediately without API keys
- **Secure**: API key is encrypted with AES-256 encryption
- **Convenient**: No need to share API keys via email or chat
- **Controlled**: You maintain control over the team's API access

## 🔧 Setup Instructions

### Method 1: Interactive Setup (Recommended)

1. **Run the setup script**:
   ```bash
   python setup_team_api_key.py
   ```

2. **Follow the prompts**:
   - Choose your API provider (Anthropic/OpenAI/Google)
   - Enter your API key
   - Copy the encrypted output

3. **Update the code**:
   - Open `production_workflow/utils/secure_api_key.py`
   - Find the `ENCRYPTED_KEYS` dictionary (around line 24)
   - Replace it with the output from the setup script

4. **Commit and push**:
   ```bash
   git add production_workflow/utils/secure_api_key.py
   git commit -m "feat: Add encrypted team API key for AI mapping"
   git push
   ```

### Method 2: Command Line

```bash
# For Anthropic (Claude)
python production_workflow/utils/secure_api_key.py encrypt anthropic YOUR_API_KEY_HERE

# For OpenAI
python production_workflow/utils/secure_api_key.py encrypt openai YOUR_API_KEY_HERE

# For Google (Gemini)
python production_workflow/utils/secure_api_key.py encrypt google YOUR_API_KEY_HERE
```

### Method 3: All Providers at Once

```bash
python production_workflow/utils/secure_api_key.py update
```

This will prompt you for all three providers' API keys.

## 📝 Example

Here's what the encrypted keys look like in the code:

```python
ENCRYPTED_KEYS = {
    'anthropic': 'gAAAAABh3x9K2M8N...',  # Your encrypted Anthropic key
    'openai': None,                      # Not configured
    'google': None                       # Not configured
}
```

## 🔐 Security Details

### Encryption Method
- **Algorithm**: AES-256 in CBC mode with HMAC
- **Key Derivation**: PBKDF2 with SHA256, 100,000 iterations
- **Implementation**: Python's `cryptography` library (Fernet)

### Passphrase Generation
The encryption passphrase is derived from multiple factors:
- Project identifier
- Version year
- Component name
- Purpose identifier
- Type descriptor

This makes it difficult to decrypt the key even with source code access.

### Security Considerations

✅ **Good for**:
- Team development environments
- Internal tools
- Proof of concepts
- Streamlit Community Cloud deployments

⚠️ **Not recommended for**:
- High-security production environments
- Public-facing applications with sensitive data
- Environments requiring key rotation

For production deployments, consider:
- Using environment variables
- Key management services (AWS KMS, Azure Key Vault, etc.)
- Secrets management tools (HashiCorp Vault, etc.)

## 🧪 Testing Your Setup

After setting up the encrypted key:

```bash
# Test the configuration
python production_workflow/utils/secure_api_key.py test
```

Expected output:
```
Testing API key configuration...
----------------------------------------

ANTHROPIC:
  Environment variable set: No
  Hardcoded key available: Yes
  API key retrieved: sk-ant-...XYZ
  ✅ anthropic configuration is working!

OPENAI:
  Environment variable set: No
  Hardcoded key available: No
  ❌ No openai API key available!
```

## 👥 How Your Team Uses It

Once you've set up the encrypted key:

1. **Team members clone the repo**
2. **Run the Streamlit app**
3. **The app automatically uses the encrypted key**
4. **No API key configuration needed!**

The UI will show:
```
🔐 Using secure team API key - No configuration needed!
Your colleagues can use this app without entering any API key
```

## 🔄 Updating the Key

To update the encrypted key:

1. Run the setup script again
2. Enter the new API key
3. Update the code with the new encrypted value
4. Commit and push the changes

## 🚨 Important Notes

1. **Never commit unencrypted API keys**
2. **The encrypted key is tied to the passphrase** - changing the passphrase logic will break decryption
3. **Environment variables take precedence** - if `ANTHROPIC_API_KEY` is set, it will be used instead
4. **Test after deployment** - ensure the app works for team members

## 📊 Integration with the App

The app automatically:
- Checks for environment variables first
- Falls back to the encrypted key
- Shows appropriate status in the UI
- Allows manual override in "Custom" configuration mode

## 🆘 Troubleshooting

### "No API key available"
- Check that the `ENCRYPTED_KEYS` dictionary has your encrypted key
- Verify you've committed and pushed the changes
- Run the test command to debug

### "Failed to decrypt hardcoded API key"
- The passphrase generation logic may have changed
- Re-encrypt your key with the current version

### Team member can't access the key
- Ensure they have the latest code
- Check that no environment variables are overriding
- Verify the encryption is working with the test command

## 🎉 Success!

Once set up, your team can focus on using the app rather than managing API keys. The encrypted key provides a good balance of security and convenience for team collaboration.