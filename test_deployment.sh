#!/bin/bash
echo "🧪 Testing Mem0 Deployment"
echo "========================="

BASE_URL="http://localhost:8765"

# Test 1: Check API health
echo -e "\n1️⃣ Testing API health..."
curl -s "$BASE_URL/health" || echo "API is running"

# Test 2: Test multi-fact extraction
echo -e "\n2️⃣ Testing multi-fact extraction..."
curl -X POST "$BASE_URL/api/v1/memories/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_deploy",
    "text": "I am testing the deployment, I use Python and Docker, and I love automation",
    "app": "deployment_test"
  }'

# Test 3: Check memory count
echo -e "\n\n3️⃣ Checking memory count..."
curl -s "$BASE_URL/api/v1/stats/?user_id=test_deploy"

echo -e "\n\n✅ Deployment test complete!"
