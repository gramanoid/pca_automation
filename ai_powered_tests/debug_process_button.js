/**
 * Debug test to understand why Process button remains disabled
 */

import { chromium } from 'playwright';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const STREAMLIT_URL = process.env.STREAMLIT_APP_URL || "http://localhost:8501";

async function debugProcessButton() {
  console.log("🔍 DEBUG: Process Button Investigation");
  console.log("=" * 60 + "\n");
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate to app
    console.log("📱 Loading app...");
    await page.goto(STREAMLIT_URL);
    await page.waitForTimeout(3000);
    
    // Enable Debug Mode specifically
    console.log("\n🔧 Enabling Debug Mode first...");
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    const debugCheckbox = checkboxes[checkboxes.length - 1]; // Debug Mode is last
    await debugCheckbox.check({ force: true });
    await page.waitForTimeout(1000);
    
    // Enable File Validation
    console.log("📋 Enabling File Validation...");
    const fileValidationCheckbox = checkboxes[1]; // File Validation is second
    await fileValidationCheckbox.check({ force: true });
    await page.waitForTimeout(1000);
    
    // Now enable all other features
    console.log("✅ Enabling all other features...");
    for (let i = 0; i < checkboxes.length - 1; i++) {
      if (i !== 1) { // Skip File Validation, already enabled
        await checkboxes[i].check({ force: true });
      }
    }
    await page.waitForTimeout(2000);
    
    // Look for debug information
    console.log("\n📊 Looking for Debug Information:");
    const debugInfo = await page.locator('text=/Debug Info|Uploaded files:|Validation states:/').all();
    console.log(`Found ${debugInfo.length} debug sections`);
    
    // Get all text from sidebar
    const sidebarText = await page.locator('.stSidebar').textContent();
    console.log("\n📝 Sidebar content includes:");
    if (sidebarText.includes("Debug Info")) {
      console.log("✅ Debug Info section found");
      
      // Extract debug details
      const uploadedMatch = sidebarText.match(/Uploaded files: (\{[^}]*\})/);
      const validationMatch = sidebarText.match(/Validation states: (\{[^}]*\})/);
      
      if (uploadedMatch) console.log(`Uploaded files: ${uploadedMatch[1]}`);
      if (validationMatch) console.log(`Validation states: ${validationMatch[1]}`);
    } else {
      console.log("❌ Debug Info section NOT found");
    }
    
    // Upload files
    console.log("\n📁 Uploading test files:");
    const fileInputs = await page.locator('input[type="file"]').all();
    console.log(`Found ${fileInputs.length} file inputs`);
    
    // Upload each file
    const files = [
      { type: "PLANNED", path: join(__dirname, '../test_fixtures/PLANNED_TEST_FIXTURE.xlsx') },
      { type: "DELIVERED", path: join(__dirname, '../test_fixtures/DELIVERED_TEST_FIXTURE.xlsx') },
      { type: "TEMPLATE", path: join(__dirname, '../test_fixtures/OUTPUT_TEMPLATE_TEST_FIXTURE.xlsx') }
    ];
    
    for (let i = 0; i < Math.min(fileInputs.length, files.length); i++) {
      console.log(`Uploading ${files[i].type}...`);
      await fileInputs[i].setInputFiles(files[i].path);
      await page.waitForTimeout(2000);
      
      // Check for validation messages
      const alerts = await page.locator('.stAlert').allTextContents();
      const recentAlerts = alerts.slice(-3); // Get last 3 alerts
      if (recentAlerts.length > 0) {
        console.log(`  Recent messages:`);
        recentAlerts.forEach(alert => console.log(`    - ${alert.substring(0, 80)}...`));
      }
    }
    
    // Wait for validation to complete
    console.log("\n⏳ Waiting for validation to complete...");
    await page.waitForTimeout(3000);
    
    // Check debug info again
    console.log("\n📊 Checking Debug Info after uploads:");
    const sidebarTextAfter = await page.locator('.stSidebar').textContent();
    
    // Extract session state info
    const sessionInfo = await page.evaluate(() => {
      // Try to access Streamlit's session state if available
      try {
        return {
          hasStreamlit: typeof window.streamlit !== 'undefined',
          // Can't directly access st.session_state from browser
        };
      } catch (e) {
        return { error: e.message };
      }
    });
    console.log("Browser session info:", sessionInfo);
    
    // Check for Process button
    console.log("\n🔘 Checking Process button:");
    const processButtons = await page.locator('button').all();
    let foundProcessButton = false;
    
    for (const button of processButtons) {
      const text = await button.textContent();
      const isDisabled = await button.isDisabled();
      
      if (text.includes("Process") || text.includes("Continue")) {
        foundProcessButton = true;
        console.log(`Found button: "${text}" - Disabled: ${isDisabled}`);
        
        if (isDisabled) {
          // Try to understand why
          const buttonElement = await button.elementHandle();
          const attributes = await buttonElement.evaluate(el => {
            return {
              disabled: el.disabled,
              ariaDisabled: el.getAttribute('aria-disabled'),
              className: el.className,
              dataTestId: el.getAttribute('data-testid')
            };
          });
          console.log("Button attributes:", attributes);
        }
      }
    }
    
    if (!foundProcessButton) {
      console.log("❌ No Process/Continue button found!");
    }
    
    // Check for any warnings about missing files
    console.log("\n⚠️  Checking for warnings:");
    const warnings = await page.locator('.stAlert[data-baseweb="notification"]').all();
    console.log(`Found ${warnings.length} alerts`);
    
    for (const warning of warnings.slice(-5)) { // Last 5 warnings
      const text = await warning.textContent();
      console.log(`- ${text.substring(0, 100)}...`);
    }
    
    // Final summary
    console.log("\n" + "=" * 60);
    console.log("📊 SUMMARY:");
    console.log("- Debug Mode: " + (sidebarText.includes("Debug Mode") ? "Enabled" : "Not found"));
    console.log("- File Inputs: " + fileInputs.length);
    console.log("- Process Button: " + (foundProcessButton ? "Found" : "Not found"));
    console.log("- Debug Info Section: " + (sidebarText.includes("Debug Info") ? "Visible" : "Not visible"));
    
  } catch (error) {
    console.error("\n❌ Test error:", error);
  } finally {
    console.log("\n⏸️  Keeping browser open for manual inspection...");
    await page.waitForTimeout(10000); // Keep open longer for debugging
    await browser.close();
  }
}

// Run the debug test
debugProcessButton().catch(console.error);