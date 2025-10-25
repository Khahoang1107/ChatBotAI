import re
import unicodedata
from typing import List, Dict, Any

class TextProcessor:
    def __init__(self):
        # Vietnamese stopwords
        self.stopwords = {
            'và', 'của', 'có', 'là', 'được', 'một', 'này', 'đó', 'các', 'cho',
            'với', 'từ', 'tại', 'về', 'để', 'trong', 'trên', 'dưới', 'sau',
            'trước', 'giữa', 'bên', 'cạnh', 'gần', 'xa', 'cao', 'thấp'
        }
        
        # Common abbreviations
        self.abbreviations = {
            'hđ': 'hóa đơn',
            'vat': 'thuế giá trị gia tăng',
            'mst': 'mã số thuế',
            'cty': 'công ty',
            'tnhh': 'trách nhiệm hữu hạn',
            'cp': 'cổ phần'
        }
    
    def normalize(self, text: str) -> str:
        """Chuẩn hóa text đầu vào"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Convert to lowercase for processing (but keep original case)
        normalized = text.lower()
        
        # Expand abbreviations
        for abbr, full in self.abbreviations.items():
            normalized = re.sub(r'\b' + abbr + r'\b', full, normalized)
        
        # Remove special characters but keep Vietnamese characters
        normalized = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', normalized)
        
        # Remove extra spaces again
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def extract_keywords(self, text: str) -> List[str]:
        """Trích xuất từ khóa quan trọng"""
        normalized = self.normalize(text)
        words = normalized.split()
        
        # Remove stopwords and short words
        keywords = [
            word for word in words 
            if word not in self.stopwords and len(word) > 2
        ]
        
        return keywords
    
    def extract_numbers(self, text: str) -> List[str]:
        """Trích xuất các số từ text"""
        # Pattern cho số tiền Việt Nam
        money_patterns = [
            r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?',  # 1,000,000.50
            r'\d+[.,]\d+',  # 1000.50
            r'\d+'  # 1000
        ]
        
        numbers = []
        for pattern in money_patterns:
            numbers.extend(re.findall(pattern, text))
        
        return list(set(numbers))  # Remove duplicates
    
    def extract_dates(self, text: str) -> List[str]:
        """Trích xuất ngày tháng từ text"""
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',  # dd/mm/yyyy
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2}',   # dd/mm/yy
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',   # yyyy/mm/dd
            r'\d{1,2}\s+(tháng\s+)?\d{1,2}\s+(năm\s+)?\d{4}',  # 15 tháng 12 năm 2023
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))
        
        return dates
    
    def extract_invoice_numbers(self, text: str) -> List[str]:
        """Trích xuất số hóa đơn từ text"""
        patterns = [
            r'(?:hd|hóa đơn|invoice)[:\s]*([a-z0-9]+)',
            r'số[:\s]*([a-z0-9]+)',
            r'([a-z]{1,3}\d{6,})',  # ABC123456
            r'(\d{7,})',  # 1234567
        ]
        
        invoice_numbers = []
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            invoice_numbers.extend(matches)
        
        return list(set(invoice_numbers))
    
    def extract_tax_codes(self, text: str) -> List[str]:
        """Trích xuất mã số thuế từ text"""
        patterns = [
            r'(?:mst|mã số thuế|tax code)[:\s]*(\d{10,13})',
            r'(\d{10})',  # 10 digits
            r'(\d{13})',  # 13 digits
        ]
        
        tax_codes = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            # Filter valid tax codes (10 or 13 digits)
            valid_codes = [code for code in matches if len(code) in [10, 13]]
            tax_codes.extend(valid_codes)
        
        return list(set(tax_codes))
    
    def clean_amount(self, amount_str: str) -> float:
        """Chuyển đổi chuỗi số tiền thành float"""
        try:
            # Remove currency symbols and spaces
            cleaned = re.sub(r'[^\d.,]', '', amount_str)
            
            # Handle Vietnamese number format (1.000.000,50)
            if ',' in cleaned and '.' in cleaned:
                # Check if comma is decimal separator
                if cleaned.rfind(',') > cleaned.rfind('.'):
                    # Vietnamese format: 1.000.000,50
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    # US format: 1,000,000.50
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Could be decimal separator
                parts = cleaned.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Decimal separator: 1000,50
                    cleaned = cleaned.replace(',', '.')
                else:
                    # Thousand separator: 1,000,000
                    cleaned = cleaned.replace(',', '')
            
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def similarity(self, text1: str, text2: str) -> float:
        """Tính độ tương tự giữa hai chuỗi text"""
        # Simple Jaccard similarity
        words1 = set(self.extract_keywords(text1))
        words2 = set(self.extract_keywords(text2))
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def highlight_keywords(self, text: str, keywords: List[str]) -> str:
        """Highlight keywords trong text"""
        highlighted = text
        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted = pattern.sub(f'**{keyword}**', highlighted)
        
        return highlighted