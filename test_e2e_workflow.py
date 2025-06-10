"""
End-to-End Test Script for Media Plan to Raw Data Automation
Uses Playwright with Python to test the Streamlit application
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, expect


class TestMediaPlanAutomation:
    """E2E test suite for Media Plan to Raw Data Automation application"""
    
    def __init__(self, headed=False, slow_mo=0):
        self.headed = headed
        self.slow_mo = slow_mo
        self.base_url = "http://127.0.0.1:8501"
        self.screenshots_dir = Path("test_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
    def take_screenshot(self, page, name):
        """Take a screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.png"
        filepath = self.screenshots_dir / filename
        page.screenshot(path=str(filepath))
        print(f"Screenshot saved: {filepath}")
        
    def setup_browser(self, playwright):
        """Setup browser with configuration"""
        browser = playwright.chromium.launch(
            headless=not self.headed,
            slow_mo=self.slow_mo
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True
        )
        page = context.new_page()
        
        # Set longer timeout for Streamlit apps (they can be slow to load)
        page.set_default_timeout(30000)  # 30 seconds
        
        return browser, context, page
    
    def test_app_loads(self):
        """Test Scenario 1: Application Loads and Core UI Elements are Present"""
        print("\n=== Running Test Scenario 1: Application Load Test ===")
        
        with sync_playwright() as playwright:
            browser, context, page = self.setup_browser(playwright)
            
            try:
                # Navigate to the application
                print(f"Navigating to {self.base_url}")
                page.goto(self.base_url)
                
                # Wait for Streamlit to fully load
                page.wait_for_load_state("networkidle")
                
                # Assertion 1: Verify page title
                print("Checking page title...")
                # Streamlit apps often have custom titles
                title = page.title()
                assert "Media Plan" in title or "PCA Automation" in title, f"Unexpected title: {title}"
                print(f"✓ Page title verified: {title}")
                
                # Assertion 2: Verify file uploader is present
                print("Looking for file uploader...")
                # Streamlit file uploaders have specific structure
                file_uploader = page.locator('input[type="file"]').first
                assert file_uploader.is_visible(), "File uploader not found"
                print("✓ File uploader is visible")
                
                # Assertion 3: Verify primary action button
                print("Looking for process button...")
                # Look for buttons with various possible texts
                process_button = None
                button_texts = ["Process Data", "Process", "Start Processing", "Run Workflow", "Upload"]
                
                for text in button_texts:
                    try:
                        button = page.get_by_role("button", name=text)
                        if button.is_visible():
                            process_button = button
                            break
                    except:
                        continue
                
                # Also check for Streamlit buttons by class
                if not process_button:
                    buttons = page.locator('button[kind="primary"], button[kind="secondary"]')
                    if buttons.count() > 0:
                        process_button = buttons.first
                
                assert process_button is not None, "No process button found"
                print("✓ Process button is visible")
                
                # Take success screenshot
                self.take_screenshot(page, "test1_app_loaded_success")
                print("\n✅ Test Scenario 1: PASSED")
                
            except Exception as e:
                print(f"\n❌ Test Scenario 1: FAILED - {str(e)}")
                self.take_screenshot(page, "test1_app_loaded_failure")
                raise
            finally:
                browser.close()
    
    def test_file_processing(self):
        """Test Scenario 2: Successful File Upload, Processing, and Output Verification"""
        print("\n=== Running Test Scenario 2: File Processing Test ===")
        
        with sync_playwright() as playwright:
            browser, context, page = self.setup_browser(playwright)
            
            try:
                # Navigate to the application
                print(f"Navigating to {self.base_url}")
                page.goto(self.base_url)
                page.wait_for_load_state("networkidle")
                
                # Find test file
                test_files = [
                    "input/PLANNED_INPUT_TEMPLATE_Final Media Plan Template_060525.xlsx",
                    "input/sample_media_plan.csv",
                    "test_fixtures/PLANNED_TEST_FIXTURE.xlsx"
                ]
                
                test_file = None
                for file_path in test_files:
                    if os.path.exists(file_path):
                        test_file = file_path
                        break
                
                assert test_file is not None, f"No test file found. Looked for: {test_files}"
                print(f"Using test file: {test_file}")
                
                # Upload file
                print("Uploading file...")
                file_input = page.locator('input[type="file"]').first
                file_input.set_input_files(test_file)
                
                # Wait for file upload to process
                page.wait_for_timeout(2000)  # Give Streamlit time to process
                
                # Verify file upload
                print("Verifying file upload...")
                # Look for filename in the page
                filename = os.path.basename(test_file)
                file_indicator = page.locator(f'text="{filename}"').or_(
                    page.locator(f'text=*{filename[:20]}*')  # Partial match for long names
                )
                
                # Streamlit might show the file in various ways
                if not file_indicator.is_visible():
                    # Check for generic upload success indicators
                    uploaded_indicators = [
                        page.locator('text="File uploaded"'),
                        page.locator('text="1 file uploaded"'),
                        page.locator('[data-testid="stFileUploader"]').locator('text=/.*\\.(xlsx|csv)/')
                    ]
                    
                    file_uploaded = any(ind.is_visible() for ind in uploaded_indicators)
                    assert file_uploaded, "File upload confirmation not found"
                
                print("✓ File uploaded successfully")
                
                # Look for and click process button
                print("Looking for process button...")
                # Try multiple strategies to find the button
                process_button = None
                
                # Strategy 1: Look for specific button texts
                button_texts = ["Process Data", "Process", "Start Processing", "Run Workflow", "Next", "Continue"]
                for text in button_texts:
                    try:
                        button = page.get_by_role("button", name=text)
                        if button.is_visible():
                            process_button = button
                            break
                    except:
                        continue
                
                # Strategy 2: Look for any enabled button after file upload
                if not process_button:
                    all_buttons = page.locator('button:not([disabled])')
                    if all_buttons.count() > 0:
                        # Skip the first button if it's the file uploader button
                        for i in range(all_buttons.count()):
                            btn = all_buttons.nth(i)
                            btn_text = btn.inner_text()
                            if "browse" not in btn_text.lower() and "upload" not in btn_text.lower():
                                process_button = btn
                                break
                
                assert process_button is not None, "Process button not found"
                print(f"✓ Found process button")
                
                # Click process button
                process_button.click()
                print("✓ Clicked process button")
                
                # Wait for processing
                print("Waiting for processing to complete...")
                # Look for processing indicators
                processing_indicators = [
                    page.locator('text="Processing"'),
                    page.locator('text="Loading"'),
                    page.locator('[data-testid="stSpinner"]'),
                    page.locator('.stSpinner'),
                    page.locator('[role="status"]')
                ]
                
                # Wait for any processing indicator to appear and disappear
                for indicator in processing_indicators:
                    try:
                        indicator.wait_for(state="visible", timeout=5000)
                        indicator.wait_for(state="hidden", timeout=60000)
                        break
                    except:
                        continue
                
                # Give extra time for results to render
                page.wait_for_timeout(3000)
                
                # Check for success indicators
                print("Checking for success indicators...")
                success_indicators = [
                    "Data processed successfully",
                    "Processing complete",
                    "Success",
                    "Completed",
                    "Download",
                    "Results",
                    "Validation Results",
                    "Output"
                ]
                
                success_found = False
                for indicator in success_indicators:
                    try:
                        if page.locator(f'text=/{indicator}/i').is_visible():
                            success_found = True
                            print(f"✓ Found success indicator: {indicator}")
                            break
                    except:
                        continue
                
                # Also check for output elements
                if not success_found:
                    # Check for download buttons, data tables, or charts
                    output_elements = [
                        page.locator('button:has-text("Download")'),
                        page.locator('[data-testid="stDataFrame"]'),
                        page.locator('table'),
                        page.locator('[data-testid="stMetric"]'),
                        page.locator('.stDownloadButton')
                    ]
                    
                    for element in output_elements:
                        if element.count() > 0 and element.first.is_visible():
                            success_found = True
                            print("✓ Found output elements")
                            break
                
                assert success_found, "No success indicators or output elements found"
                
                # Take success screenshot
                self.take_screenshot(page, "test2_processing_success")
                print("\n✅ Test Scenario 2: PASSED")
                
            except Exception as e:
                print(f"\n❌ Test Scenario 2: FAILED - {str(e)}")
                self.take_screenshot(page, "test2_processing_failure")
                raise
            finally:
                browser.close()
    
    def run_all_tests(self):
        """Run all test scenarios"""
        print("\n" + "="*60)
        print("MEDIA PLAN TO RAW DATA AUTOMATION - E2E TEST SUITE")
        print("="*60)
        
        results = []
        
        # Run each test
        tests = [
            ("Application Load Test", self.test_app_loads),
            ("File Processing Test", self.test_file_processing)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
                results.append((test_name, "PASSED"))
            except Exception as e:
                results.append((test_name, f"FAILED: {str(e)}"))
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, status in results if status == "PASSED")
        total = len(results)
        
        for test_name, status in results:
            status_symbol = "✅" if status == "PASSED" else "❌"
            print(f"{status_symbol} {test_name}: {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        print("="*60)
        
        return passed == total


def main():
    """Main entry point for the test script"""
    parser = argparse.ArgumentParser(
        description="E2E tests for Media Plan to Raw Data Automation"
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run tests in headed mode (visible browser)"
    )
    parser.add_argument(
        "--slow-mo",
        type=int,
        default=0,
        help="Slow down browser operations by specified milliseconds"
    )
    
    args = parser.parse_args()
    
    # Create test instance
    tester = TestMediaPlanAutomation(
        headed=args.headed,
        slow_mo=args.slow_mo
    )
    
    # Run tests
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()