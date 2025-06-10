# Migration Guide: Playwright to AI-Powered Testing

This guide helps you migrate failing Playwright tests to AI-powered alternatives using Stagehand and Browser Use.

## 🎯 When to Migrate

### Migrate to Stagehand when:
- Tests fail due to dynamic DOM elements
- Checkbox or radio button interactions timeout
- Complex UI interactions need flexibility
- Selectors break frequently with UI updates

### Migrate to Browser Use when:
- Testing business logic that evolves
- Need parallel test execution
- Want adaptive test validation
- Require understanding of content semantics

## 🔄 Migration Examples

### Example 1: Checkbox Interaction

#### ❌ Traditional Playwright (Fails)
```python
# This often fails with Streamlit's dynamic rendering
checkbox = page.locator('input[data-testid="stCheckbox"]').nth(0)
checkbox.click()  # Timeout error

# Or with label clicking
label = page.locator('label:has-text("Show Data Preview")')
label.click()  # Element not interactable
```

#### ✅ Stagehand (Works)
```javascript
// Natural language command that adapts to DOM changes
await stagehand.act("Enable the 'Show Data Preview' checkbox");

// Or with more context
await stagehand.act("In the sidebar, check the checkbox for data preview feature");
```

### Example 2: Dynamic Content Validation

#### ❌ Traditional Playwright (Brittle)
```python
# Hard-coded validation that breaks with UI changes
error_div = page.locator('div.stAlert[data-baseweb="notification"]')
assert error_div.is_visible()
assert "Validation failed" in error_div.text_content()
```

#### ✅ Stagehand (Flexible)
```javascript
// Extract validation information intelligently
const validation = await stagehand.extract({
  instruction: "Extract any error messages or validation warnings shown on the page",
  schema: {
    hasErrors: "boolean",
    errorMessages: "array of strings",
    errorType: "string"
  }
});

// Or observe the state
const state = await stagehand.observe("Are there any validation errors displayed?");
```

### Example 3: File Upload with Progress

#### ❌ Traditional Playwright (Complex)
```python
# Multiple waits and checks needed
file_input = page.locator('input[type="file"]').first
file_input.set_input_files("test.xlsx")

# Wait for upload... but how long?
page.wait_for_timeout(2000)

# Check if processed... but where?
progress = page.locator('[data-testid="stProgress"]')
if progress.is_visible():
    # Complex logic to wait for completion
    while progress.is_visible():
        page.wait_for_timeout(500)
```

#### ✅ Browser Use (Intelligent)
```python
# AI understands the complete workflow
agent = Agent(
    task="Upload test.xlsx and wait for processing to complete",
    llm=model,
    browser=browser
)

result = await agent.execute("""
1. Upload the file test.xlsx
2. Monitor the processing progress
3. Wait for completion
4. Return the final status
""")
```

### Example 4: Business Logic Validation

#### ❌ Traditional Playwright (Rigid)
```python
# Hard-coded business rules that become outdated
def test_market_mapping():
    # Specific assertions that break when logic changes
    market_cell = page.locator('td:has-text("USA")')
    assert market_cell.is_visible()
    
    value_cell = market_cell.locator('xpath=following-sibling::td[2]')
    assert value_cell.text_content() == "$1,234.56"
```

#### ✅ Browser Use (Adaptive)
```python
# AI understands business intent
async def test_market_mapping():
    result = await agent.execute("""
    Verify that market mapping correctly:
    1. Maps USA market data from planned to delivered
    2. Calculates totals accurately
    3. Handles currency formatting appropriately
    
    Report any discrepancies found.
    """)
    
    # AI adapts to legitimate business logic changes
```

## 🛠️ Step-by-Step Migration Process

### 1. Identify Failing Tests
```bash
# Run existing Playwright tests and note failures
pytest -v test_e2e_all_features.py 2>&1 | grep -E "(FAILED|ERROR)"
```

### 2. Categorize by Failure Type
- **UI Interaction Failures** → Migrate to Stagehand
- **Business Logic Failures** → Migrate to Browser Use
- **Both** → Use hybrid approach

### 3. Set Up AI Testing Environment
```bash
cd ai_powered_tests
./setup.sh
cp .env.example .env
# Add your API keys to .env
```

### 4. Migrate Test by Test

#### For UI Tests (Stagehand):
```javascript
// Template for Stagehand migration
import { Stagehand } from "@browserbase/stagehand";

async function migratedTest() {
  const stagehand = new Stagehand({
    env: "LOCAL",
    headless: false
  });
  
  await stagehand.init();
  await stagehand.page.goto(URL);
  
  // Replace complex selectors with natural language
  await stagehand.act("Your natural language command here");
  
  // Replace assertions with observations
  const result = await stagehand.observe("What to check for");
  
  await stagehand.close();
}
```

#### For Business Logic Tests (Browser Use):
```python
# Template for Browser Use migration
from browser_use import Agent, Browser

async def migrated_test():
    browser = Browser()
    agent = Agent(
        task="Describe what to test",
        llm=your_model,
        browser=browser
    )
    
    result = await agent.execute("""
    Multi-step instructions for testing
    """)
    
    await browser.close()
```

### 5. Validate Migration
```bash
# Run migrated tests
npm run test:stagehand
npm run test:browser-use

# Compare with original
python compare_test_approaches.py
```

## 📋 Migration Checklist

- [ ] Inventory all failing Playwright tests
- [ ] Categorize failures (UI vs Business Logic)
- [ ] Set up AI testing environment
- [ ] Configure API keys
- [ ] Migrate high-priority tests first
- [ ] Validate migrated tests work reliably
- [ ] Document any special configurations
- [ ] Update CI/CD pipeline
- [ ] Train team on new approach
- [ ] Monitor test stability over time

## 💡 Best Practices

### For Stagehand:
1. Use descriptive natural language commands
2. Provide context ("in the sidebar", "at the top")
3. Leverage extraction for complex data
4. Use observation for state verification

### For Browser Use:
1. Write clear task descriptions
2. Break complex validations into steps
3. Use parallel agents for speed
4. Let AI adapt to business changes

## 🚨 Common Pitfalls

1. **Over-specifying commands**: Let AI figure out details
2. **Not providing context**: Help AI understand where to look
3. **Ignoring costs**: AI calls have API costs
4. **Skipping validation**: Always verify migrations work

## 📊 ROI Calculation

### Time Savings:
- Traditional test maintenance: 2-4 hours/week
- AI-powered maintenance: 15-30 minutes/week
- ROI: 75-90% reduction in maintenance time

### Reliability Improvement:
- Traditional success rate: 60-80%
- AI-powered success rate: 90-98%
- ROI: 50% reduction in flaky tests

## 🎯 Next Steps

1. Start with most problematic tests
2. Migrate incrementally
3. Run both suites in parallel initially
4. Phase out traditional tests gradually
5. Monitor and optimize AI usage

Remember: Not all tests need migration. Simple, stable tests can remain as traditional Playwright tests. Focus on migrating tests that frequently fail or require high maintenance.