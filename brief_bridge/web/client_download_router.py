"""Client download router for serving client scripts"""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
import os

router = APIRouter()


@router.get("/client/download/windows", 
           response_class=PlainTextResponse,
           summary="Download Windows PowerShell Client", 
           description="Download the Brief Bridge PowerShell client script for Windows with base64 support",
           tags=["client-download"])
async def download_windows_client():
    """Download Windows PowerShell client script"""
    
    # Read the PowerShell client script from the windows-client directory
    script_path = os.path.join(os.path.dirname(__file__), "..", "..", "windows-client", "BriefBridgeClient.ps1")
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        return script_content
    except FileNotFoundError:
        # Fallback: return a basic script if file not found
        return """# Brief Bridge Client - Base64 Support
Write-Host "Error: Client script not found. Please contact support." -ForegroundColor Red
exit 1
"""