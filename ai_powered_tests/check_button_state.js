/**
 * Check why Process button is disabled
 */

import { chromium } from 'playwright';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const STREAMLIT_URL = process.env.STREAMLIT_APP_URL || "http://localhost:8501";

async function checkButtonState() {
  console.log("🔍 Checking Process Button State");
  console.log("=" * 60 + "\n");
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate to app
    await page.goto(STREAMLIT_URL);
    await page.waitForTimeout(3000);
    
    // Enable all features at once (simpler approach)
    console.log("✅ Enabling all features...");
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    for (const cb of checkboxes) {
      try {
        await cb.scrollIntoViewIfNeeded();
        await cb.check({ force: true });
      } catch (e) {
        // Skip if can't check
      }
    }
    await page.waitForTimeout(2000);
    
    // Upload files
    console.log("\n📁 Uploading files...");
    const fileInputs = await page.locator('input[type="file"]').all();
    
    await fileInputs[0].setInputFiles(join(__dirname, '../test_fixtures/PLANNED_TEST_FIXTURE.xlsx'));
    await page.waitForTimeout(1000);
    await fileInputs[1].setInputFiles(join(__dirname, '../test_fixtures/DELIVERED_TEST_FIXTURE.xlsx'));
    await page.waitForTimeout(1000);
    await fileInputs[2].setInputFiles(join(__dirname, '../test_fixtures/OUTPUT_TEMPLATE_TEST_FIXTURE.xlsx'));
    await page.waitForTimeout(2000);
    
    // Now check ALL buttons
    console.log("\n🔘 Checking ALL buttons in the app:");
    const allButtons = await page.locator('button').all();
    
    console.log(`Found ${allButtons.length} buttons total:\n`);
    
    for (let i = 0; i < allButtons.length; i++) {
      const button = allButtons[i];
      const text = await button.textContent();
      const isDisabled = await button.isDisabled();
      const isVisible = await button.isVisible();
      
      console.log(`Button ${i + 1}:`);
      console.log(`  Text: "${text.trim()}"`);
      console.log(`  Disabled: ${isDisabled}`);
      console.log(`  Visible: ${isVisible}`);
      
      // Check if this might be our process button
      if (text.toLowerCase().includes('process') || 
          text.toLowerCase().includes('continue') || 
          text.toLowerCase().includes('next')) {
        console.log(`  >>> POTENTIAL PROCESS BUTTON <<<`);
        
        // Get more details
        const buttonInfo = await button.evaluate(el => {
          return {
            fullHTML: el.outerHTML.substring(0, 200),
            parent: el.parentElement?.className,
            onclick: el.onclick ? 'Has onclick' : 'No onclick'
          };
        });
        console.log(`  Details:`, buttonInfo);
      }
      console.log("");
    }
    
    // Check for stage navigation
    console.log("\n📍 Checking for stage/navigation elements:");
    const stageElements = await page.locator('text=/Stage|Step|Continue|Next|Process/i').all();
    console.log(`Found ${stageElements.length} potential navigation elements`);
    
    for (const elem of stageElements.slice(0, 5)) {
      const text = await elem.textContent();
      console.log(`- "${text.trim().substring(0, 50)}..."`);
    }
    
    // Check main content area
    console.log("\n📄 Checking main content area:");
    const mainContent = await page.locator('.main').textContent();
    if (mainContent.includes("Process")) {
      console.log("✅ Found 'Process' in main content");
    }
    if (mainContent.includes("Continue")) {
      console.log("✅ Found 'Continue' in main content");
    }
    
    // Check for any error messages
    console.log("\n⚠️  Checking for errors/warnings:");
    const alerts = await page.locator('.stAlert').allTextContents();
    if (alerts.length > 0) {
      console.log(`Found ${alerts.length} alerts:`);
      alerts.slice(-3).forEach((alert, i) => {
        console.log(`${i + 1}. ${alert.substring(0, 100)}...`);
      });
    }
    
  } catch (error) {
    console.error("\n❌ Error:", error.message);
  } finally {
    console.log("\n⏸️  Keeping browser open for inspection...");
    await page.waitForTimeout(10000);
    await browser.close();
  }
}

// Run the check
checkButtonState().catch(console.error);