# Brief Bridge

一個輕量級的開發輔助工具，透過 HTTP polling 讓 AI coding assistant 管理分散在內網的多個 client。

## 設計理念

使用 polling 機制確保最大相容性，client 只需要 shell 內建的 HTTP 功能，無需安裝額外工具。

## 能做什麼

### 典型應用場景
- **異質環境開發**：AI coding assistant 在不同 OS/架構上測試和驗證程式碼
- **Runtime context 收集**：AI 獲取真實執行環境的狀態、logs、錯誤訊息
- **跨平台除錯**：AI 在多個環境中重現和診斷問題
- **開發環境同步**：AI 協助在不同機器間同步開發環境和設定

### 使用體驗
```powershell
# Windows - 一行啟動 client
& ([scriptblock]::Create((Invoke-WebRequest 'https://your-public-endpoint.com/client.ps1').Content)) -Start
```

```bash
# Linux/macOS - 一行啟動 client
curl -sSL https://your-public-endpoint.com/client.sh | bash
```

啟動後，client 自動開始 polling server 獲取 AI coding assistant 派發的任務。

## 架構設計

### 架構組件與職責

**AI Coding Assistant**
- 分析開發需求，生成具體執行指令
- 解析 runtime context，提供智慧建議

**HTTP Server** 
- 管理 client 註冊和狀態
- 命令 queue 和結果收集
- 提供 AI Coding Assistant API interface

**Public Endpoint**
- 網路穿透和 routing
- 提供穩定的外網存取點

**Client Nodes**
- 執行環境探測和指令執行
- Runtime context 收集和回報
- 輕量級 polling 和狀態同步

```
AI Coding Assistant <-> HTTP Server <-> Public Endpoint <-> Client (Polling)
```

### 實作技術 (MVP)
- **HTTP Server**：FastAPI (memory-based storage)
- **Client**：純 Shell（PowerShell `Invoke-WebRequest`、curl + bash）
- **Public Endpoint**：ngrok, Cloudflare Tunnel 等
- **通訊協定**：HTTP RESTful API

## MVP 必要功能

### 核心驗證：AI Coding Assistant 指令執行循環
完整流程：AI Coding Assistant 發送指令 → Client 執行 → 回傳結果

### Server 端
- **Client 註冊**：記錄上線的 client
- **命令分發**：接收 AI 指令，推送給指定 client  
- **結果收集**：接收並回傳執行結果給 AI
- **基礎 API**：`/register`, `/commands`, `/results`

### Client 端  
- **Polling**：定期檢查新命令
- **執行**：執行 shell 指令並捕獲輸出
- **回報**：將結果回傳給 server
- **一行啟動**：直接執行，無需安裝

### AI Integration
- **自學習 API**：GET `/` - 提供使用說明讓 AI 學習 bridge 用法
- **指令 API**：POST `/commands` - 提交指令，GET `/commands/{id}` - 查詢結果
- **基本指令**：支援常見 shell 命令（`ls`, `pwd`, `echo` 等）

## API 參考

#### 核心 API
```
GET  /                     # AI 獲取 bridge 使用說明
POST /clients/register     # Client 註冊
GET  /clients/{id}/commands # Client 獲取命令  
POST /clients/{id}/results  # Client 回傳結果
POST /commands             # AI 提交新命令
GET  /commands/{id}        # AI 查詢執行結果
GET  /clients              # AI 查詢可用 client
```

## 開發進程

### Phase 1: Core Components
- HTTP Server 基礎架構
- Client polling 機制
- 命令執行和結果回傳
- 一行啟動 script

### Phase 2: Integration Layer  
- AI Coding Assistant API integration
- Client-Server 完整串接
- 基本 error handling

### Phase 3: Enhancement
- Web dashboard 
- 安全機制 (API token)
- Retry logic 和穩定性改善

## 成功指標

- **啟動時間** < 1 分鐘
- **Client 註冊成功率** > 95%
- **命令執行成功率** > 90%
- **Polling 延遲** < 30 秒

## 參與貢獻

歡迎貢獻！請隨時提交 issues 和 pull requests。

## 授權

MIT License