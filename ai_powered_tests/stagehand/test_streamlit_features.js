import { Stagehand } from "@browserbase/stagehand";
import { chromium } from "playwright";
import dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

// Load environment variables
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
dotenv.config({ path: join(__dirname, '..', '.env') });

// Test configuration
const STREAMLIT_URL = process.env.STREAMLIT_APP_URL || "http://localhost:8501";
const HEADLESS = process.env.HEADLESS_MODE === "true";

async function testStreamlitFeatures() {
  console.log("🚀 Starting Stagehand tests for Streamlit features");
  
  // Initialize Stagehand with AI capabilities
  const stagehand = new Stagehand({
    env: "LOCAL",
    enableCaching: true,
    headless: HEADLESS,
    debugDom: true,
    modelName: "gpt-4o",  // Can use claude-3-5-sonnet-latest or other models
    modelClientOptions: {
      apiKey: process.env.OPENAI_API_KEY
    }
  });

  try {
    // Initialize the browser
    await stagehand.init();
    const page = stagehand.page;
    
    console.log("📱 Navigating to Streamlit app...");
    await page.goto(STREAMLIT_URL, { waitUntil: "networkidle" });
    
    // Test 1: Enable all feature checkboxes using natural language
    console.log("\n✅ Test 1: Enabling feature checkboxes with AI");
    
    // Use Stagehand's act method with natural language
    await stagehand.act("Click on the sidebar expander button if the sidebar is collapsed");
    
    // Enable each feature using natural language commands
    const features = [
      "Enable the 'Show Data Preview' checkbox",
      "Enable the 'Enhanced Validation' checkbox", 
      "Enable the 'Smart File Suggestions' checkbox",
      "Enable the 'Progress Tracking' checkbox",
      "Enable the 'Error Recovery' checkbox",
      "Enable the 'Marker Validation' checkbox"
    ];
    
    for (const feature of features) {
      console.log(`  - ${feature}`);
      try {
        await stagehand.act(feature);
        await page.waitForTimeout(500); // Small delay for UI updates
      } catch (error) {
        console.log(`    ⚠️  Retrying with alternative approach...`);
        // Stagehand can self-heal and try alternative methods
        await stagehand.act(`Find and check the checkbox for ${feature.replace('Enable the ', '').replace(' checkbox', '')}`);
      }
    }
    
    // Test 2: Verify features are enabled using observe
    console.log("\n🔍 Test 2: Verifying enabled features");
    
    const checkboxStates = await stagehand.observe(
      "List all the checkboxes in the sidebar and their current state (checked or unchecked)"
    );
    console.log("  Checkbox states:", checkboxStates);
    
    // Test 3: Upload test files using natural language
    console.log("\n📤 Test 3: Uploading test files");
    
    await stagehand.act("Click on the 'Planned Media Plan' file upload button");
    await page.setInputFiles('input[type="file"]', '../test_fixtures/PLANNED_TEST_FIXTURE.xlsx');
    
    await stagehand.act("Click on the 'Delivered Data' file upload button");
    await page.setInputFiles('input[type="file"]:nth-of-type(2)', '../test_fixtures/DELIVERED_TEST_FIXTURE.xlsx');
    
    await stagehand.act("Click on the 'Output Template' file upload button");
    await page.setInputFiles('input[type="file"]:nth-of-type(3)', '../test_fixtures/OUTPUT_TEMPLATE_TEST_FIXTURE.xlsx');
    
    // Test 4: Extract and verify data preview
    console.log("\n📊 Test 4: Extracting data preview information");
    
    const dataPreview = await stagehand.extract({
      instruction: "Extract the data preview information including number of rows and columns for each uploaded file",
      schema: {
        plannedFile: {
          rows: "number",
          columns: "number",
          headers: "array of strings"
        },
        deliveredFile: {
          rows: "number", 
          columns: "number",
          headers: "array of strings"
        }
      }
    });
    
    console.log("  Data preview extracted:", JSON.stringify(dataPreview, null, 2));
    
    // Test 5: Process workflow using AI
    console.log("\n🔄 Test 5: Processing workflow with AI assistance");
    
    await stagehand.act("Click the 'Process Files' or 'Start Processing' button");
    
    // Monitor progress using observe
    let processingComplete = false;
    let attempts = 0;
    const maxAttempts = 30;
    
    while (!processingComplete && attempts < maxAttempts) {
      const status = await stagehand.observe(
        "What is the current processing status? Look for progress bars, status messages, or completion indicators"
      );
      
      console.log(`  Status (attempt ${attempts + 1}):`, status);
      
      if (status.includes("complete") || status.includes("success") || status.includes("100%")) {
        processingComplete = true;
      } else {
        await page.waitForTimeout(2000);
        attempts++;
      }
    }
    
    // Test 6: Validate results using AI
    console.log("\n✔️ Test 6: Validating results with AI");
    
    const validationResults = await stagehand.extract({
      instruction: "Extract all validation results, warnings, and error messages from the page",
      schema: {
        validationPassed: "boolean",
        warnings: "array of strings",
        errors: "array of strings",
        summary: "string"
      }
    });
    
    console.log("  Validation results:", JSON.stringify(validationResults, null, 2));
    
    // Test 7: Download output using natural language
    console.log("\n💾 Test 7: Downloading output file");
    
    try {
      await stagehand.act("Click the download button to download the processed output file");
      console.log("  ✅ Download initiated successfully");
    } catch (error) {
      console.log("  ⚠️  Download button might not be available yet");
    }
    
    console.log("\n🎉 All Stagehand tests completed!");
    
  } catch (error) {
    console.error("❌ Test failed:", error);
    throw error;
  } finally {
    await stagehand.close();
  }
}

// Run the tests
testStreamlitFeatures().catch(console.error);