#!/usr/bin/env python3
"""
Startup script for Invoice Chat Backend
Chạy: python run_backend.py
"""

import os
import sys
import subprocess

# Change to backend directory
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)

# Add backend to path
sys.path.insert(0, backend_dir)

# Import and run
import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
