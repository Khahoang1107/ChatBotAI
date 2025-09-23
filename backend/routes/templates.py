from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from models import db, InvoiceTemplate, User
from services.training_service import TrainingDataService
import requests
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

templates_bp = Blueprint('templates', __name__)

# Cấu hình Rasa
RASA_SERVER_URL = "http://localhost:5005"  # URL của Rasa server

# Validation schemas
class TemplateSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str()
    field_mappings = fields.Dict()
    ocr_zones = fields.Dict()
    is_default = fields.Bool(missing=False)

@templates_bp.route('', methods=['GET'])
@jwt_required()
def get_templates():
    """Get all templates for the current user"""
    current_user_id = get_jwt_identity()
    
    # Get user templates
    user_templates = InvoiceTemplate.query.filter_by(user_id=current_user_id).all()
    
    # Get default templates (if any)
    default_templates = InvoiceTemplate.query.filter_by(is_default=True).all()
    
    # Combine and remove duplicates
    all_templates = user_templates + [t for t in default_templates if t not in user_templates]
    
    return jsonify({
        'templates': [template.to_dict() for template in all_templates]
    })

@templates_bp.route('/<int:template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    """Get a specific template"""
    current_user_id = get_jwt_identity()
    
    template = InvoiceTemplate.query.filter(
        db.or_(
            db.and_(InvoiceTemplate.id == template_id, InvoiceTemplate.user_id == current_user_id),
            db.and_(InvoiceTemplate.id == template_id, InvoiceTemplate.is_default == True)
        )
    ).first()
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    return jsonify({'template': template.to_dict()})

@templates_bp.route('', methods=['POST'])
@jwt_required()
def create_template():
    """Create a new template"""
    current_user_id = get_jwt_identity()
    schema = TemplateSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Check if template name already exists for this user
    existing_template = InvoiceTemplate.query.filter_by(
        name=data['name'],
        user_id=current_user_id
    ).first()
    
    if existing_template:
        return jsonify({'error': 'Template name already exists'}), 400
    
    # Create template
    template = InvoiceTemplate(
        name=data['name'],
        user_id=current_user_id,
        description=data.get('description'),
        is_default=data.get('is_default', False)
    )
    
    # Set field mappings and OCR zones
    if 'field_mappings' in data:
        template.set_field_mappings(data['field_mappings'])
    
    if 'ocr_zones' in data:
        template.set_ocr_zones(data['ocr_zones'])
    
    try:
        db.session.add(template)
        db.session.commit()
        
        # Lưu training data cho AI ngay sau khi tạo template thành công
        try:
            training_service = TrainingDataService()
            training_id = training_service.save_template_training_data(
                template, 
                additional_metadata={
                    "created_by_user": current_user_id,
                    "creation_method": "manual_creation",
                    "has_field_mappings": 'field_mappings' in data,
                    "has_ocr_zones": 'ocr_zones' in data
                }
            )
            
            if training_id:
                logger.info(f"Đã lưu training data cho template {template.id}, training_id: {training_id}")
            else:
                logger.warning(f"Không thể lưu training data cho template {template.id}")
                
        except Exception as training_error:
            logger.error(f"Lỗi khi lưu training data cho template {template.id}: {str(training_error)}")
            # Không làm fail việc tạo template, chỉ log lỗi
        
        return jsonify({
            'message': 'Template created successfully',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create template', 'message': str(e)}), 500

@templates_bp.route('/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    """Update an existing template"""
    current_user_id = get_jwt_identity()
    
    template = InvoiceTemplate.query.filter_by(id=template_id, user_id=current_user_id).first()
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    schema = TemplateSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Check if template name conflicts with another template
    if data['name'] != template.name:
        existing_template = InvoiceTemplate.query.filter_by(
            name=data['name'],
            user_id=current_user_id
        ).first()
        
        if existing_template:
            return jsonify({'error': 'Template name already exists'}), 400
    
    # Update template fields
    template.name = data['name']
    template.description = data.get('description')
    template.is_default = data.get('is_default', False)
    
    # Update field mappings and OCR zones
    if 'field_mappings' in data:
        template.set_field_mappings(data['field_mappings'])
    
    if 'ocr_zones' in data:
        template.set_ocr_zones(data['ocr_zones'])
    
    try:
        db.session.commit()
        
        # Cập nhật training data sau khi update template thành công
        try:
            training_service = TrainingDataService()
            training_id = training_service.save_template_training_data(
                template, 
                additional_metadata={
                    "updated_by_user": current_user_id,
                    "creation_method": "template_update",
                    "has_field_mappings": 'field_mappings' in data,
                    "has_ocr_zones": 'ocr_zones' in data,
                    "update_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            if training_id:
                logger.info(f"Đã cập nhật training data cho template {template.id}, training_id: {training_id}")
            else:
                logger.warning(f"Không thể cập nhật training data cho template {template.id}")
                
        except Exception as training_error:
            logger.error(f"Lỗi khi cập nhật training data cho template {template.id}: {str(training_error)}")
            # Không làm fail việc update template, chỉ log lỗi
        
        return jsonify({
            'message': 'Template updated successfully',
            'template': template.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update template', 'message': str(e)}), 500

@templates_bp.route('/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    """Delete a template"""
    current_user_id = get_jwt_identity()
    
    template = InvoiceTemplate.query.filter_by(id=template_id, user_id=current_user_id).first()
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Check if template is being used by any invoices
    if template.invoices:
        return jsonify({
            'error': 'Cannot delete template that is being used by invoices',
            'invoice_count': len(template.invoices)
        }), 400
    
    try:
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'message': 'Template deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete template', 'message': str(e)}), 500

@templates_bp.route('/<int:template_id>/usage', methods=['POST'])
@jwt_required()
def update_template_usage(template_id):
    """Update template usage statistics"""
    current_user_id = get_jwt_identity()
    
    template = InvoiceTemplate.query.filter(
        db.or_(
            db.and_(InvoiceTemplate.id == template_id, InvoiceTemplate.user_id == current_user_id),
            db.and_(InvoiceTemplate.id == template_id, InvoiceTemplate.is_default == True)
        )
    ).first()
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    data = request.json
    success = data.get('success', True)
    
    template.increment_usage(success=success)
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Template usage updated',
            'usage_count': template.usage_count,
            'success_rate': template.success_rate
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update usage', 'message': str(e)}), 500

@templates_bp.route('/default', methods=['GET'])
def get_default_templates():
    """Get default templates (no authentication required for demo purposes)"""
    default_templates = InvoiceTemplate.query.filter_by(is_default=True).all()
    
    return jsonify({
        'templates': [template.to_dict() for template in default_templates]
    })

@templates_bp.route('/create-from-invoice', methods=['POST'])
@jwt_required()
def create_template_from_invoice():
    """Create a template from an existing invoice"""
    current_user_id = get_jwt_identity()
    
    data = request.json
    invoice_id = data.get('invoice_id')
    template_name = data.get('template_name')
    
    if not invoice_id or not template_name:
        return jsonify({'error': 'invoice_id and template_name are required'}), 400
    
    # Get the invoice
    from models import Invoice
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user_id).first()
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    # Check if template name already exists
    existing_template = InvoiceTemplate.query.filter_by(
        name=template_name,
        user_id=current_user_id
    ).first()
    
    if existing_template:
        return jsonify({'error': 'Template name already exists'}), 400
    
    # Create template based on invoice structure
    template = InvoiceTemplate(
        name=template_name,
        user_id=current_user_id,
        description=f'Template created from invoice {invoice.invoice_number}'
    )
    
    # Create basic field mappings based on invoice data
    field_mappings = {
        'invoice_number': {'required': True, 'type': 'string'},
        'company_name': {'required': True, 'type': 'string'},
        'customer_name': {'required': True, 'type': 'string'},
        'total_amount': {'required': True, 'type': 'decimal'},
        'invoice_date': {'required': True, 'type': 'date'},
        'due_date': {'required': False, 'type': 'date'}
    }
    
    if invoice.company_address:
        field_mappings['company_address'] = {'required': False, 'type': 'string'}
    if invoice.company_tax_id:
        field_mappings['company_tax_id'] = {'required': False, 'type': 'string'}
    if invoice.customer_address:
        field_mappings['customer_address'] = {'required': False, 'type': 'string'}
    if invoice.customer_tax_id:
        field_mappings['customer_tax_id'] = {'required': False, 'type': 'string'}
    
    template.set_field_mappings(field_mappings)
    
    try:
        db.session.add(template)
        db.session.commit()
        
        # Train Rasa với template mới
        try:
            train_rasa_with_template(template)
        except Exception as rasa_error:
            print(f"Rasa training error: {rasa_error}")
            # Không fail request nếu Rasa có lỗi
        
        return jsonify({
            'message': 'Template created successfully from invoice',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create template', 'message': str(e)}), 500

# Rasa Integration Functions
def train_rasa_with_template(template):
    """Gửi template data đến Rasa để training"""
    try:
        # Tạo training data từ template
        training_data = {
            "template_id": template.id,
            "template_name": template.name,
            "field_mappings": template.get_field_mappings(),
            "ocr_zones": template.get_ocr_zones(),
            "user_id": template.user_id
        }
        
        # Gửi đến Rasa webhook hoặc training endpoint
        response = requests.post(
            f"{RASA_SERVER_URL}/webhooks/training",
            json=training_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"Successfully sent template {template.id} to Rasa for training")
        else:
            print(f"Failed to send template to Rasa: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Rasa: {e}")

def send_to_rasa(text: str, template):
    """Gửi text đến Rasa để xử lý với context của template"""
    try:
        # Prepare message for Rasa
        message_data = {
            "sender": f"template_{template.id}",
            "message": text,
            "metadata": {
                "template_id": template.id,
                "template_name": template.name,
                "field_mappings": template.get_field_mappings(),
                "ocr_zones": template.get_ocr_zones()
            }
        }
        
        # Send to Rasa
        response = requests.post(
            f"{RASA_SERVER_URL}/webhooks/rest/webhook",
            json=message_data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Rasa server error: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to communicate with Rasa: {str(e)}"}

@templates_bp.route('/<int:template_id>/process-rasa', methods=['POST'])
@jwt_required()
def process_template_with_rasa(template_id):
    """Xử lý template với Rasa để trích xuất thông tin"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        template = InvoiceTemplate.query.filter_by(
            id=template_id,
            user_id=current_user_id
        ).first()
        
        if not template:
            return jsonify({"error": "Template not found"}), 404
        
        # Gửi dữ liệu đến Rasa để xử lý
        rasa_response = send_to_rasa(data.get('text', ''), template)
        
        return jsonify({
            "template_id": template_id,
            "template_name": template.name,
            "rasa_response": rasa_response,
            "processed_at": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@templates_bp.route('/rasa/train', methods=['POST'])
@jwt_required()
def trigger_rasa_training():
    """Trigger Rasa training với tất cả templates của user"""
    try:
        current_user_id = get_jwt_identity()
        templates = InvoiceTemplate.query.filter_by(user_id=current_user_id).all()
        
        # Gửi tất cả templates đến Rasa
        for template in templates:
            train_rasa_with_template(template)
        
        return jsonify({
            "message": f"Triggered Rasa training with {len(templates)} templates",
            "template_count": len(templates)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500