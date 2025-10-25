#!/usr/bin/env python3
"""
🔄 Async OCR Worker
====================

Polls the ocr_jobs table and processes queued jobs:
1. Fetch queued jobs
2. Run OCR (pytesseract)
3. Extract fields (regex)
4. Save invoice to DB
5. Update job status
6. (Future) emit WebSocket notification

Usage:
    python backend/worker.py

Environment variables:
    POLL_INTERVAL: seconds between polls (default: 5)
    MAX_JOBS_PER_POLL: max jobs to process per poll (default: 3)
    TESSERACT_PATH: path to tesseract executable (optional, auto-detect)
"""

import sys
import os
import time
import logging
import threading
from datetime import datetime, timedelta
import asyncio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add chatbot path for database tools
chatbot_path = os.path.join(os.path.dirname(__file__), '..', 'chatbot')
sys.path.insert(0, chatbot_path)

try:
    from utils.database_tools import get_database_tools
    db_tools = get_database_tools()
    logger.info("✅ Database tools initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize database tools: {e}")
    sys.exit(1)

# Add backend path for WebSocket manager
sys.path.insert(0, os.path.dirname(__file__))
from main import extract_invoice_fields, calculate_pattern_confidence

# Import WebSocket manager for real-time notifications
try:
    from websocket_manager import websocket_manager
    logger.info("✅ WebSocket manager initialized")
except Exception as e:
    logger.warning(f"⚠️ WebSocket manager not available: {e}")
    websocket_manager = None

# Configuration
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '5'))
MAX_JOBS_PER_POLL = int(os.getenv('MAX_JOBS_PER_POLL', '3'))
MAX_RETRIES = 3


async def send_ocr_notification(job_id: str, status: str, user_id: str = "anonymous", invoice_data: dict = None, error: str = None):
    """
    Send WebSocket notification for OCR job status update
    """
    if not websocket_manager:
        logger.debug("WebSocket manager not available, skipping notification")
        return

    try:
        notification = {
            "type": "ocr_job_update",
            "job_id": job_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }

        if status == "done" and invoice_data:
            notification.update({
                "message": "OCR processing completed successfully",
                "invoice_data": invoice_data
            })
        elif status == "failed" and error:
            notification.update({
                "message": f"OCR processing failed: {error}",
                "error": error
            })
        elif status == "processing":
            notification.update({
                "message": "OCR processing started"
            })

        # Send to specific user
        await websocket_manager.send_to_user(user_id, notification)
        logger.info(f"📡 WebSocket notification sent to {user_id}: {status}")

    except Exception as e:
        logger.error(f"❌ Failed to send WebSocket notification: {e}")


def run_ocr_on_file(filepath: str, filename: str) -> tuple:
    """
    Run OCR on a file and extract fields.
    Returns: (success: bool, ocr_text: str, extracted_data: dict, error: str)
    """
    try:
        from PIL import Image
        import pytesseract
        import tempfile
        
        if not os.path.exists(filepath):
            return False, "", {}, f"File not found: {filepath}"
        
        # Open image and run Tesseract
        image = Image.open(filepath)
        
        # Configure pytesseract
        from ocr_config import configure_tesseract
        if configure_tesseract():
            ocr_text = pytesseract.image_to_string(image, lang='vie+eng')
        else:
            raise Exception("Tesseract not configured properly")
        
        if not ocr_text or len(ocr_text.strip()) == 0:
            return False, "", {}, "OCR produced no text (image may be blank)"
        
        # Extract structured fields
        extracted_data = extract_invoice_fields(ocr_text, filename)
        confidence = calculate_pattern_confidence(extracted_data)
        
        logger.info(f"✅ OCR success for {filename}: {len(ocr_text)} chars, confidence {confidence:.2f}")
        return True, ocr_text, extracted_data, None
    
    except ImportError as e:
        return False, "", {}, f"Missing dependency: {e} (ensure pytesseract and Tesseract are installed)"
    except Exception as e:
        return False, "", {}, f"OCR failed: {str(e)}"


def process_job(job_id: str, filepath: str, filename: str, user_id: str = "anonymous") -> bool:
    """
    Process a single OCR job.
    Returns: True if successful, False otherwise
    """
    conn = None
    try:
        logger.info(f"🔄 Processing job {job_id}: {filename}")
        
        conn = db_tools.connect()
        if not conn:
            logger.error(f"❌ Cannot connect to database for job {job_id}")
            return False
        
        # Update job status to 'processing'
        conn.rollback()  # Ensure clean state
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE ocr_jobs
                SET status = %s, started_at = %s, updated_at = %s
                WHERE id = %s
            """, ('processing', datetime.now(), datetime.now(), job_id))
            conn.commit()

        # Send WebSocket notification for processing start
        asyncio.run(send_ocr_notification(job_id, "processing", user_id))
        
        # Run OCR
        success, ocr_text, extracted_data, error = run_ocr_on_file(filepath, filename)
        
        if not success:
            # OCR failed - update job with error and retry attempt
            conn.rollback()  # Ensure clean state
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE ocr_jobs
                    SET status = %s, error_message = %s, attempts = attempts + 1, updated_at = %s
                    WHERE id = %s
                """, ('failed', error, datetime.now(), job_id))
                conn.commit()

            # Send WebSocket notification for failure
            asyncio.run(send_ocr_notification(job_id, "failed", user_id, error=error))

            logger.error(f"❌ Job {job_id} failed: {error}")
            return False        # OCR succeeded - save invoice to DB
        try:
            confidence = min((len(ocr_text) / 500 + calculate_pattern_confidence(extracted_data)) / 2, 1.0)
            
            conn.rollback()  # Ensure clean state
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO invoices
                    (filename, invoice_code, invoice_type, buyer_name, seller_name, 
                     total_amount, confidence_score, raw_text, invoice_date, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    filename,
                    extracted_data.get('invoice_code', 'INV-UNKNOWN'),
                    extracted_data.get('invoice_type', 'general'),
                    extracted_data.get('buyer_name', 'N/A'),
                    extracted_data.get('seller_name', 'N/A'),
                    extracted_data.get('total_amount', 'N/A'),
                    confidence,
                    ocr_text[:2000],  # Store first 2000 chars
                    extracted_data.get('date', datetime.now().strftime("%d/%m/%Y")),
                    datetime.now()
                ))
                result = cursor.fetchone()
                invoice_id = result[0] if result else None
                conn.commit()
            
            # Update job to 'done' with invoice_id
            conn.rollback()  # Ensure clean state
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE ocr_jobs
                    SET status = %s, invoice_id = %s, completed_at = %s, updated_at = %s
                    WHERE id = %s
                """, ('done', invoice_id, datetime.now(), datetime.now(), job_id))
                conn.commit()

            # Send WebSocket notification for success
            invoice_notification_data = {
                "invoice_id": invoice_id,
                "invoice_code": extracted_data.get('invoice_code', 'INV-UNKNOWN'),
                "buyer_name": extracted_data.get('buyer_name', 'N/A'),
                "seller_name": extracted_data.get('seller_name', 'N/A'),
                "total_amount": extracted_data.get('total_amount', 'N/A'),
                "confidence_score": confidence
            }
            asyncio.run(send_ocr_notification(job_id, "done", user_id, invoice_data=invoice_notification_data))

            logger.info(f"✅ Job {job_id} completed successfully (invoice_id: {invoice_id})")
            return True
        
        except Exception as db_err:
            logger.error(f"❌ Database error while saving invoice for job {job_id}: {db_err}")
            conn.rollback()  # Ensure clean state
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE ocr_jobs
                    SET status = %s, error_message = %s, updated_at = %s
                    WHERE id = %s
                """, ('failed', str(db_err), datetime.now(), job_id))
                conn.commit()
            return False
    
    except Exception as e:
        logger.error(f"❌ Unexpected error processing job {job_id}: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


def fetch_queued_jobs(limit: int = 5) -> list:
    """Fetch queued jobs from DB that haven't exceeded max retries"""
    conn = None
    try:
        conn = db_tools.connect()
        if not conn:
            return []
        
        conn.rollback()  # Ensure clean state
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, filepath, filename, user_id
                FROM ocr_jobs
                WHERE status = %s AND attempts < %s
                ORDER BY created_at ASC
                LIMIT %s
            """, ('queued', MAX_RETRIES, limit))
            results = cursor.fetchall()
        
        # Debug: log what we got
        if results:
            logger.info(f"DEBUG: Fetched {len(results)} jobs")
            for i, row in enumerate(results):
                logger.info(f"  Job {i}: {row}")
        
        return results if results else []
    
    except Exception as e:
        logger.error(f"❌ Error fetching queued jobs: {e}")
        return []
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


def poll_and_process():
    """Main polling loop"""
    logger.info(f"🔄 Worker started - polling every {POLL_INTERVAL}s for up to {MAX_JOBS_PER_POLL} jobs")
    
    while True:
        try:
            # Fetch queued jobs
            jobs = fetch_queued_jobs(limit=MAX_JOBS_PER_POLL)
            
            if jobs:
                logger.info(f"📋 Found {len(jobs)} queued job(s)")
                
                for job_row in jobs:
                    job_id, filepath, filename, user_id = job_row
                    # Process each job
                    process_job(job_id, filepath, filename, user_id or "anonymous")
                    # Small delay between jobs to avoid overwhelming the system
                    time.sleep(0.5)
            else:
                # No jobs - log less frequently
                logger.debug("⏳ No queued jobs at this moment")
            
            # Wait before polling again
            time.sleep(POLL_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("🛑 Worker interrupted by user")
            break
        except Exception as e:
            logger.error(f"❌ Unexpected error in polling loop: {e}")
            time.sleep(POLL_INTERVAL)
    
    logger.info("✅ Worker stopped")


def health_check():
    """Check if worker can connect to DB and process jobs"""
    try:
        conn = db_tools.connect()
        if not conn:
            logger.error("❌ Health check failed: Cannot connect to database")
            return False
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        logger.info("✅ Health check passed")
        return True
    
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("🚀 OCR Worker starting...")
    
    # Run health check
    if not health_check():
        logger.error("❌ Health check failed. Exiting.")
        sys.exit(1)
    
    # Start polling
    try:
        poll_and_process()
    except Exception as e:
        logger.error(f"❌ Worker failed: {e}")
        sys.exit(1)
