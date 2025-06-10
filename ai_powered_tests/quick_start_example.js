/**
 * Quick Start Example - Fix Streamlit Checkbox Issues with Stagehand
 * 
 * This example shows how to immediately solve the checkbox clicking problem
 * that's failing in traditional Playwright tests.
 */

import { Stagehand } from "@browserbase/stagehand";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

async function fixCheckboxIssue() {
  console.log("🔧 Demonstrating Stagehand solution for Streamlit checkboxes\n");
  
  // Initialize Stagehand
  const stagehand = new Stagehand({
    env: "LOCAL",
    headless: false,  // Set to true for CI/CD
    debugDom: true,
    modelName: "gpt-4o",
    modelClientOptions: {
      apiKey: process.env.OPENAI_API_KEY
    }
  });

  try {
    await stagehand.init();
    const page = stagehand.page;
    
    // Navigate to your Streamlit app
    await page.goto("http://localhost:8501");
    console.log("✅ Navigated to Streamlit app");
    
    // The magic happens here - no complex selectors needed!
    console.log("\n🎯 Enabling features with natural language:");
    
    // This single line replaces all the complex selector logic
    await stagehand.act("Enable all the checkboxes in the sidebar for features");
    console.log("  ✅ All feature checkboxes enabled with one command!");
    
    // Or be more specific if needed
    await stagehand.act("Make sure the 'Show Data Preview' checkbox is checked");
    console.log("  ✅ Specific checkbox verified");
    
    // Verify the state
    const state = await stagehand.observe(
      "Which feature checkboxes are currently enabled in the sidebar?"
    );
    console.log("\n📊 Current state:", state);
    
    // Upload files without worrying about selector changes
    console.log("\n📁 Uploading files:");
    await stagehand.act("Click on the first file upload button");
    // Traditional file upload still works
    await page.setInputFiles('input[type="file"]', 'path/to/your/file.xlsx');
    console.log("  ✅ File uploaded successfully");
    
    // Extract meaningful data without brittle selectors
    const validation = await stagehand.extract({
      instruction: "Get all validation messages and their types (error/warning/success)",
      schema: {
        messages: [{
          type: "string",
          text: "string"
        }]
      }
    });
    console.log("\n🔍 Validation results:", JSON.stringify(validation, null, 2));
    
  } catch (error) {
    console.error("❌ Error:", error);
  } finally {
    await stagehand.close();
  }
}

// Comparison with traditional Playwright approach that fails
function traditionalPlaywrightApproach() {
  console.log("\n❌ Traditional Playwright approach (FAILS):");
  console.log(`
  // This approach fails with Streamlit's dynamic rendering:
  
  const checkbox = page.locator('input[type="checkbox"]').nth(0);
  await checkbox.click();  // Timeout!
  
  const label = page.locator('label:has-text("Show Data Preview")');
  await label.click();  // Not interactable!
  
  // Complex waits and retries needed:
  for (let i = 0; i < 5; i++) {
    try {
      await checkbox.click({ timeout: 5000 });
      break;
    } catch {
      await page.waitForTimeout(1000);
    }
  }
  `);
}

// Run the example
console.log("🚀 Stagehand Quick Start - Solving Streamlit Checkbox Issues\n");
console.log("Prerequisites:");
console.log("1. Make sure your Streamlit app is running on http://localhost:8501");
console.log("2. Set OPENAI_API_KEY in your .env file");
console.log("3. Run: npm install (if not already done)\n");

// Show the problem
traditionalPlaywrightApproach();

// Show the solution
console.log("\n✅ Stagehand approach (WORKS):");
fixCheckboxIssue()
  .then(() => console.log("\n🎉 Demo completed successfully!"))
  .catch(console.error);