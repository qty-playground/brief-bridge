# User Story: Tunnel Setup Use Case

## 故事描述

作為一個 Brief Bridge 系統管理員，
我希望能輕鬆設定公開可訪問的 URL（透過 tunnel 服務），
這樣遠端客戶端就能連接到我的本地開發伺服器，支援一鍵安裝和遠端部署。

## 背景說明

Brief Bridge 伺服器通常運行在：
1. 本地開發環境 (localhost:8000)
2. 內部網路環境
3. 防火牆後方

為了讓外部客戶端能夠連接，我們需要：
- 公開可訪問的 URL
- 自動的 tunnel 設定
- 簡單的配置流程

## 驗收標準

### Scenario 1: 自動 Tunnel 設定 (ngrok)
```gherkin
Given Brief Bridge 伺服器正在本地運行
And ngrok 已安裝在系統中
When 管理員啟動伺服器時加入 --enable-tunnel 參數：
  """
  python main.py --enable-tunnel
  """
Then 系統應該自動啟動 ngrok tunnel
And 應該顯示公開 URL：
  """
  Tunnel established: https://abc123.ngrok.io
  Install URL: https://abc123.ngrok.io/install.ps1
  """
And API 應該可透過公開 URL 訪問
```

### Scenario 2: 手動 Tunnel 設定
```gherkin
Given Brief Bridge 伺服器正在運行
When 管理員呼叫 tunnel 設定 API：
  """
  POST /tunnel/setup
  {
    "provider": "ngrok",
    "auth_token": "optional-auth-token"
  }
  """
Then 系統應該啟動指定的 tunnel 服務
And 回應應該包含：
  """
  {
    "status": "active",
    "public_url": "https://abc123.ngrok.io",
    "provider": "ngrok",
    "install_urls": {
      "powershell": "https://abc123.ngrok.io/install.ps1",
      "bash": "https://abc123.ngrok.io/install.sh"
    }
  }
  """
```

### Scenario 3: 使用自定義域名
```gherkin
Given 管理員有自己的域名和 SSL 憑證
When 管理員設定自定義 tunnel：
  """
  POST /tunnel/setup
  {
    "provider": "custom",
    "public_url": "https://brief-bridge.example.com"
  }
  """
Then 系統應該使用提供的 URL
And 不應該啟動任何 tunnel 服務
And 安裝 URL 應該使用自定義域名
```

### Scenario 4: Cloudflare Tunnel 設定
```gherkin
Given 管理員有 Cloudflare 帳號
When 管理員設定 Cloudflare tunnel：
  """
  POST /tunnel/setup
  {
    "provider": "cloudflare",
    "config": {
      "tunnel_name": "brief-bridge-tunnel",
      "credentials": "..."
    }
  }
  """
Then 系統應該設定 Cloudflare tunnel
And 提供穩定的公開 URL
```

### Scenario 5: 獲取當前 Tunnel 狀態
```gherkin
Given Tunnel 已經設定並運行
When 管理員查詢 tunnel 狀態：
  """
  GET /tunnel/status
  """
Then 回應應該顯示：
  """
  {
    "active": true,
    "provider": "ngrok",
    "public_url": "https://abc123.ngrok.io",
    "uptime": 3600,
    "connections": 5,
    "install_commands": {
      "windows": "iex ((Invoke-WebRequest 'https://abc123.ngrok.io/install.ps1').Content)",
      "linux": "curl -sSL https://abc123.ngrok.io/install.sh | bash"
    }
  }
  """
```

### Scenario 6: Tunnel 斷線重連
```gherkin
Given Tunnel 正在運行
When Tunnel 連線中斷
Then 系統應該自動嘗試重連
And 如果重連失敗應該：
  - 記錄錯誤
  - 發送通知（如果設定）
  - 嘗試備用 tunnel 服務
```

### Scenario 7: 多個 Tunnel 提供者容錯
```gherkin
Given 系統配置了多個 tunnel 提供者優先順序：
  1. ngrok
  2. cloudflare
  3. localtunnel
When 主要 tunnel 服務失敗
Then 系統應該自動切換到下一個可用的服務
And 更新所有相關的 URL
```

## 技術需求

### Tunnel 管理模組

```python
# brief_bridge/tunnel/tunnel_manager.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class TunnelProvider(ABC):
    @abstractmethod
    async def setup(self, config: Dict[str, Any]) -> str:
        """設定 tunnel 並返回公開 URL"""
        pass
    
    @abstractmethod
    async def teardown(self) -> None:
        """關閉 tunnel"""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """獲取 tunnel 狀態"""
        pass

class NgrokProvider(TunnelProvider):
    async def setup(self, config: Dict[str, Any]) -> str:
        # 啟動 ngrok
        # 返回公開 URL
        pass

class CloudflareProvider(TunnelProvider):
    async def setup(self, config: Dict[str, Any]) -> str:
        # 設定 Cloudflare tunnel
        pass

class TunnelManager:
    def __init__(self):
        self.providers = {
            "ngrok": NgrokProvider(),
            "cloudflare": CloudflareProvider(),
            "custom": CustomProvider()
        }
        self.active_provider: Optional[TunnelProvider] = None
        self.public_url: Optional[str] = None
    
    async def setup_tunnel(self, provider: str, config: Dict[str, Any]) -> str:
        """設定指定的 tunnel 提供者"""
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        if self.active_provider:
            await self.active_provider.teardown()
        
        self.active_provider = self.providers[provider]
        self.public_url = await self.active_provider.setup(config)
        return self.public_url
```

### API 端點

```python
# brief_bridge/web/tunnel_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/tunnel", tags=["tunnel"])

class TunnelSetupRequest(BaseModel):
    provider: str  # ngrok, cloudflare, custom
    config: Optional[Dict[str, Any]] = {}
    public_url: Optional[str] = None  # for custom provider

class TunnelStatusResponse(BaseModel):
    active: bool
    provider: Optional[str]
    public_url: Optional[str]
    uptime: Optional[int]
    connections: Optional[int]
    install_commands: Optional[Dict[str, str]]

@router.post("/setup")
async def setup_tunnel(request: TunnelSetupRequest):
    """設定 tunnel 服務"""
    manager = get_tunnel_manager()
    
    try:
        public_url = await manager.setup_tunnel(
            provider=request.provider,
            config=request.config or {}
        )
        
        return {
            "status": "active",
            "public_url": public_url,
            "provider": request.provider,
            "install_urls": {
                "powershell": f"{public_url}/install.ps1",
                "bash": f"{public_url}/install.sh"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_tunnel_status():
    """獲取當前 tunnel 狀態"""
    manager = get_tunnel_manager()
    
    if not manager.active_provider:
        return TunnelStatusResponse(active=False)
    
    status = await manager.active_provider.get_status()
    
    return TunnelStatusResponse(
        active=True,
        provider=manager.active_provider.__class__.__name__.replace("Provider", "").lower(),
        public_url=manager.public_url,
        install_commands={
            "windows": f"iex ((Invoke-WebRequest '{manager.public_url}/install.ps1').Content)",
            "linux": f"curl -sSL {manager.public_url}/install.sh | bash"
        } if manager.public_url else None,
        **status
    )

@router.delete("/teardown")
async def teardown_tunnel():
    """關閉當前 tunnel"""
    manager = get_tunnel_manager()
    
    if manager.active_provider:
        await manager.active_provider.teardown()
        manager.active_provider = None
        manager.public_url = None
    
    return {"status": "stopped"}
```

### 配置檔案支援

```yaml
# config/tunnel.yaml
tunnel:
  auto_start: true
  provider: ngrok
  fallback_providers:
    - cloudflare
    - localtunnel
  
  ngrok:
    auth_token: ${NGROK_AUTH_TOKEN}
    region: us
    
  cloudflare:
    tunnel_name: brief-bridge
    credentials_file: /path/to/credentials.json
    
  custom:
    public_url: https://brief-bridge.example.com
```

### 啟動參數

```python
# main.py
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--enable-tunnel', action='store_true',
                       help='Enable tunnel for public access')
    parser.add_argument('--tunnel-provider', default='ngrok',
                       help='Tunnel provider (ngrok, cloudflare, custom)')
    parser.add_argument('--tunnel-config', type=str,
                       help='Path to tunnel configuration file')
    
    args = parser.parse_args()
    
    if args.enable_tunnel:
        # 自動設定 tunnel
        tunnel_manager = TunnelManager()
        public_url = await tunnel_manager.setup_tunnel(
            provider=args.tunnel_provider,
            config=load_config(args.tunnel_config) if args.tunnel_config else {}
        )
        
        print(f"Tunnel established: {public_url}")
        print(f"Install URL (Windows): iex ((Invoke-WebRequest '{public_url}/install.ps1').Content)")
        print(f"Install URL (Linux): curl -sSL {public_url}/install.sh | bash")
    
    # 啟動 FastAPI 伺服器
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 實作優先級

### Phase 1: 基礎 Tunnel 功能
- [ ] 實作 TunnelProvider 介面
- [ ] 實作 NgrokProvider
- [ ] 實作基本 API 端點

### Phase 2: 整合與自動化
- [ ] 整合到主程式啟動流程
- [ ] 自動重連機制
- [ ] 狀態監控

### Phase 3: 多提供者支援
- [ ] Cloudflare Tunnel 支援
- [ ] LocalTunnel 支援
- [ ] 容錯切換機制

### Phase 4: 進階功能
- [ ] Webhook 通知
- [ ] 流量監控
- [ ] 自動 SSL 憑證

## 成功指標

1. **設定時間**: < 10 秒完成 tunnel 設定
2. **穩定性**: > 99% uptime
3. **延遲**: < 200ms 額外延遲
4. **易用性**: 一個命令或 API 呼叫完成設定

## 風險與緩解

1. **風險**: Tunnel 服務不穩定
   - **緩解**: 實作多個提供者和自動切換

2. **風險**: 免費 tunnel 服務限制
   - **緩解**: 支援付費計劃和自定義域名

3. **風險**: 安全性問題
   - **緩解**: 實作認證機制和 IP 白名單

## 相關文件
- [One-Click Install Use Case](./one_click_install_use_case.md)
- [Submit Command Use Case](./submit_command_use_case.md)
- [PowerShell Integration Research](../powershell-integration-research.md)