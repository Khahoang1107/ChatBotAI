"""
Start FastAPI backend with proper configuration
"""

import os
import sys

# Set working directory
os.chdir('f:/DoAnCN/fastapi_backend')
sys.path.insert(0, 'f:/DoAnCN/fastapi_backend')

print("🚀 Starting FastAPI Backend...")
print("=" * 60)
print(f"   Working dir: {os.getcwd()}")
print(f"   Python path: {sys.path[0]}")
print("=" * 60)

# Import and run
from main import app
import uvicorn

# Run server
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8001,  # Use 8001 temporarily
    log_level="info",
    access_log=True
)
