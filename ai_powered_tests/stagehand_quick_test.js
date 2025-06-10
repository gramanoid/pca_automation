/**
 * Quick focused test using Stagehand to understand checkbox automation
 */

import { Stagehand } from '@browserbasehq/stagehand';
import { z } from 'zod';
import dotenv from 'dotenv';

dotenv.config();

const STREAMLIT_URL = process.env.STREAMLIT_APP_URL || "http://localhost:8501";

async function quickStagehandTest() {
  console.log("🚀 STAGEHAND QUICK TEST - Streamlit Checkboxes");
  console.log("=".repeat(50) + "\n");
  
  const stagehand = new Stagehand({
    env: "LOCAL",
    headless: false,
    verbose: 1,  // Less verbose
    debugDom: false,
    enableCaching: false,
    modelName: process.env.ANTHROPIC_API_KEY ? "claude-3-5-sonnet-latest" : "gpt-4o",
    modelClientOptions: {
      apiKey: process.env.ANTHROPIC_API_KEY || process.env.OPENAI_API_KEY,
    },
  });

  try {
    await stagehand.init();
    await stagehand.page.goto(STREAMLIT_URL);
    await stagehand.page.waitForTimeout(3000);
    
    console.log("✅ Page loaded\n");
    
    // Quick extraction
    console.log("📊 Extracting checkbox information...");
    const checkboxes = await stagehand.extract({
      instruction: "Find all checkboxes in the Feature Selection section and tell me their labels and whether they are checked",
      schema: z.object({
        checkboxes: z.array(z.object({
          label: z.string(),
          checked: z.boolean()
        }))
      })
    });
    
    console.log("Found checkboxes:");
    checkboxes.checkboxes.forEach(cb => {
      console.log(`- ${cb.label}: ${cb.checked ? '✅' : '⬜'}`);
    });
    
    // Try to enable one checkbox
    console.log("\n🎯 Attempting to enable 'Data Preview' checkbox...");
    
    try {
      await stagehand.act("Click on the Data Preview checkbox to enable it");
      await stagehand.page.waitForTimeout(2000);
      
      // Check result
      const afterState = await stagehand.extract({
        instruction: "Is the Data Preview checkbox now checked?",
        schema: z.object({
          checked: z.boolean()
        })
      });
      
      console.log(`Result: Data Preview is ${afterState.checked ? 'checked ✅' : 'still unchecked ❌'}`);
      
      if (!afterState.checked) {
        // Try alternative approach
        console.log("\n🔄 Trying alternative approach...");
        await stagehand.act("In the Feature Selection section, find the checkbox with the label containing 'Data Preview' and click on it");
        await stagehand.page.waitForTimeout(2000);
        
        const finalState = await stagehand.extract({
          instruction: "Is the Data Preview checkbox checked now?",
          schema: z.object({
            checked: z.boolean()
          })
        });
        
        console.log(`Alternative result: ${finalState.checked ? 'Success! ✅' : 'Still failed ❌'}`);
      }
      
    } catch (error) {
      console.log(`Error during action: ${error.message}`);
    }
    
    // Try batch operation
    console.log("\n📦 Testing batch operation...");
    try {
      await stagehand.act("Enable all the checkboxes in the Feature Selection section at once");
      await stagehand.page.waitForTimeout(3000);
      
      const batchResult = await stagehand.extract({
        instruction: "Count how many checkboxes are checked in Feature Selection",
        schema: z.object({
          checkedCount: z.number(),
          totalCount: z.number()
        })
      });
      
      console.log(`Batch result: ${batchResult.checkedCount}/${batchResult.totalCount} checkboxes checked`);
      
    } catch (error) {
      console.log(`Batch operation error: ${error.message}`);
    }
    
    // Get technical details
    console.log("\n🔍 Technical analysis...");
    const analysis = await stagehand.observe({
      instruction: "Look at the checkboxes and describe any visual feedback when you hover over them or click them. Do they appear clickable? Are there any error messages?"
    });
    
    console.log(`Observation: ${analysis}`);
    
    console.log("\n✅ Test completed!");
    
  } catch (error) {
    console.error("❌ Test error:", error);
  } finally {
    await stagehand.close();
  }
}

// Run the test
quickStagehandTest().catch(console.error);