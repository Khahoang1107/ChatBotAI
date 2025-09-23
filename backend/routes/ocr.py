from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from werkzeug.utils import secure_filename
import os
import time
from datetime import datetime
from models import db, OCRResult, InvoiceTemplate, Invoice
from services.ocr_service import OCRService

ocr_bp = Blueprint('ocr', __name__)

# Validation schemas
class OCRProcessSchema(Schema):
    template_id = fields.Int(required=False)
    confidence_threshold = fields.Float(missing=0.8)

@ocr_bp.route('/process', methods=['POST'])
@jwt_required()
def process_ocr():
    """Process OCR on uploaded file"""
    current_user_id = get_jwt_identity()
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    if not ('.' in file.filename and 
            file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, pdf'}), 400
    
    # Get form data
    template_id = request.form.get('template_id', type=int)
    confidence_threshold = float(request.form.get('confidence_threshold', 0.8))
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    timestamp = str(int(time.time()))
    filename = f"{timestamp}_{filename}"
    
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # Create OCR result record
    ocr_result = OCRResult(
        original_filename=file.filename,
        file_path=file_path,
        template_id=template_id,
        status='processing'
    )
    
    try:
        db.session.add(ocr_result)
        db.session.flush()  # Get the ID
        
        # Get template if specified
        template = None
        if template_id:
            template = InvoiceTemplate.query.filter(
                db.or_(
                    db.and_(InvoiceTemplate.id == template_id, InvoiceTemplate.user_id == current_user_id),
                    db.and_(InvoiceTemplate.id == template_id, InvoiceTemplate.is_default == True)
                )
            ).first()
        
        # Process OCR
        ocr_service = OCRService()
        start_time = time.time()
        
        extracted_data = ocr_service.process_image(
            file_path, 
            template=template,
            confidence_threshold=confidence_threshold
        )
        
        processing_time = time.time() - start_time
        
        # Update OCR result
        ocr_result.extracted_data = extracted_data.get('structured_data', {})
        ocr_result.extracted_text = extracted_data.get('raw_text', '')
        ocr_result.confidence_score = extracted_data.get('confidence', 0.0)
        ocr_result.processing_time = processing_time
        ocr_result.status = 'completed'
        
        # Update template usage if used
        if template:
            success = ocr_result.confidence_score >= confidence_threshold
            template.increment_usage(success=success)
        
        db.session.commit()
        
        return jsonify({
            'message': 'OCR processing completed',
            'ocr_result': ocr_result.to_dict(),
            'extracted_data': extracted_data
        })
        
    except Exception as e:
        db.session.rollback()
        
        # Update OCR result with error
        ocr_result.status = 'failed'
        ocr_result.error_message = str(e)
        db.session.commit()
        
        return jsonify({
            'error': 'OCR processing failed', 
            'message': str(e),
            'ocr_result_id': ocr_result.id
        }), 500

@ocr_bp.route('/results', methods=['GET'])
@jwt_required()
def get_ocr_results():
    """Get OCR results for the current user"""
    current_user_id = get_jwt_identity()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Filter by status
    status = request.args.get('status')
    
    # Build query - get OCR results for user's invoices or standalone results
    query = db.session.query(OCRResult).outerjoin(Invoice).filter(
        db.or_(
            Invoice.user_id == current_user_id,
            Invoice.id.is_(None)  # Standalone OCR results
        )
    )
    
    if status:
        query = query.filter(OCRResult.status == status)
    
    query = query.order_by(OCRResult.created_at.desc())
    
    # Paginate
    results = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'ocr_results': [result.to_dict() for result in results.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': results.total,
            'pages': results.pages,
            'has_next': results.has_next,
            'has_prev': results.has_prev
        }
    })

@ocr_bp.route('/results/<int:result_id>', methods=['GET'])
@jwt_required()
def get_ocr_result(result_id):
    """Get a specific OCR result"""
    current_user_id = get_jwt_identity()
    
    # Get OCR result and check permissions
    ocr_result = db.session.query(OCRResult).outerjoin(Invoice).filter(
        OCRResult.id == result_id,
        db.or_(
            Invoice.user_id == current_user_id,
            Invoice.id.is_(None)  # Standalone OCR results
        )
    ).first()
    
    if not ocr_result:
        return jsonify({'error': 'OCR result not found'}), 404
    
    return jsonify({'ocr_result': ocr_result.to_dict()})

@ocr_bp.route('/results/<int:result_id>/create-invoice', methods=['POST'])
@jwt_required()
def create_invoice_from_ocr(result_id):
    """Create an invoice from OCR result"""
    current_user_id = get_jwt_identity()
    
    # Get OCR result
    ocr_result = db.session.query(OCRResult).outerjoin(Invoice).filter(
        OCRResult.id == result_id,
        db.or_(
            Invoice.user_id == current_user_id,
            Invoice.id.is_(None)
        )
    ).first()
    
    if not ocr_result:
        return jsonify({'error': 'OCR result not found'}), 404
    
    if ocr_result.status != 'completed':
        return jsonify({'error': 'OCR processing not completed'}), 400
    
    if ocr_result.invoice_id:
        return jsonify({'error': 'Invoice already created from this OCR result'}), 400
    
    # Get extracted data
    extracted_data = ocr_result.get_extracted_data()
    
    if not extracted_data:
        return jsonify({'error': 'No extracted data available'}), 400
    
    # Create invoice from extracted data
    invoice = Invoice(
        user_id=current_user_id,
        invoice_number=extracted_data.get('invoice_number', f'INV-{int(time.time())}'),
        company_name=extracted_data.get('company_name', ''),
        company_address=extracted_data.get('company_address'),
        company_tax_id=extracted_data.get('company_tax_id'),
        company_phone=extracted_data.get('company_phone'),
        company_email=extracted_data.get('company_email'),
        customer_name=extracted_data.get('customer_name', ''),
        customer_address=extracted_data.get('customer_address'),
        customer_tax_id=extracted_data.get('customer_tax_id'),
        customer_phone=extracted_data.get('customer_phone'),
        customer_email=extracted_data.get('customer_email'),
        subtotal=extracted_data.get('subtotal'),
        tax_amount=extracted_data.get('tax_amount'),
        total_amount=extracted_data.get('total_amount', 0),
        currency=extracted_data.get('currency', 'VND'),
        template_id=ocr_result.template_id,
        original_file_path=ocr_result.file_path,
        ocr_confidence=ocr_result.confidence_score,
        status='pending'
    )
    
    # Parse dates
    if extracted_data.get('invoice_date'):
        try:
            invoice.invoice_date = datetime.strptime(
                extracted_data['invoice_date'], '%Y-%m-%d'
            ).date()
        except ValueError:
            pass
    
    if extracted_data.get('due_date'):
        try:
            invoice.due_date = datetime.strptime(
                extracted_data['due_date'], '%Y-%m-%d'
            ).date()
        except ValueError:
            pass
    
    try:
        db.session.add(invoice)
        db.session.flush()  # Get invoice ID
        
        # Add invoice items if available
        if 'items' in extracted_data:
            from models import InvoiceItem
            for item_data in extracted_data['items']:
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=item_data.get('description', ''),
                    quantity=item_data.get('quantity', 1),
                    unit_price=item_data.get('unit_price', 0),
                    total_price=item_data.get('total_price', 0),
                    tax_rate=item_data.get('tax_rate', 0)
                )
                db.session.add(item)
        
        # Link OCR result to invoice
        ocr_result.invoice_id = invoice.id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Invoice created successfully from OCR result',
            'invoice': invoice.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create invoice', 'message': str(e)}), 500

@ocr_bp.route('/supported-formats', methods=['GET'])
def get_supported_formats():
    """Get supported file formats for OCR"""
    return jsonify({
        'supported_formats': ['png', 'jpg', 'jpeg', 'gif', 'pdf'],
        'max_file_size': '16MB',
        'recommended_formats': ['png', 'jpg', 'pdf'],
        'notes': {
            'pdf': 'Only first page will be processed',
            'image_quality': 'Higher resolution images produce better results',
            'text_clarity': 'Clear, high-contrast text is recommended'
        }
    })

@ocr_bp.route('/templates/<int:template_id>/test', methods=['POST'])
@jwt_required()
def test_template_with_ocr(template_id):
    """Test a template with OCR processing"""
    current_user_id = get_jwt_identity()
    
    # Get template
    template = InvoiceTemplate.query.filter(
        db.or_(
            db.and_(InvoiceTemplate.id == template_id, InvoiceTemplate.user_id == current_user_id),
            db.and_(InvoiceTemplate.id == template_id, InvoiceTemplate.is_default == True)
        )
    ).first()
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save temporary file
    filename = secure_filename(file.filename)
    timestamp = str(int(time.time()))
    filename = f"test_{timestamp}_{filename}"
    
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    try:
        # Process OCR with template
        ocr_service = OCRService()
        start_time = time.time()
        
        extracted_data = ocr_service.process_image(
            file_path, 
            template=template,
            confidence_threshold=0.8
        )
        
        processing_time = time.time() - start_time
        
        # Clean up temporary file
        os.remove(file_path)
        
        return jsonify({
            'message': 'Template test completed',
            'template_id': template_id,
            'template_name': template.name,
            'processing_time': processing_time,
            'extracted_data': extracted_data,
            'test_results': {
                'confidence': extracted_data.get('confidence', 0.0),
                'fields_extracted': len(extracted_data.get('structured_data', {})),
                'template_match': extracted_data.get('confidence', 0.0) >= 0.8
            }
        })
        
    except Exception as e:
        # Clean up temporary file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({
            'error': 'Template test failed', 
            'message': str(e)
        }), 500