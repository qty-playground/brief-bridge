# Manual QA Test Plan - Brief Bridge System

## 📋 Test Overview

**Test Objective**: Verify end-to-end functionality of Brief Bridge system including server APIs, client registration, command submission, and client execution.

**Test Environment**:
- Server: Brief Bridge FastAPI (Python)  
- Client: Linux/macOS shell script
- Platform: macOS/Linux
- Dependencies: curl, jq

**Test Duration**: ~30-45 minutes

---

## 🧪 Test Cases

### **TC01: System Startup and Health Check**
**Priority**: P0 (Blocker)  
**Objective**: Verify server starts correctly and health endpoints work

**Pre-conditions**: 
- Server not running
- Dependencies installed

**Test Steps**:
1. Start Brief Bridge server: `uvicorn brief_bridge.main:app --reload`
2. Verify server starts without errors
3. Test health endpoint: `curl http://localhost:8000/health`
4. Test root endpoint: `curl http://localhost:8000/`
5. Verify OpenAPI docs: Open `http://localhost:8000/docs`

**Expected Results**:
- Server starts on port 8000 without errors
- Health endpoint returns `{"status": "healthy"}`
- Root endpoint returns `{"message": "Brief Bridge API"}`
- Swagger docs load successfully
- All API endpoints visible in documentation

---

### **TC02: Client Script Dependencies**
**Priority**: P0 (Blocker)  
**Objective**: Verify client script dependencies and help functionality

**Test Steps**:
1. Check `curl` availability: `which curl`
2. Check `jq` availability: `which jq` 
3. Test client script help: `./testkits/clients/brief-client.sh --help`
4. Test client script without required args: `./testkits/clients/brief-client.sh`

**Expected Results**:
- `curl` and `jq` are available (install with `brew install curl jq` if missing)
- Help message displays correctly with usage information
- Script shows error when `--client-id` is missing

---

### **TC03: Client Registration - Success Case**
**Priority**: P0 (Critical)  
**Objective**: Verify successful client registration

**Test Steps**:
1. Start client with valid parameters:
   ```bash
   ./testkits/clients/brief-client.sh --client-id qa-test-001 --client-name "QA Test Client" --debug
   ```
2. Observe registration logs
3. Verify in another terminal: `curl http://localhost:8000/clients/qa-test-001`
4. List all clients: `curl http://localhost:8000/clients/`

**Expected Results**:
- Client registration successful message appears
- Client appears in GET /clients/{client_id} response
- Client appears in GET /clients/ list
- Client starts polling for commands

---

### **TC04: Client Registration - Duplicate Registration**
**Priority**: P1 (Important)  
**Objective**: Verify behavior with duplicate client registration

**Test Steps**:
1. Keep first client (qa-test-001) running
2. Start second client with same ID in another terminal:
   ```bash
   ./testkits/clients/brief-client.sh --client-id qa-test-001 --client-name "Duplicate Client" --debug
   ```
3. Observe both client behaviors

**Expected Results**:
- Second client registers successfully (updates existing client info)
- Both clients continue polling
- Only one entry in clients list with updated information

---

### **TC05: Command Submission via API**
**Priority**: P0 (Critical)  
**Objective**: Verify command submission to registered client

**Test Steps**:
1. Ensure qa-test-001 client is running
2. Submit simple command via API:
   ```bash
   curl -X POST http://localhost:8000/commands/submit \
   -H "Content-Type: application/json" \
   -d '{
     "target_client_id": "qa-test-001",
     "command_content": "echo \"Hello from Brief Bridge\"",
     "command_type": "shell"
   }'
   ```
3. Observe client terminal for command execution
4. Check command was created: `curl http://localhost:8000/commands/`

**Expected Results**:
- API returns successful submission response with command_id
- Client executes command and shows output "Hello from Brief Bridge"
- Command appears in commands list with "pending" status

---

### **TC06: Command Submission - Multiple Commands**
**Priority**: P1 (Important)  
**Objective**: Verify multiple commands can be submitted and executed

**Test Steps**:
1. Submit multiple commands:
   ```bash
   curl -X POST http://localhost:8000/commands/submit \
   -H "Content-Type: application/json" \
   -d '{"target_client_id": "qa-test-001", "command_content": "pwd", "command_type": "shell"}'
   
   curl -X POST http://localhost:8000/commands/submit \
   -H "Content-Type: application/json" \
   -d '{"target_client_id": "qa-test-001", "command_content": "date", "command_type": "shell"}'
   
   curl -X POST http://localhost:8000/commands/submit \
   -H "Content-Type: application/json" \
   -d '{"target_client_id": "qa-test-001", "command_content": "uname -a", "command_type": "shell"}'
   ```
2. Observe client execution of all commands
3. Check commands list: `curl http://localhost:8000/commands/client/qa-test-001`

**Expected Results**:
- All three commands execute successfully in sequence
- Client shows current working directory, current date, and system info
- All commands appear in client's command list

---

### **TC07: Command Submission - Error Cases**
**Priority**: P1 (Important)  
**Objective**: Verify proper error handling for invalid submissions

**Test Steps**:
1. Submit to unregistered client:
   ```bash
   curl -X POST http://localhost:8000/commands/submit \
   -H "Content-Type: application/json" \
   -d '{"target_client_id": "nonexistent-client", "command_content": "echo test", "command_type": "shell"}'
   ```
2. Submit with empty content:
   ```bash
   curl -X POST http://localhost:8000/commands/submit \
   -H "Content-Type: application/json" \
   -d '{"target_client_id": "qa-test-001", "command_content": "", "command_type": "shell"}'
   ```
3. Submit with empty client ID:
   ```bash
   curl -X POST http://localhost:8000/commands/submit \
   -H "Content-Type: application/json" \
   -d '{"target_client_id": "", "command_content": "echo test", "command_type": "shell"}'
   ```

**Expected Results**:
- Case 1: Returns error "Target client not found"
- Case 2: Returns error "Command content cannot be empty"
- Case 3: Returns error "Target client ID cannot be empty"
- No commands are created for failed submissions

---

### **TC08: Command with Errors**
**Priority**: P1 (Important)  
**Objective**: Verify client handles command execution errors

**Test Steps**:
1. Submit command that will fail:
   ```bash
   curl -X POST http://localhost:8000/commands/submit \
   -H "Content-Type: application/json" \
   -d '{"target_client_id": "qa-test-001", "command_content": "ls /nonexistent/directory", "command_type": "shell"}'
   ```
2. Observe client behavior and logging

**Expected Results**:
- Client attempts to execute command
- Client logs show command failed with appropriate exit code
- Client continues polling after error (doesn't crash)

---

### **TC09: Multiple Clients**
**Priority**: P1 (Important)  
**Objective**: Verify system works with multiple registered clients

**Test Steps**:
1. Start second client:
   ```bash
   ./testkits/clients/brief-client.sh --client-id qa-test-002 --client-name "Second QA Client" --debug
   ```
2. Submit commands to both clients:
   ```bash
   curl -X POST http://localhost:8000/commands/submit \
   -H "Content-Type: application/json" \
   -d '{"target_client_id": "qa-test-001", "command_content": "echo \"Client 001 here\"", "command_type": "shell"}'
   
   curl -X POST http://localhost:8000/commands/submit \
   -H "Content-Type: application/json" \
   -d '{"target_client_id": "qa-test-002", "command_content": "echo \"Client 002 here\"", "command_type": "shell"}'
   ```
3. Verify both clients execute their respective commands
4. Check clients list: `curl http://localhost:8000/clients/`

**Expected Results**:
- Both clients register successfully
- Commands are routed to correct clients
- Each client only executes commands targeted to them
- Both clients appear in clients list

---

### **TC10: API Endpoints Validation**
**Priority**: P1 (Important)  
**Objective**: Verify all API endpoints work correctly

**Test Steps**:
1. Test GET /clients/ - List all clients
2. Test GET /clients/{client_id} - Get specific client  
3. Test GET /commands/ - List all commands
4. Test GET /commands/{command_id} - Get specific command (use ID from previous test)
5. Test GET /commands/client/{client_id} - Get commands for specific client

**Expected Results**:
- All endpoints return 200 status
- Responses match expected schema
- Data consistency across endpoints
- Proper 404 responses for nonexistent resources

---

### **TC11: Client Graceful Shutdown**
**Priority**: P2 (Nice to have)  
**Objective**: Verify client handles shutdown correctly

**Test Steps**:
1. Start client and wait for registration
2. Send SIGINT (Ctrl+C) to client
3. Observe shutdown behavior

**Expected Results**:
- Client displays "Shutting down client..." message
- Client exits gracefully without errors
- No zombie processes left behind

---

### **TC12: Server Performance Under Load**
**Priority**: P2 (Nice to have)  
**Objective**: Basic performance validation

**Test Steps**:
1. Start 3-5 clients with different IDs
2. Submit 10-20 commands rapidly using a loop:
   ```bash
   for i in {1..10}; do
     curl -X POST http://localhost:8000/commands/submit \
     -H "Content-Type: application/json" \
     -d "{\"target_client_id\": \"qa-test-001\", \"command_content\": \"echo Command $i\", \"command_type\": \"shell\"}"
   done
   ```
3. Observe system behavior

**Expected Results**:
- Server remains responsive
- All commands are eventually executed
- No errors or crashes occur
- Clients process commands in reasonable time

---

## 📊 Test Result Collection Template

### Test Execution Summary
- **Date**: ___________
- **Tester**: ___________  
- **Environment**: ___________
- **Server Version**: ___________
- **Total Test Cases**: 12
- **Passed**: ___/12
- **Failed**: ___/12
- **Blocked**: ___/12

### Detailed Results
| Test Case | Status | Notes | Issues Found |
|-----------|---------|-------|-------------|
| TC01 | ⚪ | | |
| TC02 | ⚪ | | |
| TC03 | ⚪ | | |
| TC04 | ⚪ | | |
| TC05 | ⚪ | | |
| TC06 | ⚪ | | |
| TC07 | ⚪ | | |
| TC08 | ⚪ | | |
| TC09 | ⚪ | | |
| TC10 | ⚪ | | |
| TC11 | ⚪ | | |
| TC12 | ⚪ | | |

**Legend**: ✅ Pass | ❌ Fail | ⚠️ Blocked | ⚪ Not Tested

### Critical Issues Found
1. ___________
2. ___________

### Recommendations
1. ___________
2. ___________

### Overall System Assessment
- **Functionality**: ___________
- **Reliability**: ___________
- **Performance**: ___________
- **Usability**: ___________