from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from datetime import datetime, date
from models import db, Invoice, InvoiceItem, User
from sqlalchemy.exc import IntegrityError

invoices_bp = Blueprint('invoices', __name__)

# Validation schemas
class InvoiceItemSchema(Schema):
    description = fields.Str(required=True)
    quantity = fields.Decimal(required=True, as_string=True)
    unit_price = fields.Decimal(required=True, as_string=True)
    total_price = fields.Decimal(required=True, as_string=True)
    tax_rate = fields.Decimal(as_string=True, missing=0)

class InvoiceSchema(Schema):
    invoice_number = fields.Str(required=True)
    company_name = fields.Str(required=True)
    company_address = fields.Str()
    company_tax_id = fields.Str()
    company_phone = fields.Str()
    company_email = fields.Email()
    customer_name = fields.Str(required=True)
    customer_address = fields.Str()
    customer_tax_id = fields.Str()
    customer_phone = fields.Str()
    customer_email = fields.Email()
    subtotal = fields.Decimal(as_string=True)
    tax_amount = fields.Decimal(as_string=True)
    total_amount = fields.Decimal(required=True, as_string=True)
    currency = fields.Str(missing='VND')
    invoice_date = fields.Date()
    due_date = fields.Date()
    template_id = fields.Int()
    items = fields.List(fields.Nested(InvoiceItemSchema))

@invoices_bp.route('', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get all invoices for the current user"""
    current_user_id = get_jwt_identity()
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Filter parameters
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search = request.args.get('search')
    
    # Build query
    query = Invoice.query.filter_by(user_id=current_user_id)
    
    if status:
        query = query.filter(Invoice.status == status)
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Invoice.invoice_date >= start_date)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Invoice.invoice_date <= end_date)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Invoice.invoice_number.ilike(search_term),
                Invoice.company_name.ilike(search_term),
                Invoice.customer_name.ilike(search_term)
            )
        )
    
    # Order by created_at desc
    query = query.order_by(Invoice.created_at.desc())
    
    # Paginate
    invoices = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'invoices': [invoice.to_dict() for invoice in invoices.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': invoices.total,
            'pages': invoices.pages,
            'has_next': invoices.has_next,
            'has_prev': invoices.has_prev
        }
    })

@invoices_bp.route('/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Get a specific invoice"""
    current_user_id = get_jwt_identity()
    
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user_id).first()
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    return jsonify({'invoice': invoice.to_dict()})

@invoices_bp.route('', methods=['POST'])
@jwt_required()
def create_invoice():
    """Create a new invoice"""
    current_user_id = get_jwt_identity()
    schema = InvoiceSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Check if invoice number already exists for this user
    existing_invoice = Invoice.query.filter_by(
        invoice_number=data['invoice_number'],
        user_id=current_user_id
    ).first()
    
    if existing_invoice:
        return jsonify({'error': 'Invoice number already exists'}), 400
    
    # Create invoice
    invoice = Invoice(
        user_id=current_user_id,
        invoice_number=data['invoice_number'],
        company_name=data['company_name'],
        company_address=data.get('company_address'),
        company_tax_id=data.get('company_tax_id'),
        company_phone=data.get('company_phone'),
        company_email=data.get('company_email'),
        customer_name=data['customer_name'],
        customer_address=data.get('customer_address'),
        customer_tax_id=data.get('customer_tax_id'),
        customer_phone=data.get('customer_phone'),
        customer_email=data.get('customer_email'),
        subtotal=data.get('subtotal'),
        tax_amount=data.get('tax_amount'),
        total_amount=data['total_amount'],
        currency=data.get('currency', 'VND'),
        invoice_date=data.get('invoice_date'),
        due_date=data.get('due_date'),
        template_id=data.get('template_id')
    )
    
    try:
        db.session.add(invoice)
        db.session.flush()  # To get the invoice ID
        
        # Add invoice items
        if 'items' in data:
            for item_data in data['items']:
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=item_data['description'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price'],
                    tax_rate=item_data.get('tax_rate', 0)
                )
                db.session.add(item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Invoice created successfully',
            'invoice': invoice.to_dict()
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database integrity error', 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create invoice', 'message': str(e)}), 500

@invoices_bp.route('/<int:invoice_id>', methods=['PUT'])
@jwt_required()
def update_invoice(invoice_id):
    """Update an existing invoice"""
    current_user_id = get_jwt_identity()
    
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user_id).first()
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    schema = InvoiceSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Check if invoice number conflicts with another invoice
    if data['invoice_number'] != invoice.invoice_number:
        existing_invoice = Invoice.query.filter_by(
            invoice_number=data['invoice_number'],
            user_id=current_user_id
        ).first()
        
        if existing_invoice:
            return jsonify({'error': 'Invoice number already exists'}), 400
    
    # Update invoice fields
    invoice.invoice_number = data['invoice_number']
    invoice.company_name = data['company_name']
    invoice.company_address = data.get('company_address')
    invoice.company_tax_id = data.get('company_tax_id')
    invoice.company_phone = data.get('company_phone')
    invoice.company_email = data.get('company_email')
    invoice.customer_name = data['customer_name']
    invoice.customer_address = data.get('customer_address')
    invoice.customer_tax_id = data.get('customer_tax_id')
    invoice.customer_phone = data.get('customer_phone')
    invoice.customer_email = data.get('customer_email')
    invoice.subtotal = data.get('subtotal')
    invoice.tax_amount = data.get('tax_amount')
    invoice.total_amount = data['total_amount']
    invoice.currency = data.get('currency', 'VND')
    invoice.invoice_date = data.get('invoice_date')
    invoice.due_date = data.get('due_date')
    invoice.template_id = data.get('template_id')
    
    try:
        # Update items
        if 'items' in data:
            # Remove existing items
            InvoiceItem.query.filter_by(invoice_id=invoice.id).delete()
            
            # Add new items
            for item_data in data['items']:
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=item_data['description'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price'],
                    tax_rate=item_data.get('tax_rate', 0)
                )
                db.session.add(item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Invoice updated successfully',
            'invoice': invoice.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update invoice', 'message': str(e)}), 500

@invoices_bp.route('/<int:invoice_id>', methods=['DELETE'])
@jwt_required()
def delete_invoice(invoice_id):
    """Delete an invoice"""
    current_user_id = get_jwt_identity()
    
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user_id).first()
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    
    try:
        db.session.delete(invoice)
        db.session.commit()
        
        return jsonify({'message': 'Invoice deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete invoice', 'message': str(e)}), 500

@invoices_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_invoice_stats():
    """Get invoice statistics for the current user"""
    current_user_id = get_jwt_identity()
    
    # Total invoices
    total_invoices = Invoice.query.filter_by(user_id=current_user_id).count()
    
    # Invoices by status
    status_counts = db.session.query(
        Invoice.status,
        db.func.count(Invoice.id)
    ).filter_by(user_id=current_user_id).group_by(Invoice.status).all()
    
    # Total amount
    total_amount = db.session.query(
        db.func.sum(Invoice.total_amount)
    ).filter_by(user_id=current_user_id).scalar() or 0
    
    # Recent invoices (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_invoices = Invoice.query.filter(
        Invoice.user_id == current_user_id,
        Invoice.created_at >= thirty_days_ago
    ).count()
    
    return jsonify({
        'total_invoices': total_invoices,
        'status_counts': {status: count for status, count in status_counts},
        'total_amount': float(total_amount),
        'recent_invoices': recent_invoices
    })