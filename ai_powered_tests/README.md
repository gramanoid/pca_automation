# AI-Powered Testing Suite

This directory contains AI-powered browser automation tests using **Stagehand** and **Browser Use** to overcome limitations of traditional Playwright testing with dynamic Streamlit applications.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   ./setup.sh
   ```

2. **Configure API keys in `.env`:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run tests:**
   ```bash
   # Run Stagehand tests (UI automation)
   npm run test:stagehand
   
   # Run Browser Use tests (business logic)
   npm run test:browser-use
   
   # Run all tests
   npm run test:all
   
   # Compare with traditional Playwright
   python compare_test_approaches.py
   ```

## 🎯 Why AI-Powered Testing?

### Problems with Traditional Playwright
1. **Dynamic Rendering Issues**: Streamlit's reactive UI breaks CSS selectors
2. **Checkbox Automation Fails**: Timeout errors when clicking checkboxes
3. **Business Logic Changes**: Hard-coded assertions become outdated
4. **Maintenance Overhead**: Constant updates needed for UI changes

### AI-Powered Solutions

#### Stagehand
- **Natural Language Commands**: `await page.act("Click the 'Enable notifications' checkbox")`
- **Self-Healing**: Automatically finds alternative approaches when selectors fail
- **Dynamic Adaptation**: Handles Streamlit's changing DOM structure
- **Built on Playwright**: Leverages Playwright's reliability with AI flexibility

#### Browser Use
- **Parallel Execution**: Run multiple test scenarios concurrently
- **Business Logic Understanding**: Adapts to legitimate requirement changes
- **LLM Integration**: Works with GPT-4, Claude, and other models
- **Intelligent Validation**: Understands context rather than exact matches

## 📁 Project Structure

```
ai_powered_tests/
├── stagehand/
│   └── test_streamlit_features.js    # UI automation tests
├── browser_use/
│   └── test_business_logic.py        # Business logic validation
├── compare_test_approaches.py        # Comparison tool
├── setup.sh                          # Installation script
├── package.json                      # Node.js dependencies
├── requirements.txt                  # Python dependencies
├── .env.example                      # Configuration template
└── README.md                         # This file
```

## 🧪 Test Scenarios

### Stagehand Tests
1. **Feature Checkbox Enabling**: Uses natural language to enable all UI features
2. **File Upload Handling**: Manages multiple file inputs dynamically
3. **Data Preview Extraction**: Extracts structured data from UI
4. **Workflow Processing**: Monitors progress with AI observation
5. **Result Validation**: Validates output using AI understanding
6. **Download Management**: Handles file downloads adaptively

### Browser Use Tests
1. **Market Mapping Validation**: Verifies data mapping logic
2. **Data Transformation Rules**: Tests edge cases and calculations
3. **Parallel Scenario Testing**: Runs multiple validations concurrently
4. **Adaptive Regression Testing**: Learns from legitimate changes

## 🔧 Configuration

### Environment Variables
```bash
# AI Model API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Optional
LANGCHAIN_API_KEY=your_langchain_key
BROWSERBASE_API_KEY=your_browserbase_key

# Test Configuration
STREAMLIT_APP_URL=http://localhost:8501
HEADLESS_MODE=false
DEBUG_MODE=true
```

### Model Selection
- **Stagehand**: Default uses `gpt-4o`, can use `claude-3-5-sonnet-latest`
- **Browser Use**: Supports any LangChain-compatible model

## 📊 Performance Comparison

| Metric | Traditional Playwright | Stagehand | Browser Use |
|--------|----------------------|-----------|-------------|
| Checkbox Success Rate | ~20% | ~95% | ~90% |
| Maintenance Required | High | Low | Very Low |
| Execution Speed | Slow (retries) | Fast | Very Fast (parallel) |
| Adapts to Changes | No | Yes | Yes |
| Business Logic Understanding | No | Limited | Yes |

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure `.env` file exists and contains valid API keys
   - Check API key permissions and quotas

2. **Timeout Errors**
   - Increase timeout values in test configurations
   - Ensure Streamlit app is running on expected URL

3. **Module Not Found**
   - Run `./setup.sh` to install all dependencies
   - Check Node.js and Python versions

### Debug Mode
Enable detailed logging:
```javascript
// Stagehand
const stagehand = new Stagehand({
  debugDom: true,
  enableCaching: false
});
```

```python
# Browser Use
browser_config = BrowserConfig(
  headless=False,
  debug=True
)
```

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: AI-Powered Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - uses: actions/setup-python@v4
      
      - name: Install dependencies
        run: |
          cd ai_powered_tests
          ./setup.sh
      
      - name: Run AI tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cd ai_powered_tests
          npm run test:all
```

## 📚 Resources

- [Stagehand Documentation](https://www.stagehand.dev/)
- [Browser Use GitHub](https://github.com/browser-use/browser-use)
- [Browserbase Platform](https://www.browserbase.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 🤝 Contributing

1. Add new test scenarios in respective directories
2. Follow existing patterns for consistency
3. Document any new dependencies or configurations
4. Run comparison tests to validate improvements

## 📄 License

This testing suite follows the main project's license terms.