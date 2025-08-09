# 最小化 Entity 變化的實作方案

## 核心策略：只加一個欄位

### 方案：使用單一 JSON 欄位儲存所有結果

```python
@dataclass
class Command:
    command_id: str
    target_client_id: str
    content: str
    type: str = "shell"
    status: str = "pending"  # 已存在，繼續使用
    created_at: Optional[datetime] = None  # 已存在
    
    # 🔴 只新增這一個欄位
    result_data: Optional[Dict[str, Any]] = None  # JSON 格式儲存所有結果
```

### result_data 欄位內容
```python
# 執行成功時
result_data = {
    "output": "Hello World",
    "execution_time": 0.15,
    "completed_at": "2025-08-09T10:30:00Z",
    "success": True
}

# 執行失敗時
result_data = {
    "error": "Command not found",
    "execution_time": 0.05,
    "completed_at": "2025-08-09T10:30:00Z",
    "success": False
}
```

## 實作調整

### 1. Repository 層最小改變
```python
class FileBasedCommandRepository:
    def _command_to_dict(self, command: Command) -> dict:
        return {
            "command_id": command.command_id,
            "target_client_id": command.target_client_id,
            "content": command.content,
            "type": command.type,
            "status": command.status,
            "created_at": command.created_at.isoformat() if command.created_at else None,
            "result_data": command.result_data  # 🔴 只加這一行
        }
    
    def _dict_to_command(self, data: dict) -> Command:
        return Command(
            command_id=data["command_id"],
            target_client_id=data["target_client_id"],
            content=data["content"],
            type=data.get("type", "shell"),
            status=data.get("status", "pending"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            result_data=data.get("result_data")  # 🔴 只加這一行
        )
```

### 2. API 端點實作

#### `/commands/submit` - 等待機制
```python
@router.post("/commands/submit")
async def submit_command(request: SubmitCommandRequest):
    command = Command(
        command_id=str(uuid.uuid4()),
        target_client_id=request.target_client_id,
        content=request.command_content,
        type=request.command_type,
        status="pending",
        created_at=datetime.now(),
        result_data=None  # 初始為空
    )
    
    await command_repository.save(command)
    
    # 等待結果
    for _ in range(60):  # 30 秒
        await asyncio.sleep(0.5)
        
        updated = await command_repository.get(command.command_id)
        if updated.status == "completed" and updated.result_data:
            # 🔴 從 result_data 提取結果
            return {
                "command_id": command.command_id,
                "submission_successful": updated.result_data.get("success", False),
                "submission_message": updated.result_data.get("output", ""),
                "error": updated.result_data.get("error")
            }
        elif updated.status == "failed":
            return {
                "command_id": command.command_id,
                "submission_successful": False,
                "submission_message": "Command execution failed",
                "error": updated.result_data.get("error") if updated.result_data else None
            }
    
    # 超時
    return {
        "command_id": command.command_id,
        "submission_successful": False,
        "submission_message": "Command execution timeout",
        "error": "timeout"
    }
```

#### `/commands/{client_id}/result` - 接收結果
```python
@router.post("/commands/{client_id}/result")
async def submit_result(client_id: str, request: Request):
    body = await request.json()
    
    # 找到執行中的命令
    commands = await command_repository.get_all()
    processing_command = None
    
    for cmd in commands:
        if cmd.target_client_id == client_id and cmd.status == "processing":
            processing_command = cmd
            break
    
    if not processing_command:
        raise HTTPException(404, "No processing command found")
    
    # 🔴 將所有結果打包到 result_data
    processing_command.status = "completed" if body.get("success") else "failed"
    processing_command.result_data = {
        "output": body.get("output", ""),
        "error": body.get("error"),
        "execution_time": body.get("execution_time", 0),
        "completed_at": datetime.now().isoformat(),
        "success": body.get("success", False)
    }
    
    await command_repository.save(processing_command)
    
    return {"status": "success", "message": "Result recorded"}
```

#### `/commands/client/{id}` - 保持簡單
```python
@router.get("/commands/client/{client_id}")
async def get_commands_for_client(client_id: str):
    commands = await command_repository.get_all()
    
    # 檢查是否有執行中的命令
    for cmd in commands:
        if cmd.target_client_id == client_id and cmd.status == "processing":
            return []  # 已有執行中，不給新的
    
    # 找待執行的命令
    for cmd in commands:
        if cmd.target_client_id == client_id and cmd.status == "pending":
            # 標記為執行中
            cmd.status = "processing"
            await command_repository.save(cmd)
            return [cmd.to_dict()]
    
    return []
```

## Client 端修改（最小化）

### simple-client.sh 只加結果提交
```bash
# 新增函數：提交結果
submit_result() {
    local command_id="$1"
    local success="$2"
    local output="$3"
    local error="${4:-}"
    local execution_time="${5:-0}"
    
    # 建構 JSON（簡單版）
    if [ "$success" = "true" ]; then
        json_body="{\"command_id\":\"$command_id\",\"success\":true,\"output\":\"$(echo "$output" | sed 's/"/\\"/g')\"}"
    else
        json_body="{\"command_id\":\"$command_id\",\"success\":false,\"error\":\"$(echo "$error" | sed 's/"/\\"/g')\"}"
    fi
    
    curl -s -X POST "$SERVER_URL/commands/$CLIENT_ID/result" \
        -H "Content-Type: application/json" \
        -d "$json_body" > /dev/null
    
    log "INFO" "Result submitted for command: $command_id"
}

# 修改執行函數
execute_command() {
    local command_content="$1"
    local command_id="$2"
    
    log "INFO" "Executing command: $command_id"
    
    # 執行命令
    if output=$(eval "$command_content" 2>&1); then
        log "INFO" "Command executed successfully"
        # 🔴 新增：提交成功結果
        submit_result "$command_id" "true" "$output"
    else
        log "WARN" "Command failed"
        # 🔴 新增：提交失敗結果
        submit_result "$command_id" "false" "" "$output"
    fi
    
    # 顯示輸出（保持原有行為）
    echo "=== Command Output ==="
    echo "$output"
    echo "======================"
}
```

## 優勢

### 1. 最小化 Entity 變化
- ✅ 只新增一個欄位 `result_data`
- ✅ 保持原有欄位不變
- ✅ 向後相容性最佳

### 2. 靈活性
- ✅ result_data 可儲存任意 JSON 資料
- ✅ 未來可擴展而不需改 schema
- ✅ 不同類型命令可有不同結果格式

### 3. 簡單實作
- ✅ Repository 只需加兩行
- ✅ 檔案格式保持 JSON 相容
- ✅ 不需要資料庫 migration

## 測試方式

### 快速驗證
```bash
# 1. 啟動 server
python -m uvicorn brief_bridge.main:app --reload

# 2. 啟動改良版 client
./simple-client-v2.sh --client-id test-client

# 3. 提交命令並等待結果
curl -X POST http://localhost:8000/commands/submit \
    -H "Content-Type: application/json" \
    -d '{"target_client_id": "test-client", "command_content": "date"}'

# 應該會等待並返回：
{
  "command_id": "xxx",
  "submission_successful": true,
  "submission_message": "Fri Aug 9 10:30:00 PDT 2025"
}
```

## 實作時程（更短）

### Day 1 (4 小時)
1. **Hour 1**: 加入 result_data 欄位到 Command entity
2. **Hour 2**: 更新 Repository 的 to_dict/from_dict
3. **Hour 3**: 實作 `/commands/{client_id}/result` 端點
4. **Hour 4**: 修改 `/commands/submit` 加入等待

### Day 2 (4 小時)
1. **Hour 1-2**: 更新 client script 加入結果提交
2. **Hour 3-4**: 整合測試與調試

這個方案將 Entity 變化降到最低，同時保持功能完整性。