from flask import Blueprint

# Import all route blueprints
from .auth import bp as auth_bp
from .invoices import invoices_bp
from .templates import templates_bp
from .ocr import ocr_bp

def register_routes(app):
    """Register all route blueprints with the Flask app"""
    
    # API version prefix
    api_prefix = '/api/v1'
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(invoices_bp, url_prefix=f'{api_prefix}/invoices')
    app.register_blueprint(templates_bp, url_prefix=f'{api_prefix}/templates')
    app.register_blueprint(ocr_bp, url_prefix=f'{api_prefix}/ocr')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Invoice Management API is running'}