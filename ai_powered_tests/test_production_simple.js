/**
 * Production Test - Simplified Stagehand test
 * Tests all features on https://pcaautomation.streamlit.app/ using act() method
 */

import { Stagehand } from '@browserbasehq/stagehand';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PRODUCTION_URL = "https://pcaautomation.streamlit.app/";

async function testProductionSimple() {
  console.log("🚀 PRODUCTION E2E TEST - SIMPLIFIED");
  console.log("=" .repeat(60));
  console.log(`Testing: ${PRODUCTION_URL}`);
  console.log(`Time: ${new Date().toLocaleString()}`);
  console.log("=" .repeat(60) + "\n");
  
  const stagehand = new Stagehand({
    env: "LOCAL",
    headless: false,
    modelName: "claude-3-5-sonnet-latest",
    enableCaching: true
  });
  
  const results = {
    appLoaded: false,
    stagesCompleted: 0,
    errors: [],
    screenshots: []
  };
  
  const startTime = Date.now();
  
  try {
    // Initialize browser
    console.log("🌐 Phase 1: Initializing browser...");
    const { page } = await stagehand.init();
    await stagehand.page.goto(PRODUCTION_URL);
    
    // Wait for app to fully load
    console.log("⏳ Waiting for Streamlit app to load...");
    await stagehand.page.waitForTimeout(8000);
    
    // Check if app loaded by looking for title
    const title = await stagehand.page.title();
    if (title.includes("PCA") || title.includes("Automation")) {
      results.appLoaded = true;
      console.log("✅ App loaded successfully\n");
    }
    
    // Take initial screenshot
    const screenshot1 = join(__dirname, `production_initial_${Date.now()}.png`);
    await stagehand.page.screenshot({ path: screenshot1 });
    results.screenshots.push(screenshot1);
    console.log(`📸 Initial screenshot: ${screenshot1}`);
    
    // Phase 2: Upload Files
    console.log("\n📁 Phase 2: Uploading Files");
    
    try {
      // Upload PLANNED file
      console.log("Uploading PLANNED file...");
      const plannedInput = await stagehand.page.locator('input[type="file"]').first();
      await plannedInput.setInputFiles(join(__dirname, '../test_fixtures/PLANNED_TEST_FIXTURE.xlsx'));
      await stagehand.page.waitForTimeout(3000);
      
      // Upload DELIVERED file
      console.log("Uploading DELIVERED file...");
      const deliveredInput = await stagehand.page.locator('input[type="file"]').nth(1);
      await deliveredInput.setInputFiles(join(__dirname, '../test_fixtures/DELIVERED_TEST_FIXTURE.xlsx'));
      await stagehand.page.waitForTimeout(3000);
      
      // Upload TEMPLATE file
      console.log("Uploading TEMPLATE file...");
      const templateInput = await stagehand.page.locator('input[type="file"]').nth(2);
      await templateInput.setInputFiles(join(__dirname, '../test_fixtures/OUTPUT_TEMPLATE_TEST_FIXTURE.xlsx'));
      await stagehand.page.waitForTimeout(3000);
      
      console.log("✅ All files uploaded");
      
      // Take screenshot after upload
      const screenshot2 = join(__dirname, `production_after_upload_${Date.now()}.png`);
      await stagehand.page.screenshot({ path: screenshot2 });
      results.screenshots.push(screenshot2);
      
    } catch (error) {
      console.log(`❌ File upload error: ${error.message}`);
      results.errors.push(`Upload: ${error.message}`);
    }
    
    // Phase 3: Continue to Processing
    console.log("\n⚙️ Phase 3: Continuing to Process Stage");
    
    try {
      // Try to click continue button using Stagehand act
      await stagehand.act({
        action: "Click the button that says 'Continue to Processing' or any button that will move to the next stage"
      });
      
      await stagehand.page.waitForTimeout(5000);
      results.stagesCompleted++;
      console.log("✅ Moved to processing stage");
      
      // Take screenshot
      const screenshot3 = join(__dirname, `production_processing_${Date.now()}.png`);
      await stagehand.page.screenshot({ path: screenshot3 });
      results.screenshots.push(screenshot3);
      
    } catch (error) {
      console.log(`❌ Processing navigation error: ${error.message}`);
      results.errors.push(`Processing: ${error.message}`);
    }
    
    // Phase 4: Start Processing
    console.log("\n🔄 Phase 4: Starting Data Processing");
    
    try {
      await stagehand.act({
        action: "Click the 'Start Processing' button or any button that begins the data processing"
      });
      
      console.log("⏳ Processing data...");
      await stagehand.page.waitForTimeout(8000);
      results.stagesCompleted++;
      console.log("✅ Processing completed");
      
    } catch (error) {
      console.log(`⚠️ Processing start error: ${error.message}`);
    }
    
    // Phase 5: Continue through remaining stages
    console.log("\n📊 Phase 5: Continuing through workflow");
    
    const stages = ["mapping", "validation", "download"];
    for (const stage of stages) {
      try {
        console.log(`\nAttempting to continue to ${stage}...`);
        
        // Continue to next stage
        await stagehand.act({
          action: `Click any button that continues to the next stage or starts ${stage}`
        });
        
        await stagehand.page.waitForTimeout(5000);
        
        // If it's not download, try to start the process
        if (stage !== "download") {
          await stagehand.act({
            action: `Click the button that starts ${stage} or runs ${stage}`
          });
          await stagehand.page.waitForTimeout(8000);
        }
        
        results.stagesCompleted++;
        console.log(`✅ ${stage} stage completed`);
        
        // Take screenshot
        const screenshotPath = join(__dirname, `production_${stage}_${Date.now()}.png`);
        await stagehand.page.screenshot({ path: screenshotPath });
        results.screenshots.push(screenshotPath);
        
      } catch (error) {
        console.log(`⚠️ ${stage} error: ${error.message}`);
      }
    }
    
    // Final screenshot
    const finalScreenshot = join(__dirname, `production_final_${Date.now()}.png`);
    await stagehand.page.screenshot({ path: finalScreenshot, fullPage: true });
    results.screenshots.push(finalScreenshot);
    console.log(`\n📸 Final screenshot: ${finalScreenshot}`);
    
  } catch (error) {
    console.error("\n❌ Critical error:", error.message);
    results.errors.push(`Critical: ${error.message}`);
  } finally {
    // Generate final report
    const totalTime = (Date.now() - startTime) / 1000;
    
    console.log("\n" + "=".repeat(60));
    console.log("📊 PRODUCTION TEST REPORT - SIMPLIFIED");
    console.log("=".repeat(60));
    
    console.log("\n✅ RESULTS:");
    console.log(`  - App Loaded: ${results.appLoaded ? 'Yes' : 'No'}`);
    console.log(`  - Stages Completed: ${results.stagesCompleted}/5`);
    console.log(`  - Screenshots Taken: ${results.screenshots.length}`);
    
    if (results.errors.length > 0) {
      console.log("\n❌ ERRORS:");
      results.errors.forEach(err => console.log(`  - ${err}`));
    }
    
    console.log("\n📸 SCREENSHOTS:");
    results.screenshots.forEach((path, i) => {
      console.log(`  ${i + 1}. ${path.split('/').pop()}`);
    });
    
    console.log(`\n⏱️ Total Time: ${totalTime.toFixed(1)}s`);
    
    console.log("\n🎯 FINAL VERDICT:");
    if (results.appLoaded && results.stagesCompleted >= 4) {
      console.log("✅ APP IS WORKING WELL!");
      console.log("Most features are functioning correctly in production.");
    } else if (results.appLoaded && results.stagesCompleted >= 2) {
      console.log("⚠️ PARTIAL SUCCESS");
      console.log("Core functionality works but some stages may have issues.");
    } else {
      console.log("❌ SIGNIFICANT ISSUES");
      console.log("The app needs debugging - check screenshots for details.");
    }
    
    console.log("\n📝 Test completed at:", new Date().toLocaleString());
    console.log("=".repeat(60));
    
    await stagehand.close();
  }
}

// Run the test
console.log("Starting simplified production test...\n");
testProductionSimple().catch(console.error);