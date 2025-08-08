# Brief Bridge - 簡化架構目錄結構

## 整體結構概覽

我們採用簡化的架構方式：**Framework ↔ UseCase ↔ Entity/Repository**，重點是依賴注入和可測試性，避免過度工程化。

```
brief_bridge/
├── __init__.py
├── main.py                          # FastAPI 應用程式進入點
│
├── entities/                        # 業務實體 (包含業務邏輯)
│   ├── __init__.py
│   ├── client.py                    # Client entity with business rules
│   ├── command.py                   # Command entity  
│   └── execution_result.py          # ExecutionResult entity
│
├── use_cases/                       # 用例實作 (依賴注入模式)
│   ├── __init__.py
│   ├── submit_command_use_case.py   # AI 助手提交指令
│   ├── query_execution_result_use_case.py  # 查詢執行結果
│   ├── list_available_clients_use_case.py  # 列出可用客戶端
│   ├── register_client_use_case.py         # 註冊客戶端
│   ├── poll_for_commands_use_case.py       # 輪詢指令
│   ├── execute_command_and_report_use_case.py  # 執行指令並回報
│   └── maintain_heartbeat_use_case.py      # 維持心跳
│
├── repositories/                    # 資料持久化 (具體實作)
│   ├── __init__.py
│   ├── client_repository.py         # 客戶端資料存取
│   ├── command_repository.py        # 指令資料存取
│   └── execution_result_repository.py  # 執行結果資料存取
│
└── web/                            # Framework 層 (FastAPI)
    ├── __init__.py
    ├── routers/                    # API 路由
    │   ├── __init__.py
    │   ├── ai_assistant.py         # AI 助手端點
    │   └── clients.py              # 客戶端端點
    ├── schemas/                    # Pydantic 結構描述 (轉換用)
    │   ├── __init__.py
    │   ├── client_schemas.py
    │   ├── command_schemas.py
    │   └── execution_result_schemas.py
    └── dependencies.py             # FastAPI 依賴注入設定
```

## 架構原則

### 1. Framework ↔ UseCase ↔ Entity/Repository 流程

**資料流向:**
```
HTTP Request 
↓ (Framework 轉換)
Simple Dict/Class 
↓ (UseCase 處理)  
Entity Business Logic + Repository Persistence
↓ (UseCase 回傳)
Simple Dict/Class
↓ (Framework 轉換)
HTTP Response
```

### 2. 依賴注入模式

**UseCase 範例:**
```python
# brief_bridge/use_cases/submit_command_use_case.py
class SubmitCommandUseCase:
    def __init__(self, client_repo: ClientRepository, command_repo: CommandRepository):
        self._client_repo = client_repo  # 依賴注入
        self._command_repo = command_repo  # 依賴注入
        
    async def execute(self, request: dict) -> dict:
        client = await self._client_repo.find(request["client_id"])
        if not client.can_accept_new_command():  # 業務邏輯在 entity
            raise ClientNotAvailableError()
            
        command_id = str(uuid.uuid4())
        await self._command_repo.save(command_id, request["content"])
        return {"status": "success", "command_id": command_id}
```

### 3. Entity 業務邏輯

**Entity 範例:**
```python
# brief_bridge/entities/client.py
class Client:
    def __init__(self, client_id: str, info: dict):
        self.client_id = client_id
        self.info = info
        self.status = "ONLINE"
        self.availability = "IDLE"
        
    def can_accept_new_command(self) -> bool:
        """業務規則: 客戶端可用性檢查"""
        return self.status == "ONLINE" and self.availability == "IDLE"
        
    def assign_command(self, command_id: str, content: str) -> None:
        """業務規則: 一個客戶端同時只能執行一個指令"""
        if self.has_active_command():
            raise ClientBusyError("Client already executing command")
        self.current_command = {"id": command_id, "content": content}
        self.availability = "BUSY"
```

### 4. Repository 具體實作

**Repository 範例:**
```python
# brief_bridge/repositories/client_repository.py
class ClientRepository:
    def __init__(self):
        self._clients = {}  # 簡單的記憶體儲存
        
    async def save(self, client: Client) -> None:
        self._clients[client.client_id] = client
        
    async def find(self, client_id: str) -> Client:
        return self._clients.get(client_id)
        
    async def find_all_online(self) -> List[Client]:
        return [c for c in self._clients.values() if c.status == "ONLINE"]
```

### 5. Framework 層轉換

**Controller 範例:**
```python
# brief_bridge/web/routers/ai_assistant.py
@router.post("/commands")
async def submit_command(
    request: CommandRequest, 
    use_case: SubmitCommandUseCase = Depends()
):
    # Framework DTO 轉換為簡單資料結構
    result = await use_case.execute({
        "client_id": request.client_id,
        "content": request.content
    })
    return result  # UseCase 回傳簡單資料結構
```

## 測試策略

### 雙層測試模式

**1. E2E 測試 (通過 Framework)**
```python
def test_submit_command_via_http():
    response = client.post("/commands", json={
        "client_id": "client-001",
        "content": "ls -la"
    })
    assert response.status_code == 200
    assert "command_id" in response.json()
```

**2. UseCase 單元測試 (直接測試)**
```python  
def test_submit_command_use_case():
    # Mock 注入的依賴
    client_repo = Mock()
    command_repo = Mock()
    use_case = SubmitCommandUseCase(client_repo, command_repo)
    
    result = await use_case.execute({"client_id": "test", "content": "ls"})
    assert result["status"] == "success"
```

## 實作指導原則

### ✅ 採用的做法

1. **依賴注入**: UseCase 透過建構子注入外部依賴
2. **簡單資料結構**: UseCase 內部使用 dict/簡單類別
3. **業務邏輯在 Entity**: 領域規則實作在實體方法中
4. **具體實作優先**: 先用具體類別，需要時再抽象化
5. **可測試性優先**: 架構服務於測試，不是相反

### ❌ 避免的做法

1. **過度抽象**: 避免不必要的介面和工廠模式
2. **複雜值物件**: 避免過度細分值物件類別
3. **嚴格分層**: 不強制執行嚴格的層次依賴規則
4. **領域事件**: 對簡單狀態變更避免使用領域事件
5. **服務層傳遞**: 避免只是傳遞資料的服務層

## 資料夾說明

| 資料夾 | 職責 | 重點 |
|--------|------|------|
| `entities/` | 業務邏輯實體 | 包含業務規則方法 |
| `use_cases/` | 業務用例協調 | 依賴注入，簡單資料結構 |
| `repositories/` | 資料持久化 | 具體實作，易於測試 |
| `web/` | Framework 層 | 資料轉換，路由處理 |

## 開發流程

1. **從 Entity 開始**: 設計業務實體和規則
2. **UseCase 協調**: 使用依賴注入組合業務邏輯
3. **Repository 實作**: 提供資料存取功能
4. **Framework 集成**: 處理 HTTP 請求轉換
5. **雙層測試**: E2E + UseCase 單元測試

這個架構著重實用性和可測試性，避免過度工程化，讓開發更專注於業務價值的實現。