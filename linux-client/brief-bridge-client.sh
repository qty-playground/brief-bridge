#!/bin/bash
# Brief Bridge Client Script for Linux/macOS with Base64 support
# Handles client registration, command polling, and base64 encoded commands

set -euo pipefail

# Default configuration
SERVER_URL="http://localhost:2266"
CLIENT_ID=""
CLIENT_NAME=""
POLL_INTERVAL=5
LOG_FILE=""
DEBUG=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO") echo -e "${GREEN}[INFO]${NC} $timestamp - $message" ;;
        "WARN") echo -e "${YELLOW}[WARN]${NC} $timestamp - $message" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} $timestamp - $message" >&2 ;;
        "DEBUG") 
            if [ "$DEBUG" = true ]; then
                echo -e "${BLUE}[DEBUG]${NC} $timestamp - $message"
            fi
            ;;
    esac
    
    # Write to log file if specified
    if [ -n "$LOG_FILE" ]; then
        echo "[$level] $timestamp - $message" >> "$LOG_FILE"
    fi
}

# Display usage information
usage() {
    cat << EOF
Brief Bridge Client v1.1.0 - Linux/macOS

Usage: $0 [OPTIONS]

OPTIONS:
    --server URL         Brief Bridge server URL (default: http://localhost:2266)
    --client-id ID       Unique client identifier (required)
    --client-name NAME   Human-readable client name (optional)
    --poll-interval SEC  Polling interval in seconds (default: 5)
    --log-file FILE      Log file path (optional)
    --debug              Enable debug logging
    --help               Show this help message

Examples:
    $0 --client-id test-client-001
    $0 --server http://192.168.1.100:2266 --client-id laptop-001 --client-name "My Laptop"
    $0 --client-id ci-runner --poll-interval 2 --debug

Features:
    ✓ Base64 encoded commands support
    ✓ Enhanced error handling and logging  
    ✓ Comprehensive command execution reporting
    ✓ Graceful shutdown handling

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --server)
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
            --log-file)
                LOG_FILE="$2"
                shift 2
                ;;
            --debug)
                DEBUG=true
                shift
                ;;
            --help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1" >&2
                usage
                exit 1
                ;;
        esac
    done
    
    # Validate required arguments
    if [ -z "$CLIENT_ID" ]; then
        echo "Error: --client-id is required" >&2
        usage
        exit 1
    fi
    
    # Set default client name if not provided
    if [ -z "$CLIENT_NAME" ]; then
        CLIENT_NAME="Bash-Client-$CLIENT_ID"
    fi
}

# Check if required tools are available
check_dependencies() {
    local missing=()
    
    if ! command -v curl &> /dev/null; then
        missing+=("curl")
    fi
    
    if ! command -v jq &> /dev/null; then
        missing+=("jq")
    fi
    
    if ! command -v base64 &> /dev/null; then
        missing+=("base64")
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        log "ERROR" "Missing required dependencies: ${missing[*]}"
        log "INFO" "Please install missing tools:"
        for tool in "${missing[@]}"; do
            case "$tool" in
                "curl") log "INFO" "  - Ubuntu/Debian: sudo apt-get install curl" ;;
                "jq") log "INFO" "  - Ubuntu/Debian: sudo apt-get install jq" ;;
                "base64") log "INFO" "  - Usually included in coreutils package" ;;
            esac
        done
        exit 1
    fi
}

# Register client with server
register_client() {
    log "INFO" "Registering client '$CLIENT_ID' with server $SERVER_URL"
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "{\"client_id\":\"$CLIENT_ID\",\"name\":\"$CLIENT_NAME\"}" \
        "$SERVER_URL/clients/register" 2>/dev/null)
    
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    log "DEBUG" "Registration response: HTTP $http_code, Body: $body"
    
    if [ "$http_code" != "200" ]; then
        log "ERROR" "Failed to register client (HTTP $http_code)"
        log "ERROR" "Response: $body"
        return 1
    fi
    
    # Parse response to check success
    local success=$(echo "$body" | jq -r '.success' 2>/dev/null || echo "false")
    if [ "$success" != "true" ]; then
        log "ERROR" "Registration failed: $(echo "$body" | jq -r '.message' 2>/dev/null || echo 'Unknown error')"
        return 1
    fi
    
    log "INFO" "Client registration successful"
    log "DEBUG" "Registration details: $(echo "$body" | jq -c . 2>/dev/null || echo "$body")"
    return 0
}

# Get pending commands using polling API
get_pending_commands() {
    log "DEBUG" "Polling for commands for client '$CLIENT_ID'"
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "{\"client_id\":\"$CLIENT_ID\"}" \
        "$SERVER_URL/commands/poll" 2>/dev/null)
    
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" != "200" ]; then
        log "WARN" "Failed to poll for commands (HTTP $http_code): $body"
        return 1
    fi
    
    # Check if we got a command
    if [ -n "$body" ] && [ "$body" != "{}" ]; then
        local command_id=$(echo "$body" | jq -r '.command_id' 2>/dev/null)
        if [ "$command_id" != "null" ] && [ -n "$command_id" ]; then
            log "INFO" "Found command: $command_id"
            echo "$body"
            return 0
        fi
    fi
    
    log "DEBUG" "No pending commands found"
    return 0
}

# Decode base64 content if needed
decode_command_content() {
    local content="$1"
    local encoding="$2"
    
    if [ "$encoding" = "base64" ]; then
        log "DEBUG" "Decoding base64 encoded command"
        
        # Validate base64 format first
        if ! echo "$content" | grep -qE '^[A-Za-z0-9+/]*={0,2}$'; then
            log "ERROR" "Invalid base64 format"
            return 1
        fi
        
        local decoded_content
        if decoded_content=$(echo "$content" | base64 -d 2>/dev/null) && [ -n "$decoded_content" ]; then
            log "DEBUG" "Successfully decoded base64 command"
            log "DEBUG" "Decoded content: $decoded_content"
            echo "$decoded_content"
        else
            log "ERROR" "Failed to decode base64 command"
            return 1
        fi
    else
        echo "$content"
    fi
}

# Execute a single command
execute_command() {
    local command_json="$1"
    
    local command_id=$(echo "$command_json" | jq -r '.command_id')
    local content=$(echo "$command_json" | jq -r '.command_content')
    local timeout=$(echo "$command_json" | jq -r '.timeout // 300')
    
    log "INFO" "Executing command: $command_id"
    log "DEBUG" "Command content: $content"
    log "DEBUG" "Command timeout: ${timeout}s"
    
    local start_time=$(date +%s.%N)
    local exit_code=0
    local output=""
    local error_message=""
    
    # Execute command with timeout
    if output=$(timeout "$timeout" bash -c "$content" 2>&1); then
        exit_code=0
        log "INFO" "Command executed successfully"
        log "DEBUG" "Command output: $output"
    else
        exit_code=$?
        if [ $exit_code -eq 124 ]; then
            error_message="Command timed out after ${timeout} seconds"
            log "WARN" "$error_message"
        else
            error_message="Command failed with exit code $exit_code"
            log "WARN" "$error_message"
            log "DEBUG" "Command error output: $output"
        fi
    fi
    
    local end_time=$(date +%s.%N)
    local execution_time=$(echo "$end_time - $start_time" | bc -l)
    
    # Submit execution result back to server
    submit_command_result "$command_id" "$output" "$error_message" "$execution_time" $exit_code
}

# Submit command execution result back to server
submit_command_result() {
    local command_id="$1"
    local output="$2"
    local error_message="$3"
    local execution_time="$4"
    local exit_code="$5"
    
    log "DEBUG" "Submitting result for command: $command_id"
    
    local success="true"
    if [ $exit_code -ne 0 ]; then
        success="false"
    fi
    
    # Escape JSON strings properly
    local json_output=$(echo "$output" | jq -Rs .)
    local json_error=""
    if [ -n "$error_message" ]; then
        json_error=$(echo "$error_message" | jq -Rs .)
    else
        json_error="null"
    fi
    
    local result_data="{
        \"command_id\": \"$command_id\",
        \"success\": $success,
        \"output\": $json_output,
        \"error\": $json_error,
        \"execution_time\": $execution_time
    }"
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$result_data" \
        "$SERVER_URL/commands/result" 2>/dev/null)
    
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        log "INFO" "Command result submitted successfully"
        log "DEBUG" "Result response: $body"
    else
        log "ERROR" "Failed to submit command result (HTTP $http_code): $body"
    fi
}

# Main polling loop
start_polling() {
    log "INFO" "Starting command polling (interval: ${POLL_INTERVAL}s)"
    log "INFO" "Press Ctrl+C to stop"
    
    # Trap signals for graceful shutdown
    trap 'log "INFO" "Shutting down client..."; exit 0' SIGINT SIGTERM
    
    while true; do
        if command_data=$(get_pending_commands); then
            if [ -n "$command_data" ] && [ "$command_data" != "{}" ]; then
                # Extract command info
                local command_content=$(echo "$command_data" | jq -r '.command_content')
                local encoding=$(echo "$command_data" | jq -r '.encoding // empty')
                
                # Decode base64 if needed
                local decoded_content
                if decoded_content=$(decode_command_content "$command_content" "$encoding"); then
                    # Update the command data with decoded content
                    local updated_command_data=$(echo "$command_data" | jq --arg content "$decoded_content" '.command_content = $content')
                    execute_command "$updated_command_data"
                else
                    # Base64 decode failed - report error
                    local command_id=$(echo "$command_data" | jq -r '.command_id')
                    submit_command_result "$command_id" "" "Invalid base64 encoding" "0.0" 1
                fi
            fi
        fi
        
        sleep "$POLL_INTERVAL"
    done
}

# Display startup banner
show_startup_banner() {
    echo ""
    echo "================================"
    echo "  Brief Bridge Client v1.1.0"
    echo "  Linux/macOS Bash Client"
    echo "================================"
    echo ""
}

# Cleanup function
cleanup() {
    log "INFO" "Client shutdown complete"
}

# Main function
main() {
    # Setup cleanup on exit
    trap cleanup EXIT
    
    # Parse arguments
    parse_args "$@"
    
    # Check dependencies
    check_dependencies
    
    # Display startup information
    show_startup_banner
    
    log "INFO" "Brief Bridge Client starting..."
    log "INFO" "Server: $SERVER_URL"
    log "INFO" "Client ID: $CLIENT_ID"
    log "INFO" "Client Name: $CLIENT_NAME"
    log "INFO" "Poll Interval: ${POLL_INTERVAL}s"
    
    if [ -n "$LOG_FILE" ]; then
        log "INFO" "Logging to: $LOG_FILE"
        # Create log file directory if it doesn't exist
        mkdir -p "$(dirname "$LOG_FILE")"
    fi
    
    # Register with server
    if ! register_client; then
        log "ERROR" "Failed to register client. Exiting."
        exit 1
    fi
    
    # Start polling loop
    start_polling
}

# Run main function with all arguments
main "$@"