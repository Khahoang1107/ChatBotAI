"""
Invoice Service - Handles all invoice-related business logic
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from utils.logger import get_logger

logger = get_logger(__name__)


class InvoiceService:
    """Service for handling invoice operations"""

    def __init__(self, db_tools=None):
        self.db_tools = db_tools

    def get_invoice_list(self, time_filter: str = "all", limit: int = 20, search_query: Optional[str] = None) -> Dict[str, Any]:
        """
        Get list of invoices with optional filtering and search

        Args:
            time_filter: Time filter ("all", "today", "yesterday", "week", "month")
            limit: Maximum number of invoices to return
            search_query: Search query string

        Returns:
            Dict containing invoice list and metadata
        """
        if not self.db_tools:
            raise Exception("Database not available")

        logger.info(f"📋 Getting invoices - filter: {time_filter}, limit: {limit}")

        # Get all invoices
        invoices = self.db_tools.get_all_invoices(limit=limit)

        if not invoices:
            return {
                "success": True,
                "message": "Không có hóa đơn nào",
                "data": [],
                "count": 0
            }

        # Filter by time if needed
        if time_filter != "all":
            invoices = self._filter_invoices_by_time(invoices, time_filter)

        # Search if query provided
        if search_query:
            invoices = self._search_invoices(invoices, search_query)

        logger.info(f"✅ Returning {len(invoices)} invoices")

        return {
            "success": True,
            "message": f"Tìm thấy {len(invoices)} hóa đơn",
            "data": invoices,
            "count": len(invoices)
        }

    def get_invoice_detail(self, invoice_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific invoice

        Args:
            invoice_id: Invoice identifier

        Returns:
            Dict containing invoice details
        """
        if not self.db_tools:
            raise Exception("Database not available")

        logger.info(f"📄 Getting invoice: {invoice_id}")

        invoice = self.db_tools.get_invoice_by_filename(invoice_id)

        if not invoice:
            raise Exception(f"Invoice not found: {invoice_id}")

        return {
            "success": True,
            "data": invoice
        }

    def search_invoices(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """
        Search invoices by query

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            Dict containing search results
        """
        if not self.db_tools:
            raise Exception("Database not available")

        logger.info(f"🔍 Searching invoices: {query}")

        results = self.db_tools.search_invoices(query, limit=limit)

        return {
            "success": True,
            "query": query,
            "data": results,
            "count": len(results)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get invoice statistics

        Returns:
            Dict containing statistics data
        """
        if not self.db_tools:
            raise Exception("Database not available")

        logger.info("📊 Getting invoice statistics")

        stats = self.db_tools.get_statistics()

        return {
            "success": True,
            "data": stats
        }

    def _filter_invoices_by_time(self, invoices: List[Dict], time_filter: str) -> List[Dict]:
        """Lọc hóa đơn theo thời gian"""
        from datetime import datetime, timedelta

        now = datetime.now()

        if time_filter == "today":
            today = now.date()
            return [inv for inv in invoices if str(inv.get('created_at', '')).startswith(str(today))]

        elif time_filter == "yesterday":
            yesterday = (now - timedelta(days=1)).date()
            return [inv for inv in invoices if str(inv.get('created_at', '')).startswith(str(yesterday))]

        elif time_filter == "week":
            week_ago = now - timedelta(days=7)
            return [inv for inv in invoices if datetime.fromisoformat(str(inv.get('created_at', '')).replace('Z', '+00:00')) >= week_ago]

        elif time_filter == "month":
            month_ago = now - timedelta(days=30)
            return [inv for inv in invoices if datetime.fromisoformat(str(inv.get('created_at', '')).replace('Z', '+00:00')) >= month_ago]

        return invoices

    def _search_invoices(self, invoices: List[Dict], query: str) -> List[Dict]:
        """Tìm kiếm hóa đơn trong danh sách"""
        query_lower = query.lower()
        results = []

        for inv in invoices:
            if any(query_lower in str(inv.get(field, '')).lower()
                   for field in ['filename', 'invoice_code', 'buyer_name', 'seller_name', 'invoice_type']):
                results.append(inv)

        return results