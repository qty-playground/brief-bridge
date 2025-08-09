# E2E (End-to-End) Tests

## 目的

這個目錄包含從 Web API 開始的完整綜合測試，驗證整個系統從 HTTP 請求到業務邏輯的完整流程。

## 測試層次對比

### 🧪 BDD Tests (`tests/submit_command_use_case/`, `tests/register_client_use_case/`)
- **測試層次**: Use Case 層
- **範圍**: 直接測試業務邏輯
- **特點**: 快速、隔離、專注於業務規則
- **使用場景**: 驗證核心業務邏輯正確性

### 🌐 E2E Tests (`tests/e2e/`)
- **測試層次**: Web API 層 → Use Case 層 → Entity 層 → Repository 層
- **範圍**: 完整的 HTTP 請求-響應循環
- **特點**: 真實環境模擬、完整集成測試
- **使用場景**: 驗證完整系統功能和 API 契約

### 🔧 Unit Tests (`tests/test_*_e2e.py`)
- **測試層次**: 各個組件單獨測試
- **範圍**: 單一功能或組件
- **特點**: 最快速、最隔離
- **使用場景**: 驗證個別組件功能

## 當前實作狀況

### ✅ 已完成
1. **E2E 測試基礎設施**
   - `conftest.py` - 測試配置和 fixtures
   - 獨立的 repository instances 確保測試隔離

2. **完整的 Web API 層**
   - `SubmitCommandResponseSchema` 包含 `result`, `error`, `execution_time`
   - `CommandSchema` 包含完整的執行狀態欄位  
   - `POST /commands/result` - 客戶端結果提交 API
   - `GET /commands/client/{id}` - 單一命令執行機制

3. **客戶端模擬框架**
   - `client_simulator.py` - 完整的客戶端模擬框架
   - 支援自定義命令處理器
   - 支援延遲、錯誤、並行執行模擬
   - 真實的輪詢和結果提交機制

4. **完整的 E2E 測試套件**
   - `test_command_submission_flow.py` - 基本命令提交流程
   - `test_full_command_execution_cycle.py` - 完整執行週期
   - `test_complete_command_execution_with_simulation.py` - 真實客戶端模擬測試

### 🎉 客戶端模擬框架功能

#### **ClientSimulator 類別**
- 模擬單一客戶端行為
- 自動輪詢命令並執行
- 支援自定義命令處理器
- 後台執行模式

#### **MultiClientSimulator 類別**  
- 管理多個客戶端模擬器
- 並行客戶端執行
- 統一啟動和停止控制

#### **預定義處理器**
- `create_delayed_handler()` - 自定義延遲執行
- `create_error_handler()` - 錯誤模擬
- `default_command_handler()` - 預設成功執行

### ✅ 驗證的核心功能

1. **真實等待機制** ✅
   - AI 提交命令後等待執行結果
   - 客戶端輪詢、執行、回傳結果
   - 完整的異步執行流程

2. **並行執行隔離** ✅  
   - 多客戶端同時執行不同命令
   - 命令結果正確隔離
   - 真實並行性驗證（時間測試通過）

3. **錯誤處理機制** ✅
   - 命令執行失敗處理
   - 超時機制驗證  
   - 錯誤信息正確傳遞

4. **單一執行保證** ✅
   - 客戶端一次只獲取一個命令
   - 命令狀態正確轉換（pending → processing → completed）

## 未來改進

### 🎯 短期目標
1. 實作客戶端結果提交 API
2. 改進客戶端命令獲取機制  
3. 創建更完整的客戶端模擬框架

### 🚀 長期目標
1. 真實的異步測試框架
2. 性能測試和負載測試
3. 錯誤恢復和重試機制測試

## 運行測試

```bash
# 運行所有 E2E 測試
pytest tests/e2e/ -v

# 運行特定測試文件
pytest tests/e2e/test_command_submission_flow.py -v

# 運行特定測試
pytest tests/e2e/test_command_submission_flow.py::TestCommandSubmissionE2E::test_invalid_client_command_submission -v
```

## 注意事項

- E2E 測試比 BDD 測試慢，因為它們測試完整的 HTTP 堆棧
- 部分測試可能會因為等待機制而較慢或超時
- 測試使用獨立的 in-memory repositories，不會影響開發數據