"""
Admin API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/health")
async def admin_health():
    """Admin health check"""
    return JSONResponse({
        "status": "ok",
        "service": "admin",
        "timestamp": datetime.now().isoformat()
    })

@router.get("/stats")
async def admin_stats():
    """Admin statistics"""
    return JSONResponse({
        "message": "Admin stats not implemented yet",
        "timestamp": datetime.now().isoformat()
    })