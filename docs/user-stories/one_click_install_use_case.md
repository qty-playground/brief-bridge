# User Story: One-Click Install Use Case

## 故事描述

作為一個需要部署 Brief Bridge 客戶端的使用者，
我希望能透過一行指令完成客戶端的下載、安裝和啟動，
這樣我就能快速在多台機器上部署客戶端，無需手動配置。

## 背景說明

目前客戶端部署需要：
1. 手動下載客戶端腳本
2. 設定伺服器 URL
3. 配置客戶端 ID
4. 執行腳本

這個過程對於大規模部署或臨時部署來說太過繁瑣。我們需要一個像 ws-call 那樣的一鍵安裝機制。

## 驗收標準

### Scenario 1: PowerShell 一鍵安裝成功
```gherkin
Given 伺服器正在運行並可透過公開 URL 訪問
When 使用者在 Windows PowerShell 執行安裝命令：
  """
  iex ((Invoke-WebRequest 'http://server-url/install.ps1').Content)
  """
Then 客戶端腳本應該被下載
And 客戶端應該自動註冊到伺服器
And 客戶端應該開始輪詢命令
And 使用者應該看到成功訊息
```

### Scenario 2: Bash 一鍵安裝成功
```gherkin
Given 伺服器正在運行並可透過公開 URL 訪問
When 使用者在 Linux/macOS 執行安裝命令：
  """
  curl -sSL http://server-url/install.sh | bash
  """
Then 客戶端腳本應該被下載
And 客戶端應該自動註冊到伺服器
And 客戶端應該開始輪詢命令
And 使用者應該看到成功訊息
```

### Scenario 3: 自定義客戶端 ID 安裝
```gherkin
Given 伺服器正在運行並可透過公開 URL 訪問
When 使用者執行安裝命令並指定客戶端 ID：
  """
  iex ((Invoke-WebRequest 'http://server-url/install.ps1?client_id=my-laptop').Content)
  """
Then 客戶端應該使用指定的 ID "my-laptop" 註冊
And 客戶端應該開始輪詢命令
```

### Scenario 4: 帶參數的安裝
```gherkin
Given 伺服器正在運行並可透過公開 URL 訪問
When 使用者執行安裝命令並指定多個參數：
  """
  iex ((Invoke-WebRequest 'http://server-url/install.ps1?client_id=laptop&poll_interval=5&debug=true').Content)
  """
Then 客戶端應該使用指定的參數運行：
  | Parameter     | Value  |
  | client_id     | laptop |
  | poll_interval | 5      |
  | debug         | true   |
```

### Scenario 5: 背景執行模式
```gherkin
Given 伺服器正在運行並可透過公開 URL 訪問
When 使用者執行安裝命令並指定背景執行：
  """
  iex ((Invoke-WebRequest 'http://server-url/install.ps1').Content) -Background
  """
Then 客戶端應該在背景執行
And 使用者應該能繼續使用終端
And 客戶端程序應該持續輪詢命令
```

### Scenario 6: 安裝失敗 - 伺服器無法連線
```gherkin
Given 伺服器 URL 無法訪問
When 使用者執行安裝命令
Then 應該顯示連線錯誤訊息
And 安裝應該中止
And 不應該有客戶端程序執行
```

### Scenario 7: 重複安裝處理
```gherkin
Given 客戶端已經在運行
When 使用者再次執行安裝命令
Then 應該檢測到現有客戶端
And 應該詢問是否要：
  - 停止現有客戶端並重新安裝
  - 保持現有客戶端繼續運行
  - 取消安裝
```

## 技術需求

### API 端點

1. **GET /install.ps1**
   - 返回 PowerShell 安裝腳本
   - 支援 Query Parameters:
     - `client_id`: 自定義客戶端 ID
     - `client_name`: 客戶端顯示名稱
     - `poll_interval`: 輪詢間隔（秒）
     - `debug`: 調試模式
   - 腳本應包含：
     - 伺服器 URL 自動注入
     - 客戶端自動下載邏輯
     - 自動註冊和啟動

2. **GET /install.sh**
   - 返回 Bash 安裝腳本
   - 支援相同的 Query Parameters
   - 適用於 Linux/macOS

3. **GET /client/download/{platform}**
   - 返回實際的客戶端腳本
   - 平台選項：`windows`, `linux`, `macos`

### 安裝腳本功能

PowerShell 安裝腳本應該：
```powershell
# 1. 檢查環境
$PSVersion = $PSVersionTable.PSVersion
if ($PSVersion.Major -lt 5) {
    Write-Error "PowerShell 5.1 or higher required"
    exit 1
}

# 2. 設定參數
$ServerUrl = "http://actual-server-url"  # 自動注入
$ClientId = if ($args.ClientId) { $args.ClientId } else { $env:COMPUTERNAME }

# 3. 下載客戶端
$clientScript = Invoke-WebRequest "$ServerUrl/client/download/windows"
$installPath = "$env:USERPROFILE\.brief-bridge\BriefBridgeClient.ps1"
New-Item -ItemType Directory -Force -Path (Split-Path $installPath)
Set-Content -Path $installPath -Value $clientScript.Content

# 4. 註冊為啟動項（可選）
if ($args.AutoStart) {
    # 加入到啟動項
}

# 5. 啟動客戶端
if ($args.Background) {
    Start-Process powershell -ArgumentList "-File $installPath -ServerUrl $ServerUrl -ClientId $ClientId" -WindowStyle Hidden
} else {
    & $installPath -ServerUrl $ServerUrl -ClientId $ClientId
}
```

### Tunnel 相依性

一鍵安裝功能需要：
1. **公開可訪問的 URL**
   - 本地開發：使用 ngrok 或類似服務
   - 生產環境：使用實際域名

2. **Tunnel 設定端點**
   - `GET /tunnel/status` - 獲取當前 tunnel 狀態
   - `POST /tunnel/setup` - 設定 tunnel（開發環境）
   - 返回公開 URL 供安裝使用

3. **安裝 URL 生成**
   ```python
   @router.get("/install-url")
   async def get_install_url():
       public_url = await get_public_url()  # 從 tunnel 或配置獲取
       return {
           "powershell": f"{public_url}/install.ps1",
           "bash": f"{public_url}/install.sh",
           "instructions": {
               "windows": f'iex ((Invoke-WebRequest "{public_url}/install.ps1").Content)',
               "linux": f'curl -sSL {public_url}/install.sh | bash'
           }
       }
   ```

## 實作優先級

### Phase 1: 基礎安裝腳本
- [ ] 實作 `/install.ps1` 端點
- [ ] 實作 `/install.sh` 端點
- [ ] 動態生成包含伺服器 URL 的腳本

### Phase 2: 客戶端下載機制
- [ ] 實作 `/client/download/{platform}` 端點
- [ ] 支援不同平台的客戶端版本

### Phase 3: Tunnel 整合
- [ ] 實作 tunnel 設定功能
- [ ] 自動獲取公開 URL
- [ ] 生成完整安裝指令

### Phase 4: 進階功能
- [ ] 自動啟動設定
- [ ] 客戶端更新機制
- [ ] 卸載功能

## 成功指標

1. **安裝時間**: 從執行命令到客戶端運行 < 30 秒
2. **成功率**: > 95% 的安裝應該成功
3. **跨平台**: 支援 Windows, Linux, macOS
4. **易用性**: 一行命令完成所有設定

## 風險與緩解

1. **風險**: 網路連線問題導致下載失敗
   - **緩解**: 加入重試機制和離線安裝選項

2. **風險**: 權限問題阻止安裝
   - **緩解**: 提供使用者層級和系統層級安裝選項

3. **風險**: 防火牆阻擋連線
   - **緩解**: 清楚的錯誤訊息和故障排除指南

## 使用範例

### 開發環境
```bash
# 1. 啟動伺服器並設定 tunnel
python main.py --enable-tunnel

# 2. 獲取安裝 URL
curl http://localhost:8000/install-url

# 3. 在目標機器執行安裝
iex ((Invoke-WebRequest 'https://abc123.ngrok.io/install.ps1').Content)
```

### 生產環境
```bash
# 使用實際域名
iex ((Invoke-WebRequest 'https://brief-bridge.example.com/install.ps1').Content)
```

## 相關文件
- [PowerShell Integration Research](../powershell-integration-research.md)
- [Cross-Platform Client Strategy](../archive/cross-platform-client-strategy.md)
- [Submit Command Use Case](./submit_command_use_case.md)