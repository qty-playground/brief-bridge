# Brief Bridge Implementation Phases

## 優先級定義
- **P0**: 必要功能 - POC 轉生產的最小可行功能
- **P1**: 重要功能 - 提升使用體驗和可靠性
- **P2**: 增強功能 - 生產環境優化
- **P3**: 進階功能 - 未來擴展

---

## Phase 1: Core Result Handling (P0)
**目標**: 實現命令執行結果的完整生命週期管理  
**時程**: 1-2 週  
**影響**: 解決當前 POC 最大缺陷 - 無法獲得執行結果

### 1.1 新增結果提交 API
```python
# 新增端點: POST /commands/result
@router.post("/commands/result")
async def submit_command_result(request: CommandResultRequest):
    """接收客戶端執行結果"""
    # 更新命令狀態
    # 儲存執行結果
    # 記錄執行時間
```

**實作項目**:
- [ ] 定義 `CommandResultRequest` schema
- [ ] 擴展 Command entity 增加 result, error, execution_time 欄位
- [ ] 更新 FileBasedCommandRepository 支援新欄位
- [ ] 實作結果提交端點
- [ ] 單元測試覆蓋

### 1.2 客戶端增強：結果回傳
```bash
# 修改 simple-client.sh 增加結果提交
submit_command_result() {
    local command_id="$1"
    local success="$2"
    local output="$3"
    
    curl -X POST "$SERVER_URL/commands/result" \
        -H "Content-Type: application/json" \
        -d "{\"command_id\":\"$command_id\",\"success\":$success,\"output\":\"$output\"}"
}
```

**實作項目**:
- [ ] 修改 simple-client.sh 支援結果提交
- [ ] 更新 execute_command 函數捕獲輸出
- [ ] 實作錯誤處理和重試機制
- [ ] 整合測試驗證

### 1.3 命令狀態追蹤
```python
# 命令狀態流轉
class CommandStatus(Enum):
    PENDING = "pending"       # 已提交，等待執行
    PROCESSING = "processing"  # 客戶端正在執行
    COMPLETED = "completed"    # 執行成功
    FAILED = "failed"         # 執行失敗
    TIMEOUT = "timeout"       # 執行超時
```

**實作項目**:
- [ ] 實作狀態流轉邏輯
- [ ] 新增 GET /commands/{id}/status 端點
- [ ] 更新命令查詢 API 返回完整狀態

---

## Phase 2: Polling API Standard (P0)
**目標**: 統一客戶端輪詢機制，支援多平台客戶端  
**時程**: 1 週  
**影響**: 標準化客戶端接口，為 PowerShell 客戶端鋪路

### 2.1 實作標準輪詢端點
```python
# 新增端點: POST /commands/poll
@router.post("/commands/poll")
async def poll_for_commands(request: PollingRequest):
    """統一的輪詢接口"""
    # 獲取單一待執行命令
    # 更新命令狀態為 processing
    # 記錄客戶端活動時間
```

**實作項目**:
- [ ] 實作 POST /commands/poll 端點
- [ ] 從佇列中取出單一命令 (FIFO)
- [ ] 自動標記命令為 processing
- [ ] 支援客戶端 ID 過濾

### 2.2 遷移現有客戶端
```bash
# 更新客戶端使用新的輪詢 API
poll_commands_v2() {
    response=$(curl -X POST "$SERVER_URL/commands/poll" \
        -H "Content-Type: application/json" \
        -d "{\"client_id\":\"$CLIENT_ID\"}")
    
    # 處理單一命令而非列表
    if [ -n "$response" ]; then
        execute_and_submit "$response"
    fi
}
```

**實作項目**:
- [ ] 創建 simple-client-v2.sh
- [ ] 保持向後相容性
- [ ] 測試新舊客戶端共存

---

## Phase 3: PowerShell Client (P1)
**目標**: 實現 Windows 平台支援  
**時程**: 1-2 週  
**影響**: 擴展平台覆蓋，支援 Windows 環境

### 3.1 基礎 PowerShell 客戶端
```powershell
# brief-bridge-client.ps1
param(
    [string]$ServerUrl = "http://localhost:8000",
    [string]$ClientId = $env:COMPUTERNAME
)

# 核心輪詢邏輯
while ($true) {
    $command = Get-PendingCommand
    if ($command) {
        $result = Invoke-Command $command
        Submit-Result $command.id $result
    }
    Start-Sleep -Seconds 3
}
```

**實作項目**:
- [ ] 創建 powershell-client.ps1
- [ ] 實作 HTTP 請求函數
- [ ] 實作命令執行和錯誤處理
- [ ] 測試 PowerShell 5.1+ 相容性

### 3.2 一鍵安裝機制
```python
# 新增端點: GET /install.ps1
@router.get("/install.ps1")
async def get_powershell_installer(request: Request):
    """動態生成 PowerShell 客戶端腳本"""
    server_url = get_server_url(request)
    script = generate_ps_client(server_url)
    return PlainTextResponse(script)
```

**實作項目**:
- [ ] 實作安裝腳本生成器
- [ ] 內嵌客戶端邏輯
- [ ] 支援參數自定義
- [ ] 測試一鍵安裝流程

---

## Phase 4: Synchronous Execution (P1)
**目標**: AI 提交命令後可同步等待結果  
**時程**: 1 週  
**影響**: 改善 AI Assistant 使用體驗

### 4.1 同步執行 API
```python
# 增強: POST /commands/execute-sync
@router.post("/commands/execute-sync")
async def execute_command_sync(request: CommandRequest):
    """提交命令並等待結果"""
    command = create_command(request)
    await repository.save(command)
    
    # 等待執行完成
    result = await wait_for_completion(
        command.command_id,
        timeout=request.timeout + 10
    )
    return result
```

**實作項目**:
- [ ] 實作等待機制 (asyncio)
- [ ] 處理超時情況
- [ ] 支援異步和同步模式切換
- [ ] E2E 測試覆蓋

---

## Phase 5: Client Management (P2)
**目標**: 客戶端狀態管理和監控  
**時程**: 1-2 週  
**影響**: 提升系統可觀測性

### 5.1 客戶端心跳機制
```python
# 新增端點: POST /clients/heartbeat
@router.post("/clients/heartbeat")
async def client_heartbeat(request: HeartbeatRequest):
    """更新客戶端狀態"""
    # 更新最後活動時間
    # 更新客戶端能力
    # 返回服務器配置
```

**實作項目**:
- [ ] 實作心跳端點
- [ ] 客戶端狀態追蹤
- [ ] 自動離線檢測
- [ ] 客戶端統計資訊

### 5.2 客戶端能力管理
```python
@dataclass
class Client:
    client_id: str
    name: str
    status: str  # online, offline, busy
    capabilities: List[str]  # ["bash", "powershell", "python"]
    system_info: Dict[str, Any]
    last_seen: datetime
```

**實作項目**:
- [ ] 擴展 Client entity
- [ ] 基於能力的命令路由
- [ ] 客戶端詳情 API

---

## Phase 6: Production Features (P2)
**目標**: 生產環境就緒  
**時程**: 2-3 週  
**影響**: 系統穩定性和可靠性

### 6.1 持久化增強
- [ ] 實作資料庫後端 (SQLite/PostgreSQL)
- [ ] 命令歷史記錄
- [ ] 執行日誌管理
- [ ] 資料備份機制

### 6.2 安全性
- [ ] API 認證 (API Key)
- [ ] 客戶端授權
- [ ] 命令白名單/黑名單
- [ ] 輸出內容過濾

### 6.3 可觀測性
- [ ] Prometheus metrics
- [ ] 結構化日誌
- [ ] 健康檢查端點
- [ ] 效能監控

---

## Phase 7: Advanced Features (P3)
**目標**: 進階功能和擴展性  
**時程**: 視需求而定  
**影響**: 長期產品競爭力

### 7.1 進階執行功能
- [ ] 批次命令執行
- [ ] 命令排程 (cron-like)
- [ ] 條件執行
- [ ] 命令模板

### 7.2 整合功能
- [ ] Webhook 通知
- [ ] 第三方整合 (Slack, Teams)
- [ ] CI/CD pipeline 整合
- [ ] 雲端部署 (AWS, Azure)

---

## 實施時間表

| Phase | 優先級 | 預估時程 | 依賴關係 | 狀態 |
|-------|--------|----------|----------|------|
| Phase 1: Core Result Handling | P0 | 1-2 週 | - | 🔄 Ready |
| Phase 2: Polling API Standard | P0 | 1 週 | Phase 1 | ⏳ Waiting |
| Phase 3: PowerShell Client | P1 | 1-2 週 | Phase 2 | ⏳ Waiting |
| Phase 4: Synchronous Execution | P1 | 1 週 | Phase 1 | ⏳ Waiting |
| Phase 5: Client Management | P2 | 1-2 週 | Phase 2 | ⏳ Waiting |
| Phase 6: Production Features | P2 | 2-3 週 | Phase 1-5 | ⏳ Waiting |
| Phase 7: Advanced Features | P3 | TBD | Phase 6 | 💭 Future |

## 成功指標

### Phase 1-2 完成後 (最小可行產品)
- ✅ 命令執行結果可回傳服務器
- ✅ 統一的客戶端輪詢接口
- ✅ 完整的命令生命週期追蹤

### Phase 3-4 完成後 (跨平台支援)
- ✅ Windows PowerShell 客戶端運作
- ✅ 一鍵安裝部署
- ✅ AI 可同步獲取執行結果

### Phase 5-6 完成後 (生產就緒)
- ✅ 客戶端狀態監控
- ✅ 安全的 API 存取
- ✅ 可靠的資料持久化
- ✅ 完整的可觀測性

## 立即行動項目 (Phase 1)

### Week 1 Sprint
1. **Day 1-2**: 擴展 Command entity 和 Repository
2. **Day 3-4**: 實作 /commands/result 端點
3. **Day 5**: 更新客戶端腳本支援結果提交

### Week 2 Sprint  
1. **Day 1-2**: 實作 /commands/poll 端點
2. **Day 3-4**: 創建 v2 客戶端腳本
3. **Day 5**: 整合測試和文檔更新

這個分階段計劃確保每個階段都有明確的交付價值，並且可以獨立部署和測試。