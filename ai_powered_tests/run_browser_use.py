"""
Simplified Browser Use test runner.
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import browser_use
try:
    from browser_use import Agent
    from langchain_openai import ChatOpenAI
    print("✅ Browser Use imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Installing browser-use...")
    import subprocess
    subprocess.run(["pip", "install", "browser-use", "langchain-openai"])
    from browser_use import Agent
    from langchain_openai import ChatOpenAI

# Configuration
STREAMLIT_URL = os.getenv("STREAMLIT_APP_URL", "http://localhost:8501")

async def test_with_browser_use():
    """Run Browser Use test."""
    print("\n🌐 Starting Browser Use Test")
    print("=" * 60)
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create agent
    agent = Agent(
        task="Test the Streamlit Media Plan automation app",
        llm=llm
    )
    
    try:
        # Test 1: Navigate and check features
        print("\n📌 Test 1: Navigate to app and enable features")
        result = await agent.run(f"""
        1. Go to {STREAMLIT_URL}
        2. Enable all checkbox features in the sidebar
        3. Report which features were enabled
        """)
        print(f"Result: {result}")
        
        # Test 2: Upload files
        print("\n📌 Test 2: Upload test files")
        result = await agent.run("""
        Upload these test files:
        1. First file input: ../test_fixtures/PLANNED_TEST_FIXTURE.xlsx
        2. Second file input: ../test_fixtures/DELIVERED_TEST_FIXTURE.xlsx  
        3. Third file input: ../test_fixtures/OUTPUT_TEMPLATE_TEST_FIXTURE.xlsx
        Then click Process Files button
        """)
        print(f"Result: {result}")
        
        # Test 3: Validate results
        print("\n📌 Test 3: Validate processing results")
        result = await agent.run("""
        Check the results after processing:
        1. Are there any validation warnings?
        2. Is the output ready for download?
        3. What's the overall status?
        """)
        print(f"Result: {result}")
        
        print("\n✅ Browser Use test completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if Streamlit is running on http://localhost:8501")
        print("2. Verify OpenAI API key is set correctly")
        print("3. Ensure test fixture files exist")

if __name__ == "__main__":
    print("🤖 Browser Use AI Test Runner")
    asyncio.run(test_with_browser_use())