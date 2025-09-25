from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object('config.Config')

# Enable CORS for frontend communication
CORS(app, origins=['http://localhost:5174', 'http://localhost:3000'])

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Import models (after db initialization)
from models import user, invoice, template, ocr_result

# Import routes
from routes import auth, invoices, templates, ocr, analytics

# Remove Celery initialization for simplicity
# from celery_config import make_celery
# celery = make_celery(app)

# Register blueprints
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(invoices.invoices_bp, url_prefix='/api/invoices')
app.register_blueprint(templates.templates_bp, url_prefix='/api/templates')
app.register_blueprint(ocr.ocr_bp, url_prefix='/api/ocr')
app.register_blueprint(analytics.analytics_bp, url_prefix='/api/analytics')

# Health check endpoint
@app.route('/api/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'backend-api',
        'database': 'connected' if db.engine else 'disconnected'
    }

# API Documentation endpoint
@app.route('/api/docs')
def api_docs():
    """Serve API documentation"""
    docs_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Invoice AI - API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1, h2, h3 { color: #333; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { display: inline-block; padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }
            .get { background-color: #61affe; }
            .post { background-color: #49cc90; }
            .put { background-color: #fca130; }
            .delete { background-color: #f93e3e; }
            code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; }
            pre { background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>🚀 Invoice AI System - API Documentation</h1>
        <p><strong>Base URL:</strong> <code>http://localhost:5000</code></p>
        <p><strong>Authentication:</strong> JWT Bearer Token</p>
        
        <h2>📊 Quick Start</h2>
        <pre>
# 1. Register a new user
curl -X POST http://localhost:5000/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"username":"demo","email":"demo@example.com","password":"password123"}'

# 2. Login to get token
curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username":"demo","password":"password123"}'

# 3. Use token to access protected endpoints
curl http://localhost:5000/api/invoices \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
        </pre>
        
        <h2>🔐 Authentication Endpoints</h2>
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/auth/register</strong><br>
            Register a new user account
        </div>
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/auth/login</strong><br>
            Login and receive JWT tokens
        </div>
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/auth/profile</strong><br>
            Get current user profile (requires auth)
        </div>
        
        <h2>📄 Invoice Management</h2>
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/invoices</strong><br>
            List all invoices (supports pagination: ?page=1&per_page=20)
        </div>
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/invoices</strong><br>
            Create a new invoice
        </div>
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/invoices/{id}</strong><br>
            Get specific invoice by ID
        </div>
        <div class="endpoint">
            <span class="method put">PUT</span> <strong>/api/invoices/{id}</strong><br>
            Update existing invoice
        </div>
        <div class="endpoint">
            <span class="method delete">DELETE</span> <strong>/api/invoices/{id}</strong><br>
            Delete invoice
        </div>
        
        <h2>📋 Template Management</h2>
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/templates</strong><br>
            List all invoice templates
        </div>
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/templates</strong><br>
            Create new template
        </div>
        
        <h2>🔍 OCR Processing</h2>
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/ocr/process</strong><br>
            Process invoice image with OCR (multipart/form-data)
        </div>
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/ocr-async/process</strong><br>
            Async OCR processing for large files
        </div>
        
        <h2>📊 Analytics & Reports</h2>
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/analytics/dashboard</strong><br>
            Get dashboard statistics and KPIs
        </div>
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/analytics/revenue</strong><br>
            Revenue analytics (?period=monthly&year=2024)
        </div>
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/analytics/customer-analytics</strong><br>
            Top customers by revenue
        </div>
        
        <h2>🤖 AI & Chat</h2>
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/hybrid-chat/message</strong><br>
            Send message to AI chatbot
        </div>
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/ai-training/train</strong><br>
            Train AI model with new data
        </div>
        
        <h2>🔧 System</h2>
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/health</strong><br>
            Check system health
        </div>
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/</strong><br>
            API overview and endpoints list
        </div>
        
        <hr>
        <p><strong>📝 Full Documentation:</strong> <a href="https://github.com/your-repo">GitHub README</a></p>
        <p><strong>🐛 Report Issues:</strong> <a href="https://github.com/your-repo/issues">GitHub Issues</a></p>
    </body>
    </html>
    """
    from flask import Response
    return Response(docs_content, mimetype='text/html')

# Root endpoint with comprehensive API documentation
@app.route('/')
def root():
    return {
        'service': 'Invoice Management Backend API',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'documentation': '/api/docs',
        'health_check': '/api/health',
        'endpoints': {
            'authentication': {
                'base_url': '/api/auth',
                'endpoints': [
                    'POST /api/auth/register - Register new user',
                    'POST /api/auth/login - User login',
                    'POST /api/auth/refresh - Refresh JWT token',
                    'GET /api/auth/profile - Get user profile'
                ]
            },
            'invoices': {
                'base_url': '/api/invoices',
                'endpoints': [
                    'GET /api/invoices - List all invoices (paginated)',
                    'GET /api/invoices/{id} - Get invoice by ID',
                    'POST /api/invoices - Create new invoice',
                    'PUT /api/invoices/{id} - Update invoice',
                    'DELETE /api/invoices/{id} - Delete invoice'
                ]
            },
            'templates': {
                'base_url': '/api/templates',
                'endpoints': [
                    'GET /api/templates - List all templates',
                    'GET /api/templates/{id} - Get template by ID',
                    'POST /api/templates - Create new template',
                    'PUT /api/templates/{id} - Update template',
                    'DELETE /api/templates/{id} - Delete template'
                ]
            },
            'ocr': {
                'base_url': '/api/ocr',
                'endpoints': [
                    'POST /api/ocr/process - Process invoice image',
                    'GET /api/ocr/results/{id} - Get OCR results'
                ]
            },
            'analytics': {
                'base_url': '/api/analytics',
                'endpoints': [
                    'GET /api/analytics/dashboard - Dashboard statistics',
                    'GET /api/analytics/revenue - Revenue analytics',
                    'GET /api/analytics/invoice-status - Status distribution',
                    'GET /api/analytics/customer-analytics - Customer metrics',
                    'GET /api/analytics/growth - Growth metrics'
                ]
            }
        },
        'authentication': {
            'type': 'JWT Bearer Token',
            'header': 'Authorization: Bearer {token}',
            'get_token': 'POST /api/auth/login'
        },
        'examples': {
            'curl_health': 'curl http://localhost:5000/api/health',
            'curl_login': 'curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"user","password":"pass"}\'',
            'curl_invoices': 'curl http://localhost:5000/api/invoices -H "Authorization: Bearer {token}"'
        }
    }

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500

@app.errorhandler(400)
def bad_request(error):
    return {'error': 'Bad request'}, 400

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {'error': 'Token has expired'}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {'error': 'Invalid token'}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {'error': 'Authorization token required'}, 401

# Database initialization
def create_tables():
    """Create database tables if they don't exist"""
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")

# Initialize database tables
create_tables()

if __name__ == '__main__':
    print("🚀 Starting Invoice Management Backend API...")
    print(f"📊 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"🔗 API URL: http://localhost:5000")
    print(f"📝 Swagger UI: http://localhost:5000/api/docs")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )