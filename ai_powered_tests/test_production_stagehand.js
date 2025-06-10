/**
 * Production Test - Stagehand E2E Test on Live Streamlit App
 * Tests all features on https://pcaautomation.streamlit.app/
 */

import { Stagehand } from '@browserbasehq/stagehand';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs/promises';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PRODUCTION_URL = "https://pcaautomation.streamlit.app/";

async function testProductionApp() {
  console.log("🚀 PRODUCTION E2E TEST - PCA AUTOMATION");
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
    filesUploaded: { planned: false, delivered: false, template: false },
    stages: { upload: false, process: false, map: false, validate: false, download: false },
    features: [],
    errors: [],
    warnings: [],
    timeTaken: {}
  };
  
  const startTime = Date.now();
  
  try {
    // Initialize browser
    console.log("🌐 Phase 1: Initializing browser...");
    const { page } = await stagehand.init();
    await stagehand.page.goto(PRODUCTION_URL);
    
    // Wait for app to fully load
    console.log("⏳ Waiting for Streamlit app to load...");
    await stagehand.page.waitForTimeout(5000);
    
    // Check if app loaded
    const appContent = await stagehand.page.content();
    if (appContent.includes("PCA Automation")) {
      results.appLoaded = true;
      console.log("✅ App loaded successfully\n");
    } else {
      throw new Error("App did not load properly");
    }
    
    // Phase 2: Test File Upload Stage
    console.log("📁 Phase 2: Testing File Upload Stage");
    results.timeTaken.uploadStart = Date.now();
    
    // Check current stage
    const stageIndicator = await stagehand.extract({
      instruction: "Find the current stage indicator. Look for text like 'Stage 1' or 'Upload' that indicates we're in the upload stage"
    });
    console.log(`Current stage: ${stageIndicator || 'Unknown'}`);
    
    // Upload test files
    const testFiles = [
      { 
        type: "PLANNED", 
        path: join(__dirname, '../test_fixtures/PLANNED_TEST_FIXTURE.xlsx'),
        selector: 'input[type="file"]:first-of-type'
      },
      { 
        type: "DELIVERED", 
        path: join(__dirname, '../test_fixtures/DELIVERED_TEST_FIXTURE.xlsx'),
        selector: 'input[type="file"]:nth-of-type(2)'
      },
      { 
        type: "TEMPLATE", 
        path: join(__dirname, '../test_fixtures/OUTPUT_TEMPLATE_TEST_FIXTURE.xlsx'),
        selector: 'input[type="file"]:nth-of-type(3)'
      }
    ];
    
    console.log("\n📤 Uploading test files...");
    
    for (const file of testFiles) {
      try {
        // Check if file exists
        await fs.access(file.path);
        
        // Find the specific file input
        const fileInputs = await stagehand.page.locator('input[type="file"]').all();
        const inputIndex = file.type === 'PLANNED' ? 0 : file.type === 'DELIVERED' ? 1 : 2;
        
        if (fileInputs[inputIndex]) {
          console.log(`  Uploading ${file.type} file...`);
          await fileInputs[inputIndex].setInputFiles(file.path);
          await stagehand.page.waitForTimeout(2000);
          
          // Verify upload success
          const uploadSuccess = await stagehand.extract({
            instruction: `Check if ${file.type} file was uploaded successfully. Look for success messages or the filename being displayed`
          });
          
          if (uploadSuccess && uploadSuccess.includes('success')) {
            results.filesUploaded[file.type.toLowerCase()] = true;
            console.log(`  ✅ ${file.type} file uploaded successfully`);
          } else {
            console.log(`  ⚠️ ${file.type} file upload status unclear`);
          }
        }
      } catch (error) {
        console.log(`  ❌ Failed to upload ${file.type}: ${error.message}`);
        results.errors.push(`Upload ${file.type}: ${error.message}`);
      }
    }
    
    results.timeTaken.uploadEnd = Date.now();
    console.log(`\n⏱️ Upload phase took: ${(results.timeTaken.uploadEnd - results.timeTaken.uploadStart) / 1000}s`);
    
    // Phase 3: Continue to Processing
    console.log("\n⚙️ Phase 3: Testing Data Processing Stage");
    results.timeTaken.processStart = Date.now();
    
    try {
      // Use Stagehand to find and click the continue button
      await stagehand.act({
        action: "Click the button to continue to data processing or proceed to the next stage"
      });
      
      await stagehand.page.waitForTimeout(3000);
      
      // Check if we moved to processing stage
      const processingStage = await stagehand.extract({
        instruction: "Check if we are now in the data processing stage. Look for 'Stage 2' or 'Process' or 'Data Processing'"
      });
      
      if (processingStage && processingStage.toLowerCase().includes('process')) {
        results.stages.upload = true;
        results.stages.process = true;
        console.log("✅ Successfully moved to processing stage");
        
        // Click process button
        await stagehand.act({
          action: "Click the button to start processing the data"
        });
        
        console.log("⏳ Processing data...");
        await stagehand.page.waitForTimeout(5000);
        
        // Check processing results
        const processResults = await stagehand.extract({
          instruction: "Check if data processing completed successfully. Look for success messages or completion indicators"
        });
        
        console.log(`Processing result: ${processResults || 'Unknown'}`);
      }
    } catch (error) {
      console.log(`❌ Processing stage error: ${error.message}`);
      results.errors.push(`Processing: ${error.message}`);
    }
    
    results.timeTaken.processEnd = Date.now();
    
    // Phase 4: Template Mapping
    console.log("\n🗺️ Phase 4: Testing Template Mapping");
    results.timeTaken.mapStart = Date.now();
    
    try {
      // Continue to mapping
      await stagehand.act({
        action: "Click the button to continue to template mapping or the next stage"
      });
      
      await stagehand.page.waitForTimeout(3000);
      
      // Start mapping
      await stagehand.act({
        action: "Click the button to start mapping the data to the template"
      });
      
      console.log("⏳ Mapping data to template...");
      await stagehand.page.waitForTimeout(5000);
      
      const mappingResults = await stagehand.extract({
        instruction: "Check if template mapping completed successfully. Look for mapped columns count or success messages"
      });
      
      if (mappingResults) {
        results.stages.map = true;
        console.log(`✅ Mapping completed: ${mappingResults}`);
      }
    } catch (error) {
      console.log(`❌ Mapping stage error: ${error.message}`);
      results.errors.push(`Mapping: ${error.message}`);
    }
    
    results.timeTaken.mapEnd = Date.now();
    
    // Phase 5: Validation
    console.log("\n✓ Phase 5: Testing Data Validation");
    results.timeTaken.validateStart = Date.now();
    
    try {
      // Continue to validation
      await stagehand.act({
        action: "Click the button to continue to data validation or the next stage"
      });
      
      await stagehand.page.waitForTimeout(3000);
      
      // Run validation
      await stagehand.act({
        action: "Click the button to run data validation"
      });
      
      console.log("⏳ Validating data...");
      await stagehand.page.waitForTimeout(5000);
      
      const validationResults = await stagehand.extract({
        instruction: "Extract the validation results. Look for total checks, passed checks, accuracy percentage, or any errors/warnings"
      });
      
      if (validationResults) {
        results.stages.validate = true;
        console.log(`✅ Validation completed: ${validationResults}`);
      }
    } catch (error) {
      console.log(`❌ Validation stage error: ${error.message}`);
      results.errors.push(`Validation: ${error.message}`);
    }
    
    results.timeTaken.validateEnd = Date.now();
    
    // Phase 6: Download
    console.log("\n📥 Phase 6: Testing Download Stage");
    results.timeTaken.downloadStart = Date.now();
    
    try {
      // Continue to download
      await stagehand.act({
        action: "Click the button to continue to the download stage or complete the workflow"
      });
      
      await stagehand.page.waitForTimeout(3000);
      
      // Check if download button is available
      const downloadAvailable = await stagehand.extract({
        instruction: "Check if a download button is available. Look for 'Download' button or 'Complete' status"
      });
      
      if (downloadAvailable && downloadAvailable.toLowerCase().includes('download')) {
        results.stages.download = true;
        console.log("✅ Download stage reached - workflow complete!");
      }
    } catch (error) {
      console.log(`❌ Download stage error: ${error.message}`);
      results.errors.push(`Download: ${error.message}`);
    }
    
    results.timeTaken.downloadEnd = Date.now();
    
    // Phase 7: Feature Detection
    console.log("\n🔍 Phase 7: Detecting Active Features");
    
    const featureChecks = [
      { name: "Data Preview", indicator: "preview" },
      { name: "File Validation", indicator: "validation" },
      { name: "Progress Tracking", indicator: "progress" },
      { name: "Smart Caching", indicator: "cache" },
      { name: "Error Recovery", indicator: "error" },
      { name: "Enhanced Validation", indicator: "enhanced" }
    ];
    
    for (const feature of featureChecks) {
      const featureStatus = await stagehand.extract({
        instruction: `Check if the ${feature.name} feature is active. Look for ${feature.indicator} related functionality or UI elements`
      });
      
      if (featureStatus) {
        results.features.push({
          name: feature.name,
          status: "detected",
          details: featureStatus.substring(0, 100)
        });
        console.log(`✅ ${feature.name}: Detected`);
      }
    }
    
    // Phase 8: Final Checks
    console.log("\n🏁 Phase 8: Final Checks");
    
    // Check for any errors on page
    const pageErrors = await stagehand.extract({
      instruction: "Find any error messages, warnings, or alerts displayed on the page"
    });
    
    if (pageErrors) {
      results.warnings.push(pageErrors);
      console.log(`⚠️ Page alerts: ${pageErrors}`);
    }
    
    // Take screenshot
    const screenshotPath = join(__dirname, `production_test_${Date.now()}.png`);
    await stagehand.page.screenshot({ path: screenshotPath });
    console.log(`📸 Screenshot saved: ${screenshotPath}`);
    
  } catch (error) {
    console.error("\n❌ Critical error:", error.message);
    results.errors.push(`Critical: ${error.message}`);
  } finally {
    // Generate final report
    const totalTime = (Date.now() - startTime) / 1000;
    
    console.log("\n" + "=".repeat(60));
    console.log("📊 PRODUCTION TEST REPORT");
    console.log("=".repeat(60));
    
    console.log("\n✅ SUCCESSES:");
    console.log(`  - App Loaded: ${results.appLoaded ? 'Yes' : 'No'}`);
    console.log(`  - Files Uploaded: ${Object.values(results.filesUploaded).filter(v => v).length}/3`);
    console.log(`  - Stages Completed: ${Object.values(results.stages).filter(v => v).length}/5`);
    console.log(`  - Features Detected: ${results.features.length}/6`);
    
    if (results.errors.length > 0) {
      console.log("\n❌ ERRORS:");
      results.errors.forEach(err => console.log(`  - ${err}`));
    }
    
    if (results.warnings.length > 0) {
      console.log("\n⚠️ WARNINGS:");
      results.warnings.forEach(warn => console.log(`  - ${warn.substring(0, 100)}...`));
    }
    
    console.log("\n⏱️ PERFORMANCE:");
    console.log(`  - Total Time: ${totalTime}s`);
    if (results.timeTaken.uploadEnd) {
      console.log(`  - Upload Stage: ${((results.timeTaken.uploadEnd - results.timeTaken.uploadStart) / 1000).toFixed(1)}s`);
    }
    if (results.timeTaken.processEnd) {
      console.log(`  - Process Stage: ${((results.timeTaken.processEnd - results.timeTaken.processStart) / 1000).toFixed(1)}s`);
    }
    if (results.timeTaken.mapEnd) {
      console.log(`  - Map Stage: ${((results.timeTaken.mapEnd - results.timeTaken.mapStart) / 1000).toFixed(1)}s`);
    }
    if (results.timeTaken.validateEnd) {
      console.log(`  - Validate Stage: ${((results.timeTaken.validateEnd - results.timeTaken.validateStart) / 1000).toFixed(1)}s`);
    }
    
    const allStagesComplete = Object.values(results.stages).every(v => v);
    const allFilesUploaded = Object.values(results.filesUploaded).every(v => v);
    
    console.log("\n🎯 FINAL VERDICT:");
    if (results.appLoaded && allFilesUploaded && allStagesComplete) {
      console.log("✅ ALL FEATURES WORKING PERFECTLY!");
      console.log("The production app is fully functional with the new UI/UX design.");
    } else if (results.appLoaded && Object.values(results.stages).filter(v => v).length >= 3) {
      console.log("⚠️ MOSTLY WORKING");
      console.log("Core functionality is operational but some stages may have issues.");
    } else {
      console.log("❌ SIGNIFICANT ISSUES DETECTED");
      console.log("The app has critical problems that need immediate attention.");
    }
    
    console.log("\n📝 Test completed at:", new Date().toLocaleString());
    console.log("=".repeat(60));
    
    await stagehand.close();
  }
}

// Run the production test
console.log("Starting production test...\n");
testProductionApp().catch(console.error);