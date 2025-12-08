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

    def get_all_invoices(self, limit: int = 100) -> List[Dict]:
        """Get all invoices from database"""
        try:
            conn = self.connect()
            if not conn:
                logger.error("❌ No database connection")
                return []
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id, filename, invoice_code, invoice_type,
                    buyer_name, seller_name, total_amount, 
                    confidence_score, created_at, invoice_date,
                    buyer_tax_id, seller_tax_id, buyer_address, seller_address,
                    items, currency, subtotal, tax_amount, tax_percentage,
                    total_amount_value, transaction_id, payment_method,
                    payment_account, invoice_time, due_date, raw_text
                FROM invoices 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert rows to dictionaries
            invoices = []
            for row in rows:
                # Safe field extraction with defaults
                created_at = row[8] or datetime.now().isoformat()
                invoice_date = row[9] or row[23] or created_at  # Try invoice_date, invoice_time, or created_at
                
                invoice = {
                    'id': row[0],
                    'filename': row[1] or 'unknown.jpg',
                    'invoice_code': row[2] or 'UNKNOWN',
                    'invoice_type': row[3] or 'general',
                    'buyer_name': row[4] or 'Unknown',
                    'seller_name': row[5] or 'Unknown',
                    'total_amount': row[6] or '0 VND',
                    'confidence_score': row[7] if row[7] is not None else 0.0,
                    'confidence': row[7] if row[7] is not None else 0.85,  # Frontend expects 'confidence'
                    'created_at': created_at,
                    'processed_at': created_at,  # Frontend expects 'processed_at'
                    'invoice_date': invoice_date,
                    'date': invoice_date,  # Frontend expects 'date'
                    'buyer_tax_id': row[10],
                    'seller_tax_id': row[11],
                    'buyer_address': row[12],
                    'seller_address': row[13],
                    'items': row[14],
                    'currency': row[15],
                    'subtotal': row[16],
                    'tax_amount': row[17],
                    'tax_percentage': row[18],
                    'total_amount_value': row[19],
                    'transaction_id': row[20],
                    'payment_method': row[21],
                    'payment_account': row[22],
                    'invoice_time': row[23],
                    'due_date': row[24],
                    'raw_text': row[25][:200] if row[25] else None  # Truncate raw_text
                }
                invoices.append(invoice)
            
            logger.info(f"✅ Returning {len(invoices)} invoices from database")
            return invoices
            
        except Exception as e:
            logger.error(f"❌ Error getting invoices: {e}")
            return []

    def search_invoices(self, query: str, limit: int = 20) -> List[Dict]:
        """Search invoices by invoice_code, buyer_name, seller_name"""
        try:
            conn = self.connect()
            if not conn:
                return []
            
            cursor = conn.cursor()
            search_pattern = f"%{query}%"
            
            cursor.execute("""
                SELECT 
                    id, filename, invoice_code, invoice_type,
                    buyer_name, seller_name, total_amount, 
                    confidence_score, created_at, invoice_date,
                    transaction_id, payment_method
                FROM invoices 
                WHERE 
                    invoice_code LIKE ? OR
                    buyer_name LIKE ? OR
                    seller_name LIKE ? OR
                    transaction_id LIKE ?
                ORDER BY created_at DESC 
                LIMIT ?
            """, (search_pattern, search_pattern, search_pattern, search_pattern, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'id': row[0],
                    'filename': row[1],
                    'invoice_code': row[2],
                    'invoice_type': row[3],
                    'buyer_name': row[4],
                    'seller_name': row[5],
                    'total_amount': row[6],
                    'confidence_score': row[7] or 0.0,
                    'created_at': row[8],
                    'invoice_date': row[9],
                    'transaction_id': row[10],
                    'payment_method': row[11]
                })
            
            logger.info(f"✅ Found {len(results)} invoices matching '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching invoices: {e}")
            return []

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