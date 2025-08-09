#!/bin/bash
# Brief Bridge Client Script for Linux/macOS
# Handles client registration and command polling

set -euo pipefail

# Default configuration
SERVER_URL="http://localhost:8000"
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
Brief Bridge Client - Linux/macOS

Usage: $0 [OPTIONS]

OPTIONS:
    --server URL         Brief Bridge server URL (default: http://localhost:8000)
    --client-id ID       Unique client identifier (required)
    --client-name NAME   Human-readable client name (optional)
    --poll-interval SEC  Polling interval in seconds (default: 5)
    --log-file FILE      Log file path (optional)
    --debug              Enable debug logging
    --help               Show this help message

Examples:
    $0 --client-id test-client-001
    $0 --server http://192.168.1.100:8000 --client-id laptop-001 --client-name "My Laptop"
    $0 --client-id ci-runner --poll-interval 2 --debug

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
        CLIENT_NAME="Client-$CLIENT_ID"
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
    
    if [ ${#missing[@]} -ne 0 ]; then
        log "ERROR" "Missing required dependencies: ${missing[*]}"
        log "INFO" "Please install missing tools:"
        for tool in "${missing[@]}"; do
            case "$tool" in
                "curl") log "INFO" "  - macOS: brew install curl" ;;
                "jq") log "INFO" "  - macOS: brew install jq" ;;
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

# Get pending commands for this client
get_pending_commands() {
    log "DEBUG" "Polling for commands for client '$CLIENT_ID'"
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" \
        "$SERVER_URL/commands/client/$CLIENT_ID" 2>/dev/null)
    
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" != "200" ]; then
        log "WARN" "Failed to get commands (HTTP $http_code): $body"
        return 1
    fi
    
    # Filter only pending commands
    local pending_commands
    local count
    
    if [ -n "$body" ] && [ "$body" != "" ]; then
        pending_commands=$(echo "$body" | jq -r '[.[] | select(.status == "pending")]' 2>/dev/null || echo "[]")
        count=$(echo "$pending_commands" | jq -r 'length' 2>/dev/null || echo "0")
    else
        pending_commands="[]"
        count="0"
    fi
    
    if [ "$count" -gt 0 ]; then
        log "INFO" "Found $count pending command(s)"
        echo "$pending_commands"
    fi
    
    return 0
}

# Execute a single command
execute_command() {
    local command_json="$1"
    
    local command_id=$(echo "$command_json" | jq -r '.command_id')
    local content=$(echo "$command_json" | jq -r '.content')
    local type=$(echo "$command_json" | jq -r '.type')
    
    log "INFO" "Executing command: $command_id"
    log "DEBUG" "Command content: $content"
    log "DEBUG" "Command type: $type"
    
    # Execute command based on type
    local exit_code=0
    local output=""
    
    case "$type" in
        "shell")
            log "DEBUG" "Executing shell command: $content"
            output=$(eval "$content" 2>&1) || exit_code=$?
            ;;
        *)
            log "WARN" "Unsupported command type: $type"
            output="Unsupported command type: $type"
            exit_code=1
            ;;
    esac
    
    # Log execution result
    if [ $exit_code -eq 0 ]; then
        log "INFO" "Command executed successfully"
        log "DEBUG" "Command output: $output"
    else
        log "WARN" "Command failed with exit code $exit_code"
        log "DEBUG" "Command error output: $output"
    fi
    
    # TODO: Report execution results back to server
    # This would require additional API endpoints for command status updates
    log "DEBUG" "Command execution completed (reporting not yet implemented)"
}

# Main polling loop
start_polling() {
    log "INFO" "Starting command polling (interval: ${POLL_INTERVAL}s)"
    log "INFO" "Press Ctrl+C to stop"
    
    # Trap signals for graceful shutdown
    trap 'log "INFO" "Shutting down client..."; exit 0' SIGINT SIGTERM
    
    while true; do
        if commands=$(get_pending_commands); then
            if [ -n "$commands" ] && [ "$commands" != "[]" ]; then
                # Process each pending command
                echo "$commands" | jq -c '.[]' | while IFS= read -r command; do
                    execute_command "$command"
                done
            fi
        fi
        
        sleep "$POLL_INTERVAL"
    done
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