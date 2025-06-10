/**
 * Test to check which Streamlit features are actually working
 */

import { chromium } from 'playwright';
import dotenv from 'dotenv';
dotenv.config();

const STREAMLIT_URL = process.env.STREAMLIT_APP_URL || "http://localhost:8501";

async function testFeatureStatus() {
  console.log("🔍 STREAMLIT FEATURE STATUS CHECK");
  console.log("=" * 60 + "\n");
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  const features = {
    working: [],
    broken: [],
    unknown: []
  };
  
  try {
    // Navigate to app
    await page.goto(STREAMLIT_URL);
    await page.waitForTimeout(3000);
    
    // Get all checkboxes and their labels
    console.log("📋 Checking individual features:\n");
    const checkboxes = await page.locator('input[type="checkbox"]').all();
    
    for (let i = 0; i < checkboxes.length; i++) {
      const label = await checkboxes[i].locator('..').textContent();
      const featureName = label.trim();
      
      console.log(`Testing: ${featureName}`);
      
      // Uncheck all first
      for (const cb of checkboxes) {
        await cb.uncheck();
      }
      await page.waitForTimeout(500);
      
      // Check only this feature
      await checkboxes[i].check();
      await page.waitForTimeout(1000);
      
      // Look for errors or success indicators
      const errors = await page.locator('.stAlert[data-baseweb="notification"][aria-label*="Error"]').count();
      const warnings = await page.locator('.stAlert[data-baseweb="notification"][aria-label*="Warning"]').count();
      const success = await page.locator('.stAlert[data-baseweb="notification"][aria-label*="Success"]').count();
      
      // Check for specific error messages
      const errorTexts = await page.locator('.stAlert').allTextContents();
      const hasError = errorTexts.some(text => 
        text.includes('error') || 
        text.includes('Error') || 
        text.includes('failed') ||
        text.includes('has no attribute')
      );
      
      if (hasError || errors > 0) {
        console.log(`   ❌ BROKEN - Found errors`);
        features.broken.push(featureName);
        
        // Get error details
        for (const text of errorTexts) {
          if (text.includes('error') || text.includes('Error')) {
            console.log(`      Error: ${text.substring(0, 100)}...`);
          }
        }
      } else if (warnings > 0) {
        console.log(`   ⚠️  WARNING - May have issues`);
        features.unknown.push(featureName);
      } else {
        console.log(`   ✅ WORKING`);
        features.working.push(featureName);
      }
      
      console.log("");
    }
    
    // Test with all features enabled
    console.log("📊 Testing all features together:");
    for (const cb of checkboxes) {
      await cb.check();
    }
    await page.waitForTimeout(2000);
    
    const allEnabledErrors = await page.locator('.stAlert').allTextContents();
    console.log(`Found ${allEnabledErrors.length} messages with all features enabled\n`);
    
  } catch (error) {
    console.error("Test error:", error);
  } finally {
    // Summary
    console.log("\n" + "=" * 60);
    console.log("📊 FEATURE STATUS SUMMARY");
    console.log("=" * 60 + "\n");
    
    console.log(`✅ WORKING FEATURES (${features.working.length}):`);
    features.working.forEach(f => console.log(`   - ${f}`));
    
    console.log(`\n❌ BROKEN FEATURES (${features.broken.length}):`);
    features.broken.forEach(f => console.log(`   - ${f}`));
    
    console.log(`\n⚠️  UNKNOWN STATUS (${features.unknown.length}):`);
    features.unknown.forEach(f => console.log(`   - ${f}`));
    
    console.log("\n💡 RECOMMENDATION:");
    if (features.broken.length > 0) {
      console.log("   Several features have errors and need to be fixed.");
      console.log("   Focus on fixing: Progress Display, Data Preview, Smart Caching");
    } else {
      console.log("   All features appear to be working correctly!");
    }
    
    await page.waitForTimeout(3000);
    await browser.close();
  }
}

// Run the test
testFeatureStatus().catch(console.error);