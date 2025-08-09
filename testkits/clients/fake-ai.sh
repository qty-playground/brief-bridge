#!/bin/bash
# Fake AI Assistant - Simulates AI submitting commands to Brief Bridge

set -euo pipefail

# Configuration
SERVER_URL="http://localhost:8000"
TARGET_CLIENT_ID=""
COMMAND_INTERVAL=5
TOTAL_COMMANDS=10
DEBUG=false

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# AI Assistant Commands Pool
COMMANDS=(
    "echo 'Hello from AI Assistant! Time: \$(date)'"
    "pwd"
    "whoami"
    "uname -a"
    "ls -la"
    "df -h"
    "free -h || vm_stat"
    "ps aux | head -10"
    "uptime"
    "date"
    "echo 'AI Task: System diagnostics complete'"
    "echo 'AI Task: Gathering system information'"
    "cat /etc/hosts | head -5 || echo 'Checking network configuration...'"
    "echo 'AI Assistant is monitoring system health'"
    "echo 'Performing automated maintenance check...'"
)

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "AI") echo -e "${PURPLE}[🤖 AI]${NC} $timestamp - $message" ;;
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
Fake AI Assistant - Command Submission Simulator

Usage: $0 --target-client ID [OPTIONS]

OPTIONS:
    --target-client ID   Target client ID to send commands to (required)
    --server URL         Server URL (default: http://localhost:8000)
    --interval SEC       Interval between commands in seconds (default: 5)
    --count NUM          Total number of commands to send (default: 10)
    --debug              Enable debug logging
    --help               Show this help

Examples:
    $0 --target-client laptop-001
    $0 --target-client laptop-001 --interval 3 --count 20 --debug

EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --target-client)
                TARGET_CLIENT_ID="$2"
                shift 2
                ;;
            --server)
                SERVER_URL="$2"
                shift 2
                ;;
            --interval)
                COMMAND_INTERVAL="$2"
                shift 2
                ;;
            --count)
                TOTAL_COMMANDS="$2"
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
    
    if [ -z "$TARGET_CLIENT_ID" ]; then
        echo "Error: --target-client is required" >&2
        usage
        exit 1
    fi
}

check_dependencies() {
    if ! command -v curl &> /dev/null; then
        log "ERROR" "curl is required"
        exit 1
    fi
}

check_target_client() {
    log "AI" "Checking if target client '$TARGET_CLIENT_ID' is available..."
    
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$SERVER_URL/clients/$TARGET_CLIENT_ID")
    
    if [ "$http_code" = "200" ]; then
        log "AI" "Target client '$TARGET_CLIENT_ID' is available ✓"
        return 0
    else
        log "ERROR" "Target client '$TARGET_CLIENT_ID' not found (HTTP $http_code)"
        log "AI" "Available clients:"
        curl -s "$SERVER_URL/clients/" | grep -o '"client_id":"[^"]*"' | sed 's/"client_id":"\([^"]*\)"/  - \1/g' || echo "  (none)"
        return 1
    fi
}

get_random_command() {
    local index=$((RANDOM % ${#COMMANDS[@]}))
    echo "${COMMANDS[$index]}"
}

submit_command() {
    local command="$1"
    local attempt="$2"
    
    log "AI" "Submitting command [$attempt/$TOTAL_COMMANDS]: $command"
    
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "{\"target_client_id\":\"$TARGET_CLIENT_ID\",\"command_content\":\"$command\",\"command_type\":\"shell\"}" \
        "$SERVER_URL/commands/submit")
    
    http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | grep -q '"submission_successful":true'; then
            local command_id=$(echo "$body" | grep -o '"command_id":"[^"]*"' | sed 's/"command_id":"\([^"]*\)"/\1/')
            log "AI" "Command submitted successfully! ID: $command_id"
            log "DEBUG" "Response: $body"
            return 0
        else
            local error_msg=$(echo "$body" | grep -o '"submission_message":"[^"]*"' | sed 's/"submission_message":"\([^"]*\)"/\1/')
            log "WARN" "Command submission failed: $error_msg"
            return 1
        fi
    else
        log "ERROR" "HTTP error $http_code: $body"
        return 1
    fi
}

show_statistics() {
    log "AI" "Getting system statistics..."
    
    # Get total commands
    local total_commands
    total_commands=$(curl -s "$SERVER_URL/commands/" | grep -o '"command_id"' | wc -l || echo "0")
    
    # Get client commands
    local client_commands
    client_commands=$(curl -s "$SERVER_URL/commands/client/$TARGET_CLIENT_ID" | grep -o '"command_id"' | wc -l || echo "0")
    
    log "AI" "📊 Statistics:"
    log "AI" "  - Total commands in system: $total_commands"
    log "AI" "  - Commands for client '$TARGET_CLIENT_ID': $client_commands"
}

start_ai_simulation() {
    log "AI" "🤖 AI Assistant starting command simulation..."
    log "AI" "Target: $TARGET_CLIENT_ID"
    log "AI" "Server: $SERVER_URL"
    log "AI" "Commands to send: $TOTAL_COMMANDS"
    log "AI" "Interval: ${COMMAND_INTERVAL}s"
    log "AI" "=================================="
    
    local successful=0
    local failed=0
    
    for ((i=1; i<=TOTAL_COMMANDS; i++)); do
        local command=$(get_random_command)
        
        if submit_command "$command" "$i"; then
            ((successful++))
        else
            ((failed++))
        fi
        
        # Show progress every 5 commands
        if [ $((i % 5)) -eq 0 ]; then
            show_statistics
        fi
        
        # Wait before next command (except for last one)
        if [ $i -lt $TOTAL_COMMANDS ]; then
            log "DEBUG" "Waiting ${COMMAND_INTERVAL}s before next command..."
            sleep "$COMMAND_INTERVAL"
        fi
    done
    
    log "AI" "=================================="
    log "AI" "🎯 AI Simulation Complete!"
    log "AI" "✅ Successful commands: $successful"
    log "AI" "❌ Failed commands: $failed"
    log "AI" "📈 Success rate: $(( successful * 100 / TOTAL_COMMANDS ))%"
    
    show_statistics
}

main() {
    parse_args "$@"
    check_dependencies
    
    log "AI" "🤖 Fake AI Assistant initializing..."
    
    if ! check_target_client; then
        log "ERROR" "Cannot proceed without valid target client"
        exit 1
    fi
    
    # Add a small delay to ensure client is ready
    log "AI" "Waiting 2 seconds for client to be ready..."
    sleep 2
    
    start_ai_simulation
    
    log "AI" "🤖 AI Assistant session completed"
}

main "$@"