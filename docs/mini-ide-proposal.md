# Brief Bridge 迷你 IDE 功能提案

## 概述

本提案建議將 Brief Bridge 的遠端客戶端擴展為具備基本檔案操作能力的「迷你 IDE」，以解決複雜指令中的引號轉義問題，並提供更直觀的遠端開發體驗。

## 問題背景

### 當前遇到的問題
1. **引號轉義複雜**: 長指令中包含 `"` 和 `'` 引號時，轉義規則複雜且容易出錯
2. **跨平台一致性**: 不同作業系統的 shell 對引號處理方式不同
3. **多檔案操作困難**: 需要操作多個檔案時，指令組合變得冗長
4. **除錯困難**: 複雜指令失敗時難以定位問題
5. **臨時檔案管理**: 缺乏有效的工作空間概念

### 典型問題場景
```bash
# 複雜的 Docker 指令
docker run -e VAR="value with \"quotes\"" -v "$(pwd):/app" image

# 多檔案處理
echo "content with 'quotes'" > file1.txt && cat file1.txt | grep "quotes"

# 腳本執行
bash -c "cd /tmp && echo 'setup' > setup.sh && chmod +x setup.sh && ./setup.sh"
```

## 解決方案：迷你 IDE 概念

### 核心理念
將遠端客戶端視為具備基本檔案操作的「迷你 IDE」：
- 客戶端啟動位置作為 **工作區 (Workspace)**
- 提供檔案的 **CRUD 操作** API
- 指令執行在工作區內進行
- 使用 **直接檔案上傳** 避免複雜的字串轉義問題

### 直接檔案上傳機制
為了徹底避免引號轉義問題，提供簡單直接的檔案上傳方式：

**核心概念**: 將複雜的檔案內容從 JSON 指令中分離出來，使用專門的檔案上傳 API

```
AI Assistant ──────────────▶ Brief Bridge Server ──────▶ Remote Client
    │                              │                           │
    │ POST /files/deploy.sh         │                           │
    │ Content-Type: text/plain      │                           │
    │ ─────────────────────────▶    │ ───── 轉發檔案 ────▶       │
    │                              │                           │
    │ 檔案內容直接在 request body    │                     建立檔案到
    │ (無需處理引號轉義)              │                      工作目錄
```

### 架構設計

```
┌─────────────────┐    API 呼叫    ┌──────────────────────────┐
│   AI Assistant  │  ────────────▶ │    Remote Client         │
│   (Local)       │                │    (Mini IDE)            │
└─────────────────┘                └──────────────────────────┘
                                                │
                                                ▼
                                    ┌──────────────────────────┐
                                    │      Workspace           │
                                    │  /path/to/workspace/     │
                                    │  ├── config.yaml         │
                                    │  ├── deploy.sh           │
                                    │  ├── src/               │
                                    │  │   └── app.py         │
                                    │  └── logs/              │
                                    └──────────────────────────┘
```

## 功能規劃

### Phase 1: 基本檔案操作 (MVP)

#### 直接檔案上傳 API
```http
# 建立/更新檔案 (內容直接在 request body)
PUT /api/workspace/files/deploy.sh
Content-Type: text/plain
X-File-Mode: 0755

#!/bin/bash
echo "Deploying application..."
docker build -t myapp .
```

```http
# 讀取檔案內容
GET /api/workspace/files/config.yaml
```

```http
# 刪除檔案
DELETE /api/workspace/files/temp.log
```

#### 簡單指令執行 API
```json
{
  "action": "execute_command",
  "command": ["bash", "deploy.sh"],
  "working_directory": ".",
  "timeout": 300
}
```

#### 目錄操作 API
```json
{
  "action": "directory_list",
  "path": ".",
  "recursive": false
}

{
  "action": "directory_create",
  "path": "logs"
}
```

#### 指令執行 API
```json
{
  "action": "execute_command",
  "command": ["bash", "deploy.sh"],
  "working_directory": ".",
  "timeout": 300
}
```

### Phase 2: 進階 IDE 功能

#### 檔案監控與搜尋
```json
{
  "action": "file_watch",
  "patterns": ["*.log", "*.yaml"],
  "callback_url": "/webhook/file-changes"
}

{
  "action": "search_in_files", 
  "pattern": "ERROR",
  "file_types": [".log", ".txt"]
}
```

#### 工作區管理
```json
{
  "action": "workspace_status",
  "include_git_info": true
}

{
  "action": "workspace_cleanup",
  "preserve_patterns": ["*.yaml", "src/"]
}
```

### Phase 3: 協作與同步功能

#### 會話管理
```json
{
  "action": "session_create",
  "session_id": "ai-coding-session-001",
  "workspace_path": "/tmp/brief-bridge-workspace"
}
```

#### 檔案同步
```json
{
  "action": "sync_directory",
  "local_path": "./project",
  "remote_path": "workspace/project",
  "sync_mode": "bidirectional"
}
```

## 使用場景示例

### 簡化後的使用場景

#### 場景 1: 部署腳本執行
```http
# 原本複雜的指令需要處理大量引號轉義
# bash -c "echo '#!/bin/bash\necho \"Starting deploy...\"\ndocker build -t app .' > deploy.sh && chmod +x deploy.sh && ./deploy.sh"

# 新方式: 直接上傳檔案
PUT /api/workspace/files/deploy.sh
Content-Type: text/plain
X-File-Mode: 0755

#!/bin/bash
echo "Starting deployment..."
docker build -t app .
docker run -d --name myapp app
```

```json
# 然後執行
{
  "command": ["bash", "deploy.sh"]
}
```

#### 場景 2: 配置檔案管理
```http
# 直接上傳 YAML 配置檔案
PUT /api/workspace/files/config.yaml
Content-Type: application/x-yaml

database:
  host: "localhost"
  user: "admin"
  password: "secret123"
```

```json
# 使用配置檔案執行程式
{
  "command": ["python", "app.py", "--config", "config.yaml"]
}
```

#### 場景 3: 多檔案專案設置
```http
# 1. 建立主程式
PUT /api/workspace/files/src/main.py
Content-Type: text/plain

print("Hello World")
import flask
app = flask.Flask(__name__)

# 2. 建立相依清單
PUT /api/workspace/files/requirements.txt
Content-Type: text/plain

flask==2.0.1
requests==2.25.1
```

```json
# 3. 逐步執行設置指令
{"command": ["python", "-m", "venv", "venv"]}
{"command": ["venv/bin/pip", "install", "-r", "requirements.txt"]}
{"command": ["venv/bin/python", "src/main.py"]}
```

## 技術實作考量

### API 設計原則
1. **RESTful 風格**: 使用標準 HTTP 動詞和路徑
2. **直接檔案操作**: 檔案內容直接透過 HTTP body 傳輸
3. **路徑即檔名**: URL 路徑直接對應工作區中的檔案路徑
4. **冪等性**: 相同操作執行多次結果一致
5. **簡潔性**: 最小化 API 複雜度，專注核心功能

### 簡化 API 設計
```http
# 核心檔案操作
PUT    /api/workspace/files/{path}      # 建立/更新檔案
GET    /api/workspace/files/{path}      # 讀取檔案內容  
DELETE /api/workspace/files/{path}      # 刪除檔案
GET    /api/workspace/files             # 列出所有檔案

# 目錄操作
POST   /api/workspace/directories       # 建立目錄
GET    /api/workspace/directories/{path} # 列出目錄內容
DELETE /api/workspace/directories/{path} # 刪除目錄

# 指令執行
POST   /api/workspace/commands          # 執行指令
```

#### 檔案權限設定
透過 HTTP Header 設定檔案權限，避免額外的 chmod 操作：
```http
PUT /api/workspace/files/script.sh
Content-Type: text/plain
X-File-Mode: 0755          # 設定執行權限

#!/bin/bash
echo "Hello World"
```

### 安全性考量
1. **路徑限制**: 所有檔案操作限制在工作區內
2. **權限控制**: 檔案權限設定和檢查機制
3. **資源限制**: 檔案大小、數量、磁碟空間限制
4. **指令白名單**: 可執行指令的限制清單

### 錯誤處理
1. **操作失敗回滾**: 批次操作失敗時的還原機制
2. **詳細錯誤訊息**: 提供具體的錯誤原因和建議
3. **部分失敗處理**: 批次操作中部分成功的處理方式

## 功能對比分析

### Brief Bridge 現有版本 vs 迷你 IDE 提案

| 功能面向 | 現有 Brief Bridge | 迷你 IDE 提案 | 改進效益 |
|---------|-----------------|-------------|----------|
| **檔案建立** | 透過指令: `echo "content" > file.txt` | 直接 API: `PUT /files/deploy.sh` | 避免引號轉義問題 |
| **複雜腳本** | 需要複雜的字串轉義和串接 | 檔案內容直接上傳 | 支援大型複雜檔案 |
| **多檔案操作** | 需要多個串接指令 | 獨立的檔案操作 API | 操作更直觀 |
| **檔案讀取** | `cat file.txt` | `GET /files/file.txt` | 程式化存取 |
| **檔案權限** | `chmod +x script.sh` | Header: `X-File-Mode: 0755` | 一次性設定 |
| **工作目錄概念** | 無持久工作區 | 持久工作區 (workspace) | 狀態保持 |
| **錯誤處理** | Shell 錯誤訊息 | HTTP 狀態碼 + 結構化錯誤 | 更好的錯誤處理 |

### 具體使用場景對比

#### 場景 1: 建立部署腳本

**現有方式 (複雜)**:
```json
{
  "command": "bash -c \"echo '#!/bin/bash\\necho \\\"Starting deployment...\\\"\\ndocker build -t app .\\ndocker run -d app' > deploy.sh && chmod +x deploy.sh\""
}
```

**迷你 IDE 方式 (簡潔)**:
```http
PUT /api/workspace/files/deploy.sh
Content-Type: text/plain
X-File-Mode: 0755

#!/bin/bash
echo "Starting deployment..."
docker build -t app .
docker run -d app
```

#### 場景 2: 配置檔案管理

**現有方式**:
```json
{
  "command": "cat << 'EOF' > config.yaml\ndatabase:\n  host: \"localhost\"\n  password: \"secret123\"\nEOF"
}
```

**迷你 IDE 方式**:
```http
PUT /api/workspace/files/config.yaml
Content-Type: application/x-yaml

database:
  host: "localhost"
  password: "secret123"
```

#### 場景 3: 多步驟操作

**現有方式 (一個巨大的指令)**:
```json
{
  "command": "mkdir -p src && echo 'print(\"Hello World\")' > src/app.py && echo 'flask==2.0.1' > requirements.txt && python -m venv venv && venv/bin/pip install -r requirements.txt && venv/bin/python src/app.py"
}
```

**迷你 IDE 方式 (清晰分步)**:
```http
# 1. 建立目錄
POST /api/workspace/directories
{"path": "src"}

# 2. 建立程式檔案  
PUT /api/workspace/files/src/app.py
print("Hello World")

# 3. 建立相依檔案
PUT /api/workspace/files/requirements.txt
flask==2.0.1

# 4. 執行指令
POST /api/workspace/commands
{"command": ["python", "-m", "venv", "venv"]}

# 5. 安裝相依套件
POST /api/workspace/commands  
{"command": ["venv/bin/pip", "install", "-r", "requirements.txt"]}

# 6. 執行程式
POST /api/workspace/commands
{"command": ["venv/bin/python", "src/app.py"]}
```

### 除錯與維護性對比

| 維護面向 | 現有方式 | 迷你 IDE 方式 |
|---------|---------|-------------|
| **指令可讀性** | 複雜轉義，難以閱讀 | HTTP API，結構清晰 |
| **除錯難度** | 整個指令失敗，難定位 | 分步執行，容易定位問題 |
| **指令複用** | 需要重新組合字串 | 檔案可重複使用 |
| **版本控制** | 指令字串難以管理 | 檔案內容可版本化 |
| **測試友善性** | 難以單獨測試部分邏輯 | 可獨立測試各步驟 |

## 預期效益

### 開發體驗改善
- ✅ **直觀性**: 像使用本地 IDE 一樣操作遠端檔案
- ✅ **除錯便利**: 可以檢視和修改個別檔案內容
- ✅ **工作流程清晰**: 分步驟執行，每步都可驗證結果
- ✅ **檔案管理**: 持久的工作區概念，檔案狀態保持

### 技術問題解決
- ✅ **避免引號問題**: 檔案內容直接傳輸，完全避免字串轉義
- ✅ **跨平台一致**: 檔案操作 API 抽象化平台差異
- ✅ **多檔案處理**: 自然支援複雜的多檔案工作流程
- ✅ **簡潔 API**: 最小化複雜度，專注核心功能
- ✅ **權限管理**: 透過 HTTP Header 一次性設定檔案權限

### 可擴展性
- ✅ **漸進式實作**: 從基本功能開始，逐步增加進階功能
- ✅ **向下相容**: 不影響現有的指令執行功能
- ✅ **RESTful 設計**: 標準化 API 設計，易於整合
- ✅ **最小可行性**: 解決核心問題而不過度設計

## 風險評估

### 實作風險
- 🔶 **複雜度增加**: 需要實作完整的檔案管理 API
- 🔶 **狀態管理**: 工作區和會話的生命週期管理
- 🔶 **並發處理**: 多個操作同時進行時的一致性

### 安全風險
- 🔴 **檔案系統存取**: 需要嚴格的路徑和權限控制
- 🔴 **資源消耗**: 檔案操作可能消耗大量磁碟空間和 I/O
- 🔴 **權限提升**: 避免透過檔案操作獲得系統權限

### 緩解策略
1. **沙盒環境**: 所有操作在隔離的工作區內進行
2. **資源配額**: 設定檔案數量、大小、執行時間限制
3. **操作審計**: 記錄所有檔案和指令操作日誌
4. **漸進式推出**: 從受限環境開始測試和部署

## 實作時程建議

### Week 1-2: Phase 1 設計與原型
- API 介面設計
- 基本檔案 CRUD 功能
- 簡單的指令執行整合

### Week 3-4: Phase 1 完整實作
- 完整的檔案管理 API
- 安全機制實作
- 錯誤處理和測試

### Week 5-6: Phase 2 進階功能
- 檔案監控和搜尋
- 工作區管理功能
- 效能優化

### Week 7-8: Phase 3 協作功能
- 會話管理
- 檔案同步機制
- 多用戶支援

## 結論

迷你 IDE 功能將使 Brief Bridge 從單純的指令執行工具，進化為功能豐富的遠端開發環境。這不僅解決了當前的引號轉義問題，更開啟了更多創新的遠端開發可能性。

建議採用漸進式開發策略，從核心的檔案操作功能開始，逐步擴展到完整的 IDE 功能集。這樣既能快速解決當前問題，又為未來的功能擴展奠定基礎。

---

*本提案書將持續更新和完善，歡迎提供反饋和建議。*