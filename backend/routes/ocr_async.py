"""
Event-Driven OCR Routes - Asynchronous Processing
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from werkzeug.utils import secure_filename
import os
import time
from datetime import datetime
from models import db, OCRResult, InvoiceTemplate
from tasks.ocr_tasks import process_ocr_task, bulk_process_ocr_task
from celery_config import celery

# Create new blueprint for event-driven OCR
ocr_async_bp = Blueprint('ocr_async', __name__)

# Validation schemas
class AsyncOCRProcessSchema(Schema):
    template_id = fields.Integer(required=False, allow_none=True)
    confidence_threshold = fields.Float(required=False, missing=0.7, validate=lambda x: 0.0 <= x <= 1.0)
    priority = fields.String(required=False, missing='normal', validate=lambda x: x in ['low', 'normal', 'high'])
    notification_email = fields.Email(required=False, allow_none=True)

class BulkOCRProcessSchema(Schema):
    template_id = fields.Integer(required=False, allow_none=True)
    confidence_threshold = fields.Float(required=False, missing=0.7)
    priority = fields.String(required=False, missing='normal')

@ocr_async_bp.route('/process-async', methods=['POST'])
@jwt_required()
def process_ocr_async():
    """
    🚀 Event-Driven OCR Processing - Không bắt user chờ đợi!
    
    User upload file → Trả về ngay task ID → OCR xử lý background → Notify khi xong
    """
    current_user_id = get_jwt_identity()
    
    # Validate request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate form data
    try:
        schema = AsyncOCRProcessSchema()
        form_data = schema.load(request.form.to_dict())
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'tiff', 'bmp'}
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        return jsonify({
            'error': 'Unsupported file format',
            'supported_formats': list(allowed_extensions)
        }), 400
    
    try:
        # Save uploaded file with timestamp
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Create OCR result record - Status: queued
        ocr_result = OCRResult(
            original_filename=file.filename,
            file_path=file_path,
            template_id=form_data.get('template_id'),
            status='queued',  # Đặt status là queued thay vì processing
            user_id=current_user_id  # Assuming you have user_id in OCRResult model
        )
        
        db.session.add(ocr_result)
        db.session.flush()  # Get the ID
        
        # 🚀 QUEUE TASK - Không chờ đợi, trả về ngay!
        priority_mapping = {'low': 1, 'normal': 5, 'high': 9}
        task_priority = priority_mapping.get(form_data.get('priority', 'normal'), 5)
        
        # Queue OCR task với Celery
        task = process_ocr_task.apply_async(
            args=[
                ocr_result.id,
                file_path,
                form_data.get('template_id'),
                form_data.get('confidence_threshold', 0.7)
            ],
            priority=task_priority,
            queue='ocr_queue'
        )
        
        # Store task ID
        ocr_result.celery_task_id = task.id
        db.session.commit()
        
        # Trả về ngay cho user - KHÔNG CHỜ ĐỢI!
        return jsonify({
            'message': '✅ File uploaded successfully! OCR processing started in background.',
            'ocr_result_id': ocr_result.id,
            'task_id': task.id,
            'status': 'queued',
            'estimated_time': '30-60 seconds',
            'check_status_url': f'/api/ocr-async/status/{ocr_result.id}',
            'notification': 'You will be notified when processing completes'
        }), 202  # 202 Accepted - Request accepted for processing
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to queue OCR task',
            'message': str(e)
        }), 500


@ocr_async_bp.route('/process-bulk', methods=['POST'])
@jwt_required()
def process_bulk_ocr():
    """
    Bulk OCR processing - Upload multiple files at once
    """
    current_user_id = get_jwt_identity()
    
    # Check if files were uploaded
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400
    
    # Validate form data
    try:
        schema = BulkOCRProcessSchema()
        form_data = schema.load(request.form.to_dict())
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    
    # Validate and save files
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'tiff', 'bmp'}
    saved_files = []
    
    try:
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        
        for file in files:
            if file.filename == '':
                continue
                
            file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if file_extension not in allowed_extensions:
                continue
            
            filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(upload_folder, filename)
            
            file.save(file_path)
            saved_files.append(file_path)
        
        if not saved_files:
            return jsonify({'error': 'No valid files to process'}), 400
        
        # Queue bulk processing task
        task = bulk_process_ocr_task.apply_async(
            args=[
                saved_files,
                form_data.get('template_id'),
                form_data.get('confidence_threshold', 0.7)
            ],
            queue='ocr_queue'
        )
        
        return jsonify({
            'message': f'✅ {len(saved_files)} files queued for bulk OCR processing',
            'task_id': task.id,
            'total_files': len(saved_files),
            'status': 'queued',
            'check_status_url': f'/api/ocr-async/bulk-status/{task.id}'
        }), 202
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to queue bulk OCR task',
            'message': str(e)
        }), 500


@ocr_async_bp.route('/status/<int:ocr_result_id>', methods=['GET'])
@jwt_required()
def get_ocr_status(ocr_result_id):
    """
    Check status of OCR processing task
    """
    current_user_id = get_jwt_identity()
    
    # Get OCR result
    ocr_result = OCRResult.query.filter_by(
        id=ocr_result_id,
        user_id=current_user_id
    ).first()
    
    if not ocr_result:
        return jsonify({'error': 'OCR result not found'}), 404
    
    response_data = {
        'ocr_result_id': ocr_result_id,
        'status': ocr_result.status,
        'original_filename': ocr_result.original_filename,
        'created_at': ocr_result.created_at.isoformat() if ocr_result.created_at else None
    }
    
    # Get Celery task status if available
    if ocr_result.celery_task_id:
        task = celery.AsyncResult(ocr_result.celery_task_id)
        response_data.update({
            'task_id': ocr_result.celery_task_id,
            'task_status': task.status,
            'task_info': task.info if task.info else None
        })
    
    # Add results if completed
    if ocr_result.status == 'completed':
        response_data.update({
            'confidence_score': ocr_result.confidence_score,
            'processing_time': ocr_result.processing_time,
            'extracted_text': ocr_result.extracted_text,
            'extracted_data': ocr_result.extracted_data
        })
    elif ocr_result.status == 'failed':
        response_data['error_message'] = ocr_result.error_message
    
    return jsonify(response_data)


@ocr_async_bp.route('/bulk-status/<task_id>', methods=['GET'])
@jwt_required()
def get_bulk_status(task_id):
    """
    Check status of bulk OCR processing
    """
    task = celery.AsyncResult(task_id)
    
    return jsonify({
        'task_id': task_id,
        'status': task.status,
        'info': task.info if task.info else None,
        'ready': task.ready(),
        'successful': task.successful() if task.ready() else None
    })


@ocr_async_bp.route('/cancel/<task_id>', methods=['POST'])
@jwt_required()
def cancel_ocr_task(task_id):
    """
    Cancel a running OCR task
    """
    try:
        celery.control.revoke(task_id, terminate=True)
        
        # Update OCR result status
        ocr_result = OCRResult.query.filter_by(celery_task_id=task_id).first()
        if ocr_result:
            ocr_result.status = 'cancelled'
            ocr_result.celery_task_id = None
            db.session.commit()
        
        return jsonify({
            'message': 'Task cancelled successfully',
            'task_id': task_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to cancel task',
            'message': str(e)
        }), 500


@ocr_async_bp.route('/queue-stats', methods=['GET'])
@jwt_required()
def get_queue_stats():
    """
    Get OCR queue statistics
    """
    try:
        # Get queue stats from Celery
        inspect = celery.control.inspect()
        
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        reserved_tasks = inspect.reserved()
        
        # Count OCR tasks
        ocr_active = 0
        ocr_scheduled = 0
        
        if active_tasks:
            for worker, tasks in active_tasks.items():
                ocr_active += len([t for t in tasks if 'ocr' in t.get('name', '')])
        
        if scheduled_tasks:
            for worker, tasks in scheduled_tasks.items():
                ocr_scheduled += len([t for t in tasks if 'ocr' in t.get('name', '')])
        
        return jsonify({
            'queue_stats': {
                'active_ocr_tasks': ocr_active,
                'scheduled_ocr_tasks': ocr_scheduled,
                'total_active': sum(len(tasks) for tasks in (active_tasks or {}).values()),
                'total_scheduled': sum(len(tasks) for tasks in (scheduled_tasks or {}).values())
            },
            'workers': list((active_tasks or {}).keys())
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get queue stats',
            'message': str(e)
        }), 500