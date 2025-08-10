"""Real ngrok tunnel manager using pyngrok library"""
import logging
import asyncio
import os
from typing import Optional
from pyngrok import ngrok, conf
from pyngrok.exception import PyngrokError

logger = logging.getLogger(__name__)


class NgrokManager:
    """Manages ngrok tunnel lifecycle and provides public URL."""
    
    def __init__(self, port: Optional[int] = None, auth_token: Optional[str] = None):
        self.port = port  # Will be dynamically determined if None
        self.tunnel = None
        self.public_url: Optional[str] = None
        
        # Set auth token if provided
        if auth_token:
            conf.get_default().auth_token = auth_token
        elif os.getenv("NGROK_AUTHTOKEN"):
            conf.get_default().auth_token = os.getenv("NGROK_AUTHTOKEN")
        # If no explicit token, pyngrok will use the system config
    
    def _get_server_port(self) -> int:
        """Dynamically determine the current server port"""
        if self.port:
            return self.port
            
        # Try to get port from environment variable
        env_port = os.getenv("BRIEF_BRIDGE_PORT")
        if env_port:
            return int(env_port)
            
        # Try to detect from running uvicorn process
        try:
            import psutil
            import re
            
            for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if process.info['name'] and 'python' in process.info['name'].lower():
                        cmdline = ' '.join(process.info['cmdline'] or [])
                        if 'uvicorn' in cmdline and 'brief_bridge.main:app' in cmdline:
                            # Look for --port argument
                            port_match = re.search(r'--port\s+(\d+)', cmdline)
                            if port_match:
                                return int(port_match.group(1))
                            # Look for :port pattern
                            host_port_match = re.search(r'127\.0\.0\.1:(\d+)', cmdline)
                            if host_port_match:
                                return int(host_port_match.group(1))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            logger.warning("psutil not available, cannot auto-detect port")
        except Exception as e:
            logger.warning(f"Failed to auto-detect port: {e}")
            
        # Default fallback
        logger.warning("Could not detect server port, using default 2266")
        return 2266
    
    async def start_tunnel(self) -> str:
        """Start ngrok tunnel and return public URL."""
        try:
            # Dynamically determine port
            actual_port = self._get_server_port()
            logger.info(f"Starting ngrok tunnel for port {actual_port}")
            
            # Start tunnel in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.tunnel = await loop.run_in_executor(
                None, 
                lambda: ngrok.connect(actual_port, "http")
            )
            
            self.public_url = self.tunnel.public_url
            logger.info(f"Ngrok tunnel started: {self.public_url}")
            
            return self.public_url
            
        except PyngrokError as e:
            logger.error(f"Failed to start ngrok tunnel: {e}")
            raise RuntimeError(f"Ngrok tunnel failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error starting ngrok tunnel: {e}")
            raise
    
    async def stop_tunnel(self):
        """Stop ngrok tunnel."""
        if self.tunnel:
            try:
                logger.info("Stopping ngrok tunnel")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, ngrok.disconnect, self.tunnel.public_url)
                self.tunnel = None
                self.public_url = None
                logger.info("Ngrok tunnel stopped")
            except Exception as e:
                logger.error(f"Error stopping ngrok tunnel: {e}")
    
    def get_public_url(self) -> Optional[str]:
        """Get the current public URL."""
        return self.public_url
    
    def is_active(self) -> bool:
        """Check if tunnel is active."""
        return self.tunnel is not None and self.public_url is not None
    
    async def get_tunnel_info(self) -> dict:
        """Get tunnel information."""
        if not self.is_active():
            return {"status": "inactive", "public_url": None}
        
        try:
            # Get tunnel info from ngrok API
            loop = asyncio.get_event_loop()
            tunnels = await loop.run_in_executor(None, ngrok.get_tunnels)
            
            active_tunnel = None
            for tunnel in tunnels:
                if tunnel.public_url == self.public_url:
                    active_tunnel = tunnel
                    break
            
            if active_tunnel:
                return {
                    "status": "active",
                    "public_url": active_tunnel.public_url,
                    "name": active_tunnel.name,
                    "proto": active_tunnel.proto,
                    "config": active_tunnel.config
                }
            else:
                return {"status": "error", "message": "Tunnel not found"}
                
        except Exception as e:
            logger.error(f"Error getting tunnel info: {e}")
            return {"status": "error", "message": str(e)}


class MockNgrokManager:
    """Mock ngrok manager for testing purposes"""
    
    def __init__(self, port: Optional[int] = None, auth_token: Optional[str] = None):
        self.port = port or 2266  # Default for mock
        self.public_url: Optional[str] = None
        self._is_active = False
    
    async def start_tunnel(self) -> str:
        """Mock start tunnel - returns fake URL"""
        import uuid
        subdomain = str(uuid.uuid4())[:8]
        self.public_url = f"https://{subdomain}.ngrok.io"
        self._is_active = True
        logger.info(f"Mock ngrok tunnel started: {self.public_url}")
        return self.public_url
    
    async def stop_tunnel(self):
        """Mock stop tunnel"""
        self.public_url = None
        self._is_active = False
        logger.info("Mock ngrok tunnel stopped")
    
    def get_public_url(self) -> Optional[str]:
        return self.public_url
    
    def is_active(self) -> bool:
        return self._is_active
    
    async def get_tunnel_info(self) -> dict:
        if not self.is_active():
            return {"status": "inactive", "public_url": None}
        return {
            "status": "active", 
            "public_url": self.public_url,
            "name": "mock-tunnel",
            "proto": "https",
            "config": {"addr": f"localhost:{self.port}"}
        }


async def cleanup_all_ngrok_tunnels():
    """Cleanup function to ensure all ngrok tunnels are properly stopped"""
    try:
        if os.getenv('BRIEF_BRIDGE_USE_MOCK_NGROK', '').lower() in ('true', '1', 'yes'):
            # Skip cleanup in mock mode
            logger.info("Skipping ngrok cleanup in mock mode")
            return
            
        # First try graceful cleanup via ngrok API
        try:
            loop = asyncio.get_event_loop()
            tunnels = await loop.run_in_executor(None, ngrok.get_tunnels)
            
            for tunnel in tunnels:
                try:
                    await loop.run_in_executor(None, ngrok.disconnect, tunnel.public_url)
                    logger.info(f"Gracefully disconnected tunnel: {tunnel.public_url}")
                except Exception as e:
                    logger.debug(f"Could not gracefully disconnect tunnel {tunnel.public_url}: {e}")
                    
        except Exception as e:
            logger.debug(f"Could not use ngrok API for cleanup: {e}")
        
        # Then ensure all ngrok processes are terminated
        import subprocess
        import time
        
        try:
            # Kill all ngrok processes
            result = subprocess.run(['pkill', '-f', 'ngrok'], check=False)
            if result.returncode == 0:
                logger.info("Ngrok processes terminated via pkill")
                # Give processes time to terminate
                time.sleep(0.5)
            else:
                logger.debug("No ngrok processes found to terminate")
        except Exception as e:
            logger.warning(f"Failed to kill ngrok processes via pkill: {e}")
            
    except Exception as e:
        logger.warning(f"Error during ngrok cleanup: {e}")
    finally:
        # Force kill any remaining ngrok daemon processes
        try:
            subprocess.run(['pkill', '-9', '-f', 'ngrok'], check=False)
        except Exception:
            pass


def create_ngrok_manager(use_mock: bool = None, port: Optional[int] = None) -> NgrokManager:
    """Factory function to create ngrok manager"""
    # Auto-detect if we should use mock (for testing)
    if use_mock is None:
        use_mock = os.getenv('BRIEF_BRIDGE_USE_MOCK_NGROK', '').lower() in ('true', '1', 'yes')
    
    if use_mock:
        return MockNgrokManager(port=port)
    else:
        return NgrokManager(port=port)