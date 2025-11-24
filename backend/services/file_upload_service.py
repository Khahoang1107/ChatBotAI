# Service Layer: File Upload and OCR Processing

from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime
import mimetypes
from core.exceptions import (
    ValidationException,
    ExternalServiceException,
    DatabaseException
)
from core.dependencies import container
from schemas.models import FileUploadResponse, OCRResult


class FileUploadService:
    """Handle file uploads and OCR processing"""
    
    def __init__(self):
        self.db = container.db
        self.settings = container.settings
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    async def upload_file(self, user_id: int, file_path: Path, filename: str) -> FileUploadResponse:
        """
        Upload file and validate
        
        Args:
            user_id: ID of user uploading file
            file_path: Path to uploaded file
            filename: Original filename
            
        Returns:
            FileUploadResponse with file metadata
            
        Raises:
            ValidationException: If file validation fails
            DatabaseException: If database operation fails
        """
        try:
            # Validate file
            self._validate_file(file_path, filename)
            
            # Get file size
            file_size = file_path.stat().st_size
            
            # Generate unique file ID
            file_id = f"{user_id}_{int(datetime.utcnow().timestamp())}"
            
            # Store file in upload directory
            upload_path = self.upload_dir / f"{file_id}_{filename}"
            file_path.rename(upload_path)
            
            # Store metadata in database
            # file_record = UploadedFile(
            #     user_id=user_id,
            #     file_id=file_id,
            #     filename=filename,
            #     file_size=file_size,
            #     file_path=str(upload_path),
            #     upload_at=datetime.utcnow()
            # )
            # self.db.add(file_record)
            # self.db.commit()
            
            return FileUploadResponse(
                file_id=file_id,
                filename=filename,
                file_size=file_size,
                upload_at=datetime.utcnow()
            )
            
        except ValidationException:
            raise
        except Exception as e:
            raise DatabaseException(f"File upload failed: {str(e)}")
    
    def _validate_file(self, file_path: Path, filename: str):
        """Validate file type and size"""
        # Check if file exists
        if not file_path.exists():
            raise ValidationException("File does not exist")
        
        # Check file size
        file_size = file_path.stat().st_size
        max_size = self.settings.MAX_UPLOAD_SIZE * 1024 * 1024  # Convert MB to bytes
        
        if file_size > max_size:
            raise ValidationException(
                f"File size {file_size / 1024 / 1024:.2f}MB exceeds limit of {self.settings.MAX_UPLOAD_SIZE}MB"
            )
        
        # Check file extension
        _, ext = Path(filename).suffix.lower(), Path(filename).suffix.lower()
        mime_type, _ = mimetypes.guess_type(filename)
        
        allowed_types = self.settings.ALLOWED_FILE_TYPES
        if ext.lstrip('.') not in allowed_types:
            raise ValidationException(
                f"File type {ext} not allowed. Allowed types: {', '.join(allowed_types)}"
            )
    
    async def process_ocr(self, file_id: str, user_id: int) -> OCRResult:
        """
        Process file with OCR
        
        Args:
            file_id: ID of uploaded file
            user_id: ID of user
            
        Returns:
            OCRResult with extracted text and confidence
            
        Raises:
            ResourceNotFoundException: If file not found
            ExternalServiceException: If OCR processing fails
        """
        try:
            # Get file from database
            # file_record = self.db.query(UploadedFile).filter(
            #     UploadedFile.file_id == file_id,
            #     UploadedFile.user_id == user_id
            # ).first()
            # if not file_record:
            #     raise ResourceNotFoundException(f"File {file_id} not found")
            
            # Call OCR service (Tesseract or Google Vision API)
            import time
            start_time = time.time()
            
            extracted_text, confidence = await self._extract_text_ocr(file_id)
            
            processing_time = time.time() - start_time
            
            # Store OCR result
            # ocr_result = OCRJobData(
            #     file_id=file_id,
            #     user_id=user_id,
            #     extracted_text=extracted_text,
            #     confidence=confidence,
            #     processing_time=processing_time,
            #     processed_at=datetime.utcnow()
            # )
            # self.db.add(ocr_result)
            # self.db.commit()
            
            return OCRResult(
                file_id=file_id,
                extracted_text=extracted_text,
                confidence=confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise ExternalServiceException(f"OCR processing failed: {str(e)}")
    
    async def _extract_text_ocr(self, file_id: str) -> Tuple[str, float]:
        """
        Extract text from file using OCR
        
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            # Implementation depends on OCR library (Tesseract, Google Vision, etc.)
            # Placeholder implementation
            return "Extracted text from file", 0.95
        except Exception as e:
            raise ExternalServiceException(f"OCR extraction failed: {str(e)}")
    
    async def get_ocr_result(self, file_id: str, user_id: int) -> OCRResult:
        """Retrieve OCR result for file"""
        try:
            # ocr_result = self.db.query(OCRJobData).filter(
            #     OCRJobData.file_id == file_id,
            #     OCRJobData.user_id == user_id
            # ).first()
            # if not ocr_result:
            #     raise ResourceNotFoundException(f"OCR result for {file_id} not found")
            
            # return OCRResult.from_orm(ocr_result)
            return None
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve OCR result: {str(e)}")
