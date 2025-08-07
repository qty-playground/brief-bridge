# Brief Bridge - Domain Model Analysis

## Domain Overview (領域總覽)

### 類別圖 (Class Diagram)

```mermaid
classDiagram
    class Client {
        +client_id: client_id
        +status: client_status
        +client_info: client_info
        +last_heartbeat: timestamp
        +register()
        +send_heartbeat()
        +is_available()
        +execute_command(command)
    }
    
    class Command {
        +command_id: command_id
        +content: command_content
        +target_client_id: client_id
        +status: execution_status
        +created_at: timestamp
        +executed_at: timestamp
        +submit()
        +assign_to_client(client)
        +mark_as_completed(result)
    }
    
    class ExecutionResult {
        +command_id: command_id
        +status: execution_status
        +stdout: string
        +stderr: string
        +exit_code: int
        +duration: duration
        +completed_at: timestamp
        +create_from_output(output)
    }
    
    %% Value Objects
    class client_id {
        +value: string
    }
    
    class command_id {
        +value: string
    }
    
    class client_status {
        +ONLINE
        +OFFLINE
        +BUSY
    }
    
    class execution_status {
        +PENDING
        +RUNNING
        +COMPLETED
        +FAILED
        +TIMEOUT
    }
    
    class client_info {
        +os: string
        +architecture: string
        +version: string
    }
    
    %% Domain Services
    class command_dispatcher {
        +dispatch_command(command, client)
        +find_available_client(client_id)
    }
    
    class client_health_monitor {
        +check_client_health(client)
        +mark_offline_clients()
    }
    
    %% Relationships
    Client ||--|| client_id : has
    Client ||--|| client_status : has
    Client ||--|| client_info : has
    Command ||--|| command_id : has
    Command ||--|| client_id : targets
    Command ||--|| execution_status : has
    Command ||--o| ExecutionResult : produces
    ExecutionResult ||--|| command_id : belongs_to
    ExecutionResult ||--|| execution_status : has
    
    %% One Client can have 0..1 running Command
    Client ||--o| Command : "0..1 running"
    
    %% Services dependencies
    command_dispatcher ..> Client : uses
    command_dispatcher ..> Command : dispatches
    client_health_monitor ..> Client : monitors
```

### 關鍵關係說明

**多重性約束 (Multiplicity Constraints):**
- `Client : Command` = `1 : 0..1` (一個客戶端同時最多執行一個命令)
- `Command : ExecutionResult` = `1 : 0..1` (一個命令最多有一個執行結果)
- `Client : client_id` = `1 : 1` (每個客戶端有唯一ID)

**相依關係 (Dependencies):**
- `command_dispatcher` 依賴 `Client` 和 `Command` 進行命令分發
- `client_health_monitor` 依賴 `Client` 進行健康狀態監控
- `Command` 透過 `client_id` 關聯到目標 `Client`
- `ExecutionResult` 透過 `command_id` 關聯到對應的 `Command`

## Domain Entities (核心實體)

### 1. Client (客戶端)
- **職責**: 代表執行命令的遠程機器
- **屬性**: 
  - 身份識別 (client_id)
  - 狀態 (在線/離線/執行中)
  - 能力/環境資訊 (OS, 架構, 版本等)
  - 最後心跳時間
- **生命週期**: 註冊 → 在線 → 執行命令 → 離線

### 2. Command (命令)
- **職責**: 需要在客戶端執行的指令
- **屬性**:
  - 命令識別 (command_id)
  - 命令內容 (shell script)
  - 目標客戶端
  - 執行狀態 (待分發/執行中/完成/失敗)
  - 創建時間
  - 執行時間
- **生命週期**: 提交 → 分發 → 執行中 → 完成/失敗

### 3. execution_result (執行結果)
- **職責**: 命令執行的輸出和狀態
- **屬性**:
  - 關聯的命令ID
  - 執行狀態
  - 標準輸出 (stdout)
  - 錯誤輸出 (stderr)
  - 退出碼
  - 執行時長
  - 完成時間

## Value Objects (值物件)

```
client_id: 客戶端唯一識別符
command_id: 命令唯一識別符  
command_content: 命令內容 (shell script)
client_info: 客戶端資訊 (OS, 架構, 版本等)
execution_output: 執行輸出 (stdout, stderr, exit_code)
execution_status: 執行狀態枚舉
timestamp: 時間戳記
duration: 持續時間
```

## 業務規則 (Business Rules)

### 客戶端管理規則 (client_management_rules)
1. **client.registration**: 客戶端必須註冊後才能接收命令
2. **client.heartbeat**: 客戶端需要定期發送心跳維持在線狀態
3. **client.offline_detection**: 超過心跳間隔的客戶端標記為離線

### 命令分發規則 (command_distribution_rules)
1. **command.target_validation**: 只能分發給在線狀態的客戶端
2. **client.concurrency**: 每個客戶端同時只能執行一個命令
3. **command.timeout**: 命令有超時機制，超時後標記為失敗

### 執行順序規則 (execution_order_rules)
1. **system.no_queue**: 不提供命令隊列機制
2. **client.availability**: 客戶端必須處於空閒狀態才能接收新命令
3. **client.serial_execution**: 同一客戶端同時只能執行一個命令
4. **command.wait_for_completion**: 新命令必須等待當前命令完成後才能分發

### 結果完整性規則 (result_integrity_rules)
1. **execution_result.completeness**: 每個命令都必須有對應的執行結果
2. **execution_result.full_output**: 執行結果必須包含完整的輸出和狀態資訊
3. **execution_result.error_preservation**: 執行失敗的命令需要保留錯誤資訊

## 潛在的領域服務 (Domain Services)

### command_dispatcher
- 負責將命令分發給合適的客戶端
- 處理負載平衡和客戶端選擇邏輯

### client_health_monitor  
- 監控客戶端健康狀態
- 處理心跳超時和狀態轉換

### execution_orchestrator
- 協調命令執行流程
- 處理超時和重試邏輯

## 主要用例 (Use Cases)

### AI 助手視角
1. **submit_command_use_case**: 提交命令到指定客戶端
2. **query_execution_result_use_case**: 查詢命令執行結果
3. **list_available_clients_use_case**: 列出可用客戶端

### 客戶端視角  
1. **register_client_use_case**: 註冊到系統
2. **poll_for_commands_use_case**: 輪詢獲取待執行命令
3. **execute_command_and_report_use_case**: 執行命令並回報結果
4. **maintain_heartbeat_use_case**: 維持心跳狀態

### 系統管理視角
1. **monitor_system_status_use_case**: 監控系統狀態
2. **manage_client_connections_use_case**: 管理客戶端連接
3. **cleanup_expired_resources_use_case**: 清理過期資源

---

*Note: 此文檔為初步分析，需要根據具體實現需求進一步細化和調整*