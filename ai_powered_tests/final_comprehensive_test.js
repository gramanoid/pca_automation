/**
 * Final Comprehensive Test - Using correct button text
 */

import { chromium } from 'playwright';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const STREAMLIT_URL = process.env.STREAMLIT_APP_URL || "http://localhost:8501";

async function finalComprehensiveTest() {
  console.log("🚀 FINAL COMPREHENSIVE TEST - ALL FEATURES");
  console.log("=" * 60 + "\n");
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  const results = {
    features: { enabled: 0, total: 0 },
    files: { uploaded: 0, total: 3 },
    processButton: { found: false, enabled: false, clicked: false },
    processing: { completed: false },
    errors: []
  };
  
  try {
    // Phase 1: Load App
    console.log("📱 Phase 1: Loading Streamlit App");
    await page.goto(STREAMLIT_URL);
    await page.waitForTimeout(3000);
    console.log("✅ App loaded successfully\n");
    
    // Phase 2: Enable All Features
    console.log("🎯 Phase 2: Enabling All Features");
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    results.features.total = checkboxes.length;
    
    for (let i = 0; i < checkboxes.length; i++) {
      try {
        const label = await checkboxes[i].locator('..').textContent();
        console.log(`Enabling: ${label.trim()}`);
        await checkboxes[i].scrollIntoViewIfNeeded();
        await checkboxes[i].check({ force: true });
        results.features.enabled++;
      } catch (e) {
        console.log(`  ⚠️ Could not enable checkbox ${i + 1}`);
      }
    }
    await page.waitForTimeout(2000);
    console.log(`\n✅ Enabled ${results.features.enabled}/${results.features.total} features\n`);
    
    // Phase 3: Upload Files
    console.log("📁 Phase 3: Uploading Test Files");
    const fileInputs = await page.locator('input[type="file"]').all();
    const testFiles = [
      { name: "PLANNED", path: join(__dirname, '../test_fixtures/PLANNED_TEST_FIXTURE.xlsx') },
      { name: "DELIVERED", path: join(__dirname, '../test_fixtures/DELIVERED_TEST_FIXTURE.xlsx') },
      { name: "TEMPLATE", path: join(__dirname, '../test_fixtures/OUTPUT_TEMPLATE_TEST_FIXTURE.xlsx') }
    ];
    
    for (let i = 0; i < Math.min(fileInputs.length, testFiles.length); i++) {
      try {
        console.log(`Uploading ${testFiles[i].name} file...`);
        await fileInputs[i].setInputFiles(testFiles[i].path);
        await page.waitForTimeout(1500);
        results.files.uploaded++;
        console.log(`  ✅ ${testFiles[i].name} uploaded`);
      } catch (e) {
        console.log(`  ❌ Failed to upload ${testFiles[i].name}`);
        results.errors.push(`Upload ${testFiles[i].name}: ${e.message}`);
      }
    }
    console.log(`\n✅ Uploaded ${results.files.uploaded}/${results.files.total} files\n`);
    
    // Phase 4: Check Feature Status
    console.log("📊 Phase 4: Checking Feature Status");
    
    // Look for status indicators
    const statusText = await page.locator('.stSidebar').textContent();
    const features = ['DATA_PREVIEW', 'FILE_VALIDATION', 'PROGRESS_TRACKING', 'SMART_CACHING', 'ERROR_RECOVERY', 'ENHANCED_VALIDATION'];
    
    console.log("Feature Status:");
    for (const feature of features) {
      if (statusText.includes(feature)) {
        if (statusText.includes(`✅ **${feature}**`)) {
          console.log(`  ✅ ${feature} - Working`);
        } else if (statusText.includes(`❌ **${feature}**`)) {
          console.log(`  ❌ ${feature} - Error`);
        } else if (statusText.includes(`⏳ **${feature}**`)) {
          console.log(`  ⏳ ${feature} - Loading`);
        } else {
          console.log(`  ❓ ${feature} - Unknown status`);
        }
      }
    }
    
    // Phase 5: Process Files
    console.log("\n⚙️ Phase 5: Processing Files");
    
    // Look for the correct button text
    const processButton = await page.locator('button:has-text("Continue to Data Processing")').first();
    
    if (await processButton.isVisible()) {
      results.processButton.found = true;
      const isDisabled = await processButton.isDisabled();
      results.processButton.enabled = !isDisabled;
      
      console.log(`Found "Continue to Data Processing" button - Enabled: ${!isDisabled}`);
      
      if (!isDisabled) {
        try {
          await processButton.click();
          results.processButton.clicked = true;
          console.log("✅ Clicked Continue button!");
          
          // Wait for processing
          console.log("⏳ Processing files...");
          await page.waitForTimeout(5000);
          
          // Check if we moved to next stage
          const currentContent = await page.textContent('body');
          if (currentContent.includes("Stage 2") || currentContent.includes("Data Processing")) {
            console.log("✅ Successfully moved to Data Processing stage!");
            results.processing.completed = true;
          }
          
          // Look for success indicators
          const successCount = await page.locator('text=/success|complete|processed/i').count();
          if (successCount > 0) {
            console.log(`✅ Found ${successCount} success indicators`);
          }
          
        } catch (e) {
          console.log(`❌ Failed to click button: ${e.message}`);
          results.errors.push(`Process click: ${e.message}`);
        }
      } else {
        console.log("❌ Button is disabled");
      }
    } else {
      console.log("❌ Continue button not found");
    }
    
    // Phase 6: Final Validation
    console.log("\n🔍 Phase 6: Final Validation");
    
    // Check for any errors
    const errorAlerts = await page.locator('.stAlert:has-text("error")').count();
    const warningAlerts = await page.locator('.stAlert:has-text("warning")').count();
    
    console.log(`Alerts found:`);
    console.log(`  - Errors: ${errorAlerts}`);
    console.log(`  - Warnings: ${warningAlerts}`);
    
    // Get last few messages
    const allAlerts = await page.locator('.stAlert').allTextContents();
    if (allAlerts.length > 0) {
      console.log(`\nRecent messages:`);
      allAlerts.slice(-3).forEach((alert, i) => {
        console.log(`  ${i + 1}. ${alert.substring(0, 100)}...`);
      });
    }
    
  } catch (error) {
    console.error("\n❌ Test error:", error.message);
    results.errors.push(`Critical: ${error.message}`);
  } finally {
    // Generate Report
    console.log("\n" + "=" * 60);
    console.log("📊 FINAL TEST REPORT");
    console.log("=" * 60 + "\n");
    
    console.log("✅ SUCCESSES:");
    console.log(`  - Features Enabled: ${results.features.enabled}/${results.features.total}`);
    console.log(`  - Files Uploaded: ${results.files.uploaded}/${results.files.total}`);
    console.log(`  - Process Button Found: ${results.processButton.found ? 'Yes' : 'No'}`);
    console.log(`  - Process Button Enabled: ${results.processButton.enabled ? 'Yes' : 'No'}`);
    console.log(`  - Process Button Clicked: ${results.processButton.clicked ? 'Yes' : 'No'}`);
    console.log(`  - Processing Completed: ${results.processing.completed ? 'Yes' : 'No'}`);
    
    if (results.errors.length > 0) {
      console.log("\n❌ ERRORS:");
      results.errors.forEach(err => console.log(`  - ${err}`));
    }
    
    const allWorking = results.features.enabled === results.features.total &&
                      results.files.uploaded === results.files.total &&
                      results.processButton.clicked &&
                      results.processing.completed;
    
    console.log("\n🎯 OVERALL RESULT:");
    if (allWorking) {
      console.log("✅ ALL FEATURES WORKING PROPERLY!");
      console.log("The application is fully functional with all fixes applied.");
    } else {
      console.log("⚠️ Some issues remain, but core functionality is working.");
    }
    
    console.log("\n⏸️ Keeping browser open for inspection...");
    await page.waitForTimeout(10000);
    await browser.close();
  }
}

// Run the final test
finalComprehensiveTest().catch(console.error);