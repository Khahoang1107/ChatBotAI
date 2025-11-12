"""
OCR Job Service - Handles async OCR job operations
"""
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)


class OCRJobService:
    """Service for handling OCR job operations"""

    def __init__(self, db_tools=None):
        self.db_tools = db_tools

    def enqueue_job(self, filepath: str, filename: str, uploader: Optional[str] = "unknown", user_id: Optional[str] = None) -> Dict[str, Any]:
        """Enqueue an OCR job for async processing"""
        if not self.db_tools:
            raise Exception("Database not available")

        job_id = str(uuid.uuid4())

        # Insert job record into ocr_jobs table
        conn = self.db_tools.connect()
        if not conn:
            raise Exception("Cannot connect to database")

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ocr_jobs (id, filepath, filename, status, uploader, user_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                job_id,
                filepath,
                filename,
                'queued',
                uploader,
                user_id,
                datetime.now(),
                datetime.now()
            ))
            conn.commit()

        logger.info(f"📋 OCR job enqueued: {job_id} for file {filename}")

        return {
            "success": True,
            "job_id": job_id,
            "status": "queued",
            "message": f"OCR job {job_id} queued successfully",
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        }

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of an OCR job"""
        if not self.db_tools:
            raise Exception("Database not available")

        conn = self.db_tools.connect()
        if not conn:
            raise Exception("Cannot connect to database")

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, filename, status, progress, invoice_id, error_message, created_at, updated_at
                FROM ocr_jobs
                WHERE id = %s
            """, (job_id,))
            result = cursor.fetchone()

        if not result:
            raise Exception(f"Job not found: {job_id}")

        job_id_db, filename, status, progress, invoice_id, error_msg, created_at, updated_at = result

        logger.info(f"📊 Job status retrieved: {job_id} → {status}")

        return {
            "success": True,
            "job_id": job_id_db,
            "filename": filename,
            "status": status,
            "progress": progress or 0,
            "invoice_id": invoice_id,
            "error_message": error_msg,
            "created_at": created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at),
            "updated_at": updated_at.isoformat() if hasattr(updated_at, 'isoformat') else str(updated_at),
            "timestamp": datetime.now().isoformat()
        }

    def update_job_status(self, job_id: str, status: str, progress: Optional[int] = None,
                         invoice_id: Optional[int] = None, error_message: Optional[str] = None) -> bool:
        """Update job status"""
        if not self.db_tools:
            return False

        try:
            conn = self.db_tools.connect()
            if not conn:
                return False

            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE ocr_jobs
                    SET status = %s, progress = %s, invoice_id = %s, error_message = %s, updated_at = %s
                    WHERE id = %s
                """, (
                    status,
                    progress,
                    invoice_id,
                    error_message,
                    datetime.now(),
                    job_id
                ))
                conn.commit()

            logger.info(f"📋 Job {job_id} updated: {status}")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating job {job_id}: {str(e)}")
            return False

    def get_pending_jobs(self, limit: int = 10) -> list:
        """Get pending jobs for processing"""
        if not self.db_tools:
            return []

        try:
            conn = self.db_tools.connect()
            if not conn:
                return []

            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, filepath, filename, uploader, user_id, created_at
                    FROM ocr_jobs
                    WHERE status = 'queued'
                    ORDER BY created_at ASC
                    LIMIT %s
                """, (limit,))
                results = cursor.fetchall()

            jobs = []
            for row in results:
                job_id, filepath, filename, uploader, user_id, created_at = row
                jobs.append({
                    'id': job_id,
                    'filepath': filepath,
                    'filename': filename,
                    'uploader': uploader,
                    'user_id': user_id,
                    'created_at': created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
                })

            return jobs

        except Exception as e:
            logger.error(f"❌ Error getting pending jobs: {str(e)}")
            return []