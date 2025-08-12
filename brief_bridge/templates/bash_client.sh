#!/bin/bash
# Brief Bridge Bash HTTP Polling Client
# Compatible with bash 4.0 and later

# Default parameters
SERVER_URL="http://localhost:8000"
CLIENT_ID=""
CLIENT_NAME="Bash Client"
POLL_INTERVAL=5
IDLE_TIMEOUT_MINUTES=10
DEBUG_MODE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --server-url)
            SERVER_URL="$2"
            shift 2
            ;;
        --client-id)
            CLIENT_ID="$2"
            shift 2
            ;;
        --client-name)
            CLIENT_NAME="$2"
            shift 2
            ;;
        --poll-interval)
            POLL_INTERVAL="$2"
            shift 2
            ;;
        --idle-timeout-minutes)
            IDLE_TIMEOUT_MINUTES="$2"
            shift 2
            ;;
        --debug)
            DEBUG_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$CLIENT_ID" ]; then
    echo "Error: CLIENT_ID is required"
    exit 1
fi

# Configuration
API_BASE="$SERVER_URL"
MAX_RETRIES=3
RETRY_DELAY=5
MAX_CONSECUTIVE_404S=3
IDLE_TIMEOUT_SECONDS=$((IDLE_TIMEOUT_MINUTES * 60))

echo "=== Brief Bridge Bash Client ==="
echo "Server: $SERVER_URL"
echo "Client ID: $CLIENT_ID"
echo "Client Name: $CLIENT_NAME"
echo "Poll Interval: $POLL_INTERVAL seconds"
echo "Idle Timeout: $IDLE_TIMEOUT_MINUTES minutes"
echo "Press Ctrl+C to stop"
echo ""

# Lifecycle tracking variables
LAST_COMMAND_TIME=$(date +%s)
CONSECUTIVE_404_COUNT=0
SHOULD_TERMINATE=false

# Function to check idle timeout
check_idle_timeout() {
    local current_time=$(date +%s)
    local idle_time=$((current_time - LAST_COMMAND_TIME))
    
    if [ $idle_time -ge $IDLE_TIMEOUT_SECONDS ]; then
        echo "[LIFECYCLE] Idle timeout reached (${idle_time}s >= ${IDLE_TIMEOUT_SECONDS}s)"
        echo "[LIFECYCLE] Client terminating due to inactivity"
        return 0
    fi
    
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] Idle time: ${idle_time}s / ${IDLE_TIMEOUT_SECONDS}s"
    fi
    
    return 1
}

# Function to handle 404 tracking
check_404_limit() {
    if [ $CONSECUTIVE_404_COUNT -ge $MAX_CONSECUTIVE_404S ]; then
        echo "[LIFECYCLE] Maximum consecutive 404s reached ($CONSECUTIVE_404_COUNT)"
        echo "[LIFECYCLE] Client terminating due to server unavailability"
        return 0
    fi
    return 1
}

# Function to make HTTP requests with enhanced error handling
make_http_request() {
    local uri="$1"
    local method="$2"
    local body="$3"
    local retries="$4"
    
    if [ -z "$retries" ]; then
        retries=$MAX_RETRIES
    fi
    
    for ((i=0; i<retries; i++)); do
        local curl_cmd="curl -s -w 'HTTPSTATUS:%{http_code}' --connect-timeout 30 --max-time 30"
        
        if [ "$method" = "POST" ]; then
            curl_cmd="$curl_cmd -X POST -H 'Content-Type: application/json'"
            if [ -n "$body" ]; then
                curl_cmd="$curl_cmd -d '$body'"
            fi
        fi
        
        curl_cmd="$curl_cmd '$uri'"
        
        local response
        response=$(eval $curl_cmd 2>/dev/null)
        local exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            local http_status=$(echo "$response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
            local body_content=$(echo "$response" | sed 's/HTTPSTATUS:[0-9]*$//')
            
            if [ "$http_status" = "404" ]; then
                CONSECUTIVE_404_COUNT=$((CONSECUTIVE_404_COUNT + 1))
                echo "HTTP 404 - Not Found (consecutive: $CONSECUTIVE_404_COUNT/$MAX_CONSECUTIVE_404S)" >&2
                
                if check_404_limit; then
                    SHOULD_TERMINATE=true
                    echo "Maximum consecutive 404s reached" >&2
                    return 1
                fi
            elif [ "$http_status" -ge 200 ] && [ "$http_status" -lt 300 ]; then
                # Reset 404 counter on successful request
                CONSECUTIVE_404_COUNT=0
                echo "$body_content"
                return 0
            fi
        fi
        
        echo "Request failed (attempt $((i + 1))/$retries): curl exit code $exit_code" >&2
        if [ $i -eq $((retries - 1)) ]; then
            return 1
        fi
        sleep $RETRY_DELAY
    done
    
    return 1
}

# Function to register client
register_client() {
    local body="{\"client_id\": \"$CLIENT_ID\", \"name\": \"$CLIENT_NAME\"}"
    
    local response
    response=$(make_http_request "$API_BASE/clients/register" "POST" "$body")
    
    if [ $? -eq 0 ]; then
        echo "[REGISTER] Client registered successfully"
        return 0
    else
        echo "Failed to register client" >&2
        return 1
    fi
}

# Function to execute bash command
execute_bash_command() {
    local command="$1"
    local timeout_seconds="$2"
    
    if [ -z "$timeout_seconds" ]; then
        timeout_seconds=30
    fi
    
    local start_time=$(date +%s)
    
    # Check for terminate command
    if [ "$(echo "$command" | tr -d '[:space:]')" = "terminate" ]; then
        echo "[LIFECYCLE] Terminate command received from server"
        echo "[LIFECYCLE] Client terminating gracefully..."
        SHOULD_TERMINATE=true
        
        local result="{\"success\": true, \"output\": \"Client terminating gracefully on server request\", \"error\": null, \"execution_time\": 0.1}"
        echo "$result"
        return 0
    fi
    
    echo "[EXEC] $command"
    
    # Update last command time for idle tracking
    LAST_COMMAND_TIME=$(date +%s)
    
    # Execute command and capture output
    local output
    local error_output
    local exit_code
    
    # Create temporary files for output capture
    local stdout_file="/tmp/bb_stdout_$$"
    local stderr_file="/tmp/bb_stderr_$$"
    
    # Execute command with timeout if available
    if command -v timeout >/dev/null 2>&1; then
        timeout "${timeout_seconds}s" bash -c "$command" >"$stdout_file" 2>"$stderr_file"
        exit_code=$?
    else
        bash -c "$command" >"$stdout_file" 2>"$stderr_file"
        exit_code=$?
    fi
    
    # Read output files
    if [ -f "$stdout_file" ]; then
        output=$(cat "$stdout_file")
        rm -f "$stdout_file"
    fi
    
    if [ -f "$stderr_file" ]; then
        error_output=$(cat "$stderr_file")
        rm -f "$stderr_file"
    fi
    
    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    
    # Combine stdout and stderr for output
    local combined_output=""
    if [ -n "$output" ]; then
        combined_output="$output"
    fi
    if [ -n "$error_output" ]; then
        if [ -n "$combined_output" ]; then
            combined_output="$combined_output\n$error_output"
        else
            combined_output="$error_output"
        fi
    fi
    
    # Escape JSON special characters
    combined_output=$(echo "$combined_output" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\t/\\t/g; s/\n/\\n/g; s/\r/\\r/g')
    
    if [ $exit_code -eq 0 ]; then
        echo "[SUCCESS] Execution time: ${execution_time}s"
        local result="{\"success\": true, \"output\": \"$combined_output\", \"error\": null, \"execution_time\": $execution_time}"
    else
        echo "[ERROR] Command failed with exit code $exit_code"
        local error_msg="Command failed with exit code $exit_code"
        error_msg=$(echo "$error_msg" | sed 's/\\/\\\\/g; s/"/\\"/g')
        local result="{\"success\": false, \"output\": \"$combined_output\", \"error\": \"$error_msg\", \"execution_time\": $execution_time}"
    fi
    
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] Generated result JSON: $result" >&2
    fi
    
    echo "$result"
    return 0
}

# Function to submit command result
submit_command_result() {
    local command_id="$1"
    local result="$2"
    
    # Create temp file for JSON payload
    local json_file="/tmp/bb_result_$$"
    
    # Parse individual fields from result JSON
    local success=$(echo "$result" | grep -o '"success":[^,}]*' | cut -d: -f2 | tr -d ' ')
    local output=$(echo "$result" | grep -o '"output":"[^"]*"' | cut -d'"' -f4)
    local error=$(echo "$result" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
    local execution_time=$(echo "$result" | grep -o '"execution_time":[^,}]*' | cut -d: -f2 | tr -d ' ')
    
    # Handle null values and escape for JSON
    if [ "$error" = "null" ] || [ -z "$error" ]; then
        error_json="null"
    else
        error_json="\"$(echo "$error" | sed 's/\\/\\\\/g; s/"/\\"/g')\""
    fi
    
    if [ -z "$output" ]; then
        output_json="\"\""
    else
        output_json="\"$(echo "$output" | sed 's/\\/\\\\/g; s/"/\\"/g')\""
    fi
    
    # Write JSON to temp file (without quotes to allow variable expansion)
    cat > "$json_file" << RESULT_EOF
{
  "command_id": "$command_id",
  "success": $success,
  "output": $output_json,
  "error": $error_json,
  "execution_time": $execution_time
}
RESULT_EOF
    
    # Log the JSON payload being sent
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] JSON payload for command $command_id:" >&2
        cat "$json_file" >&2
    fi
    
    # Submit using curl with @file
    local response
    if response=$(curl -s -w 'HTTPSTATUS:%{http_code}' --connect-timeout 30 --max-time 30 \
        -X POST -H 'Content-Type: application/json' \
        -d @"$json_file" \
        "$API_BASE/commands/result" 2>/dev/null); then
        
        local http_status=$(echo "$response" | grep -o 'HTTPSTATUS:[0-9]*' | cut -d: -f2)
        local body_content=$(echo "$response" | sed 's/HTTPSTATUS:[0-9]*$//')
        
        if [ "$http_status" -ge 200 ] && [ "$http_status" -lt 300 ]; then
            echo "[RESULT] Submitted result for command $command_id"
            rm -f "$json_file"
            return 0
        else
            echo "Failed to submit result: HTTP $http_status" >&2
            echo "[ERROR] Server response: $body_content" >&2
            if [ "$DEBUG_MODE" = "true" ]; then
                echo "[DEBUG] Full response: $response" >&2
            fi
        fi
    else
        echo "Failed to submit result: curl failed" >&2
    fi
    
    # Cleanup and return failure
    rm -f "$json_file"
    return 1
}

# Function to poll for commands
get_pending_command() {
    local body="{\"client_id\": \"$CLIENT_ID\"}"
    
    local response
    response=$(make_http_request "$API_BASE/commands/poll" "POST" "$body")
    
    if [ $? -eq 0 ]; then
        local command_id
        command_id=$(echo "$response" | grep -o '"command_id":"[^"]*"' | cut -d'"' -f4)
        
        if [ -n "$command_id" ]; then
            echo "[POLL] Received command: $command_id"
            echo "$response"
            return 0
        fi
    fi
    
    return 1
}

# Function to parse JSON field
parse_json_field() {
    local json="$1"
    local field="$2"
    echo "$json" | grep -o "\"$field\":\"[^\"]*\"" | cut -d'"' -f4
}

# Cleanup function
cleanup() {
    echo ""
    echo "[LIFECYCLE] Client shutting down..."
    echo "Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Register client
if ! register_client; then
    echo "Failed to register client. Exiting."
    exit 1
fi

# Main polling loop with lifecycle management
consecutive_errors=0
max_consecutive_errors=5

echo "Starting polling loop..."
echo "[LIFECYCLE] Monitoring idle timeout and server availability..."

while [ "$SHOULD_TERMINATE" != "true" ]; do
    # Check lifecycle conditions before polling
    if check_idle_timeout; then
        break
    fi
    
    if check_404_limit; then
        break
    fi
    
    # Poll for pending commands
    command_response=$(get_pending_command)
    
    if [ $? -eq 0 ] && [ -n "$command_response" ]; then
        # Reset error counter on successful poll
        consecutive_errors=0
        
        # Extract command details
        command_id=$(parse_json_field "$command_response" "command_id")
        command_content=$(parse_json_field "$command_response" "command_content")
        timeout=$(parse_json_field "$command_response" "timeout")
        
        if [ -z "$timeout" ]; then
            timeout=30
        fi
        
        # Execute the command
        result=$(execute_bash_command "$command_content" "$timeout")
        
        # Submit the result
        if ! submit_command_result "$command_id" "$result"; then
            echo "Failed to submit result, but continuing..."
        fi
        
        # Check if command triggered termination
        if [ "$SHOULD_TERMINATE" = "true" ]; then
            echo "[LIFECYCLE] Termination triggered by command execution"
            break
        fi
    else
        # No commands available or error, reset error counter for normal polls
        if [ $consecutive_errors -lt $max_consecutive_errors ]; then
            consecutive_errors=0
        else
            consecutive_errors=$((consecutive_errors + 1))
            echo "Polling error ($consecutive_errors/$max_consecutive_errors)" >&2
            
            if [ $consecutive_errors -ge $max_consecutive_errors ]; then
                echo "[LIFECYCLE] Too many consecutive errors. Exiting."
                break
            fi
        fi
        
        # Check if termination was triggered during error handling
        if [ "$SHOULD_TERMINATE" = "true" ]; then
            echo "[LIFECYCLE] Termination triggered during error handling"
            break
        fi
    fi
    
    # Wait before next poll
    sleep $POLL_INTERVAL
done

cleanup