#!/bin/bash

# Test script cho Hybrid Chat System
echo "🧪 Testing Hybrid Chat System"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test endpoints
BACKEND_URL="http://localhost:5000"
CHATBOT_URL="http://localhost:5001"
RASA_URL="http://localhost:5005"

echo -e "\n${YELLOW}1. Testing Backend Health${NC}"
curl -s "$BACKEND_URL/api/health" | jq '.' || echo -e "${RED}❌ Backend not responding${NC}"

echo -e "\n${YELLOW}2. Testing Chatbot Health${NC}"
curl -s "$CHATBOT_URL/health" | jq '.' || echo -e "${RED}❌ Chatbot not responding${NC}"

echo -e "\n${YELLOW}3. Testing Rasa Health${NC}"
curl -s "$RASA_URL/status" | jq '.' || echo -e "${RED}❌ Rasa not responding${NC}"

echo -e "\n${YELLOW}4. Testing Hybrid Chat Health${NC}"
curl -s "$BACKEND_URL/api/hybrid-chat/health" | jq '.' || echo -e "${RED}❌ Hybrid Chat not responding${NC}"

echo -e "\n${YELLOW}5. Testing Anonymous Chat${NC}"
curl -X POST "$BACKEND_URL/api/hybrid-chat/chat/anonymous" \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào", "session_id": "test_session"}' \
  | jq '.' || echo -e "${RED}❌ Anonymous chat failed${NC}"

echo -e "\n${YELLOW}6. Testing Rasa Direct${NC}"
curl -X POST "$RASA_URL/webhooks/rest/webhook" \
  -H "Content-Type: application/json" \
  -d '{"sender": "test", "message": "hello"}' \
  | jq '.' || echo -e "${RED}❌ Rasa webhook failed${NC}"

echo -e "\n${YELLOW}7. Testing Chatbot Direct${NC}"
curl -X POST "$CHATBOT_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào", "user_id": "test"}' \
  | jq '.' || echo -e "${RED}❌ Chatbot direct failed${NC}"

echo -e "\n${GREEN}✅ Test completed!${NC}"
echo -e "Check the responses above to verify the hybrid system is working correctly."