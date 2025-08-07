# Brief Bridge - Clean Architecture 目錄結構

## 整體結構概覽

```
brief_bridge/
├── __init__.py
├── main.py                          # FastAPI 應用程式進入點
│
├── domain/                          # 領域層 (Domain Layer)
│   ├── __init__.py
│   ├── entities/                    # 領域實體
│   │   ├── __init__.py
│   │   ├── client.py               # Client entity
│   │   ├── command.py              # Command entity  
│   │   └── execution_result.py     # ExecutionResult entity
│   ├── value_objects/              # 值物件
│   │   ├── __init__.py
│   │   ├── client_id.py
│   │   ├── command_id.py
│   │   ├── client_info.py
│   │   ├── client_status.py
│   │   ├── execution_status.py
│   │   └── execution_output.py
│   ├── services/                   # 領域服務
│   │   ├── __init__.py
│   │   ├── command_dispatcher.py
│   │   ├── client_health_monitor.py
│   │   └── execution_orchestrator.py
│   └── repositories/               # Repository 抽象介面
│       ├── __init__.py
│       ├── client_repository.py
│       ├── command_repository.py
│       └── execution_result_repository.py
│
├── application/                     # 應用層 (Application Layer)
│   ├── __init__.py
│   ├── use_cases/                  # 用例實作
│   │   ├── __init__.py
│   │   ├── ai_assistant/           # AI 助手用例
│   │   │   ├── __init__.py
│   │   │   ├── submit_command_use_case.py
│   │   │   ├── query_execution_result_use_case.py
│   │   │   └── list_available_clients_use_case.py
│   │   ├── client/                 # 客戶端用例
│   │   │   ├── __init__.py
│   │   │   ├── register_client_use_case.py
│   │   │   ├── poll_for_commands_use_case.py
│   │   │   ├── execute_command_and_report_use_case.py
│   │   │   └── maintain_heartbeat_use_case.py
│   │   └── system/                 # 系統管理用例
│   │       ├── __init__.py
│   │       ├── monitor_system_status_use_case.py
│   │       ├── manage_client_connections_use_case.py
│   │       └── cleanup_expired_resources_use_case.py
│   ├── dtos/                       # 資料傳輸物件
│   │   ├── __init__.py
│   │   ├── client_dto.py
│   │   ├── command_dto.py
│   │   └── execution_result_dto.py
│   └── services/                   # 應用服務
│       ├── __init__.py
│       └── background_tasks.py     # 背景任務 (心跳檢查等)
│
├── infrastructure/                  # 基礎設施層 (Infrastructure Layer)
│   ├── __init__.py
│   ├── persistence/                # 資料持久化
│   │   ├── __init__.py
│   │   ├── memory/                 # 記憶體儲存實作
│   │   │   ├── __init__.py
│   │   │   ├── memory_client_repository.py
│   │   │   ├── memory_command_repository.py
│   │   │   └── memory_execution_result_repository.py
│   │   └── models/                 # 資料模型
│   │       ├── __init__.py
│   │       ├── client_model.py
│   │       ├── command_model.py
│   │       └── execution_result_model.py
│   ├── external/                   # 外部服務
│   │   ├── __init__.py
│   │   └── shell_executor.py       # Shell 命令執行器
│   ├── fastapi/                    # FastAPI 相關
│   │   ├── __init__.py
│   │   ├── routers/                # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── ai_assistant.py     # AI 助手端點
│   │   │   ├── clients.py          # 客戶端端點
│   │   │   └── system.py           # 系統管理端點
│   │   ├── schemas/                # Pydantic 結構描述
│   │   │   ├── __init__.py
│   │   │   ├── client_schemas.py
│   │   │   ├── command_schemas.py
│   │   │   └── execution_result_schemas.py
│   │   └── dependencies/           # FastAPI 依賴注入
│   │       ├── __init__.py
│   │       └── container.py        # DI 容器
│   ├── scripts/                    # 客戶端腳本
│   │   ├── client.ps1              # PowerShell 客戶端
│   │   └── client.sh               # Bash 客戶端
│   └── config/                     # 設定
│       ├── __init__.py
│       └── settings.py
│
└── tests/                          # 測試
    ├── __init__.py
    ├── conftest.py
    ├── unit/                       # 單元測試
    │   ├── domain/
    │   ├── application/
    │   └── infrastructure/
    ├── integration/                # 整合測試
    │   └── api/
    └── e2e/                       # 端到端測試
        └── test_walking_skeleton.py
```

## 層級職責說明

### Domain Layer (領域層)
- **entities/**: 核心業務實體，包含業務邏輯和規則
- **value_objects/**: 不可變的值物件
- **services/**: 跨實體的業務邏輯
- **repositories/**: 資料存取的抽象介面

### Application Layer (應用層)  
- **use_cases/**: 具體的應用程式用例，協調領域物件
- **dtos/**: 跨層資料傳輸物件
- **services/**: 應用層的協調服務

### Infrastructure Layer (基礎設施層)
- **persistence/**: Repository 的具體實作和資料模型
- **external/**: 外部系統整合 (shell 執行器等)
- **fastapi/**: FastAPI 相關的路由、結構描述和依賴注入
- **scripts/**: 客戶端執行腳本
- **config/**: 系統設定

## 依賴方向

```
Infrastructure → Application → Domain
```

- 所有層級都可以依賴 Domain Layer
- Application Layer 不依賴 Infrastructure Layer 
- Infrastructure Layer 依賴 Application Layer，負責 HTTP 請求處理、資料存取和外部系統整合
- Domain Layer 不依賴任何外層
- 通過依賴反轉原則 (DIP) 處理外部依賴

## 關鍵設計原則

1. **依賴反轉**: Repository 介面定義在 Domain 層，實作在 Infrastructure 層
2. **介面隔離**: 每個用例都有明確的介面
3. **單一職責**: 每個模組都有清楚的職責
4. **開放封閉**: 通過抽象介面支援擴展

---

*此結構遵循 Clean Architecture 原則，確保業務邏輯的獨立性和可測試性*