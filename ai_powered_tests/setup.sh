#!/bin/bash

echo "🚀 Setting up AI-powered testing environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file from .env.example"
    echo "   Please update it with your API keys!"
    cp .env.example .env
fi

# Install Node.js dependencies for Stagehand
echo ""
echo "📦 Installing Node.js dependencies for Stagehand..."
npm install

# Install Python dependencies for Browser Use
echo ""
echo "🐍 Installing Python dependencies for Browser Use..."
pip install -r requirements.txt

# Install Playwright browsers
echo ""
echo "🌐 Installing Playwright browsers..."
npx playwright install chromium
python -m playwright install chromium

echo ""
echo "✅ Setup complete!"
echo ""
echo "⚠️  Important: Please update the .env file with your API keys:"
echo "   - OPENAI_API_KEY (for GPT-4 models)"
echo "   - ANTHROPIC_API_KEY (for Claude models)"
echo "   - LANGCHAIN_API_KEY (optional, for LangChain tracing)"
echo ""
echo "📚 To run tests:"
echo "   - Stagehand tests: npm run test:stagehand"
echo "   - Browser Use tests: npm run test:browser-use"
echo "   - All tests: npm run test:all"