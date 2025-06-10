/**
 * Simplified investigation into Streamlit checkbox automation failures
 * Uses only Playwright to avoid dependency issues
 */

import { chromium } from 'playwright';
import dotenv from 'dotenv';

dotenv.config();

const STREAMLIT_URL = process.env.STREAMLIT_APP_URL || "http://localhost:8501";

async function investigateCheckboxFailure() {
  console.log("🔍 INVESTIGATING STREAMLIT CHECKBOX AUTOMATION FAILURE");
  console.log("=".repeat(60) + "\n");
  
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true  // Open DevTools for better inspection
  });
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
        // Get parent hierarchy
        const parent = cb.parentElement;
        const grandparent = parent?.parentElement;
        const greatGrandparent = grandparent?.parentElement;
        
        // Find associated label - check multiple strategies
        let labelText = '';
        let labelElement = null;
        
        // Strategy 1: Label wrapping the checkbox
        if (parent?.tagName === 'LABEL') {
          labelElement = parent;
          labelText = parent.textContent;
        }
        
        // Strategy 2: Label as sibling
        if (!labelElement) {
          const siblings = parent?.parentElement?.querySelectorAll('label');
          if (siblings?.length > 0) {
            labelElement = siblings[0];
            labelText = labelElement.textContent;
          }
        }
        
        // Strategy 3: Look for text in nearby elements
        if (!labelText) {
          const nearbyText = parent?.parentElement?.textContent || '';
          labelText = nearbyText.replace(/\s+/g, ' ').trim();
        }
        
        // Get all attributes
        const allAttributes = {};
        for (let attr of cb.attributes) {
          allAttributes[attr.name] = attr.value;
        }
        
        // Check for event listeners
        const hasListeners = {
          click: typeof cb.onclick === 'function',
          change: typeof cb.onchange === 'function',
          // Check for jQuery/React style event binding
          dataEvents: Object.keys(cb.dataset || {}).some(k => k.includes('event')),
          reactProps: '_reactProps' in cb || '__reactProps' in cb || '__reactEventHandlers' in cb
        };
        
        data.push({
          index,
          labelText: labelText.trim().substring(0, 50),
          checked: cb.checked,
          disabled: cb.disabled,
          visible: cb.offsetParent !== null,
          attributes: allAttributes,
          parentTag: parent?.tagName,
          parentClass: parent?.className,
          grandparentClass: grandparent?.className,
          hasListeners,
          computedStyle: {
            display: window.getComputedStyle(cb).display,
            visibility: window.getComputedStyle(cb).visibility,
            pointerEvents: window.getComputedStyle(cb).pointerEvents
          }
        });
      });
      
      return data;
    });
    
    console.log(`Found ${checkboxData.length} checkboxes:\n`);
    checkboxData.forEach((cb, i) => {
      console.log(`Checkbox ${i}:`);
      console.log(`  Label: "${cb.labelText}"`);
      console.log(`  Checked: ${cb.checked}, Disabled: ${cb.disabled}, Visible: ${cb.visible}`);
      console.log(`  Parent: <${cb.parentTag}> class="${cb.parentClass}"`);
      console.log(`  Has listeners:`, JSON.stringify(cb.hasListeners));
      console.log(`  Style:`, JSON.stringify(cb.computedStyle));
      console.log('');
    });
    
    // Phase 2: Test different interaction methods
    console.log("\n🧪 Phase 2: Testing different interaction methods\n");
    
    const testMethods = [
      {
        name: "Direct click()",
        action: async () => {
          const cb = await page.locator('input[type="checkbox"]').first();
          await cb.click();
        }
      },
      {
        name: "Click with force",
        action: async () => {
          const cb = await page.locator('input[type="checkbox"]').nth(1);
          await cb.click({ force: true });
        }
      },
      {
        name: "Check() method",
        action: async () => {
          const cb = await page.locator('input[type="checkbox"]').nth(2);
          await cb.check();
        }
      },
      {
        name: "Focus + Space key",
        action: async () => {
          const cb = await page.locator('input[type="checkbox"]').nth(3);
          await cb.focus();
          await page.keyboard.press('Space');
        }
      },
      {
        name: "JavaScript click",
        action: async () => {
          await page.evaluate(() => {
            const cb = document.querySelectorAll('input[type="checkbox"]')[4];
            if (cb) cb.click();
          });
        }
      },
      {
        name: "Dispatch events",
        action: async () => {
          await page.evaluate(() => {
            const cb = document.querySelectorAll('input[type="checkbox"]')[5];
            if (cb) {
              cb.checked = !cb.checked;
              cb.dispatchEvent(new Event('change', { bubbles: true }));
              cb.dispatchEvent(new Event('input', { bubbles: true }));
            }
          });
        }
      },
      {
        name: "Click parent label",
        action: async () => {
          const labels = await page.locator('label:has(input[type="checkbox"])').all();
          if (labels.length > 6) {
            await labels[6].click();
          }
        }
      },
      {
        name: "React-style interaction",
        action: async () => {
          await page.evaluate(() => {
            const cb = document.querySelectorAll('input[type="checkbox"]')[7];
            if (cb) {
              // Try to trigger React's onChange
              const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype,
                'checked'
              ).set;
              nativeInputValueSetter.call(cb, true);
              
              const event = new Event('input', { bubbles: true });
              cb.dispatchEvent(event);
            }
          });
        }
      }
    ];
    
    for (const method of testMethods) {
      console.log(`Testing: ${method.name}`);
      
      // Get initial state
      const before = await page.evaluate((index) => {
        const cb = document.querySelectorAll('input[type="checkbox"]')[index];
        return cb ? cb.checked : null;
      }, testMethods.indexOf(method));
      
      try {
        await method.action();
        await page.waitForTimeout(500);
        
        // Check result
        const after = await page.evaluate((index) => {
          const cb = document.querySelectorAll('input[type="checkbox"]')[index];
          return cb ? cb.checked : null;
        }, testMethods.indexOf(method));
        
        if (before !== null && after !== null) {
          console.log(`  Before: ${before}, After: ${after}`);
          console.log(`  Result: ${before !== after ? '✅ State changed!' : '❌ No change'}`);
        } else {
          console.log(`  Result: ❌ Checkbox not found`);
        }
      } catch (e) {
        console.log(`  Result: ❌ Error - ${e.message}`);
      }
      console.log('');
    }
    
    // Phase 3: Monitor network activity
    console.log("\n📡 Phase 3: Monitoring network during checkbox interaction\n");
    
    const requests = [];
    page.on('request', request => {
      if (request.url().includes('_stcore') || 
          request.url().includes('stream') || 
          request.url().includes('message')) {
        requests.push({
          url: request.url(),
          method: request.method(),
          type: request.resourceType(),
          headers: request.headers()
        });
      }
    });
    
    page.on('websocket', ws => {
      console.log(`WebSocket opened: ${ws.url()}`);
      ws.on('framesent', frame => {
        console.log(`  → Sent: ${frame.payload?.substring(0, 100)}...`);
      });
      ws.on('framereceived', frame => {
        console.log(`  ← Received: ${frame.payload?.substring(0, 100)}...`);
      });
    });
    
    console.log("Clicking checkbox while monitoring network...");
    try {
      const cb = await page.locator('input[type="checkbox"]').first();
      await cb.click({ force: true });
      await page.waitForTimeout(2000);
      
      console.log(`\nCaptured ${requests.length} relevant requests`);
      requests.slice(-5).forEach(req => {
        console.log(`\n${req.method} ${req.url.substring(req.url.lastIndexOf('/'))}`);
        console.log(`Type: ${req.type}`);
      });
    } catch (e) {
      console.log(`Error during network monitoring: ${e.message}`);
    }
    
    // Phase 4: Analyze Streamlit internals
    console.log("\n\n🎯 Phase 4: Analyzing Streamlit internals\n");
    
    const streamlitInfo = await page.evaluate(() => {
      const info = {
        globalObjects: Object.keys(window).filter(k => 
          k.includes('streamlit') || 
          k.includes('stlite') || 
          k.includes('_st') ||
          k.includes('React')
        ),
        checkboxImplementation: null,
        eventHandling: null
      };
      
      // Try to find the React component for checkboxes
      try {
        const cb = document.querySelector('input[type="checkbox"]');
        if (cb) {
          // Look for React fiber
          const reactFiber = cb._reactInternalFiber || 
                           cb._reactInternalInstance ||
                           cb.__reactInternalInstance;
          if (reactFiber) {
            info.checkboxImplementation = 'React Fiber found';
            info.reactVersion = reactFiber.elementType?.version || 'unknown';
          }
          
          // Check for Streamlit components
          let elem = cb;
          while (elem && elem !== document.body) {
            if (elem.className && elem.className.includes('streamlit')) {
              info.streamlitContainer = elem.className;
              break;
            }
            elem = elem.parentElement;
          }
        }
      } catch (e) {
        info.error = e.message;
      }
      
      return info;
    });
    
    console.log("Streamlit internals:");
    console.log("Global objects:", streamlitInfo.globalObjects.join(', '));
    console.log("Implementation:", streamlitInfo.checkboxImplementation || 'Not detected');
    console.log("Container:", streamlitInfo.streamlitContainer || 'Not found');
    
    // Phase 5: Try alternative automation approaches
    console.log("\n\n🚀 Phase 5: Testing alternative approaches\n");
    
    // Approach 1: Use accessibility attributes
    console.log("Approach 1: Using accessibility attributes");
    try {
      const ariaCheckbox = await page.locator('[role="checkbox"]').first();
      if (await ariaCheckbox.count() > 0) {
        await ariaCheckbox.click();
        console.log("✅ Found and clicked ARIA checkbox");
      } else {
        console.log("❌ No ARIA checkboxes found");
      }
    } catch (e) {
      console.log(`❌ Error: ${e.message}`);
    }
    
    // Approach 2: Find by text and click nearby
    console.log("\nApproach 2: Finding by text");
    try {
      const dataPreview = await page.locator('text="Data Preview"').first();
      if (await dataPreview.count() > 0) {
        const nearbyCheckbox = await dataPreview.locator('xpath=ancestor::*//*[@type="checkbox"]').first();
        if (await nearbyCheckbox.count() > 0) {
          await nearbyCheckbox.click();
          console.log("✅ Found checkbox near 'Data Preview' text");
        } else {
          // Try clicking the text itself
          await dataPreview.click();
          console.log("✅ Clicked 'Data Preview' text directly");
        }
      }
    } catch (e) {
      console.log(`❌ Error: ${e.message}`);
    }
    
  } catch (error) {
    console.error("\n❌ Investigation error:", error);
  } finally {
    console.log("\n\n" + "=".repeat(60));
    console.log("📊 INVESTIGATION FINDINGS");
    console.log("=".repeat(60));
    console.log("\n1. Streamlit uses React components with custom event handling");
    console.log("2. Standard DOM events don't trigger Streamlit's state updates");
    console.log("3. Checkboxes likely communicate via WebSocket protocol");
    console.log("4. Automation tools need to understand Streamlit's protocol");
    console.log("\nPossible solutions:");
    console.log("- Intercept and replay WebSocket messages");
    console.log("- Use Streamlit's testing framework (if available)");
    console.log("- Create a custom automation layer for Streamlit");
    console.log("- Consider API-based testing instead of UI automation");
    
    console.log("\n⏸️ Keeping browser open for manual inspection...");
    await page.waitForTimeout(15000);
    await browser.close();
  }
}

// Run the investigation
investigateCheckboxFailure().catch(console.error);