"""
Database Tools for RAG Chatbot
Provides PostgreSQL query functions for chatbot to access real invoice data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseTools:
    """Tools for querying PostgreSQL database"""
    
    def __init__(self, connection_string: str = "postgresql://postgres:123@localhost:5432/ocr_database"):
        """Initialize database connection"""
        self.connection_string = connection_string
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            if not self.connection or self.connection.closed:
                self.connection = psycopg2.connect(
                    self.connection_string,
                    cursor_factory=RealDictCursor
                )
                logger.info("✅ Database connection established")
            return self.connection
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("Database connection closed")
    
    def get_all_invoices(self, limit: int = 50) -> List[Dict]:
        """Get all invoices from database"""
        try:
            conn = self.connect()
            if not conn:
                return []
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id, filename, invoice_code, invoice_type,
                        buyer_name, seller_name, total_amount, 
                        confidence_score, created_at, invoice_date
                    FROM invoices 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
                
                invoices = cursor.fetchall()
                logger.info(f"✅ Found {len(invoices)} invoices in database")
                return [dict(invoice) for invoice in invoices]
                
        except Exception as e:
            logger.error(f"❌ Error getting invoices: {e}")
            return []
    
    def search_invoices(self, query: str, limit: int = 20) -> List[Dict]:
        """Search invoices by keyword"""
        try:
            conn = self.connect()
            if not conn:
                return []
            
            search_pattern = f"%{query}%"
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id, filename, invoice_code, invoice_type,
                        buyer_name, seller_name, total_amount,
                        confidence_score, created_at
                    FROM invoices 
                    WHERE 
                        filename ILIKE %s OR
                        invoice_code ILIKE %s OR
                        buyer_name ILIKE %s OR
                        seller_name ILIKE %s OR
                        invoice_type ILIKE %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (search_pattern, search_pattern, search_pattern, 
                      search_pattern, search_pattern, limit))
                
                results = cursor.fetchall()
                logger.info(f"✅ Found {len(results)} matching invoices for query: '{query}'")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ Error searching invoices: {e}")
            return []
    
    def get_invoice_by_filename(self, filename: str) -> Optional[Dict]:
        """Get specific invoice by filename"""
        try:
            conn = self.connect()
            if not conn:
                return None
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id, filename, invoice_code, invoice_type,
                        buyer_name, seller_name, total_amount,
                        confidence_score, created_at, invoice_date,
                        raw_text
                    FROM invoices 
                    WHERE filename ILIKE %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (f"%{filename}%",))
                
                invoice = cursor.fetchone()
                if invoice:
                    logger.info(f"✅ Found invoice: {filename}")
                    return dict(invoice)
                else:
                    logger.warning(f"⚠️ No invoice found for filename: {filename}")
                    return None
                
        except Exception as e:
            logger.error(f"❌ Error getting invoice by filename: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn = self.connect()
            if not conn:
                return {}
            
            stats = {}
            
            with conn.cursor() as cursor:
                # Total invoices
                cursor.execute("SELECT COUNT(*) as count FROM invoices")
                stats['total_invoices'] = cursor.fetchone()['count']
                
                # Average confidence score
                cursor.execute("SELECT AVG(confidence_score) as avg_confidence FROM invoices")
                result = cursor.fetchone()
                stats['avg_confidence'] = float(result['avg_confidence']) if result['avg_confidence'] else 0
                
                # Invoice types breakdown
                cursor.execute("""
                    SELECT invoice_type, COUNT(*) as count 
                    FROM invoices 
                    GROUP BY invoice_type
                """)
                stats['invoice_types'] = {row['invoice_type']: row['count'] for row in cursor.fetchall()}
                
                # Recent activity
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM invoices 
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                """)
                stats['recent_7days'] = cursor.fetchone()['count']
                
                # Total amount sum
                cursor.execute("""
                    SELECT SUM(CAST(REPLACE(REPLACE(total_amount, ',', ''), ' VND', '') AS NUMERIC)) as total
                    FROM invoices 
                    WHERE total_amount IS NOT NULL
                """)
                result = cursor.fetchone()
                stats['total_amount_sum'] = float(result['total']) if result and result['total'] else 0
                
            logger.info(f"✅ Retrieved statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {e}")
            return {}
    
    def get_buyer_summary(self, buyer_name: str) -> Dict[str, Any]:
        """Get summary for specific buyer"""
        try:
            conn = self.connect()
            if not conn:
                return {}
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as invoice_count,
                        SUM(CAST(REPLACE(REPLACE(total_amount, ',', ''), ' VND', '') AS NUMERIC)) as total_spent,
                        AVG(confidence_score) as avg_confidence,
                        MIN(created_at) as first_invoice,
                        MAX(created_at) as last_invoice
                    FROM invoices
                    WHERE buyer_name ILIKE %s
                """, (f"%{buyer_name}%",))
                
                result = cursor.fetchone()
                if result:
                    summary = dict(result)
                    logger.info(f"✅ Buyer summary for '{buyer_name}': {summary}")
                    return summary
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting buyer summary: {e}")
            return {}
    
    def natural_language_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query and return database results"""
        query_lower = query.lower()
        
        # Query intent detection
        if any(keyword in query_lower for keyword in ['tất cả', 'danh sách', 'list', 'all', 'xem dữ liệu']):
            invoices = self.get_all_invoices(limit=20)
            return {
                'type': 'invoice_list',
                'data': invoices,
                'count': len(invoices),
                'message': f"Tìm thấy {len(invoices)} hóa đơn trong database"
            }
        
        elif any(keyword in query_lower for keyword in ['tìm', 'search', 'tìm kiếm']):
            # Extract search term
            search_terms = query_lower.replace('tìm', '').replace('search', '').replace('kiếm', '').strip()
            results = self.search_invoices(search_terms, limit=20)
            return {
                'type': 'search_results',
                'data': results,
                'count': len(results),
                'query': search_terms,
                'message': f"Tìm thấy {len(results)} kết quả cho '{search_terms}'"
            }
        
        elif any(keyword in query_lower for keyword in ['thống kê', 'stats', 'statistics', 'báo cáo']):
            stats = self.get_statistics()
            return {
                'type': 'statistics',
                'data': stats,
                'message': 'Thống kê database'
            }
        
        else:
            # Default: try to search
            results = self.search_invoices(query, limit=10)
            return {
                'type': 'general_search',
                'data': results,
                'count': len(results),
                'message': f"Tìm kiếm với từ khóa '{query}': {len(results)} kết quả"
            }

# Global instance
_db_tools_instance = None

def get_database_tools() -> DatabaseTools:
    """Get or create DatabaseTools singleton"""
    global _db_tools_instance
    if _db_tools_instance is None:
        _db_tools_instance = DatabaseTools()
    return _db_tools_instance
