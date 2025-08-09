# 最小實作計劃 - 異步執行架構

## 核心改變摘要

### 現狀 → 目標
- **現狀**: AI 提交命令後立即返回，無法獲得執行結果
- **目標**: AI 提交命令後等待，直到 Client 執行完成並回傳結果

## 三個關鍵 API 改變

### 1. 修改 `/commands/submit` - 加入等待機制
```python
@router.post("/commands/submit")
async def submit_command(request: SubmitCommandRequest):
    # 創建命令
    command = Command(...)
    await command_repository.save(command)
    
    # 🔴 新增：Server 端等待結果
    for _ in range(60):  # 最多等待 30 秒
        await asyncio.sleep(0.5)
        
        updated = await command_repository.get(command.command_id)
        if updated.status == "completed":
            return {
                "command_id": command.command_id,
                "submission_successful": True,
                "result": updated.result  # 🔴 返回執行結果
            }
    
    # 超時
    return {"submission_successful": False, "error": "timeout"}
```

### 2. 新增 `/commands/{client_id}/result` - 接收結果
```python
@router.post("/commands/{client_id}/result")
async def submit_result(client_id: str, request: ResultRequest):
    # 找到執行中的命令
    command = await command_repository.get_processing_command(client_id)
    
    # 🔴 更新命令結果
    command.status = "completed"
    command.result = request.output
    command.error = request.error
    command.execution_time = request.execution_time
    
    await command_repository.save(command)
    
    return {"status": "success"}
```

### 3. 保持 `/commands/client/{id}` - 確保單一執行
```python
@router.get("/commands/client/{client_id}")
async def get_commands_for_client(client_id: str):
    # 🔴 確保只返回一個命令
    commands = await command_repository.get_pending_commands(client_id)
    
    if commands and len(commands) > 0:
        command = commands[0]
        # 🔴 標記為執行中，防止重複獲取
        command.status = "processing"
        await command_repository.save(command)
        return [command.to_dict()]
    
    return []
```

## 資料模型擴展

### Command Entity 新增欄位
```python
@dataclass
class Command:
    command_id: str
    target_client_id: str
    content: str
    type: str = "shell"
    status: str = "pending"  # pending → processing → completed/failed
    created_at: Optional[datetime] = None
    
    # 🔴 新增欄位
    started_at: Optional[datetime] = None    # 開始執行時間
    completed_at: Optional[datetime] = None  # 完成時間
    result: Optional[str] = None            # 執行輸出
    error: Optional[str] = None             # 錯誤訊息
    execution_time: Optional[float] = None  # 執行時間(秒)
```

## Client 端修改

### simple-client.sh 增加結果提交
```bash
# 執行命令後提交結果
execute_and_submit() {
    local command_id="$1"
    local command_content="$2"
    
    # 執行
    start=$(date +%s.%N)
    if output=$(eval "$command_content" 2>&1); then
        success="true"
        error="null"
    else
        success="false"
        error="\"$output\""
        output=""
    fi
    end=$(date +%s.%N)
    execution_time=$(echo "$end - $start" | bc)
    
    # 🔴 提交結果
    curl -X POST "$SERVER_URL/commands/$CLIENT_ID/result" \
        -H "Content-Type: application/json" \
        -d "{
            \"command_id\": \"$command_id\",
            \"success\": $success,
            \"output\": \"$output\",
            \"error\": $error,
            \"execution_time\": $execution_time
        }"
}
```

## 實作步驟（2-3 天）

### Day 1: Server 端
1. **上午**: 擴展 Command entity 和 Repository
   - 新增 result, error, execution_time 欄位
   - 更新 FileBasedCommandRepository

2. **下午**: 實作結果接收 API
   - 新增 `/commands/{client_id}/result` 端點
   - 實作 get_processing_command 方法

### Day 2: 等待機制
1. **上午**: 修改 submit_command 加入等待
   - 實作輪詢等待迴圈
   - 處理超時情況

2. **下午**: 確保單一執行
   - 修改 get_commands_for_client
   - 防止同時多個命令執行

### Day 3: Client 端和測試
1. **上午**: 更新 client 腳本
   - 修改 simple-client.sh
   - 加入結果提交邏輯

2. **下午**: 整合測試
   - E2E 測試完整流程
   - 驗證超時處理

## 測試驗證

### 成功場景
```bash
# 1. 啟動 client
./simple-client.sh --client-id test &

# 2. AI 提交命令（會等待）
time curl -X POST http://localhost:8000/commands/submit \
    -d '{"target_client_id": "test", "command_content": "echo Hello"}'

# 預期輸出（約 3-4 秒後）：
{
  "command_id": "xxx",
  "submission_successful": true,
  "result": "Hello"
}
```

### 超時場景
```bash
# Client 離線時提交
curl -X POST http://localhost:8000/commands/submit \
    -d '{"target_client_id": "offline-client", "command_content": "echo Test"}'

# 預期（30 秒後）：
{
  "submission_successful": false,
  "error": "timeout"
}
```

## 向後相容性

- ✅ 現有 API 端點保持不變
- ✅ 舊 client 仍可運作（只是不會提交結果）
- ✅ 資料格式向後相容

## 完成標準

1. **AI 等待結果**: submit_command 會等待直到收到結果或超時
2. **單一執行**: 同一 client 同時只能執行一個命令
3. **結果回傳**: Client 執行完成後能成功提交結果
4. **超時處理**: 30 秒無回應會返回超時錯誤

這個最小實作計劃專注於核心功能，可在 2-3 天內完成。