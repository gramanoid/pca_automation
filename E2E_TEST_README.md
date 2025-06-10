# E2E Test Suite for Media Plan to Raw Data Automation

This directory contains automated end-to-end tests for the Media Plan to Raw Data Automation Streamlit application using Playwright.

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Playwright
pip install -r requirements-e2e.txt

# Install Playwright browsers (required on first setup)
playwright install chromium
```

### 2. Start the Application

Before running tests, ensure the Streamlit application is running:

```bash
# In a separate terminal, start the application
streamlit run streamlit_app.py
```

The application should be accessible at `http://127.0.0.1:8501`

## Running the Tests

### Headless Mode (Default)

Run tests in the background without visible browser:

```bash
python test_e2e_workflow.py
```

### Headed Mode (Debugging)

Run tests with visible browser for debugging:

```bash
python test_e2e_workflow.py --headed
```

### Slow Motion Mode

Run tests with slower actions for better visibility:

```bash
python test_e2e_workflow.py --headed --slow-mo 500
```

## Test Scenarios

The test suite includes the following scenarios:

### Scenario 1: Application Load Test
- Verifies the application loads successfully
- Checks for presence of file uploader
- Confirms process button is visible

### Scenario 2: File Processing Test
- Uploads a test file
- Initiates data processing
- Verifies successful completion
- Checks for output/results

## Test Output

- **Console Output**: Detailed test progress and results
- **Screenshots**: Saved in `test_screenshots/` directory
  - Success screenshots for each test
  - Failure screenshots with error details

## Troubleshooting

### Common Issues

1. **Application not running**: Ensure Streamlit is running at `http://127.0.0.1:8501`
2. **File not found**: Verify test files exist in the `input/` directory
3. **Timeout errors**: The application may be slow to load; tests have 30-second timeouts
4. **Element not found**: Streamlit's dynamic UI may require adjusting selectors

### Debug Tips

- Run with `--headed` to see what's happening
- Check screenshots in `test_screenshots/` for visual debugging
- Increase timeouts in the script if needed
- Ensure you're using the correct APP_VERSION if testing specific versions

## Test Files

The tests look for input files in these locations:
- `input/PLANNED_INPUT_TEMPLATE_Final Media Plan Template_060525.xlsx`
- `input/sample_media_plan.csv`
- `test_fixtures/PLANNED_TEST_FIXTURE.xlsx`

Ensure at least one of these files exists before running tests.

## Exit Codes

- `0`: All tests passed
- `1`: One or more tests failed