# Quick Start: Running AI-Powered Tests

## Prerequisites

1. **API Keys Required**:
   - OpenAI API key (for GPT-4o)
   - OR Anthropic API key (for Claude)
   - Optional: LangChain API key for tracing

2. **Streamlit App Running**:
   ```bash
   # In one terminal, start your Streamlit app
   streamlit run streamlit_app_interactive.py
   ```

## Step 1: Navigate to Test Directory
```bash
cd ai_powered_tests
```

## Step 2: Run Setup Script
```bash
./setup.sh
```

This will:
- Install Node.js dependencies (Stagehand)
- Install Python dependencies (Browser Use)
- Install Playwright browsers
- Create `.env` file from template

## Step 3: Configure API Keys
```bash
# Edit the .env file
nano .env
# OR
code .env
```

Add your API keys:
```env
# At minimum, you need ONE of these:
OPENAI_API_KEY=sk-...your-key-here...
# OR
ANTHROPIC_API_KEY=sk-ant-...your-key-here...

# Keep these defaults
STREAMLIT_APP_URL=http://localhost:8501
HEADLESS_MODE=false
DEBUG_MODE=true
```

## Step 4: Run Tests

### Option A: Run All Tests
```bash
npm run test:all
```

### Option B: Run Individual Test Suites
```bash
# Run Stagehand tests (UI automation)
npm run test:stagehand

# Run Browser Use tests (business logic)
npm run test:browser-use

# Compare with traditional Playwright
python compare_test_approaches.py
```

### Option C: Run Quick Demo
```bash
# See immediate results with the checkbox fix
node quick_start_example.js
```

## Expected Output

### Stagehand Tests
```
🚀 Starting Stagehand tests for Streamlit features
📱 Navigating to Streamlit app...
✅ Test 1: Enabling feature checkboxes with AI
  - Enable the 'Show Data Preview' checkbox
  - Enable the 'Enhanced Validation' checkbox
  ...
🔍 Test 2: Verifying enabled features
📊 Test 4: Extracting data preview information
🎉 All Stagehand tests completed!
```

### Browser Use Tests
```
🤖 Starting Browser Use AI-Powered Business Logic Tests
🧪 Testing Market Mapping Business Logic
📊 Testing Data Transformation Rules
🚀 Running Parallel Validation Scenarios
✅ All Browser Use tests completed!
```

## Troubleshooting

### Error: "API key not found"
- Make sure you've added your API keys to `.env` (not `.env.example`)
- Check that the keys are valid and have sufficient credits

### Error: "Cannot connect to http://localhost:8501"
- Ensure Streamlit app is running: `streamlit run streamlit_app_interactive.py`
- Check if app is on different port

### Error: "Module not found"
- Run `./setup.sh` again
- For Node issues: `npm install`
- For Python issues: `pip install -r requirements.txt`

### Tests timeout
- AI models can be slow on first run
- Increase timeouts in test files if needed
- Check your API rate limits

## Cost Estimates

- **Stagehand (GPT-4o)**: ~$0.10-0.20 per full test run
- **Browser Use (GPT-4o)**: ~$0.15-0.25 per full test run
- **Total**: ~$0.25-0.45 for complete test suite

## Next Steps

1. **Review Results**: Check `comparison_report.md` after running comparison
2. **Migrate Tests**: Use `MIGRATION_GUIDE.md` to convert failing Playwright tests
3. **CI/CD Integration**: Add to your GitHub Actions workflow
4. **Customize**: Modify tests for your specific use cases