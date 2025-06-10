/**
 * Verify Fixes Test - Simple test to check if fixes worked
 */

import { chromium } from 'playwright';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const STREAMLIT_URL = process.env.STREAMLIT_APP_URL || "http://localhost:8501";

async function verifyFixes() {
  console.log("🔍 VERIFYING FIXES");
  console.log("=" * 60 + "\n");
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate to app
    console.log("📱 Loading Streamlit app...");
    await page.goto(STREAMLIT_URL);
    await page.waitForTimeout(3000);
    console.log("✅ App loaded\n");
    
    // Use the approach that worked before - check all at once
    console.log("🎯 Enabling all features at once (proven working approach)...");
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    console.log(`Found ${checkboxes.length} checkboxes\n`);
    
    // Enable all checkboxes using force click
    for (let i = 0; i < checkboxes.length; i++) {
      try {
        const label = await checkboxes[i].locator('..').textContent();
        console.log(`Enabling: ${label.trim()}`);
        await checkboxes[i].check({ force: true });
        await page.waitForTimeout(200);
      } catch (e) {
        // Try parent click as fallback
        try {
          await checkboxes[i].locator('..').click();
        } catch (e2) {
          console.log(`  ⚠️ Could not enable checkbox ${i+1}`);
        }
      }
    }
    
    console.log("\n✅ All checkboxes enabled");
    await page.waitForTimeout(2000);
    
    // Check for specific errors that were fixed
    console.log("\n🔍 Checking for fixed errors:");
    
    // 1. Progress Display Error
    console.log("\n1. Progress Display AttributeError:");
    const progressErrors = await page.locator('text=/render_sidebar_progress|AttributeError/').count();
    if (progressErrors > 0) {
      console.log("   ❌ STILL BROKEN - AttributeError still present");
    } else {
      console.log("   ✅ FIXED - No AttributeError found");
    }
    
    // 2. Feature Status Check
    console.log("\n2. Feature Status Indicators:");
    const featureStatuses = await page.locator('.stMarkdown').allTextContents();
    
    let dataPreviewStatus = "Not found";
    let smartCachingStatus = "Not found";
    
    for (const status of featureStatuses) {
      if (status.includes("DATA_PREVIEW")) {
        if (status.includes("✅")) dataPreviewStatus = "✅ Success";
        else if (status.includes("⏳")) dataPreviewStatus = "⏳ Pending";
        else if (status.includes("❌")) dataPreviewStatus = "❌ Error";
      }
      if (status.includes("SMART_CACHING")) {
        if (status.includes("✅")) smartCachingStatus = "✅ Success";
        else if (status.includes("⏳")) smartCachingStatus = "⏳ Pending";
        else if (status.includes("❌")) smartCachingStatus = "❌ Error";
      }
    }
    
    console.log(`   - Data Preview: ${dataPreviewStatus}`);
    console.log(`   - Smart Caching: ${smartCachingStatus}`);
    
    // 3. Check for any error alerts
    console.log("\n3. Error Messages:");
    const errorAlerts = await page.locator('.stAlert:has-text("error")').all();
    const errorTexts = [];
    
    for (const alert of errorAlerts) {
      const text = await alert.textContent();
      errorTexts.push(text.substring(0, 100));
    }
    
    if (errorTexts.length === 0) {
      console.log("   ✅ No error messages found");
    } else {
      console.log(`   ❌ Found ${errorTexts.length} errors:`);
      errorTexts.forEach((err, i) => console.log(`      ${i+1}. ${err}...`));
    }
    
    // 4. Quick file processing test
    console.log("\n4. File Processing Test:");
    const fileInputs = await page.locator('input[type="file"]').all();
    
    if (fileInputs.length >= 3) {
      console.log("   Uploading test files...");
      await fileInputs[0].setInputFiles(join(__dirname, '../test_fixtures/PLANNED_TEST_FIXTURE.xlsx'));
      await page.waitForTimeout(1000);
      await fileInputs[1].setInputFiles(join(__dirname, '../test_fixtures/DELIVERED_TEST_FIXTURE.xlsx'));
      await page.waitForTimeout(1000);
      await fileInputs[2].setInputFiles(join(__dirname, '../test_fixtures/OUTPUT_TEMPLATE_TEST_FIXTURE.xlsx'));
      await page.waitForTimeout(1000);
      console.log("   ✅ Files uploaded");
      
      // Try to process
      const processBtn = await page.locator('button:has-text("Process")').first();
      if (await processBtn.isVisible()) {
        await processBtn.click();
        console.log("   ✅ Processing started");
        
        // Wait a bit and check for success
        await page.waitForTimeout(10000);
        const successIndicators = await page.locator('text=/success|complete|Download/i').count();
        if (successIndicators > 0) {
          console.log("   ✅ Processing appears successful");
        } else {
          console.log("   ⏳ Processing still running or may have issues");
        }
      }
    }
    
    // Summary
    console.log("\n" + "=" * 60);
    console.log("📊 FIX VERIFICATION SUMMARY");
    console.log("=" * 60);
    
    const fixes = {
      progressDisplay: progressErrors === 0,
      dataPreview: dataPreviewStatus === "✅ Success",
      smartCaching: smartCachingStatus === "✅ Success",
      noErrors: errorTexts.length === 0
    };
    
    console.log("\nFixes Applied:");
    console.log(`1. Progress Display AttributeError: ${fixes.progressDisplay ? '✅ FIXED' : '❌ NOT FIXED'}`);
    console.log(`2. Data Preview Status: ${fixes.dataPreview ? '✅ FIXED' : '❌ NOT FIXED'} (${dataPreviewStatus})`);
    console.log(`3. Smart Caching Status: ${fixes.smartCaching ? '✅ FIXED' : '❌ NOT FIXED'} (${smartCachingStatus})`);
    console.log(`4. No Error Messages: ${fixes.noErrors ? '✅ YES' : '❌ NO'}`);
    
    const allFixed = Object.values(fixes).every(v => v);
    console.log(`\nOverall Status: ${allFixed ? '✅ ALL FIXES WORKING' : '⚠️ SOME ISSUES REMAIN'}`);
    
  } catch (error) {
    console.error("\n❌ Test error:", error);
  } finally {
    await page.waitForTimeout(5000);
    await browser.close();
  }
}

// Run the verification
verifyFixes().catch(console.error);