#!/bin/bash
# Simple test for debugging
set -e

CLIENT_ID="simple-test-001"
SERVER_URL="http://localhost:8000"

echo "=== Testing Registration ==="
response=$(curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"client_id\":\"$CLIENT_ID\",\"name\":\"Simple Test\"}" \
    "$SERVER_URL/clients/register")
echo "Registration response: $response"

echo "=== Testing Commands Poll ==="
response=$(curl -s "$SERVER_URL/commands/client/$CLIENT_ID")
echo "Commands response: '$response'"

echo "=== Testing jq parsing ==="
echo "$response" | jq -r 'length'

echo "=== Testing filtering ==="
echo "$response" | jq -r '[.[] | select(.status == "pending")]'