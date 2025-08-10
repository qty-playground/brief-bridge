# Brief Bridge AI 使用建議

## 🎯 工作流程選擇指南

### 何時使用簡單命令工作流程？
- ✅ 單次執行的簡單任務
- ✅ 結果檔案 < 10MB
- ✅ 命令邏輯 < 200 字符
- ✅ 範例：截圖、系統資訊、單一日誌檔案

### 何時使用複雜腳本工作流程？
- ✅ 多步驟複雜邏輯
- ✅ 需要錯誤處理和重試機制
- ✅ 命令邏輯 > 200 字符  
- ✅ 範例：系統診斷、資料庫備份、軟體安裝

### 何時使用批次處理工作流程？
- ✅ 多台機器相同任務
- ✅ 需要腳本重複使用
- ✅ 集中分析多個結果
- ✅ 範例：叢集監控、批次更新、統一配置

## 📋 實用 AI 工作建議

### 1. 遠程截圖任務
**建議使用：** 簡單命令工作流程

```bash
# AI 執行步驟
curl -X POST http://localhost:2266/commands/submit \
  -H "Content-Type: application/json" \
  -d '{
    "target_client_id": "user-laptop",
    "command_content": "Add-Type -AssemblyName System.Windows.Forms,System.Drawing; $s=[System.Windows.Forms.SystemInformation]::VirtualScreen; $b=New-Object System.Drawing.Bitmap $s.Width,$s.Height; $g=[System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0,0,0,0,$s.Size); $f=\"$env:TEMP\\\\$(Get-Date -Format yyyyMMdd_HHmmss)_screenshot.png\"; $b.Save($f,[System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $b.Dispose(); $r=Invoke-RestMethod -Uri \"TUNNEL_URL/files/upload\" -Method POST -Form @{file=Get-Item $f; client_id=$env:COMPUTERNAME}; Remove-Item $f -Force; Write-Output \"SCREENSHOT_UPLOADED: $($r.file_id)\"",
    "command_type": "shell"
  }'

# 從結果提取 file_id，然後下載
curl http://localhost:2266/files/download/{file_id} > screenshot_$(date +%Y%m%d_%H%M%S).png
```

### 2. 系統診斷報告
**建議使用：** 複雜腳本工作流程

**步驟 1：準備診斷腳本 (diagnostic_script.ps1)**
```powershell
param([string]$ServerUrl, [string]$ClientId)

Write-Output "Starting system diagnostic..."

# 收集系統資訊
$systemInfo = @{
    ComputerName = $env:COMPUTERNAME
    OSVersion = [System.Environment]::OSVersion.ToString()
    TotalMemory = (Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory
    FreeMemory = (Get-WmiObject Win32_OperatingSystem).FreePhysicalMemory * 1KB
    CPUInfo = Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores
    DiskInfo = Get-WmiObject Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace
    RunningProcesses = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet
    NetworkAdapters = Get-WmiObject Win32_NetworkAdapter | Where-Object {$_.NetConnectionStatus -eq 2} | Select-Object Name, MACAddress
    EventLogErrors = Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2} -MaxEvents 50 | Select-Object TimeCreated, LevelDisplayName, Id, TaskDisplayName, Message
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

# 轉換為 JSON 並儲存
$jsonReport = $systemInfo | ConvertTo-Json -Depth 3
$reportPath = "$env:TEMP\\diagnostic_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$jsonReport | Out-File -FilePath $reportPath -Encoding UTF8

Write-Output "Diagnostic complete. Report saved to: $reportPath"

# 上傳報告
try {
    $uploadResponse = Invoke-RestMethod -Uri "$ServerUrl/files/upload" -Method POST -Form @{
        file = Get-Item $reportPath
        client_id = $ClientId
    }
    
    Remove-Item $reportPath -Force
    Write-Output "DIAGNOSTIC_UPLOADED: $($uploadResponse.file_id)"
    
} catch {
    Write-Output "UPLOAD_FAILED: $($_.Exception.Message)"
}
```

**步驟 2：AI 執行診斷**
```bash
# 1. 上傳診斷腳本
curl -X POST http://localhost:2266/files/upload \
  -F "file=@diagnostic_script.ps1" \
  -F "client_id=ai-assistant"
# 假設回應：{"file_id": "diag-script-123"}

# 2. 執行診斷
curl -X POST http://localhost:2266/commands/submit \
  -H "Content-Type: application/json" \
  -d '{
    "target_client_id": "production-server",
    "command_content": "$s=Invoke-WebRequest \"TUNNEL_URL/files/download/diag-script-123\"; $sb=[ScriptBlock]::Create($s.Content); & $sb -ServerUrl \"TUNNEL_URL\" -ClientId $env:COMPUTERNAME",
    "command_type": "shell"
  }'

# 3. 下載診斷報告（假設回應包含：DIAGNOSTIC_UPLOADED: report-456）
curl http://localhost:2266/files/download/report-456 > diagnostic_report.json

# 4. 清理檔案
curl -X DELETE http://localhost:2266/files/diag-script-123
curl -X DELETE http://localhost:2266/files/report-456
```

### 3. 批次日誌收集
**建議使用：** 批次處理工作流程

**步驟 1：準備日誌收集腳本 (log_collector.ps1)**
```powershell
param([string]$ServerUrl, [string]$ClientId, [string]$LogType = "Application", [int]$Hours = 24)

Write-Output "Collecting $LogType logs from last $Hours hours..."

try {
    $startTime = (Get-Date).AddHours(-$Hours)
    $logs = Get-WinEvent -FilterHashtable @{
        LogName = $LogType
        StartTime = $startTime
    } -MaxEvents 1000 | Select-Object TimeCreated, LevelDisplayName, Id, TaskDisplayName, Message
    
    $logData = @{
        ClientId = $env:COMPUTERNAME
        LogType = $LogType
        TimeRange = "$Hours hours"
        CollectedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        TotalEntries = $logs.Count
        Logs = $logs
    }
    
    $jsonLogs = $logData | ConvertTo-Json -Depth 4 -Compress
    $logPath = "$env:TEMP\\${LogType}_logs_${env:COMPUTERNAME}_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $jsonLogs | Out-File -FilePath $logPath -Encoding UTF8
    
    # 上傳日誌
    $uploadResponse = Invoke-RestMethod -Uri "$ServerUrl/files/upload" -Method POST -Form @{
        file = Get-Item $logPath
        client_id = $env:COMPUTERNAME
    }
    
    Remove-Item $logPath -Force
    Write-Output "LOGS_UPLOADED: $($uploadResponse.file_id)"
    
} catch {
    Write-Output "LOG_COLLECTION_FAILED: $($_.Exception.Message)"
}
```

**步驟 2：AI 批次執行**
```bash
# 1. 上傳日誌收集腳本（一次）
curl -X POST http://localhost:2266/files/upload \
  -F "file=@log_collector.ps1" \
  -F "client_id=ai-assistant"
# 回應：{"file_id": "log-script-789"}

# 2. 對多台機器執行（並行）
for client in server-01 server-02 server-03 workstation-01; do
  curl -X POST http://localhost:2266/commands/submit \
    -H "Content-Type: application/json" \
    -d "{
      \"target_client_id\": \"$client\",
      \"command_content\": \"\$s=Invoke-WebRequest 'TUNNEL_URL/files/download/log-script-789'; \$sb=[ScriptBlock]::Create(\$s.Content); & \$sb -ServerUrl 'TUNNEL_URL' -ClientId \$env:COMPUTERNAME -LogType 'System' -Hours 48\",
      \"command_type\": \"shell\"
    }" &
done
wait

# 3. 收集所有日誌檔案
curl http://localhost:2266/files/ | jq -r '.files[] | select(.client_id | contains("server") or contains("workstation")) | .file_id' > log_file_ids.txt

# 4. 下載所有日誌
mkdir -p collected_logs
while read file_id; do
  curl http://localhost:2266/files/download/$file_id > collected_logs/log_$file_id.json
done < log_file_ids.txt

# 5. 清理所有檔案
curl -X DELETE http://localhost:2266/files/log-script-789
while read file_id; do
  curl -X DELETE http://localhost:2266/files/$file_id
done < log_file_ids.txt
```

## 💡 最佳實踐建議

### 1. 錯誤處理模式
```powershell
# 在腳本中總是包含錯誤處理
try {
    # 主要邏輯
    $result = Invoke-SomeOperation
    Write-Output "SUCCESS: Operation completed"
} catch {
    Write-Output "ERROR: $($_.Exception.Message)"
    Write-Output "STACK_TRACE: $($_.ScriptStackTrace)"
}
```

### 2. 檔案 ID 提取
```bash
# 使用 jq 提取檔案 ID
response=$(curl -X POST http://localhost:2266/commands/submit -d '...')
file_id=$(echo "$response" | jq -r '.result' | grep -oE '[a-f0-9-]{36}' | head -1)
```

### 3. 批次操作模式
```bash
# 並行執行多個命令
client_ids=("client1" "client2" "client3")
for client_id in "${client_ids[@]}"; do
  execute_command "$client_id" &
done
wait  # 等待所有任務完成
```

### 4. 資源清理策略
```bash
# 定期清理 AI 上傳的腳本檔案
cleanup_ai_files() {
  curl http://localhost:2266/files/ | \
  jq -r '.files[] | select(.client_id == "ai-assistant") | .file_id' | \
  xargs -I {} curl -X DELETE http://localhost:2266/files/{}
}
```

## 🚨 注意事項

### 安全注意事項
1. **敏感資料處理：** 避免在命令中包含密碼或 API 金鑰
2. **檔案清理：** 執行完成後立即清理敏感檔案
3. **權限控制：** 確認客戶端執行權限符合最小權限原則

### 效能注意事項
1. **檔案大小限制：** 單檔建議 < 100MB
2. **並發控制：** 避免同時大量檔案傳輸
3. **網路優化：** 大型檔案建議壓縮後傳輸

### 相容性注意事項
1. **PowerShell 版本：** 確保目標機器支援所需 PowerShell 版本
2. **模組依賴：** 檢查腳本所需的 PowerShell 模組是否可用
3. **執行策略：** 考慮目標機器的 PowerShell 執行策略設定

這些建議和範例應該能幫助 AI 更有效地使用 Brief Bridge 的檔案傳輸功能！