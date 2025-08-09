#!/bin/bash
# Simplified Brief Bridge Client - Reliable version for real testing

set -euo pipefail

# Configuration
SERVER_URL="http://localhost:8000"
CLIENT_ID=""
CLIENT_NAME=""
POLL_INTERVAL=3
DEBUG=false

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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
}

usage() {
    cat << EOF
Simplified Brief Bridge Client

Usage: $0 --client-id ID [OPTIONS]

OPTIONS:
    --client-id ID       Unique client identifier (required)
    --client-name NAME   Human-readable client name (optional)
    --server URL         Server URL (default: http://localhost:8000)
    --poll-interval SEC  Polling interval in seconds (default: 3)
    --debug              Enable debug logging
    --help               Show this help

Examples:
    $0 --client-id laptop-001
    $0 --client-id laptop-001 --client-name "My Laptop" --debug

EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --client-id)
                CLIENT_ID="$2"
                shift 2
                ;;
            --client-name)
                CLIENT_NAME="$2"
                shift 2
                ;;
            --server)
                SERVER_URL="$2"
                shift 2
                ;;
            --poll-interval)
                POLL_INTERVAL="$2"
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
    
    if [ -z "$CLIENT_ID" ]; then
        echo "Error: --client-id is required" >&2
        usage
        exit 1
    fi
    
    if [ -z "$CLIENT_NAME" ]; then
        CLIENT_NAME="Client-$CLIENT_ID"
    fi
}

check_dependencies() {
    local missing=()
    
    if ! command -v curl &> /dev/null; then
        missing+=("curl")
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        log "ERROR" "Missing required dependencies: ${missing[*]}"
        exit 1
    fi
}

register_client() {
    log "INFO" "Registering client '$CLIENT_ID' with server $SERVER_URL"
    
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "{\"client_id\":\"$CLIENT_ID\",\"name\":\"$CLIENT_NAME\"}" \
        "$SERVER_URL/clients/register")
    
    if [ "$http_code" = "200" ]; then
        log "INFO" "Client registration successful"
        return 0
    else
        log "ERROR" "Registration failed (HTTP $http_code)"
        return 1
    fi
}

get_pending_commands() {
    log "DEBUG" "Polling for commands for client '$CLIENT_ID'"
    
    local response
    local http_code
    
    # Use separate calls to avoid complex parsing
    response=$(curl -s "$SERVER_URL/commands/client/$CLIENT_ID")
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$SERVER_URL/commands/client/$CLIENT_ID")
    
    if [ "$http_code" != "200" ]; then
        log "WARN" "Failed to get commands (HTTP $http_code)"
        return 1
    fi
    
    # Simple check for non-empty array
    if [ "$response" != "[]" ] && [ -n "$response" ]; then
        log "INFO" "Found pending commands"
        echo "$response"
        return 0
    fi
    
    log "DEBUG" "No pending commands"
    return 1
}

execute_command() {
    local command_content="$1"
    local command_id="$2"
    
    log "INFO" "Executing command: $command_id"
    log "DEBUG" "Command content: $command_content"
    
    local exit_code=0
    local output=""
    
    # Execute the command
    output=$(eval "$command_content" 2>&1) || exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log "INFO" "Command executed successfully"
        log "DEBUG" "Command output: $output"
    else
        log "WARN" "Command failed with exit code $exit_code"
        log "DEBUG" "Command error output: $output"
    fi
    
    # Simple output display
    echo "=== Command Output ==="
    echo "$output"
    echo "======================"
    
    return $exit_code
}

extract_commands() {
    local json_response="$1"
    
    # Very simple command extraction - look for patterns
    # This avoids complex jq parsing
    echo "$json_response" | grep -o '"content":"[^"]*"' | sed 's/"content":"\([^"]*\)"/\1/g'
}

start_polling() {
    log "INFO" "Starting command polling (interval: ${POLL_INTERVAL}s)"
    log "INFO" "Press Ctrl+C to stop"
    
    trap 'log "INFO" "Shutting down client..."; exit 0' SIGINT SIGTERM
    
    while true; do
        if response=$(get_pending_commands 2>/dev/null); then
            # Simple command extraction
            if echo "$response" | grep -q '"content"'; then
                log "INFO" "Processing commands..."
                
                # Extract command content (simplified)
                local commands
                commands=$(echo "$response" | grep -o '"content":"[^"]*"' | sed 's/"content":"\([^"]*\)"/\1/g')
                
                while IFS= read -r cmd; do
                    if [ -n "$cmd" ]; then
                        execute_command "$cmd" "extracted-command"
                    fi
                done <<< "$commands"
            fi
        fi
        
        sleep "$POLL_INTERVAL"
    done
}

main() {
    parse_args "$@"
    check_dependencies
    
    log "INFO" "Brief Bridge Client starting..."
    log "INFO" "Server: $SERVER_URL"
    log "INFO" "Client ID: $CLIENT_ID"
    log "INFO" "Client Name: $CLIENT_NAME"
    log "INFO" "Poll Interval: ${POLL_INTERVAL}s"
    
    if ! register_client; then
        log "ERROR" "Failed to register client. Exiting."
        exit 1
    fi
    
    start_polling
}

main "$@"