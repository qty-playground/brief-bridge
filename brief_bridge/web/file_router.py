"""File upload/download router for Brief Bridge"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import FileResponse
from typing import Optional
import os
import uuid
import shutil
from pathlib import Path

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/files/upload",
            summary="Upload File",
            description="Upload a file from client to server. Returns a file ID that can be used to download the file.",
            tags=["files"])
async def upload_file(
    file: UploadFile = File(...),
    client_id: Optional[str] = Form(None, description="Client ID that uploaded this file")
):
    """Upload a file to the server"""
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix if file.filename else ""
        safe_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store metadata (could be enhanced with a proper database)
        metadata_path = UPLOAD_DIR / f"{file_id}.meta"
        with open(metadata_path, "w") as meta_file:
            meta_file.write(f"original_name={file.filename or 'unknown'}\n")
            meta_file.write(f"client_id={client_id or 'unknown'}\n")
            meta_file.write(f"content_type={file.content_type or 'unknown'}\n")
            meta_file.write(f"size={file.size or 0}\n")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": file.size,
            "content_type": file.content_type,
            "client_id": client_id,
            "status": "uploaded"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/files/download/{file_id}",
           summary="Download File",
           description="Download a file by its file ID",
           tags=["files"])
async def download_file(file_id: str):
    """Download a file by file ID"""
    try:
        # Find file with this ID
        file_path = None
        for file in UPLOAD_DIR.glob(f"{file_id}.*"):
            if not file.name.endswith(".meta"):
                file_path = file
                break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get original filename from metadata
        metadata_path = UPLOAD_DIR / f"{file_id}.meta"
        original_name = "download"
        
        if metadata_path.exists():
            with open(metadata_path, "r") as meta_file:
                for line in meta_file:
                    if line.startswith("original_name="):
                        original_name = line.split("=", 1)[1].strip()
                        break
        
        return FileResponse(
            path=file_path,
            filename=original_name,
            media_type="application/octet-stream"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/files/",
           summary="List Files",
           description="List all uploaded files",
           tags=["files"])
async def list_files():
    """List all uploaded files"""
    try:
        files = []
        
        for meta_file in UPLOAD_DIR.glob("*.meta"):
            file_id = meta_file.stem
            
            # Read metadata
            metadata = {}
            with open(meta_file, "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        metadata[key] = value
            
            # Check if actual file exists
            file_exists = False
            actual_file_path = None
            for file_path in UPLOAD_DIR.glob(f"{file_id}.*"):
                if not file_path.name.endswith(".meta"):
                    file_exists = True
                    actual_file_path = file_path
                    break
            
            if file_exists:
                files.append({
                    "file_id": file_id,
                    "filename": metadata.get("original_name", "unknown"),
                    "client_id": metadata.get("client_id", "unknown"),
                    "content_type": metadata.get("content_type", "unknown"),
                    "size": int(metadata.get("size", 0)),
                    "file_path": str(actual_file_path)
                })
        
        return {
            "files": files,
            "total_count": len(files)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@router.delete("/files/{file_id}",
              summary="Delete File",
              description="Delete a file by its file ID",
              tags=["files"])
async def delete_file(file_id: str):
    """Delete a file by file ID"""
    try:
        deleted_files = []
        
        # Delete all files with this ID (including metadata)
        for file_path in UPLOAD_DIR.glob(f"{file_id}.*"):
            if file_path.exists():
                file_path.unlink()
                deleted_files.append(str(file_path))
        
        if not deleted_files:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "file_id": file_id,
            "deleted_files": deleted_files,
            "status": "deleted"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")