"""
Nextcloud file management endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import os
import logging
from typing import Optional

from backend.nextcloud import NextcloudClient, get_nextcloud_client

router = APIRouter(prefix="/api/files", tags=["files"])
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_to_nextcloud(
    file: UploadFile = File(...),
    remote_path: str = "/",
    client: NextcloudClient = Depends(get_nextcloud_client)
) -> dict:
    """
    Upload a file to Nextcloud.

    Args:
        file: File to upload
        remote_path: Target path in Nextcloud (e.g., /Documents/myfile.pdf)

    Returns:
        Success status and file info
    """
    try:
        # Save file temporarily
        temp_path = f"/tmp/{file.filename}"
        os.makedirs("/tmp", exist_ok=True)

        with open(temp_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # Upload to Nextcloud
        success = client.upload_file(temp_path, remote_path)

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if success:
            return {
                "status": "success",
                "message": f"File uploaded to {remote_path}",
                "filename": file.filename,
                "remote_path": remote_path
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upload file to Nextcloud")

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/download")
async def download_from_nextcloud(
    remote_path: str,
    client: NextcloudClient = Depends(get_nextcloud_client)
):
    """
    Download a file from Nextcloud.

    Args:
        remote_path: Path in Nextcloud (e.g., /Documents/myfile.pdf)

    Returns:
        File content
    """
    try:
        # Download to temporary location
        temp_path = f"/tmp/download_{os.path.basename(remote_path)}"
        os.makedirs("/tmp", exist_ok=True)

        success = client.download_file(remote_path, temp_path)

        if success and os.path.exists(temp_path):
            return FileResponse(
                path=temp_path,
                filename=os.path.basename(remote_path),
                media_type='application/octet-stream'
            )
        else:
            raise HTTPException(status_code=404, detail="File not found or download failed")

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.post("/folder")
async def create_folder(
    folder_path: str,
    client: NextcloudClient = Depends(get_nextcloud_client)
) -> dict:
    """
    Create a folder in Nextcloud.

    Args:
        folder_path: Path for new folder (e.g., /Documents/NewFolder/)

    Returns:
        Success status
    """
    try:
        if not folder_path.endswith("/"):
            folder_path += "/"

        success = client.create_folder(folder_path)

        if success:
            return {
                "status": "success",
                "message": f"Folder created: {folder_path}",
                "folder_path": folder_path
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create folder")

    except Exception as e:
        logger.error(f"Folder creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/file")
async def delete_file(
    remote_path: str,
    client: NextcloudClient = Depends(get_nextcloud_client)
) -> dict:
    """
    Delete a file from Nextcloud.

    Args:
        remote_path: Path in Nextcloud (e.g., /Documents/file.pdf)

    Returns:
        Success status
    """
    try:
        success = client.delete_file(remote_path)

        if success:
            return {
                "status": "success",
                "message": f"File deleted: {remote_path}",
                "remote_path": remote_path
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete file")

    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
