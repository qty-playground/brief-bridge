# Brief Bridge 文檔總覽

## 核心文檔

### 🎯 當前實作指南
- **[minimal-implementation-plan.md](minimal-implementation-plan.md)** - 最小實作計劃（2-3天可完成）
  - AI 等待結果機制
  - Client 結果提交
  - 單一命令執行保證

- **[async-execution-architecture.md](async-execution-architecture.md)** - 異步執行架構設計
  - 完整的執行流程圖
  - Server 端等待機制
  - 錯誤處理策略

### 📚 研究與參考
- **[powershell-integration-research.md](powershell-integration-research.md)** - ws-call PowerShell 原型研究
  - ws-call 架構分析
  - PowerShell 客戶端實現
  - 一鍵安裝機制
  - API 設計參考

### 🗓️ 長期規劃
- **[implementation-phases.md](implementation-phases.md)** - 分階段實施計劃
  - Phase 1-2: 核心功能（P0優先）
  - Phase 3-4: 跨平台支援（P1）
  - Phase 5-7: 生產功能（P2-P3）

### 📋 產品規格
- **[prd-zh-tw.md](prd-zh-tw.md)** - 產品需求文檔（中文）
  - 專案背景與目標
  - 功能需求
  - 技術架構

### 🏗️ 架構設計
- **[architecture-options/README.md](architecture-options/README.md)** - 架構選項評估
  - Simplified Architecture 設計
  - 依賴注入模式

### 📖 使用案例
- **[user-stories/](user-stories/)** - 使用者故事
  - [register_client_use_case.md](user-stories/register_client_use_case.md) - 客戶端註冊
  - [submit_command_use_case.md](user-stories/submit_command_use_case.md) - 命令提交

## 快速開始

### 下一步行動（最優先）
1. 閱讀 [minimal-implementation-plan.md](minimal-implementation-plan.md) 了解 2-3 天實作計劃
2. 參考 [async-execution-architecture.md](async-execution-architecture.md) 了解完整架構
3. 查看 [powershell-integration-research.md](powershell-integration-research.md) 了解 ws-call 研究成果

### 長期規劃
參考 [implementation-phases.md](implementation-phases.md) 了解完整的產品演進路線圖。

## 歸檔文檔
舊版或過時的文檔已移至 `archive/` 目錄。