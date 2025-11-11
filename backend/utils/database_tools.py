"""
Database Tools for RAG Chatbot
Provides PostgreSQL query functions for chatbot to access real invoice data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import time
import os

logger = logging.getLogger(__name__)

class DatabaseTools:
    """Tools for querying PostgreSQL database with connection pooling"""
    
    def __init__(self, connection_string: str = None):
        """Initialize database connection pool"""
        if connection_string is None:
            connection_string = os.getenv(
                "DATABASE_URL", 
                "postgresql://postgres:123@localhost:5432/ocr_database_new"
            )
        
        self.connection_string = connection_string
        self.connection_pool = None
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
        # Initialize connection pool
        self._init_connection_pool()
    
    def _init_connection_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,  # Maximum connections in pool
                dsn=self.connection_string,
                cursor_factory=RealDictCursor
            )
            logger.info("✅ Database connection pool initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize connection pool: {e}")
            self.connection_pool = None
    
    def _get_connection_with_retry(self):
        """Get connection from pool with retry logic"""
        if not self.connection_pool:
            logger.error("❌ Connection pool not initialized")
            return None
        
        for attempt in range(self.max_retries):
            try:
                conn = self.connection_pool.getconn()
                # Test connection
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                return conn
            except Exception as e:
                logger.warning(f"❌ Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error("❌ All connection attempts failed")
                    return None
    
    def connect(self):
        """Get database connection from pool"""
        return self._get_connection_with_retry()
    
    def release_connection(self, conn):
        """Return connection to pool"""
        if self.connection_pool and conn:
            try:
                self.connection_pool.putconn(conn)
            except Exception as e:
                logger.warning(f"❌ Error releasing connection: {e}")
    
    def close(self):
        """Close connection pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")
    
    def get_all_invoices(self, limit: int = 50) -> List[Dict]:
        """Get all invoices from database"""
        conn = None
        try:
            conn = self.connect()
            if not conn:
                return []
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id, filename, invoice_code, invoice_type,
                        buyer_name, seller_name, total_amount, 
                        confidence_score, created_at, invoice_date,
                        buyer_tax_id, seller_tax_id, buyer_address, seller_address,
                        items, currency, subtotal, tax_amount, tax_percentage,
                        total_amount_value, transaction_id, payment_method, 
                        payment_account, invoice_time, due_date
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
        finally:
            if conn:
                self.release_connection(conn)
    
    def search_invoices(self, query: str, limit: int = 20) -> List[Dict]:
        """Search invoices by keyword"""
        conn = None
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
                        confidence_score, created_at, transaction_id,
                        payment_method, payment_account
                    FROM invoices 
                    WHERE 
                        filename ILIKE %s OR
                        invoice_code ILIKE %s OR
                        buyer_name ILIKE %s OR
                        seller_name ILIKE %s OR
                        invoice_type ILIKE %s OR
                        transaction_id ILIKE %s OR
                        payment_account ILIKE %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (search_pattern, search_pattern, search_pattern, 
                      search_pattern, search_pattern, search_pattern,
                      search_pattern, limit))
                
                results = cursor.fetchall()
                logger.info(f"✅ Found {len(results)} matching invoices for query: '{query}'")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ Error searching invoices: {e}")
            return []
        finally:
            if conn:
                self.release_connection(conn)
    
    def get_invoice_by_filename(self, filename: str) -> Optional[Dict]:
        """Get specific invoice by filename"""
        conn = None
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
                        raw_text, buyer_tax_id, seller_tax_id, 
                        buyer_address, seller_address, items, currency,
                        subtotal, tax_amount, tax_percentage,
                        total_amount_value, transaction_id, payment_method, 
                        payment_account, invoice_time, due_date
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
        finally:
            if conn:
                self.release_connection(conn)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = None
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
        finally:
            if conn:
                self.release_connection(conn)
    
    def get_buyer_summary(self, buyer_name: str) -> Dict[str, Any]:
        """Get summary for specific buyer"""
        conn = None
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
        finally:
            if conn:
                self.release_connection(conn)
    
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
    
    def create_ocr_job(self, job_id: str, filepath: str, filename: str, uploader: str = "unknown", user_id: str = "anonymous"):
        """Create OCR job in database"""
        conn = None
        try:
            conn = self.connect()
            if not conn:
                return False
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ocr_jobs (id, filepath, filename, status, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (job_id, filepath, filename, 'queued'))
            
            conn.commit()
            logger.info(f"✅ OCR job created: {job_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error creating OCR job: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.release_connection(conn)
    
    def get_ocr_job(self, job_id: str) -> Optional[Dict]:
        """Get OCR job status"""
        conn = None
        try:
            conn = self.connect()
            if not conn:
                return None
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, filepath, filename, status, result, error_message, invoice_id, created_at, completed_at
                    FROM ocr_jobs
                    WHERE id = %s
                """, (job_id,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"❌ Error getting OCR job: {e}")
            return None
        finally:
            if conn:
                self.release_connection(conn)
    
    def get_queued_ocr_jobs(self, limit: int = 5) -> List[Dict]:
        """Get queued OCR jobs"""
        conn = None
        try:
            conn = self.connect()
            if not conn:
                return []
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, filepath, filename, status, created_at
                    FROM ocr_jobs
                    WHERE status = 'queued'
                    ORDER BY created_at ASC
                    LIMIT %s
                """, (limit,))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"❌ Error getting queued jobs: {e}")
            return []
        finally:
            if conn:
                self.release_connection(conn)
    
    def update_ocr_job(self, job_id: str, status: str, result: Optional[str] = None, error_message: Optional[str] = None, invoice_id: Optional[int] = None):
        """Update OCR job status"""
        conn = None
        try:
            conn = self.connect()
            if not conn:
                return False
            
            with conn.cursor() as cursor:
                if status == 'completed':
                    cursor.execute("""
                        UPDATE ocr_jobs
                        SET status = %s, result = %s, invoice_id = %s, completed_at = NOW(), updated_at = NOW()
                        WHERE id = %s
                    """, (status, result, invoice_id, job_id))
                elif status == 'failed':
                    cursor.execute("""
                        UPDATE ocr_jobs
                        SET status = %s, error_message = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (status, error_message, job_id))
                else:
                    cursor.execute("""
                        UPDATE ocr_jobs
                        SET status = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (status, job_id))
                
                conn.commit()
                logger.info(f"✅ OCR job updated: {job_id} -> {status}")
                return True
        except Exception as e:
            logger.error(f"❌ Error updating OCR job: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.release_connection(conn)
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute a raw SQL query"""
        conn = None
        try:
            conn = self.connect()
            if not conn:
                return False
            
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
            
            conn.commit()
            logger.info("✅ Query executed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error executing query: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.release_connection(conn)
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health and connection status"""
        conn = None
        try:
            conn = self.connect()
            if not conn:
                return {
                    "status": "unhealthy",
                    "message": "Cannot establish database connection",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            with conn.cursor() as cursor:
                # Test basic connectivity
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                
                # Get basic stats
                cursor.execute("SELECT COUNT(*) as user_count FROM users")
                user_count = cursor.fetchone()['user_count']
                
                cursor.execute("SELECT COUNT(*) as invoice_count FROM invoices")
                invoice_count = cursor.fetchone()['invoice_count']
                
                return {
                    "status": "healthy",
                    "message": "Database connection successful",
                    "user_count": user_count,
                    "invoice_count": invoice_count,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Database health check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            if conn:
                self.release_connection(conn)

# Global instance
_db_tools_instance = None

def get_database_tools() -> DatabaseTools:
    """Get or create DatabaseTools singleton"""
    global _db_tools_instance
    if _db_tools_instance is None:
        _db_tools_instance = DatabaseTools()
    return _db_tools_instance
