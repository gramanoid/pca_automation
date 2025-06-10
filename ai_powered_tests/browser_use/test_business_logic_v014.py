"""
Browser Use AI-powered tests for business logic validation.
Updated for browser-use v0.1.14 API.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from browser_use import Agent

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

# Configuration
STREAMLIT_URL = os.getenv("STREAMLIT_APP_URL", "http://localhost:8501")
HEADLESS = os.getenv("HEADLESS_MODE", "false").lower() == "true"

class BusinessLogicValidator:
    """AI-powered validator that adapts to business logic changes."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize with specified LLM model."""
        self.model = self._get_model(model_name)
        
    def _get_model(self, model_name: str):
        """Get appropriate LLM model."""
        if "gpt" in model_name:
            return ChatOpenAI(
                model=model_name,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif "claude" in model_name:
            return ChatAnthropic(
                model=model_name,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            raise ValueError(f"Unsupported model: {model_name}")
    
    async def validate_market_mapping_logic(self):
        """Validate market mapping business logic adaptively."""
        print("🧪 Testing Market Mapping Business Logic")
        
        agent = Agent(
            task="Validate that the market mapping logic correctly maps data between planned and delivered formats",
            llm=self.model
        )
        
        try:
            # Navigate and set up test
            print("  📱 Navigating to application...")
            await agent.run(f"Navigate to {STREAMLIT_URL}")
            
            # Upload test files with known data
            print("  📁 Uploading test files...")
            test_instruction = f"""
            1. Go to {STREAMLIT_URL}
            2. Upload these test files:
               - For the first file input: upload a file from path '../test_fixtures/PLANNED_TEST_FIXTURE.xlsx'
               - For the second file input: upload a file from path '../test_fixtures/DELIVERED_TEST_FIXTURE.xlsx'  
               - For the third file input: upload a file from path '../test_fixtures/OUTPUT_TEMPLATE_TEST_FIXTURE.xlsx'
            3. Click the Process Files button
            4. Wait for processing to complete
            5. Report back on:
               - Were the files uploaded successfully?
               - Did processing complete?
               - Are there any validation warnings or errors?
               - Is the market mapping correct?
            """
            
            result = await agent.run(test_instruction)
            print(f"  📊 Market Mapping Result:\n    {result}")
            
            # AI analyzes if business logic is correct
            validation_check = await agent.run(
                "Based on the processed data you see on screen, check if there are any discrepancies in how markets "
                "are mapped between planned and delivered data. List any issues found. "
                "Pay special attention to market names and platform alignment."
            )
            print(f"  🔍 Validation Check:\n    {validation_check}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    async def validate_data_transformation_rules(self):
        """Validate data transformation rules with AI understanding."""
        print("\n📊 Testing Data Transformation Rules")
        
        agent = Agent(
            task="Validate data transformation rules and calculations in the Media Plan automation",
            llm=self.model
        )
        
        try:
            # Test with edge cases
            print("  🔄 Testing edge cases...")
            edge_case_instruction = f"""
            Navigate to {STREAMLIT_URL} and test the following edge cases:
            1. Check how the system handles empty market names
            2. Look for duplicate entry handling
            3. Verify missing value behavior
            4. Check if currency values are formatted correctly
            5. Examine date format handling
            
            Document how each case is handled and whether it aligns with expected business logic.
            Focus on the validation messages and any warnings shown.
            """
            
            result = await agent.run(edge_case_instruction)
            print(f"  📋 Edge Case Results:\n    {result}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    async def validate_parallel_scenarios(self):
        """Run multiple validation scenarios in parallel."""
        print("\n🚀 Running Parallel Validation Scenarios")
        
        scenarios = [
            {
                "name": "Multi-Market Validation",
                "task": f"Go to {STREAMLIT_URL} and validate handling of multiple markets across different platforms (DV360, Meta, TikTok)"
            },
            {
                "name": "Platform-Specific Rules",
                "task": f"Go to {STREAMLIT_URL} and verify platform-specific business rules - check if DV360, Meta, and TikTok data is processed correctly"
            },
            {
                "name": "Budget Calculations",
                "task": f"Go to {STREAMLIT_URL} and validate that budget calculations and spend aggregations are accurate"
            }
        ]
        
        # Run scenarios in parallel
        print("  ⚡ Launching parallel tests...")
        tasks = []
        for scenario in scenarios:
            agent = Agent(
                task=scenario["task"],
                llm=self.model
            )
            tasks.append(self._run_scenario(agent, scenario))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Summarize results
        print("\n📋 Parallel Validation Summary:")
        for scenario, result in zip(scenarios, results):
            if isinstance(result, Exception):
                print(f"  ❌ {scenario['name']}: Failed - {result}")
            else:
                print(f"  ✅ {scenario['name']}: {result['status']}")
                if result.get('issues'):
                    print(f"     Issues: {', '.join(result['issues'])}")
    
    async def _run_scenario(self, agent: Agent, scenario: dict) -> dict:
        """Run a single validation scenario."""
        try:
            # Execute scenario
            result = await agent.run(scenario['task'])
            
            # Check for issues
            issue_check = await agent.run(
                "Based on what you just tested, list any issues or unexpected behaviors found. "
                "If everything works as expected, say 'No issues found'."
            )
            
            issues = [] if "no issues" in issue_check.lower() else [issue_check]
            
            return {
                "status": "Passed" if not issues else "Has Issues",
                "issues": issues,
                "details": result
            }
        except Exception as e:
            return {
                "status": "Error",
                "issues": [str(e)],
                "details": None
            }
    
    async def adaptive_regression_test(self):
        """Perform adaptive regression testing that learns from changes."""
        print("\n🔄 Adaptive Regression Testing")
        
        agent = Agent(
            task="Perform regression testing on the Media Plan automation system",
            llm=self.model
        )
        
        try:
            # First, understand current behavior
            print("  📊 Establishing baseline behavior...")
            baseline_instruction = f"""
            1. Navigate to {STREAMLIT_URL}
            2. Enable all feature checkboxes in the sidebar
            3. Process a test case with sample files
            4. Document the current behavior for:
               - How markets are mapped
               - What validations are performed
               - What warnings/errors are shown
               - How the output is structured
            5. Create a baseline understanding of expected behavior
            """
            
            baseline = await agent.run(baseline_instruction)
            print(f"  📝 Baseline established")
            
            # Test with variations
            print("  🔬 Testing variations...")
            variation_instruction = """
            Now test with variations:
            1. Try disabling some features and see how behavior changes
            2. Test with files that have slightly different formats
            3. Check edge case handling
            
            For each variation, determine if the changes are expected or unexpected.
            """
            
            variations = await agent.run(variation_instruction)
            print(f"  🔍 Variation analysis complete")
            
            # Generate recommendations
            recommendations = await agent.run(
                "Based on your testing, what test cases should be updated? "
                "What new test cases should be added? Give specific recommendations."
            )
            print(f"\n  📝 Test Recommendations:\n{recommendations}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")


async def run_all_tests():
    """Run all Browser Use tests."""
    print("🤖 Starting Browser Use AI-Powered Business Logic Tests")
    print("=" * 60)
    
    validator = BusinessLogicValidator()
    
    # Run tests sequentially to see results
    await validator.validate_market_mapping_logic()
    await validator.validate_data_transformation_rules()
    await validator.validate_parallel_scenarios()
    await validator.adaptive_regression_test()
    
    print("\n" + "=" * 60)
    print("✅ All Browser Use tests completed!")


if __name__ == "__main__":
    asyncio.run(run_all_tests())