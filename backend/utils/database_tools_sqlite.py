"""
Simple SQLite Database Tools for ChatBotAI
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class DatabaseTools:
    """Simple SQLite database tools"""

    def __init__(self, connection_string: str = None):
        """Initialize SQLite database connection"""
        if connection_string is None:
            connection_string = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")

        # Convert from SQLAlchemy format to SQLite path
        if connection_string.startswith("sqlite:///"):
            self.db_path = connection_string.replace("sqlite:///", "")
        else:
            self.db_path = "chatbot.db"

        logger.info(f"Using SQLite database: {self.db_path}")

    def connect(self):
        """Get SQLite connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            return None

    def get_all_invoices(self, limit: int = 20) -> List[Dict]:
        """Get all invoices (mock data for now)"""
        try:
            # Return mock data since we don't have real tables yet
            mock_invoices = [
                {
                    'id': 1,
                    'filename': 'sample_invoice.jpg',
                    'invoice_code': 'INV-001',
                    'buyer_name': 'Sample Buyer',
                    'seller_name': 'Sample Seller',
                    'total_amount': '1000000 VND',
                    'confidence_score': 0.95,
                    'created_at': datetime.now().isoformat(),
                    'invoice_type': 'general'
                }
            ]
            logger.info(f"✅ Returning {len(mock_invoices)} mock invoices")
            return mock_invoices[:limit]
        except Exception as e:
            logger.error(f"❌ Error getting invoices: {e}")
            return []

    def search_invoices(self, query: str, limit: int = 20) -> List[Dict]:
        """Search invoices (mock implementation)"""
        all_invoices = self.get_all_invoices()
        results = [inv for inv in all_invoices if query.lower() in str(inv).lower()]
        return results[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics (mock)"""
        return {
            'total_invoices': 1,
            'avg_confidence': 0.95,
            'invoice_types': {'general': 1},
            'recent_7days': 1,
            'total_amount_sum': 1000000
        }

    def health_check(self) -> Dict[str, Any]:
        """Database health check"""
        try:
            conn = self.connect()
            if conn:
                conn.close()
                return {
                    "status": "healthy",
                    "message": "SQLite connection successful",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Cannot connect to SQLite",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"SQLite health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

# Global instance
_db_tools_instance = None

def get_database_tools() -> DatabaseTools:
    """Get or create DatabaseTools singleton"""
    global _db_tools_instance
    if _db_tools_instance is None:
        _db_tools_instance = DatabaseTools()
    return _db_tools_instance