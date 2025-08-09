# PowerShell Integration Research

## 概述

基於 ws-call PowerShell prototype 的分析，本文件記錄了將 PowerShell 客戶端整合到 Brief Bridge 系統的研究成果，作為下一階段實作的技術參考。

## 現狀對比

### Brief Bridge (Current POC)
- **架構**: HTTP REST API + 文件持久化
- **客戶端**: Bash 輪詢客戶端 (僅顯示輸出)
- **API**: `GET /commands/client/{id}` 獲取命令
- **結果處理**: 僅在客戶端本地顯示
- **部署**: 手動執行腳本

### ws-call PowerShell Prototype (Target)
- **架構**: HTTP 輪詢 + 指令佇列 + 結果回傳
- **客戶端**: PowerShell 自動執行 + 結果提交
- **API**: `POST /commands/poll` + `POST /commands/result`
- **結果處理**: 自動提交執行結果到服務器
- **部署**: 一鍵安裝與啟動

## 核心技術差異

### 1. 客戶端執行模式

**Current (Bash Client)**:
```bash
# 獲取命令
response=$(curl -s "$SERVER_URL/commands/client/$CLIENT_ID")

# 執行並本地顯示
if [ "$response" != "[]" ]; then
    execute_command "$cmd" "extracted-command"
    echo "=== Command Output ==="
    echo "$output"
    echo "======================"
fi
```

**Target (PowerShell Client)**:
```powershell
# 輪詢命令
$response = Invoke-RestMethod -Uri "$ApiBase/poll" -Method POST -Body $body

if ($response.id) {
    # 執行命令
    $output = Invoke-Expression $response.command
    
    # 自動提交結果
    $resultBody = @{
        command_id = $response.id
        success = $success
        output = $output
        error = $error
        execution_time = $executionTime
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "$ApiBase/result" -Method POST -Body $resultBody
}
```

### 2. API 端點設計

**需要新增的端點**:

#### `POST /commands/poll`
```http
POST /commands/poll
Content-Type: application/json

{
  "client_id": "device-b"
}

Response (有命令時):
{
  "id": "cmd-123",
  "command": "Get-Date",
  "timeout": 30
}

Response (無命令時):
{
  "id": null,
  "command": null,
  "timeout": null
}
```

#### `POST /commands/result`
```http
POST /commands/result
Content-Type: application/json

{
  "command_id": "cmd-123",
  "success": true,
  "output": "2025年8月9日 上午 10:30:00",
  "error": null,
  "execution_time": 0.5
}

Response:
{
  "status": "success",
  "message": "Result recorded"
}
```

### 3. 一鍵部署機制

**ws-call 的一鍵安裝**:
```powershell
# 一行指令完成安裝和啟動
iex ((Invoke-WebRequest 'http://abc123.ngrok.io/commands/install.ps1').Content) -Start
```

**需實現的安裝端點**:
```http
GET /install.ps1  # PowerShell 客戶端
GET /install.sh   # Linux/macOS 客戶端
```

## 實作計劃

### Phase 1: API 端點擴展
1. **實作 `/commands/poll` 端點**
   - 基於現有 `get_commands_for_client` 邏輯
   - 返回單一命令而非命令列表
   - 支援客戶端心跳更新

2. **實作 `/commands/result` 端點**
   - 接收客戶端執行結果
   - 更新命令狀態為 completed/failed
   - 記錄執行時間和輸出

3. **擴展 Command 實體**
   ```python
   @dataclass
   class Command:
       command_id: str
       target_client_id: str
       content: str
       type: str = "shell"
       status: str = "pending"  # pending, processing, completed, failed
       created_at: Optional[datetime] = None
       completed_at: Optional[datetime] = None  # 新增
       result: Optional[str] = None  # 新增
       error: Optional[str] = None   # 新增
       execution_time: Optional[float] = None  # 新增
   ```

### Phase 2: PowerShell 客戶端
1. **移植 powershell-polling-client.ps1**
   ```powershell
   # Brief Bridge PowerShell Client
   param(
       [string]$ServerUrl = "http://localhost:8000",
       [string]$ClientId = $env:COMPUTERNAME,
       [int]$PollInterval = 2
   )
   
   $ApiBase = "$ServerUrl/commands"
   
   # 主輪詢迴圈
   while ($true) {
       $body = @{ client_id = $ClientId } | ConvertTo-Json
       $response = Invoke-RestMethod -Uri "$ApiBase/poll" -Method POST -Body $body
       
       if ($response.id) {
           # 執行命令並提交結果
           $result = Invoke-PowerShellCommand -Command $response.command
           Submit-CommandResult -CommandId $response.id -Result $result
       }
       
       Start-Sleep -Seconds $PollInterval
   }
   ```

2. **適配 Brief Bridge API 格式**
   - 調整 JSON 結構以符合現有 schemas
   - 整合客戶端註冊機制
   - 實作錯誤重試邏輯

### Phase 3: 一鍵安裝系統
1. **實作安裝端點**
   ```python
   @router.get("/install.ps1")
   async def get_powershell_installer():
       script_content = generate_powershell_client_script()
       return PlainTextResponse(script_content)
   ```

2. **動態腳本生成**
   - 自動注入服務器 URL
   - 支援自定義參數 (ClientId, PollInterval)
   - 包含連線測試和錯誤處理

### Phase 4: 增強功能
1. **客戶端狀態管理**
   - 實作心跳機制
   - 在線/離線狀態追蹤
   - 客戶端能力註冊

2. **命令執行等待機制**
   ```python
   # 類似 ws-call 的同步等待
   @router.post("/commands/execute-sync")
   async def execute_command_sync(request: CommandRequest):
       command = create_command(request)
       await add_to_queue(command)
       
       # 等待執行完成
       result = await wait_for_completion(command.id, timeout=request.timeout)
       return result
   ```

## 技術細節

### JSON Schema 調整
```python
# 輪詢請求
class PollingRequest(BaseModel):
    client_id: str

# 輪詢回應
class PollingResponse(BaseModel):
    id: Optional[str] = None
    command: Optional[str] = None  
    timeout: Optional[int] = None

# 結果提交
class CommandResultRequest(BaseModel):
    command_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
```

### 資料庫 Schema 更新
```python
# FileBasedCommandRepository 需支援新欄位
def _command_to_dict(self, command: Command) -> dict:
    return {
        "command_id": command.command_id,
        "target_client_id": command.target_client_id,
        "content": command.content,
        "type": command.type,
        "status": command.status,
        "created_at": command.created_at.isoformat() if command.created_at else None,
        "completed_at": command.completed_at.isoformat() if command.completed_at else None,  # 新增
        "result": command.result,  # 新增
        "error": command.error,    # 新增
        "execution_time": command.execution_time  # 新增
    }
```

## 測試策略

### 整合測試
1. **PowerShell 客戶端測試**
   ```powershell
   # 測試腳本
   .\test-powershell-client.ps1 -ServerUrl "http://localhost:8000"
   ```

2. **API 端點測試**
   ```bash
   # 測試輪詢
   curl -X POST http://localhost:8000/commands/poll \
     -H "Content-Type: application/json" \
     -d '{"client_id": "test-client"}'
   
   # 測試結果提交
   curl -X POST http://localhost:8000/commands/result \
     -H "Content-Type: application/json" \
     -d '{"command_id": "cmd-123", "success": true, "output": "result"}'
   ```

### E2E 測試情境
1. **多平台客戶端混合**
   - Linux/macOS Bash 客戶端
   - Windows PowerShell 客戶端
   - 同時連線和執行命令

2. **一鍵安裝驗證**
   ```powershell
   # 驗證一鍵安裝可行性
   iex ((Invoke-WebRequest 'http://localhost:8000/commands/install.ps1').Content) -Start
   ```

## 優先級建議

### P0 (必要功能)
- `/commands/poll` 端點實作
- `/commands/result` 端點實作
- PowerShell 客戶端基本功能

### P1 (重要功能)
- 一鍵安裝機制
- 命令狀態追蹤
- 錯誤處理和重試

### P2 (增強功能)
- 客戶端心跳機制
- 同步執行等待
- 高級部署功能

## 結論

PowerShell prototype 提供了完整的跨平台遠端命令執行解決方案的參考實現。核心改進包括：

1. **結果回傳機制**: 從僅顯示輸出升級為完整的結果提交系統
2. **一鍵部署**: 大幅簡化客戶端安裝和配置流程
3. **狀態管理**: 完整的命令生命週期追蹤

這些功能將使 Brief Bridge 從 POC 階段演進為生產就緒的遠端命令執行系統。