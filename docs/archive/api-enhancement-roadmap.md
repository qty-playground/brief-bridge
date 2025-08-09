# API Enhancement Roadmap

基於 PowerShell prototype 分析，本文件定義 Brief Bridge API 的增強路線圖。

## Current vs Target API Architecture

### 當前架構 (POC Phase)
```
AI Assistant → POST /commands/submit → Server
Client → GET /commands/client/{id} → Server → [本地顯示輸出]
```

### 目標架構 (Production Phase)  
```
AI Assistant → POST /commands/execute → Server → [等待結果]
Client → POST /commands/poll → Server → [執行] → POST /commands/result
```

## API Endpoints Roadmap

### Phase 1: Core Result Handling

#### 1.1 新增 `POST /commands/poll`
```http
POST /commands/poll
Content-Type: application/json

Request:
{
  "client_id": "laptop-001"
}

Response (有命令):
{
  "id": "cmd-uuid-123",
  "command": "ls -la",
  "timeout": 30,
  "type": "shell"
}

Response (無命令):
{
  "id": null,
  "command": null,
  "timeout": null
}
```

**實作要點**:
- 基於現有 `get_commands_for_client` 邏輯
- 返回單一命令 (FIFO)
- 自動將命令狀態更新為 `processing`
- 記錄客戶端最後活動時間

#### 1.2 新增 `POST /commands/result`
```http
POST /commands/result  
Content-Type: application/json

Request:
{
  "command_id": "cmd-uuid-123",
  "success": true,
  "output": "total 24\ndrwxr-xr-x 3 user staff 96 Aug 9 16:00 .",
  "error": null,
  "execution_time": 0.15
}

Response:
{
  "status": "success",
  "message": "Result recorded successfully"
}
```

**實作要點**:
- 更新命令狀態為 `completed` 或 `failed`
- 記錄 `completed_at` 時間戳
- 儲存執行結果到檔案系統
- 觸發等待中的 `/commands/execute` 請求

### Phase 2: Synchronous Execution

#### 2.1 增強 `POST /commands/execute` 
```http
POST /commands/execute
Content-Type: application/json

Request:
{
  "target_client_id": "laptop-001",
  "command_content": "ps aux | head -10", 
  "command_type": "shell",
  "timeout": 30,
  "wait_for_result": true  // 新增參數
}

Response (同步模式):
{
  "command_id": "cmd-uuid-123",
  "success": true,
  "output": "PID COMMAND...",
  "error": null,
  "execution_time": 2.1,
  "status": "completed"
}
```

**實作邏輯**:
```python
@router.post("/commands/execute")
async def execute_command(request: CommandRequest):
    # 創建命令
    command = create_command(request)
    await command_repository.save(command)
    
    if request.wait_for_result:
        # 等待客戶端執行完成
        result = await wait_for_completion(
            command.command_id, 
            timeout=request.timeout + 10
        )
        return result
    else:
        # 異步模式：立即返回命令 ID
        return {"command_id": command.command_id, "status": "submitted"}
```

#### 2.2 新增 `GET /commands/{command_id}/status`
```http
GET /commands/cmd-uuid-123/status

Response:
{
  "command_id": "cmd-uuid-123",
  "status": "processing",  // pending, processing, completed, failed, timeout
  "created_at": "2025-08-09T08:50:24.024477",
  "completed_at": null,
  "result": null,
  "error": null,
  "execution_time": null,
  "target_client_id": "laptop-001"
}
```

### Phase 3: Client Management  

#### 3.1 客戶端心跳機制
```http
POST /clients/heartbeat
Content-Type: application/json

Request:
{
  "client_id": "laptop-001",
  "capabilities": ["shell", "powershell"],
  "system_info": {
    "os": "darwin", 
    "version": "24.5.0",
    "arch": "x86_64"
  }
}

Response:
{
  "status": "registered",
  "server_time": "2025-08-09T16:50:24Z",
  "poll_interval": 3
}
```

#### 3.2 增強客戶端狀態 API
```http
GET /clients/{client_id}/status

Response:
{
  "client_id": "laptop-001",
  "name": "Test Laptop", 
  "status": "online",  // online, offline, busy
  "last_seen": "2025-08-09T16:50:24Z",
  "current_command": "cmd-uuid-123",  // 執行中的命令
  "capabilities": ["shell", "powershell"],
  "system_info": {...},
  "statistics": {
    "total_commands": 156,
    "successful_commands": 152, 
    "failed_commands": 4,
    "avg_execution_time": 1.2
  }
}
```

### Phase 4: Installation & Deployment

#### 4.1 一鍵安裝端點
```http
GET /install.ps1?client_id=my-laptop&poll_interval=5

Response: PowerShell script content
```

```http
GET /install.sh?client_id=my-server&poll_interval=3  

Response: Bash script content
```

**腳本特性**:
- 自動偵測服務器 URL
- 內嵌客戶端邏輯
- 支援自定義參數
- 包含錯誤處理和重試
- 連線測試和健康檢查

#### 4.2 動態配置端點
```http
GET /config/{client_id}

Response:
{
  "server_url": "http://localhost:8000",
  "poll_interval": 3,
  "timeout": 30,
  "max_retries": 3,
  "capabilities_required": ["shell"]
}
```

## Data Model Enhancements

### Enhanced Command Entity
```python
@dataclass
class Command:
    command_id: str
    target_client_id: str
    content: str
    type: str = "shell"
    status: str = "pending"  # pending, processing, completed, failed, timeout
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None    # 新增：開始執行時間
    completed_at: Optional[datetime] = None  # 新增：完成時間
    result: Optional[str] = None             # 新增：執行輸出
    error: Optional[str] = None              # 新增：錯誤訊息  
    execution_time: Optional[float] = None   # 新增：執行時間(秒)
    timeout: int = 30                        # 新增：超時設定
    retry_count: int = 0                     # 新增：重試次數
```

### Enhanced Client Entity
```python
@dataclass  
class Client:
    client_id: str
    name: str
    status: str = "offline"  # online, offline, busy
    last_seen: Optional[datetime] = None
    current_command: Optional[str] = None    # 新增：執行中的命令 ID
    capabilities: List[str] = None           # 新增：客戶端能力
    system_info: Dict[str, Any] = None       # 新增：系統資訊
    registered_at: Optional[datetime] = None # 新增：註冊時間
    total_commands: int = 0                  # 新增：統計資訊
    successful_commands: int = 0
    failed_commands: int = 0
```

## Implementation Phases

### Phase 1: Basic Result Handling (Week 1-2)
- [ ] 實作 `POST /commands/poll` 端點
- [ ] 實作 `POST /commands/result` 端點  
- [ ] 擴展 Command 實體支援新欄位
- [ ] 更新 FileBasedCommandRepository
- [ ] 建立基本的 PowerShell 客戶端

### Phase 2: Synchronous Execution (Week 3-4)  
- [ ] 實作命令執行等待機制
- [ ] 增強 `POST /commands/execute` 支援同步模式
- [ ] 新增 `GET /commands/{id}/status` 端點
- [ ] 實作超時和錯誤處理
- [ ] E2E 測試：提交命令 → 執行 → 獲取結果

### Phase 3: Client Management (Week 5-6)
- [ ] 實作客戶端心跳機制
- [ ] 擴展 Client 實體和 Repository  
- [ ] 新增客戶端統計和監控
- [ ] 實作客戶端能力管理
- [ ] 在線/離線狀態追蹤

### Phase 4: Production Features (Week 7-8)
- [ ] 一鍵安裝腳本生成
- [ ] 動態配置管理
- [ ] 安全性增強 (認證、授權)
- [ ] 效能最佳化和快取
- [ ] 完整的監控和日誌

## Success Metrics

### Functional Requirements
- [x] 多平台客戶端支援 (Linux/macOS Bash, Windows PowerShell)
- [ ] 同步命令執行 (< 3 秒回應時間)
- [ ] 一鍵部署安裝
- [ ] 95%+ 命令執行成功率
- [ ] 客戶端斷線重連機制

### Non-Functional Requirements  
- [ ] 支援 100+ 並發客戶端
- [ ] 99.9% 服務可用性
- [ ] 完整的 API 文檔和測試覆蓋
- [ ] 安全的跨網路通訊
- [ ] 實時狀態監控和告警

## Migration Strategy

### 向後相容性
- 保持現有 API 端點不變
- 新功能透過新端點提供
- 逐步遷移客戶端到新 API

### 測試策略
```bash
# 現有客戶端繼續運作
./testkits/clients/simple-client.sh --client-id legacy-client

# 新 PowerShell 客戶端
iex ((Invoke-WebRequest 'http://localhost:8000/install.ps1').Content) -Start

# 混合測試
./testkits/clients/fake-ai.sh --target-client legacy-client --count 5
./testkits/clients/fake-ai.sh --target-client ps-client --count 5
```

這個路線圖將 Brief Bridge 從 POC 概念驗證階段演進為生產就緒的遠端命令執行平台。