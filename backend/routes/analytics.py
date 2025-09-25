from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Invoice, InvoiceItem, User
from sqlalchemy import func, extract, and_
from datetime import datetime, timedelta
from decimal import Decimal

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for the current user"""
    current_user_id = get_jwt_identity()
    
    # Base query for user's invoices
    base_query = Invoice.query.filter_by(user_id=current_user_id)
    
    # Total invoices
    total_invoices = base_query.count()
    
    # Pending invoices
    pending_invoices = base_query.filter_by(status='pending').count()
    
    # Paid invoices
    paid_invoices = base_query.filter_by(status='paid').count()
    
    # Overdue invoices
    overdue_invoices = base_query.filter(
        and_(Invoice.due_date < datetime.now().date(), Invoice.status != 'paid')
    ).count()
    
    # Total revenue (paid invoices)
    total_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
        and_(Invoice.user_id == current_user_id, Invoice.status == 'paid')
    ).scalar() or Decimal('0')
    
    # Pending revenue
    pending_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
        and_(Invoice.user_id == current_user_id, Invoice.status == 'pending')
    ).scalar() or Decimal('0')
    
    # This month's revenue
    current_month = datetime.now().replace(day=1)
    monthly_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
        and_(
            Invoice.user_id == current_user_id,
            Invoice.status == 'paid',
            Invoice.invoice_date >= current_month
        )
    ).scalar() or Decimal('0')
    
    # Recent invoices (last 5)
    recent_invoices = base_query.order_by(Invoice.created_at.desc()).limit(5).all()
    
    return jsonify({
        'summary': {
            'total_invoices': total_invoices,
            'pending_invoices': pending_invoices,
            'paid_invoices': paid_invoices,
            'overdue_invoices': overdue_invoices,
            'total_revenue': str(total_revenue),
            'pending_revenue': str(pending_revenue),
            'monthly_revenue': str(monthly_revenue)
        },
        'recent_invoices': [
            {
                'id': inv.id,
                'invoice_number': inv.invoice_number,
                'customer_name': inv.customer_name,
                'total_amount': str(inv.total_amount),
                'status': inv.status,
                'due_date': inv.due_date.isoformat() if inv.due_date else None
            } for inv in recent_invoices
        ]
    })

@analytics_bp.route('/revenue', methods=['GET'])
@jwt_required()
def get_revenue_analytics():
    """Get revenue analytics with time periods"""
    current_user_id = get_jwt_identity()
    period = request.args.get('period', 'monthly')  # daily, weekly, monthly, yearly
    year = request.args.get('year', datetime.now().year, type=int)
    
    base_query = db.session.query(
        Invoice.invoice_date,
        func.sum(Invoice.total_amount).label('revenue')
    ).filter(
        and_(
            Invoice.user_id == current_user_id,
            Invoice.status == 'paid',
            extract('year', Invoice.invoice_date) == year
        )
    )
    
    if period == 'monthly':
        # Group by month
        revenue_data = base_query.group_by(
            extract('month', Invoice.invoice_date)
        ).all()
        
        # Format monthly data
        monthly_data = {}
        for item in revenue_data:
            month = item[0].month if item[0] else 1
            monthly_data[month] = str(item[1])
        
        # Fill missing months with 0
        result = []
        for month in range(1, 13):
            result.append({
                'period': f"{year}-{month:02d}",
                'revenue': monthly_data.get(month, '0')
            })
        
        return jsonify({
            'period': period,
            'year': year,
            'data': result
        })
    
    elif period == 'yearly':
        # Group by year
        yearly_query = db.session.query(
            extract('year', Invoice.invoice_date).label('year'),
            func.sum(Invoice.total_amount).label('revenue')
        ).filter(
            and_(
                Invoice.user_id == current_user_id,
                Invoice.status == 'paid'
            )
        ).group_by(extract('year', Invoice.invoice_date)).all()
        
        result = [
            {
                'period': str(int(item.year)),
                'revenue': str(item.revenue)
            } for item in yearly_query
        ]
        
        return jsonify({
            'period': period,
            'data': result
        })

@analytics_bp.route('/invoice-status', methods=['GET'])
@jwt_required()
def get_invoice_status_report():
    """Get invoice status distribution"""
    current_user_id = get_jwt_identity()
    
    status_data = db.session.query(
        Invoice.status,
        func.count(Invoice.id).label('count'),
        func.sum(Invoice.total_amount).label('total')
    ).filter_by(user_id=current_user_id).group_by(Invoice.status).all()
    
    result = [
        {
            'status': item.status,
            'count': item.count,
            'total_amount': str(item.total or Decimal('0'))
        } for item in status_data
    ]
    
    return jsonify({
        'status_distribution': result
    })

@analytics_bp.route('/customer-analytics', methods=['GET'])
@jwt_required()
def get_customer_analytics():
    """Get customer analytics - top customers by revenue"""
    current_user_id = get_jwt_identity()
    
    customer_data = db.session.query(
        Invoice.customer_name,
        func.count(Invoice.id).label('invoice_count'),
        func.sum(Invoice.total_amount).label('total_revenue')
    ).filter_by(user_id=current_user_id).group_by(
        Invoice.customer_name
    ).order_by(func.sum(Invoice.total_amount).desc()).limit(10).all()
    
    result = [
        {
            'customer_name': item.customer_name,
            'invoice_count': item.invoice_count,
            'total_revenue': str(item.total_revenue)
        } for item in customer_data
    ]
    
    return jsonify({
        'top_customers': result
    })

@analytics_bp.route('/growth', methods=['GET'])
@jwt_required()
def get_growth_metrics():
    """Get growth metrics comparing periods"""
    current_user_id = get_jwt_identity()
    
    # Current month
    now = datetime.now()
    current_month_start = now.replace(day=1)
    
    # Previous month
    if now.month == 1:
        prev_month_start = now.replace(year=now.year-1, month=12, day=1)
        prev_month_end = now.replace(day=1) - timedelta(days=1)
    else:
        prev_month_start = now.replace(month=now.month-1, day=1)
        prev_month_end = current_month_start - timedelta(days=1)
    
    # Current month metrics
    current_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
        and_(
            Invoice.user_id == current_user_id,
            Invoice.status == 'paid',
            Invoice.invoice_date >= current_month_start
        )
    ).scalar() or Decimal('0')
    
    current_invoices = db.session.query(func.count(Invoice.id)).filter(
        and_(
            Invoice.user_id == current_user_id,
            Invoice.created_at >= current_month_start
        )
    ).scalar() or 0
    
    # Previous month metrics
    prev_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
        and_(
            Invoice.user_id == current_user_id,
            Invoice.status == 'paid',
            Invoice.invoice_date >= prev_month_start,
            Invoice.invoice_date <= prev_month_end
        )
    ).scalar() or Decimal('0')
    
    prev_invoices = db.session.query(func.count(Invoice.id)).filter(
        and_(
            Invoice.user_id == current_user_id,
            Invoice.created_at >= prev_month_start,
            Invoice.created_at <= prev_month_end
        )
    ).scalar() or 0
    
    # Calculate growth rates
    revenue_growth = 0
    if prev_revenue > 0:
        revenue_growth = float((current_revenue - prev_revenue) / prev_revenue * 100)
    
    invoice_growth = 0
    if prev_invoices > 0:
        invoice_growth = float((current_invoices - prev_invoices) / prev_invoices * 100)
    
    return jsonify({
        'current_month': {
            'revenue': str(current_revenue),
            'invoice_count': current_invoices
        },
        'previous_month': {
            'revenue': str(prev_revenue),
            'invoice_count': prev_invoices
        },
        'growth': {
            'revenue_growth_percent': round(revenue_growth, 2),
            'invoice_growth_percent': round(invoice_growth, 2)
        }
    })

# Blueprint registration
bp = analytics_bp