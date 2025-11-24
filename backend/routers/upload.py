# API Router: File Upload and OCR

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from pathlib import Path
from schemas.models import FileUploadResponse, OCRResult
from services.file_upload_service import FileUploadService
from core.logging import logger

router = APIRouter(prefix="/api/upload", tags=["file-upload"])


async def get_upload_service() -> FileUploadService:
    """Dependency for file upload service"""
    return FileUploadService()


@router.post("/file", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = None,
    upload_service: FileUploadService = Depends(get_upload_service)
):
    """
    Upload file for processing
    
    Args:
        file: File to upload
        user_id: ID of user uploading file
        
    Returns:
        FileUploadResponse with file metadata and ID
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required"
            )
        
        logger.info(f"File upload started by user {user_id}: {file.filename}")
        
        # Create temporary file path
        temp_file = Path(f"/tmp/{file.filename}")
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Upload and validate
        response = await upload_service.upload_file(user_id, temp_file, file.filename)
        
        logger.info(f"File uploaded successfully: {file.filename} (ID: {response.file_id})")
        return response
        
    except Exception as e:
        logger.error(f"File upload failed for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/ocr/{file_id}", response_model=OCRResult)
async def process_ocr(
    file_id: str,
    user_id: int,
    upload_service: FileUploadService = Depends(get_upload_service)
):
    """
    Process file with OCR to extract text
    
    Args:
        file_id: ID of uploaded file
        user_id: ID of user (verify ownership)
        
    Returns:
        OCRResult with extracted text and confidence
    """
    try:
        logger.info(f"OCR processing started for file {file_id}")
        
        result = await upload_service.process_ocr(file_id, user_id)
        
        logger.info(f"OCR processing completed for file {file_id}")
        return result
        
    except Exception as e:
        logger.error(f"OCR processing failed for file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OCR processing failed"
        )


@router.get("/ocr/{file_id}", response_model=OCRResult)
async def get_ocr_result(
    file_id: str,
    user_id: int,
    upload_service: FileUploadService = Depends(get_upload_service)
):
    """
    Get OCR result for uploaded file
    
    Args:
        file_id: ID of uploaded file
        user_id: ID of user
        
    Returns:
        OCRResult with extracted text
    """
    try:
        logger.info(f"Retrieving OCR result for file {file_id}")
        
        result = await upload_service.get_ocr_result(file_id, user_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OCR result for file {file_id} not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve OCR result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve OCR result"
        )


@router.delete("/file/{file_id}")
async def delete_file(
    file_id: str,
    user_id: int,
    upload_service: FileUploadService = Depends(get_upload_service)
):
    """
    Delete uploaded file
    
    Args:
        file_id: ID of file to delete
        user_id: ID of user (verify ownership)
    """
    try:
        logger.info(f"Deleting file {file_id} for user {user_id}")
        
        # TODO: Implement delete logic in FileUploadService
        # await upload_service.delete_file(file_id, user_id)
        
        return {"success": True, "message": f"File {file_id} deleted"}
        
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )
