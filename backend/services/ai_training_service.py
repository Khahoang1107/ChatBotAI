"""
AI Training Service - Handles AI training and user correction operations
"""
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)


class AITrainingService:
    """Service for handling AI training operations"""

    def __init__(self, db_tools=None):
        self.db_tools = db_tools

    def submit_user_correction(self, correction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit user correction for AI training

        Args:
            correction: Correction data dictionary

        Returns:
            Dict containing submission result
        """
        logger.info(f"📝 Received user correction: {correction}")

        # Validate required fields
        required_fields = ['original_text', 'corrected_amount', 'correction_type']
        for field in required_fields:
            if field not in correction:
                raise Exception(f"Missing required field: {field}")

        correction_id = None

        # Store correction in database for training
        if self.db_tools:
            try:
                conn = self.db_tools.connect()
                if conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO user_corrections
                            (original_text, corrected_amount, invoice_type, user_id, correction_type,
                             confidence_score, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            correction.get('original_text', ''),
                            correction.get('corrected_amount', ''),
                            correction.get('invoice_type', 'general'),
                            correction.get('user_id', 'anonymous'),
                            correction.get('correction_type', 'general'),
                            1.0,  # High confidence for user corrections
                            datetime.now(),
                            datetime.now()
                        ))
                        result = cursor.fetchone()
                        if result:
                            correction_id = result[0]
                            conn.commit()
                            logger.info(f"✅ User correction stored with ID: {correction_id}")
                        else:
                            conn.commit()
                            logger.warning("⚠️ User correction inserted but RETURNING failed")
            except Exception as db_err:
                logger.error(f"❌ Database error storing correction: {db_err}")
                # Continue without failing - correction can still be processed

        # Update training patterns based on correction
        if correction.get('correction_type') == 'dash_amount_recognition':
            # Extract patterns from the correction
            self._update_dash_patterns_from_correction(correction)

        return {
            "success": True,
            "message": "User correction submitted successfully",
            "correction_id": correction_id
        }

    def get_dash_patterns(self) -> Dict[str, Any]:
        """
        Get learned dash amount patterns for AI training

        Returns:
            Dict containing patterns data
        """
        logger.info("📊 Getting dash patterns for training")

        patterns = []

        # Get patterns from user corrections
        if self.db_tools:
            try:
                conn = self.db_tools.connect()
                if conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT original_text, corrected_amount, invoice_type,
                                   COUNT(*) as correction_count,
                                   AVG(confidence_score) as avg_confidence,
                                   MAX(created_at) as last_updated
                            FROM user_corrections
                            WHERE correction_type = 'dash_amount_recognition'
                            GROUP BY original_text, corrected_amount, invoice_type
                            ORDER BY correction_count DESC, last_updated DESC
                            LIMIT 50
                        """)

                        results = cursor.fetchall()

                        for row in results:
                            original_text, corrected_amount, invoice_type, count, avg_confidence, last_updated = row

                            # Generate pattern from the correction
                            pattern = self._generate_pattern_from_correction(original_text, corrected_amount)

                            if pattern:
                                patterns.append({
                                    'pattern': pattern,
                                    'confidence': min(avg_confidence + (count * 0.1), 1.0),  # Boost confidence with more corrections
                                    'description': f'Learned from {count} user correction(s)',
                                    'validated_by_corrections': count,
                                    'invoice_type': invoice_type,
                                    'last_updated': last_updated.isoformat() if hasattr(last_updated, 'isoformat') else str(last_updated)
                                })
            except Exception as db_err:
                logger.error(f"❌ Database error getting dash patterns: {db_err}")

        # Add default patterns if no learned patterns
        if not patterns:
            patterns = [
                {
                    'pattern': r'(?:^\s*-\s*|-\s+)([0-9,\.]+)(?:\s*(?:vnd|đ|vnđ))?',
                    'confidence': 0.8,
                    'description': 'Default: Line starting with dash',
                    'validated_by_corrections': 0,
                    'invoice_type': 'general'
                },
                {
                    'pattern': r'(\d+(?:,\d{3})*(?:\.\d{2})?)(?:\s*(?:vnd|đ|vnđ))?\s*$',
                    'confidence': 0.6,
                    'description': 'Default: Amount at end of line',
                    'validated_by_corrections': 0,
                    'invoice_type': 'general'
                }
            ]

        return {
            "success": True,
            "patterns": patterns,
            "count": len(patterns)
        }

    def _update_dash_patterns_from_correction(self, correction: Dict[str, Any]):
        """
        Update dash patterns based on user correction
        """
        try:
            original_text = correction.get('original_text', '')
            corrected_amount = correction.get('corrected_amount', '')

            # Generate pattern from this correction
            pattern = self._generate_pattern_from_correction(original_text, corrected_amount)

            if pattern:
                logger.info(f"📝 Generated pattern from correction: {pattern}")
            else:
                logger.warning("⚠️ Could not generate pattern from correction")

        except Exception as e:
            logger.error(f"❌ Error updating dash patterns: {str(e)}")

    def _generate_pattern_from_correction(self, original_text: str, corrected_amount: str) -> Optional[str]:
        """
        Generate regex pattern from user correction

        Args:
            original_text: The OCR text
            corrected_amount: The corrected amount string

        Returns:
            Regex pattern string or None if cannot generate
        """
        import re

        # Clean the corrected amount for matching
        clean_amount = corrected_amount.replace(',', '').replace('.', '').replace(' ', '')

        # Look for the amount in the original text
        amount_patterns = [
            r'\b' + re.escape(clean_amount) + r'\b',  # Exact match
            r'\b\d+\b',  # Any number that matches
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, original_text)
            if match:
                found_amount = match.group(0)

                # Check if the amount appears after a dash
                amount_pos = original_text.find(found_amount)

                # Look for dash before the amount (within 10 characters)
                dash_search_start = max(0, amount_pos - 10)
                dash_search_text = original_text[dash_search_start:amount_pos]

                if '-' in dash_search_text:
                    # Found dash before amount - create dash pattern
                    return r'(?:^\s*-\s*|-\s+)([0-9,\.]+)(?:\s*(?:vnd|đ|vnđ))?'

        # If no dash found, check if amount is at end of line
        lines = original_text.split('\n')
        for line in lines:
            if clean_amount in line.replace(',', '').replace('.', '').replace(' ', ''):
                # Check if amount is at end of line
                line_end = line.strip()
                if line_end.replace(',', '').replace('.', '').replace(' ', '').endswith(clean_amount):
                    return r'([0-9,\.]+)(?:\s*(?:vnd|đ|vnđ))?\s*$'

        return None