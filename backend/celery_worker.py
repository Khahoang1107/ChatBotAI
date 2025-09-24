#!/usr/bin/env python3
"""
Celery Worker Entry Point for Event-Driven Processing
"""
import os
import sys
from celery import Celery

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask app and Celery config
from app import app
from celery_config import make_celery

# Create Celery worker
celery = make_celery(app)

if __name__ == '__main__':
    # Start Celery worker
    celery.start()