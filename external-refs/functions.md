# PowerShell Client 專案流程文件

## 專案概述

本專案為 client-server 架構中的 client side 組件，使用 PowerShell 5.1 相容的 script 實作。Client 採用 polling 機制與 server 端通訊，主要功能是接收並執行來自 server 的 PowerShell 指令，適用於臨時性的遠程控制需求。

## 系統架構

- **Client Side**: PowerShell 5.1 相容腳本
- **通訊協定**: HTTP + JSON
- **通訊方式**: Polling（5秒間隔）
- **部署方式**: 臨時執行，非持久性服務
- **生命週期**: 支援 idle timeout (10分鐘) 和優雅關閉

## 完整流程

### 1. 部署與啟動階段

#### 1.1 遠程部署
```powershell
# 使用者在目標機器上手動執行
irm https://abc123.ngrok-free.app/install.ps1 | iex
```

#### 1.2 Client 初始化
- 腳本在當前 PowerShell session 中直接運行
- **自動偵測 Client ID**：
  - 優先順序：`$env:COMPUTERNAME` → `$env:HOSTNAME` → `$env:USER-隨機數` → `pwsh-client-隨機數`
- 從安裝 URL 自動解析 server 連線資訊
- **Client 註冊**：向 server 註冊 Client ID 和名稱

#### 1.3 API Endpoints 設定
- 註冊 API：`POST /clients/register`
- 輪詢 API：`POST /commands/poll`  
- 結果回傳 API：`POST /commands/result`
- 檔案下載：`GET /files/download/{FILE_ID}`
- 檔案上傳：`POST /files/upload`

### 2. 主要運行階段

#### 2.1 Polling 迴圈
- 每 5 秒向 server 發送 HTTP POST request 到 `/commands/poll`
- 請求包含 Client ID 的 JSON 資料
- 無限迴圈運行，直到收到終止指示
- Polling 同時作為心跳檢測機制

#### 2.2 生命週期管理
- **Idle Timeout**：10分鐘無指令時自動終止
- **404 檢測**：連續3次404回應時自動終止  
- **錯誤重試**：最多重試3次，間隔5秒
- **優雅關閉**：收到 `terminate` 指令時停止運行

#### 2.3 錯誤處理
- 執行過程中遇到錯誤會記錄但繼續運行
- 連續錯誤達到5次時終止 client
- 各類錯誤分別計數和處理

### 3. Command Execution 階段

#### 3.1 指令接收與解析
Server 回應格式：
```json
{
    "command_id": "unique_id", 
    "command_content": "powershell -executionpolicy bypass -file script.ps1",
    "timeout": 30
}
```

#### 3.2 指令執行
- 使用 `Invoke-Expression` 執行指令內容
- 設定執行 timeout（預設30秒）
- 捕獲 stdout、stderr 和執行時間
- 特殊處理 `terminate` 指令觸發優雅關閉

#### 3.3 執行範例
```powershell
# 詳細診斷腳本範例
Write-Output "=== Module Compatibility Test ==="
Write-Output "PowerShell Version: $($PSVersionTable.PSVersion)"

try {
    # 透過 FILE_ID 下載模組檔案
    Invoke-WebRequest -Uri "TUNNEL_URL/files/download/FILE_ID_PSM1" -OutFile "Module.psm1"
    Invoke-WebRequest -Uri "TUNNEL_URL/files/download/FILE_ID_PSD1" -OutFile "Module.psd1"
    
    # 測試模組匯入
    Import-Module ".\Module.psd1" -Force
    
    # 驗證模組載入
    $module = Get-Module ModuleName
    Write-Output "Module loaded: $($module -ne $null)"
    Write-Output "Exported functions: $($module.ExportedFunctions.Count)"
    
} catch {
    Write-Output "ERROR: $($_.Exception.Message)"
}
```

### 4. 結果回傳階段

#### 4.1 結果收集
執行結果格式：
```json
{
    "command_id": "unique_id",
    "success": true/false,
    "output": "stdout內容", 
    "error": "錯誤訊息或null",
    "execution_time": 1.23
}
```

#### 4.2 結果回傳
- 透過 `POST /commands/result` 回傳執行結果
- 包含完整的執行狀態和輸出資訊
- 失敗時記錄警告但不中斷主流程

#### 4.3 檔案上傳回傳（擴充功能）
對於大型結果，仍可使用檔案上傳機制：
```powershell
# 上傳結果檔案到 POST /files/upload
$uploadResult = Invoke-RestMethod -Uri "$ServerUrl/files/upload" -Method POST -Form @{
    file = Get-Item "result.json"
    client_id = $ClientId
}
```

### 5. 終止階段

#### 5.1 終止觸發條件
- 收到 server 的 `terminate` 指令
- Idle timeout 達到10分鐘
- 連續3次404回應
- 連續5次一般錯誤
- 使用者手動中斷（Ctrl+C）

#### 5.2 優雅關閉流程
- 停止 polling 迴圈
- 清理暫存檔案（如果有的話）
- 輸出關閉訊息
- 結束 PowerShell session

## 關鍵特性

### 彈性執行
- 支援多種 PowerShell 執行模式
- 透過 FILE_ID 機制實現動態內容下載
- Server 可根據需求靈活調整執行內容

### 臨時性設計
- 不安裝為系統服務或排程工作
- 依賴使用者保持 PowerShell session 開啟
- 適合短期或一次性遠程控制需求

### 容錯機制
- 執行錯誤不會中斷整體運行
- 透過 polling 提供持續的連線檢測
- 支援優雅關閉和強制終止

### 檔案管理
- Server 預先上傳檔案並分配 FILE_ID
- Client 透過 FILE_ID 下載實際執行內容
- 支援大型結果透過檔案上傳回傳

## 技術規格

- **PowerShell 版本**: 5.1 相容（支援跨平台）
- **Polling 間隔**: 5 秒
- **通訊協定**: HTTP + JSON
- **執行原則**: `-executionpolicy bypass`
- **Client ID**: 自動偵測系統資訊生成
- **Timeout 設定**: 
  - HTTP 請求：30秒
  - 指令執行：可設定（預設30秒）
  - Idle timeout：10分鐘
- **重試機制**:
  - HTTP 重試：3次，間隔5秒
  - 最大連續404：3次
  - 最大連續錯誤：5次

## 流程步驟編號

### 1. 部署與啟動階段
- **1.1** 遠程執行安裝指令
- **1.2** 下載並執行 install.ps1，載入內建 functions
- **1.3** 自動偵測並生成 Client ID  
- **1.4** 解析 server 連線資訊，設定 API endpoints
- **1.5** 向 server 註冊 client

### 2. 主要運行階段
- **2.1** 初始化 polling 迴圈（5秒間隔）
- **2.2** 發送 HTTP POST polling request
- **2.3** 檢查 server 回應和指令
- **2.4** 生命週期檢查（idle timeout、404計數、錯誤計數）
- **2.5** 處理各類錯誤和重試機制

### 3. Command Execution 階段  
- **3.1** 接收 command execution request（含 command_id、content、timeout）
- **3.2** 解析指令內容
- **3.3** 使用 Invoke-Expression 執行 PowerShell 指令
- **3.4** 監控執行時間和 timeout
- **3.5** 捕獲執行結果（success、output、error、execution_time）
- **3.6** 處理特殊指令（如 terminate）

### 4. 結果回傳階段
- **4.1** 格式化執行結果為 JSON
- **4.2** 透過 POST /commands/result 回傳結果  
- **4.3** 確認回傳成功（失敗時記錄警告）
- **4.4** 檔案上傳回傳（選用，適用大型結果）

### 5. 終止階段
- **5.1** 檢測各種終止條件（terminate指令、timeout、404、錯誤）
- **5.2** 停止 polling 迴圈
- **5.3** 清理暫存資源
- **5.4** 輸出關閉訊息並結束

## 內建 Functions 需求對應表

| 步驟編號 | 功能需求 | Function 提案 | 說明 |
|---------|---------|--------------|------|
| 1.3 | 自動偵測 Client ID | `Get-ClientId` | 跨平台偵測 COMPUTERNAME/HOSTNAME/USER，含備用方案 |
| 1.4 | 解析連線資訊 | `Initialize-ClientConfig` | 從安裝 URL 解析並設定所有 API endpoints |
| 1.5 | 註冊 client | `Register-Client` | POST /clients/register，包含 client_id 和 name |
| 2.1, 2.2 | HTTP 請求處理 | `Invoke-HttpRequest` | 統一的 HTTP 請求，含重試機制和錯誤處理 |
| 2.2 | 輪詢指令 | `Get-PendingCommand` | POST /commands/poll，回傳待執行指令 |
| 2.4 | Idle timeout 檢查 | `Test-IdleTimeout` | 檢查距離上次指令時間是否超過10分鐘 |
| 2.4 | 404 計數檢查 | `Test-404Limit` | 追蹤連續404次數，達到3次時觸發終止 |
| 2.5 | 錯誤重試機制 | `Handle-RetryableError` | 處理可重試錯誤，含延遲和計數邏輯 |
| 3.3 | 執行 PowerShell 指令 | `Invoke-PowerShellCommand` | 執行指令並捕獲結果，含 timeout 處理 |
| 3.5 | 收集執行結果 | `New-ExecutionResult` | 標準化建立執行結果物件 |
| 3.6 | 處理特殊指令 | `Test-TerminateCommand` | 檢查是否為 terminate 指令 |
| 4.1 | 格式化結果 | `Format-CommandResult` | 將執行結果轉換為 API 所需的 JSON 格式 |
| 4.2 | 回傳指令結果 | `Submit-CommandResult` | POST /commands/result，回傳執行結果 |
| 4.4 | 檔案上傳 | `Submit-ResultFile` | POST /files/upload，上傳大型結果檔案 |
| 3.4, 4.4 | 檔案下載 | `Invoke-ClientDownload` | GET /files/download/{FILE_ID}，下載檔案 |
| 5.1 | 檢查終止條件 | `Test-ShouldTerminate` | 綜合檢查所有終止條件 |
| 5.3 | 清理暫存檔案 | `Clear-ClientTempFiles` | 清理執行過程產生的暫存檔案 |
| 通用 | 標準化輸出 | `Write-ClientOutput` | 統一的輸出格式，含顏色和時間戳記 |
| 通用 | 標準化錯誤輸出 | `Write-ClientError` | 統一的錯誤輸出格式 |
| 通用 | 日誌記錄 | `Write-ClientLog` | 統一的日誌記錄，含 debug 模式支援 |
| 通用 | 系統資訊收集 | `Get-ClientSystemInfo` | 收集平台、版本等系統資訊 |
| 通用 | 生命週期狀態 | `Get-ClientLifecycleStatus` | 取得當前 client 生命週期狀態資訊 |