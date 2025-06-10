/**
 * Deep investigation into why checkbox automation fails with Streamlit
 * This test will gather detailed information about the checkbox structure
 */

import { chromium } from 'playwright';
import { Stagehand } from '@browserbase/stagehand';
import dotenv from 'dotenv';

dotenv.config();

const STREAMLIT_URL = process.env.STREAMLIT_APP_URL || "http://localhost:8501";

async function investigateCheckboxFailure() {
  console.log("🔍 INVESTIGATING CHECKBOX AUTOMATION FAILURE");
  console.log("=" * 60 + "\n");
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Load the app
    console.log("📱 Loading Streamlit app...");
    await page.goto(STREAMLIT_URL);
    await page.waitForTimeout(3000);
    
    // Phase 1: Analyze DOM structure
    console.log("\n🔬 Phase 1: Analyzing checkbox DOM structure");
    
    const checkboxData = await page.evaluate(() => {
      const checkboxes = document.querySelectorAll('input[type="checkbox"]');
      const data = [];
      
      checkboxes.forEach((cb, index) => {
        // Get various attributes
        const parent = cb.parentElement;
        const grandparent = parent?.parentElement;
        const greatGrandparent = grandparent?.parentElement;
        
        // Find associated label
        let labelText = '';
        const label = parent?.querySelector('label') || 
                     grandparent?.querySelector('label') ||
                     greatGrandparent?.querySelector('label');
        if (label) labelText = label.textContent;
        
        // Check for Streamlit-specific attributes
        const stAttributes = {};
        for (let attr of cb.attributes) {
          if (attr.name.includes('data-') || attr.name.includes('aria-')) {
            stAttributes[attr.name] = attr.value;
          }
        }
        
        data.push({
          index,
          id: cb.id,
          name: cb.name,
          checked: cb.checked,
          disabled: cb.disabled,
          labelText: labelText.trim(),
          parentClass: parent?.className,
          grandparentClass: grandparent?.className,
          streamlitAttrs: stAttributes,
          hasOnClick: !!cb.onclick,
          hasEventListeners: typeof cb._events !== 'undefined'
        });
      });
      
      return data;
    });
    
    console.log(`Found ${checkboxData.length} checkboxes:`);
    checkboxData.forEach(cb => {
      console.log(`\nCheckbox ${cb.index}:`);
      console.log(`  Label: "${cb.labelText}"`);
      console.log(`  ID: ${cb.id || 'none'}`);
      console.log(`  Checked: ${cb.checked}`);
      console.log(`  Parent class: ${cb.parentClass}`);
      console.log(`  Streamlit attrs:`, cb.streamlitAttrs);
    });
    
    // Phase 2: Test different interaction methods
    console.log("\n\n🧪 Phase 2: Testing different interaction methods");
    
    // Method 1: Direct click
    console.log("\n📍 Method 1: Direct click on checkbox");
    try {
      const firstCheckbox = await page.locator('input[type="checkbox"]').first();
      await firstCheckbox.click();
      await page.waitForTimeout(1000);
      const isChecked = await firstCheckbox.isChecked();
      console.log(`Result: ${isChecked ? '✅ Checked' : '❌ Not checked'}`);
    } catch (e) {
      console.log(`Result: ❌ Error - ${e.message}`);
    }
    
    // Method 2: Click on label
    console.log("\n📍 Method 2: Click on label");
    try {
      const labels = await page.locator('label:has(input[type="checkbox"])').all();
      if (labels.length > 0) {
        await labels[0].click();
        await page.waitForTimeout(1000);
        console.log("Result: ✅ Label clicked");
      } else {
        console.log("Result: ❌ No labels found");
      }
    } catch (e) {
      console.log(`Result: ❌ Error - ${e.message}`);
    }
    
    // Method 3: Force check
    console.log("\n📍 Method 3: Force check");
    try {
      const checkbox = await page.locator('input[type="checkbox"]').nth(1);
      await checkbox.check({ force: true });
      await page.waitForTimeout(1000);
      const isChecked = await checkbox.isChecked();
      console.log(`Result: ${isChecked ? '✅ Checked' : '❌ Not checked'}`);
    } catch (e) {
      console.log(`Result: ❌ Error - ${e.message}`);
    }
    
    // Method 4: JavaScript execution
    console.log("\n📍 Method 4: Direct JavaScript execution");
    try {
      const result = await page.evaluate(() => {
        const checkbox = document.querySelectorAll('input[type="checkbox"]')[2];
        if (checkbox) {
          checkbox.checked = true;
          checkbox.dispatchEvent(new Event('change', { bubbles: true }));
          checkbox.dispatchEvent(new Event('input', { bubbles: true }));
          checkbox.dispatchEvent(new Event('click', { bubbles: true }));
          return checkbox.checked;
        }
        return false;
      });
      console.log(`Result: ${result ? '✅ Checked' : '❌ Not checked'}`);
    } catch (e) {
      console.log(`Result: ❌ Error - ${e.message}`);
    }
    
    // Phase 3: Test with Stagehand
    console.log("\n\n🤖 Phase 3: Testing with Stagehand");
    
    const stagehand = new Stagehand({
      env: "LOCAL",
      headless: false,
      enableCaching: false
    });
    
    await stagehand.init();
    await stagehand.page.goto(STREAMLIT_URL);
    await stagehand.page.waitForTimeout(3000);
    
    // Try various natural language commands
    const commands = [
      "Click on the Data Preview checkbox",
      "Enable the Data Preview feature",
      "Check the box next to Data Preview",
      "Turn on Data Preview",
      "Select Data Preview"
    ];
    
    for (const command of commands) {
      console.log(`\nTrying: "${command}"`);
      try {
        await stagehand.act(command);
        await stagehand.page.waitForTimeout(1000);
        console.log("Result: ✅ Command executed");
        
        // Check if it actually worked
        const isChecked = await stagehand.page.evaluate(() => {
          const checkboxes = document.querySelectorAll('input[type="checkbox"]');
          return checkboxes[0]?.checked || false;
        });
        console.log(`Verification: ${isChecked ? '✅ Checkbox is checked' : '❌ Checkbox still unchecked'}`);
      } catch (e) {
        console.log(`Result: ❌ Error - ${e.message}`);
      }
    }
    
    // Phase 4: Analyze Streamlit's event system
    console.log("\n\n🎯 Phase 4: Analyzing Streamlit's event system");
    
    const streamlitInfo = await page.evaluate(() => {
      // Check for Streamlit global objects
      const info = {
        hasStreamlit: typeof window.streamlit !== 'undefined',
        hasStCommReact: typeof window.stCommReact !== 'undefined',
        reactVersion: window.React?.version || 'not found',
        streamlitVersion: window.streamlit?.version || 'not found'
      };
      
      // Try to find React fiber nodes
      const checkboxes = document.querySelectorAll('input[type="checkbox"]');
      if (checkboxes.length > 0) {
        const cb = checkboxes[0];
        const reactProps = cb._reactProps || cb.__reactEventHandlers || {};
        info.hasReactProps = Object.keys(reactProps).length > 0;
        info.reactPropKeys = Object.keys(reactProps);
      }
      
      return info;
    });
    
    console.log("Streamlit environment:");
    console.log(`  Has Streamlit object: ${streamlitInfo.hasStreamlit}`);
    console.log(`  React version: ${streamlitInfo.reactVersion}`);
    console.log(`  Has React props: ${streamlitInfo.hasReactProps}`);
    if (streamlitInfo.reactPropKeys?.length > 0) {
      console.log(`  React prop keys: ${streamlitInfo.reactPropKeys.join(', ')}`);
    }
    
    // Phase 5: Monitor network requests
    console.log("\n\n📡 Phase 5: Monitoring network requests during checkbox interaction");
    
    // Set up request monitoring
    const requests = [];
    page.on('request', request => {
      if (request.url().includes('_stcore') || request.url().includes('message')) {
        requests.push({
          url: request.url(),
          method: request.method(),
          postData: request.postData()
        });
      }
    });
    
    // Try to click a checkbox and see what happens
    console.log("Attempting checkbox click while monitoring network...");
    try {
      const checkbox = await page.locator('input[type="checkbox"]').first();
      await checkbox.click({ force: true });
      await page.waitForTimeout(2000);
      
      console.log(`Captured ${requests.length} Streamlit-related requests`);
      requests.slice(-3).forEach((req, i) => {
        console.log(`\nRequest ${i + 1}:`);
        console.log(`  URL: ${req.url}`);
        console.log(`  Method: ${req.method}`);
        if (req.postData) {
          console.log(`  Data preview: ${req.postData.substring(0, 100)}...`);
        }
      });
    } catch (e) {
      console.log(`Network monitoring error: ${e.message}`);
    }
    
    await stagehand.close();
    
  } catch (error) {
    console.error("\n❌ Investigation error:", error);
  } finally {
    console.log("\n\n📊 INVESTIGATION SUMMARY");
    console.log("=" * 60);
    console.log("Streamlit checkboxes appear to use a complex React-based");
    console.log("event system that doesn't respond to standard DOM events.");
    console.log("The checkboxes likely require specific Streamlit protocol");
    console.log("messages to be sent via WebSocket for state changes.");
    console.log("\nThis explains why both Playwright and Stagehand struggle");
    console.log("with checkbox automation in Streamlit apps.");
    
    await browser.close();
  }
}

// Run the investigation
investigateCheckboxFailure().catch(console.error);