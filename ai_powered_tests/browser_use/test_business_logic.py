"""
Browser Use AI-powered tests for business logic validation.
This handles complex business logic changes that break traditional unit tests.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
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
        self.headless = HEADLESS
        
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
            result = await agent.run("Navigate to " + STREAMLIT_URL)
            
            # Upload test files with known data
            test_instruction = """
            1. Upload the test files:
               - Planned file: test_fixtures/PLANNED_TEST_FIXTURE.xlsx
               - Delivered file: test_fixtures/DELIVERED_TEST_FIXTURE.xlsx  
               - Template file: test_fixtures/OUTPUT_TEMPLATE_TEST_FIXTURE.xlsx
            2. Process the files
            3. Analyze the mapping results and verify:
               - Market names are correctly mapped
               - Platform data is properly aligned
               - Values are accurately transferred
            4. Return a detailed validation report
            """
            
            result = await agent.execute(test_instruction)
            print(f"  Market Mapping Validation: {result}")
            
            # AI analyzes if business logic is correct
            validation_check = await agent.execute(
                "Based on the processed data, are there any discrepancies in how markets "
                "are mapped between planned and delivered data? List any issues found."
            )
            print(f"  Issues Found: {validation_check}")
            
        finally:
            await browser.close()
    
    async def validate_data_transformation_rules(self):
        """Validate data transformation rules with AI understanding."""
        print("\n📊 Testing Data Transformation Rules")
        
        browser = Browser(config=self.browser_config)
        agent = Agent(
            task="Validate data transformation rules and calculations",
            llm=self.model,
            browser=browser
        )
        
        try:
            await agent.execute("Navigate to " + STREAMLIT_URL)
            
            # Test with edge cases
            edge_case_instruction = """
            Test the following edge cases in data transformation:
            1. Empty market names - should they be handled?
            2. Duplicate entries - how are they consolidated?
            3. Missing values - what's the fallback behavior?
            4. Currency conversions - are they applied correctly?
            5. Date format handling - are all formats supported?
            
            Document how each case is handled and whether it aligns with expected business logic.
            """
            
            result = await agent.execute(edge_case_instruction)
            print(f"  Edge Case Handling: {result}")
            
        finally:
            await browser.close()
    
    async def validate_parallel_scenarios(self):
        """Run multiple validation scenarios in parallel."""
        print("\n🚀 Running Parallel Validation Scenarios")
        
        scenarios = [
            {
                "name": "Multi-Market Validation",
                "task": "Validate handling of multiple markets across different platforms"
            },
            {
                "name": "Platform-Specific Rules",
                "task": "Verify platform-specific business rules for DV360, Meta, and TikTok"
            },
            {
                "name": "Budget Calculations",
                "task": "Validate budget calculations and spend aggregations"
            },
            {
                "name": "Time Period Handling",
                "task": "Verify correct handling of different time periods and date ranges"
            }
        ]
        
        # Run scenarios in parallel
        tasks = []
        for scenario in scenarios:
            browser = Browser(config=self.browser_config)
            agent = Agent(
                task=scenario["task"],
                llm=self.model,
                browser=browser
            )
            tasks.append(self._run_scenario(agent, browser, scenario))
        
        results = await asyncio.gather(*tasks)
        
        # Summarize results
        print("\n📋 Parallel Validation Summary:")
        for scenario, result in zip(scenarios, results):
            print(f"  - {scenario['name']}: {result['status']}")
            if result['issues']:
                print(f"    Issues: {', '.join(result['issues'])}")
    
    async def _run_scenario(self, agent: Agent, browser: Browser, scenario: dict) -> dict:
        """Run a single validation scenario."""
        try:
            await agent.execute(f"Navigate to {STREAMLIT_URL}")
            
            # Execute scenario-specific validation
            result = await agent.execute(
                f"Perform the following validation: {scenario['task']}. "
                f"Upload necessary test files and analyze the results. "
                f"Return a summary of findings."
            )
            
            # Check for issues
            issue_check = await agent.execute(
                "Based on your analysis, list any issues or unexpected behaviors found. "
                "If everything works as expected, return 'No issues found'."
            )
            
            issues = [] if "no issues" in issue_check.lower() else [issue_check]
            
            return {
                "status": "✅ Passed" if not issues else "⚠️ Issues Found",
                "issues": issues,
                "details": result
            }
        finally:
            await browser.close()
    
    async def adaptive_regression_test(self):
        """Perform adaptive regression testing that learns from changes."""
        print("\n🔄 Adaptive Regression Testing")
        
        browser = Browser(config=self.browser_config)
        agent = Agent(
            task="Perform regression testing while adapting to legitimate business logic changes",
            llm=self.model,
            browser=browser
        )
        
        try:
            await agent.execute("Navigate to " + STREAMLIT_URL)
            
            # First, understand current behavior
            baseline_instruction = """
            1. Process a standard test case with all features enabled
            2. Document the current behavior for:
               - How markets are mapped
               - How validations are performed
               - What warnings/errors are shown
               - How the output is structured
            3. Create a baseline understanding of expected behavior
            """
            
            baseline = await agent.execute(baseline_instruction)
            print(f"  Baseline established: {baseline[:200]}...")
            
            # Test with variations
            variation_instruction = """
            Now test with variations:
            1. Disable some features and see how behavior changes
            2. Use files with slightly different formats
            3. Test with edge case data
            
            For each variation, determine if the changes are:
            - Expected (due to feature changes)
            - Bugs (unexpected behavior)
            - Improvements (better handling than baseline)
            """
            
            variations = await agent.execute(variation_instruction)
            print(f"  Variation analysis: {variations[:200]}...")
            
            # Generate adaptive test recommendations
            recommendations = await agent.execute(
                "Based on your testing, what test cases should be updated to reflect "
                "the current business logic? What new test cases should be added?"
            )
            print(f"\n  📝 Test Recommendations:\n{recommendations}")
            
        finally:
            await browser.close()


async def run_all_tests():
    """Run all Browser Use tests."""
    validator = BusinessLogicValidator()
    
    # Run tests sequentially to see results
    await validator.validate_market_mapping_logic()
    await validator.validate_data_transformation_rules()
    await validator.validate_parallel_scenarios()
    await validator.adaptive_regression_test()


if __name__ == "__main__":
    print("🤖 Starting Browser Use AI-Powered Business Logic Tests\n")
    asyncio.run(run_all_tests())
    print("\n✅ All Browser Use tests completed!")