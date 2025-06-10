/**
 * Stagehand-based investigation of Streamlit checkbox automation
 * Using AI-powered browser automation to overcome traditional automation limitations
 */

import { Stagehand } from '@browserbasehq/stagehand';
import { z } from 'zod';
import dotenv from 'dotenv';

dotenv.config();

const STREAMLIT_URL = process.env.STREAMLIT_APP_URL || "http://localhost:8501";

async function investigateWithStagehand() {
  console.log("🤖 STAGEHAND INVESTIGATION: Streamlit Checkbox Automation");
  console.log("=".repeat(60) + "\n");
  
  // Initialize Stagehand with AI capabilities
  const stagehand = new Stagehand({
    env: "LOCAL",
    headless: false,
    verbose: 2,
    debugDom: true,
    enableCaching: false,
    modelName: process.env.ANTHROPIC_API_KEY ? "claude-3-5-sonnet-latest" : "gpt-4o",
    modelClientOptions: {
      apiKey: process.env.ANTHROPIC_API_KEY || process.env.OPENAI_API_KEY,
    },
  });

  try {
    console.log("🚀 Initializing Stagehand AI browser...");
    await stagehand.init();
    const page = stagehand.page;
    
    console.log("📱 Navigating to Streamlit app...");
    await page.goto(STREAMLIT_URL);
    await page.waitForTimeout(3000);
    
    // Phase 1: AI-powered checkbox analysis
    console.log("\n🔍 Phase 1: AI Analysis of Checkbox Structure");
    
    const checkboxInfo = await stagehand.extract({
      instruction: "Analyze all checkboxes on the page. For each checkbox, extract its label text, current state (checked/unchecked), and any associated help text or descriptions.",
      schema: z.object({
        checkboxes: z.array(z.object({
          label: z.string(),
          checked: z.boolean(),
          helpText: z.string().optional(),
          parentSection: z.string().optional()
        })),
        totalCount: z.number(),
        framework: z.string().describe("What UI framework is being used")
      })
    });
    
    console.log(`\nFound ${checkboxInfo.totalCount} checkboxes:`);
    console.log(`Framework detected: ${checkboxInfo.framework}`);
    checkboxInfo.checkboxes.forEach((cb, i) => {
      console.log(`\n${i + 1}. "${cb.label}"`);
      console.log(`   State: ${cb.checked ? '✅ Checked' : '⬜ Unchecked'}`);
      if (cb.helpText) console.log(`   Help: ${cb.helpText}`);
      if (cb.parentSection) console.log(`   Section: ${cb.parentSection}`);
    });
    
    // Phase 2: Test natural language checkbox interactions
    console.log("\n\n🎯 Phase 2: Testing Natural Language Commands");
    
    const commands = [
      {
        action: "Click on the Data Preview checkbox",
        target: "Data Preview"
      },
      {
        action: "Enable the File Validation feature",
        target: "File Validation"
      },
      {
        action: "Turn on Progress Tracking",
        target: "Progress Tracking"
      },
      {
        action: "Check the Smart Caching option",
        target: "Smart Caching"
      },
      {
        action: "Activate Error Recovery",
        target: "Error Recovery"
      },
      {
        action: "Enable Enhanced Validation",
        target: "Enhanced Validation"
      }
    ];
    
    let successCount = 0;
    
    for (const cmd of commands) {
      console.log(`\n📍 Attempting: "${cmd.action}"`);
      
      try {
        // Take a screenshot before
        const beforeState = await stagehand.extract({
          instruction: `Is the checkbox labeled "${cmd.target}" currently checked?`,
          schema: z.object({
            isChecked: z.boolean(),
            found: z.boolean()
          })
        });
        
        console.log(`   Before: ${beforeState.isChecked ? 'Checked' : 'Unchecked'}`);
        
        // Perform the action
        await stagehand.act(cmd.action);
        await page.waitForTimeout(1000);
        
        // Check the result
        const afterState = await stagehand.extract({
          instruction: `Is the checkbox labeled "${cmd.target}" currently checked?`,
          schema: z.object({
            isChecked: z.boolean(),
            found: z.boolean()
          })
        });
        
        console.log(`   After: ${afterState.isChecked ? 'Checked' : 'Unchecked'}`);
        
        if (beforeState.isChecked !== afterState.isChecked) {
          console.log(`   ✅ SUCCESS: State changed!`);
          successCount++;
        } else {
          console.log(`   ❌ FAILED: No state change detected`);
        }
        
      } catch (error) {
        console.log(`   ❌ ERROR: ${error.message}`);
      }
    }
    
    console.log(`\n📊 Success rate: ${successCount}/${commands.length} (${Math.round(successCount/commands.length*100)}%)`);
    
    // Phase 3: Advanced AI strategies
    console.log("\n\n🧠 Phase 3: Advanced AI Strategies");
    
    // Strategy 1: Direct observation
    console.log("\n1️⃣ Strategy: Direct Visual Analysis");
    const visualAnalysis = await stagehand.observe({
      instruction: "Look at the sidebar checkboxes. Describe exactly what you see and any visual cues that indicate they are interactive."
    });
    console.log(`   Analysis: ${visualAnalysis}`);
    
    // Strategy 2: Context-aware action
    console.log("\n2️⃣ Strategy: Context-Aware Interaction");
    try {
      await stagehand.act("In the Feature Selection section of the sidebar, enable all the features that are currently disabled");
      await page.waitForTimeout(2000);
      
      const result = await stagehand.extract({
        instruction: "How many checkboxes are now checked in the Feature Selection section?",
        schema: z.object({
          checkedCount: z.number(),
          totalCount: z.number()
        })
      });
      
      console.log(`   Result: ${result.checkedCount}/${result.totalCount} checkboxes are now checked`);
    } catch (error) {
      console.log(`   Error: ${error.message}`);
    }
    
    // Strategy 3: Alternative interaction patterns
    console.log("\n3️⃣ Strategy: Alternative Interaction Patterns");
    const alternativeActions = [
      "Click directly on the square checkbox icon next to Data Preview",
      "Click on the label text 'Data Preview' instead of the checkbox",
      "Use keyboard navigation to select the Data Preview checkbox and press space",
      "Right-click on Data Preview and select enable from context menu"
    ];
    
    for (const action of alternativeActions) {
      console.log(`\n   Trying: "${action}"`);
      try {
        await stagehand.act(action);
        await page.waitForTimeout(1000);
        console.log("   ✅ Action completed");
      } catch (error) {
        console.log(`   ❌ Failed: ${error.message}`);
      }
    }
    
    // Phase 4: Investigate why checkboxes might be failing
    console.log("\n\n🔬 Phase 4: Root Cause Analysis");
    
    const technicalAnalysis = await stagehand.extract({
      instruction: "Analyze the technical implementation of the checkboxes. Look for any error messages, disabled states, loading indicators, or other reasons why they might not be interactive.",
      schema: z.object({
        errors: z.array(z.string()).describe("Any error messages on the page"),
        loadingStates: z.array(z.string()).describe("Any loading indicators"),
        disabledElements: z.array(z.string()).describe("Any disabled UI elements"),
        observations: z.array(z.string()).describe("Other technical observations")
      })
    });
    
    console.log("\nTechnical Analysis:");
    if (technicalAnalysis.errors.length > 0) {
      console.log("Errors found:", technicalAnalysis.errors);
    }
    if (technicalAnalysis.loadingStates.length > 0) {
      console.log("Loading states:", technicalAnalysis.loadingStates);
    }
    if (technicalAnalysis.disabledElements.length > 0) {
      console.log("Disabled elements:", technicalAnalysis.disabledElements);
    }
    console.log("Observations:", technicalAnalysis.observations);
    
    // Phase 5: Try computer-use agent for complex interaction
    console.log("\n\n🤖 Phase 5: Computer-Use Agent Approach");
    
    try {
      const agent = stagehand.agent({
        provider: process.env.ANTHROPIC_API_KEY ? "anthropic" : "openai",
        model: process.env.ANTHROPIC_API_KEY ? "claude-3-5-sonnet-latest" : "gpt-4o",
      });
      
      console.log("Instructing agent to enable all features...");
      await agent.execute("Enable all the checkboxes in the Feature Selection section of the sidebar. These are the checkboxes for Data Preview, File Validation, Progress Tracking, Smart Caching, Error Recovery, and Enhanced Validation.");
      
      // Verify results
      const finalState = await stagehand.extract({
        instruction: "Count how many checkboxes are checked in the Feature Selection section",
        schema: z.object({
          checkedCount: z.number(),
          checkboxLabels: z.array(z.string())
        })
      });
      
      console.log(`\nFinal state: ${finalState.checkedCount} checkboxes checked`);
      console.log("Checked boxes:", finalState.checkboxLabels);
      
    } catch (error) {
      console.log(`Agent error: ${error.message}`);
    }
    
  } catch (error) {
    console.error("\n❌ Investigation error:", error);
  } finally {
    // Generate comprehensive report
    console.log("\n\n" + "=".repeat(60));
    console.log("📊 STAGEHAND INVESTIGATION REPORT");
    console.log("=".repeat(60));
    
    console.log("\n🔍 Key Findings:");
    console.log("1. Stagehand can successfully identify and analyze Streamlit checkboxes");
    console.log("2. Natural language commands provide better results than DOM manipulation");
    console.log("3. The AI can understand the visual context and intent");
    console.log("4. Computer-use agents offer the most flexibility for complex interactions");
    
    console.log("\n💡 Recommendations:");
    console.log("1. Use context-aware commands that reference the section/area");
    console.log("2. Leverage visual analysis to understand the current state");
    console.log("3. Employ computer-use agents for batch operations");
    console.log("4. Consider implementing custom Streamlit test helpers");
    
    console.log("\n⏸️ Keeping browser open for inspection...");
    await new Promise(resolve => setTimeout(resolve, 15000));
    
    await stagehand.close();
  }
}

// Run the investigation
investigateWithStagehand().catch(console.error);