"""
OCR Background Tasks - Event-Driven Processing
"""
from celery import current_task
from celery_config import celery
from models import db, OCRResult, InvoiceTemplate
from services.ocr_service import OCRService
from services.notification_service import NotificationService
import time
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

@celery.task(bind=True, name='tasks.ocr.process_ocr_task')
def process_ocr_task(self, ocr_result_id, file_path, template_id=None, confidence_threshold=0.7):
    """
    Event-driven OCR processing task
    
    Args:
        ocr_result_id: ID of OCRResult record
        file_path: Path to uploaded file
        template_id: Optional template ID for structured extraction
        confidence_threshold: Minimum confidence for successful processing
    """
    try:
        # Update task status
        current_task.update_state(
            state='PROCESSING',
            meta={'message': 'Starting OCR processing...', 'progress': 10}
        )
        
        # Get OCR result record
        ocr_result = OCRResult.query.get(ocr_result_id)
        if not ocr_result:
            raise Exception(f"OCR result {ocr_result_id} not found")
        
        # Update status in database
        ocr_result.status = 'processing'
        ocr_result.celery_task_id = self.request.id
        db.session.commit()
        
        # Get template if specified
        template = None
        if template_id:
            template = InvoiceTemplate.query.get(template_id)
            current_task.update_state(
                state='PROCESSING',
                meta={'message': f'Using template: {template.name}', 'progress': 20}
            )
        
        # Initialize OCR service
        ocr_service = OCRService()
        start_time = time.time()
        
        current_task.update_state(
            state='PROCESSING',
            meta={'message': 'Processing image with OCR...', 'progress': 40}
        )
        
        # Process OCR
        extracted_data = ocr_service.process_image(
            file_path, 
            template=template,
            confidence_threshold=confidence_threshold
        )
        
        processing_time = time.time() - start_time
        
        current_task.update_state(
            state='PROCESSING',
            meta={'message': 'Saving extracted data...', 'progress': 80}
        )
        
        # Update OCR result with extracted data
        ocr_result.extracted_data = extracted_data.get('structured_data', {})
        ocr_result.extracted_text = extracted_data.get('raw_text', '')
        ocr_result.confidence_score = extracted_data.get('confidence', 0.0)
        ocr_result.processing_time = processing_time
        ocr_result.status = 'completed'
        ocr_result.celery_task_id = None
        
        # Update template usage if used
        if template:
            success = ocr_result.confidence_score >= confidence_threshold
            template.increment_usage(success=success)
        
        db.session.commit()
        
        # Send notification about completion
        notification_data = {
            'type': 'ocr_completed',
            'ocr_result_id': ocr_result_id,
            'success': True,
            'confidence_score': ocr_result.confidence_score,
            'processing_time': processing_time,
            'extracted_data': extracted_data
        }
        
        # Trigger notification task
        send_ocr_notification.delay(notification_data)
        
        current_task.update_state(
            state='SUCCESS',
            meta={
                'message': 'OCR processing completed successfully',
                'progress': 100,
                'result': {
                    'ocr_result_id': ocr_result_id,
                    'confidence_score': ocr_result.confidence_score,
                    'processing_time': processing_time,
                    'extracted_data': extracted_data
                }
            }
        )
        
        return {
            'status': 'success',
            'ocr_result_id': ocr_result_id,
            'confidence_score': ocr_result.confidence_score,
            'processing_time': processing_time
        }
        
    except Exception as e:
        logger.error(f"OCR task failed: {str(e)}")
        
        # Update OCR result with error
        try:
            ocr_result = OCRResult.query.get(ocr_result_id)
            if ocr_result:
                ocr_result.status = 'failed'
                ocr_result.error_message = str(e)
                ocr_result.celery_task_id = None
                db.session.commit()
        except Exception:
            pass
        
        # Send error notification
        notification_data = {
            'type': 'ocr_failed',
            'ocr_result_id': ocr_result_id,
            'success': False,
            'error_message': str(e)
        }
        
        send_ocr_notification.delay(notification_data)
        
        # Update task state
        current_task.update_state(
            state='FAILURE',
            meta={'message': f'OCR processing failed: {str(e)}', 'error': str(e)}
        )
        
        raise


@celery.task(bind=True, name='tasks.ocr.bulk_process_ocr')
def bulk_process_ocr_task(self, file_paths, template_id=None, confidence_threshold=0.7):
    """
    Process multiple files in batch
    """
    results = []
    total_files = len(file_paths)
    
    for i, file_path in enumerate(file_paths):
        try:
            current_task.update_state(
                state='PROCESSING',
                meta={
                    'message': f'Processing file {i+1}/{total_files}',
                    'progress': int((i / total_files) * 100),
                    'current_file': os.path.basename(file_path)
                }
            )
            
            # Create OCR result record for each file
            ocr_result = OCRResult(
                original_filename=os.path.basename(file_path),
                file_path=file_path,
                template_id=template_id,
                status='queued'
            )
            db.session.add(ocr_result)
            db.session.flush()
            
            # Start individual OCR task
            task = process_ocr_task.delay(
                ocr_result.id, 
                file_path, 
                template_id, 
                confidence_threshold
            )
            
            results.append({
                'ocr_result_id': ocr_result.id,
                'task_id': task.id,
                'filename': os.path.basename(file_path)
            })
            
        except Exception as e:
            logger.error(f"Failed to queue file {file_path}: {str(e)}")
            results.append({
                'filename': os.path.basename(file_path),
                'error': str(e)
            })
    
    db.session.commit()
    
    return {
        'status': 'success',
        'total_files': total_files,
        'queued_tasks': len(results),
        'results': results
    }


@celery.task(name='tasks.ocr.send_ocr_notification')
def send_ocr_notification(notification_data):
    """
    Send notification about OCR completion
    """
    try:
        notification_service = NotificationService()
        
        if notification_data['success']:
            message = f"✅ OCR processing completed with {notification_data['confidence_score']:.1%} confidence"
        else:
            message = f"❌ OCR processing failed: {notification_data.get('error_message', 'Unknown error')}"
        
        # Send notification (WebSocket, Email, etc.)
        notification_service.send_notification(
            type=notification_data['type'],
            message=message,
            data=notification_data
        )
        
        return {'status': 'notification_sent'}
        
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        return {'status': 'notification_failed', 'error': str(e)}


@celery.task(name='tasks.ocr.cleanup_old_files')
def cleanup_old_files():
    """
    Periodic task to cleanup old uploaded files
    """
    try:
        # Delete files older than 7 days
        import datetime
        from pathlib import Path
        
        upload_folder = Path('uploads')
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=7)
        
        deleted_count = 0
        for file_path in upload_folder.glob('*'):
            if file_path.is_file():
                file_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
        
        return {'status': 'cleanup_completed', 'deleted_files': deleted_count}
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        return {'status': 'cleanup_failed', 'error': str(e)}