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
from routes import auth, invoices, templates, ocr, analytics, ai_training

# Register blueprints
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(invoices.bp, url_prefix='/api/invoices')
app.register_blueprint(templates.bp, url_prefix='/api/templates')
app.register_blueprint(ocr.bp, url_prefix='/api/ocr')
app.register_blueprint(analytics.bp, url_prefix='/api/analytics')
app.register_blueprint(ai_training.ai_training_bp, url_prefix='/api/ai-training')

# Health check endpoint
@app.route('/api/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'backend-api',
        'database': 'connected' if db.engine else 'disconnected'
    }

# Root endpoint
@app.route('/')
def root():
    return {
        'message': 'Invoice Management Backend API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/auth/*',
            'invoices': '/api/invoices/*',
            'templates': '/api/templates/*',
            'ocr': '/api/ocr/*',
            'analytics': '/api/analytics/*'
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
@app.before_first_request
def create_tables():
    """Create database tables if they don't exist"""
    try:
        db.create_all()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")

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