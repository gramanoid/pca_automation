/**
 * Comprehensive Stagehand Test - Post-Fix Verification
 * Tests all features after fixes have been applied
 */

import { chromium } from 'playwright';
import OpenAI from 'openai';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

const STREAMLIT_URL = process.env.STREAMLIT_APP_URL || "http://localhost:8501";

// Color codes for better output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

async function log(message, type = 'info') {
  const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
  const typeColors = {
    'success': colors.green,
    'error': colors.red,
    'warning': colors.yellow,
    'info': colors.cyan,
    'header': colors.blue + colors.bright
  };
  console.log(`${typeColors[type] || ''}${timestamp} ${message}${colors.reset}`);
}

async function runComprehensiveTest() {
  await log("🚀 COMPREHENSIVE STAGEHAND TEST - POST-FIX VERIFICATION", 'header');
  await log("Testing all features after applying fixes\n", 'info');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  const testResults = {
    features: {
      total: 0,
      working: [],
      broken: [],
      warnings: []
    },
    fileProcessing: {
      upload: { success: false, files: [] },
      processing: { started: false, completed: false },
      output: { available: false }
    },
    errors: [],
    performance: {
      startTime: Date.now(),
      checkpointTimes: {}
    }
  };
  
  try {
    // Phase 1: App Navigation
    await log("\n📱 PHASE 1: App Navigation", 'header');
    await page.goto(STREAMLIT_URL);
    await page.waitForTimeout(3000);
    await log("✅ App loaded successfully", 'success');
    testResults.performance.checkpointTimes.appLoad = Date.now() - testResults.performance.startTime;
    
    // Phase 2: Feature Testing (Individual)
    await log("\n🔬 PHASE 2: Individual Feature Testing", 'header');
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    testResults.features.total = checkboxes.length;
    
    const featureNames = [];
    for (const checkbox of checkboxes) {
      const label = await checkbox.locator('..').textContent();
      featureNames.push(label.trim());
    }
    
    await log(`Found ${checkboxes.length} features to test:`, 'info');
    featureNames.forEach((name, i) => console.log(`  ${i + 1}. ${name}`));
    
    // Test each feature individually
    for (let i = 0; i < checkboxes.length; i++) {
      const featureName = featureNames[i];
      await log(`\nTesting: ${featureName}`, 'info');
      
      // Clear all checkboxes first
      for (const cb of checkboxes) {
        try {
          await cb.uncheck();
        } catch (e) {
          // Some might already be unchecked
        }
      }
      await page.waitForTimeout(500);
      
      // Enable only this feature
      try {
        await checkboxes[i].check();
        await page.waitForTimeout(1000);
        
        // Check feature status indicator
        const statusElements = await page.locator('.stAlert').all();
        let hasError = false;
        let errorMessage = '';
        
        for (const elem of statusElements) {
          const text = await elem.textContent();
          if (text.toLowerCase().includes('error') || text.includes('has no attribute')) {
            hasError = true;
            errorMessage = text.substring(0, 100);
            break;
          }
        }
        
        // Check sidebar status indicators
        const statusIcons = await page.locator('span:has-text("✅")').all();
        const pendingIcons = await page.locator('span:has-text("⏳")').all();
        const errorIcons = await page.locator('span:has-text("❌")').all();
        
        if (hasError) {
          await log(`  ❌ BROKEN: ${errorMessage}`, 'error');
          testResults.features.broken.push({ name: featureName, error: errorMessage });
        } else if (errorIcons.length > 0) {
          await log(`  ❌ Feature shows error status`, 'error');
          testResults.features.broken.push({ name: featureName, error: 'Shows ❌ status' });
        } else if (pendingIcons.length > statusIcons.length) {
          await log(`  ⚠️  WARNING: Feature shows pending status`, 'warning');
          testResults.features.warnings.push({ name: featureName, warning: 'Shows ⏳ status' });
        } else {
          await log(`  ✅ WORKING: Feature enabled successfully`, 'success');
          testResults.features.working.push(featureName);
        }
        
      } catch (e) {
        await log(`  ❌ FAILED: ${e.message}`, 'error');
        testResults.features.broken.push({ name: featureName, error: e.message });
      }
    }
    
    // Phase 3: All Features Together
    await log("\n🎯 PHASE 3: All Features Enabled Test", 'header');
    for (const checkbox of checkboxes) {
      await checkbox.check();
    }
    await page.waitForTimeout(2000);
    
    const allFeaturesErrors = await page.locator('.stAlert:has-text("error")').count();
    const allFeaturesWarnings = await page.locator('.stAlert:has-text("warning")').count();
    
    await log(`With all features enabled:`, 'info');
    await log(`  - Errors: ${allFeaturesErrors}`, allFeaturesErrors > 0 ? 'error' : 'success');
    await log(`  - Warnings: ${allFeaturesWarnings}`, allFeaturesWarnings > 0 ? 'warning' : 'success');
    
    // Phase 4: File Processing Test
    await log("\n📁 PHASE 4: File Processing Test", 'header');
    
    // Upload files
    const fileInputs = await page.locator('input[type="file"]').all();
    const testFiles = [
      { name: "Planned Media Plan", path: join(__dirname, '../test_fixtures/PLANNED_TEST_FIXTURE.xlsx') },
      { name: "Delivered Data", path: join(__dirname, '../test_fixtures/DELIVERED_TEST_FIXTURE.xlsx') },
      { name: "Output Template", path: join(__dirname, '../test_fixtures/OUTPUT_TEMPLATE_TEST_FIXTURE.xlsx') }
    ];
    
    for (let i = 0; i < Math.min(fileInputs.length, testFiles.length); i++) {
      try {
        await log(`Uploading: ${testFiles[i].name}`, 'info');
        await fileInputs[i].setInputFiles(testFiles[i].path);
        await page.waitForTimeout(1000);
        testResults.fileProcessing.upload.files.push(testFiles[i].name);
        await log(`  ✅ Upload successful`, 'success');
      } catch (e) {
        await log(`  ❌ Upload failed: ${e.message}`, 'error');
        testResults.errors.push(`File upload: ${e.message}`);
      }
    }
    testResults.fileProcessing.upload.success = testResults.fileProcessing.upload.files.length === 3;
    
    // Process files
    await log("\nStarting file processing...", 'info');
    try {
      const processBtn = await page.locator('button:has-text("Process")').first();
      await processBtn.click();
      testResults.fileProcessing.processing.started = true;
      await log("  ✅ Processing started", 'success');
      
      // Wait for completion with progress updates
      let processed = false;
      for (let i = 0; i < 60; i++) {
        await page.waitForTimeout(1000);
        
        // Check multiple success indicators
        const successIndicators = [
          await page.locator('text=/successfully|complete|ready/i').count(),
          await page.locator('button:has-text("Download")').count(),
          await page.locator('.stSuccess').count()
        ];
        
        if (successIndicators.some(count => count > 0)) {
          processed = true;
          testResults.fileProcessing.processing.completed = true;
          break;
        }
        
        if (i % 5 === 0) {
          await log(`  ⏳ Processing... (${i}s)`, 'info');
        }
      }
      
      if (processed) {
        await log("  ✅ Processing completed!", 'success');
        
        // Check for download button
        const downloadBtn = await page.locator('button:has-text("Download")').count();
        testResults.fileProcessing.output.available = downloadBtn > 0;
        
        if (downloadBtn > 0) {
          await log("  ✅ Output file ready for download", 'success');
        }
      } else {
        await log("  ⚠️  Processing timeout - may still be running", 'warning');
      }
      
    } catch (e) {
      await log(`  ❌ Processing error: ${e.message}`, 'error');
      testResults.errors.push(`Processing: ${e.message}`);
    }
    
    // Phase 5: Final Validation
    await log("\n🔍 PHASE 5: Final Validation", 'header');
    
    // Get all validation messages
    const validationMessages = await page.locator('.stAlert').allTextContents();
    await log(`Found ${validationMessages.length} validation messages`, 'info');
    
    // Categorize messages
    const messageTypes = {
      errors: 0,
      warnings: 0,
      success: 0,
      info: 0
    };
    
    for (const msg of validationMessages) {
      if (msg.toLowerCase().includes('error') || msg.includes('❌')) messageTypes.errors++;
      else if (msg.toLowerCase().includes('warning') || msg.includes('⚠️')) messageTypes.warnings++;
      else if (msg.toLowerCase().includes('success') || msg.includes('✅')) messageTypes.success++;
      else messageTypes.info++;
    }
    
    await log(`Message breakdown:`, 'info');
    await log(`  - Errors: ${messageTypes.errors}`, messageTypes.errors > 0 ? 'error' : 'success');
    await log(`  - Warnings: ${messageTypes.warnings}`, 'info');
    await log(`  - Success: ${messageTypes.success}`, 'success');
    await log(`  - Info: ${messageTypes.info}`, 'info');
    
  } catch (error) {
    await log(`\n❌ Critical test failure: ${error.message}`, 'error');
    testResults.errors.push(`Critical: ${error.message}`);
  } finally {
    // Calculate total time
    testResults.performance.totalTime = Date.now() - testResults.performance.startTime;
    
    // Generate comprehensive report
    await log("\n" + "=".repeat(80), 'header');
    await log("📊 COMPREHENSIVE TEST REPORT", 'header');
    await log("=".repeat(80), 'header');
    
    await log("\n✅ FEATURE SUMMARY:", 'header');
    await log(`Total Features: ${testResults.features.total}`, 'info');
    await log(`Working: ${testResults.features.working.length} (${(testResults.features.working.length/testResults.features.total*100).toFixed(1)}%)`, 'success');
    await log(`Broken: ${testResults.features.broken.length} (${(testResults.features.broken.length/testResults.features.total*100).toFixed(1)}%)`, testResults.features.broken.length > 0 ? 'error' : 'success');
    await log(`Warnings: ${testResults.features.warnings.length}`, testResults.features.warnings.length > 0 ? 'warning' : 'success');
    
    if (testResults.features.working.length > 0) {
      await log("\n✅ Working Features:", 'success');
      testResults.features.working.forEach(f => console.log(`   - ${f}`));
    }
    
    if (testResults.features.broken.length > 0) {
      await log("\n❌ Broken Features:", 'error');
      testResults.features.broken.forEach(f => console.log(`   - ${f.name}: ${f.error}`));
    }
    
    if (testResults.features.warnings.length > 0) {
      await log("\n⚠️  Features with Warnings:", 'warning');
      testResults.features.warnings.forEach(f => console.log(`   - ${f.name}: ${f.warning}`));
    }
    
    await log("\n📁 FILE PROCESSING:", 'header');
    await log(`Files Uploaded: ${testResults.fileProcessing.upload.files.length}/3`, testResults.fileProcessing.upload.success ? 'success' : 'error');
    await log(`Processing Started: ${testResults.fileProcessing.processing.started ? 'Yes' : 'No'}`, testResults.fileProcessing.processing.started ? 'success' : 'error');
    await log(`Processing Completed: ${testResults.fileProcessing.processing.completed ? 'Yes' : 'No'}`, testResults.fileProcessing.processing.completed ? 'success' : 'warning');
    await log(`Output Available: ${testResults.fileProcessing.output.available ? 'Yes' : 'No'}`, testResults.fileProcessing.output.available ? 'success' : 'warning');
    
    await log("\n⏱️  PERFORMANCE:", 'header');
    await log(`Total Test Time: ${(testResults.performance.totalTime/1000).toFixed(2)}s`, 'info');
    await log(`App Load Time: ${(testResults.performance.checkpointTimes.appLoad/1000).toFixed(2)}s`, 'info');
    
    if (testResults.errors.length > 0) {
      await log("\n❌ ERRORS ENCOUNTERED:", 'error');
      testResults.errors.forEach(err => console.log(`   - ${err}`));
    }
    
    await log("\n🎯 OVERALL ASSESSMENT:", 'header');
    const overallScore = (testResults.features.working.length / testResults.features.total) * 100;
    const processingSuccess = testResults.fileProcessing.processing.completed && testResults.fileProcessing.output.available;
    
    if (overallScore === 100 && processingSuccess) {
      await log("✅ ALL FEATURES WORKING PERFECTLY!", 'success');
      await log("The application is fully functional with all fixes applied.", 'success');
    } else if (overallScore >= 80 && processingSuccess) {
      await log("✅ APPLICATION MOSTLY FUNCTIONAL", 'success');
      await log(`${overallScore.toFixed(1)}% of features working, file processing successful.`, 'info');
    } else if (overallScore >= 60) {
      await log("⚠️  APPLICATION PARTIALLY FUNCTIONAL", 'warning');
      await log(`Only ${overallScore.toFixed(1)}% of features working. Needs attention.`, 'warning');
    } else {
      await log("❌ APPLICATION HAS CRITICAL ISSUES", 'error');
      await log(`Only ${overallScore.toFixed(1)}% of features working. Major fixes needed.`, 'error');
    }
    
    await log("\n" + "=".repeat(80), 'header');
    
    await page.waitForTimeout(5000); // Let user see final state
    await browser.close();
  }
}

// Run the comprehensive test
runComprehensiveTest().catch(console.error);