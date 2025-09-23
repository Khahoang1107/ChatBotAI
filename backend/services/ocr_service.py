"""
OCR Service for processing invoice images and extracting structured data.
Supports both generic OCR and template-based extraction.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from PIL import Image
import pytesseract
import openai
from pdf2image import convert_from_path


class OCRService:
    def __init__(self):
        """Initialize OCR Service with OpenAI API key"""
        self.openai_client = None
        if os.environ.get('OPENAI_API_KEY'):
            openai.api_key = os.environ.get('OPENAI_API_KEY')
            self.openai_client = openai
    
    def process_image(self, file_path: str, template=None, confidence_threshold: float = 0.8) -> Dict[str, Any]:
        """
        Process an image file and extract invoice data
        
        Args:
            file_path: Path to the image file
            template: Optional InvoiceTemplate object for guided extraction
            confidence_threshold: Minimum confidence score required
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        try:
            # Extract text from image
            raw_text = self._extract_text_from_file(file_path)
            
            if not raw_text.strip():
                return {
                    'raw_text': '',
                    'structured_data': {},
                    'confidence': 0.0,
                    'error': 'No text could be extracted from the image'
                }
            
            # Process with template if provided
            if template:
                structured_data = self._extract_with_template(raw_text, template)
            else:
                structured_data = self._extract_generic(raw_text)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(structured_data, template)
            
            return {
                'raw_text': raw_text,
                'structured_data': structured_data,
                'confidence': confidence,
                'template_used': template.id if template else None,
                'processing_method': 'template' if template else 'generic'
            }
            
        except Exception as e:
            return {
                'raw_text': '',
                'structured_data': {},
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from image or PDF file"""
        try:
            file_extension = file_path.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                # Convert PDF to images and extract text from first page
                images = convert_from_path(file_path, first_page=1, last_page=1)
                if images:
                    return pytesseract.image_to_string(images[0], lang='vie+eng')
                return ''
            else:
                # Process image file
                image = Image.open(file_path)
                return pytesseract.image_to_string(image, lang='vie+eng')
                
        except Exception as e:
            raise Exception(f"Failed to extract text from file: {str(e)}")
    
    def _extract_with_template(self, text: str, template) -> Dict[str, Any]:
        """Extract data using template-guided extraction"""
        try:
            field_mappings = template.get_field_mappings()
            ocr_zones = template.get_ocr_zones()
            
            extracted_data = {}
            
            # Use OpenAI for intelligent extraction if available
            if self.openai_client:
                extracted_data = self._extract_with_ai(text, field_mappings)
            else:
                # Fallback to pattern-based extraction
                extracted_data = self._extract_with_patterns(text, field_mappings)
            
            # Apply template-specific validation and formatting
            extracted_data = self._validate_and_format_data(extracted_data, field_mappings)
            
            return extracted_data
            
        except Exception as e:
            # Fallback to generic extraction
            return self._extract_generic(text)
    
    def _extract_with_ai(self, text: str, field_mappings: Dict) -> Dict[str, Any]:
        """Use OpenAI to extract structured data from text"""
        try:
            # Create field descriptions for AI
            field_descriptions = []
            for field_name, field_config in field_mappings.items():
                field_type = field_config.get('type', 'string')
                required = 'required' if field_config.get('required', False) else 'optional'
                field_descriptions.append(f"- {field_name} ({field_type}, {required})")
            
            prompt = f"""
            Extract the following invoice information from the text below. Return the data as a JSON object.
            
            Fields to extract:
            {chr(10).join(field_descriptions)}
            
            Additional fields:
            - items (array of objects with description, quantity, unit_price, total_price)
            
            Invoice text:
            {text}
            
            Return only valid JSON without any additional text or formatting.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured data from invoice text. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON response
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return {}
                
        except Exception as e:
            print(f"AI extraction failed: {e}")
            return {}
    
    def _extract_with_patterns(self, text: str, field_mappings: Dict) -> Dict[str, Any]:
        """Extract data using regex patterns"""
        extracted_data = {}
        
        # Common patterns for Vietnamese invoices
        patterns = {
            'invoice_number': [
                r'(?:Số hóa đơn|Invoice No|Invoice Number)[:\s]+([A-Z0-9\-/]+)',
                r'(?:HD|INV)[:\s]*([A-Z0-9\-/]+)',
                r'(\d{4,})',  # Fallback: any 4+ digit number
            ],
            'company_name': [
                r'(?:Công ty|Company)[:\s]*([^\n]+)',
                r'^([A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯĂÂÊÔƠƯ][^\n]{10,})',  # Capitalized line
            ],
            'customer_name': [
                r'(?:Khách hàng|Customer|Đơn vị)[:\s]*([^\n]+)',
                r'(?:Tên|Name)[:\s]*([^\n]+)',
            ],
            'total_amount': [
                r'(?:Tổng cộng|Total|Thành tiền)[:\s]*([0-9,.\s]+)',
                r'([0-9,]+\.?\d*)\s*(?:VND|đ|VNĐ)',
            ],
            'invoice_date': [
                r'(?:Ngày|Date)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ],
            'tax_amount': [
                r'(?:VAT|Thuế)[:\s]*([0-9,.\s]+)',
            ],
            'company_tax_id': [
                r'(?:MST|Tax ID)[:\s]*([0-9\-]+)',
            ],
        }
        
        # Extract using patterns
        for field_name, field_patterns in patterns.items():
            if field_name in field_mappings:
                for pattern in field_patterns:
                    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        extracted_data[field_name] = match.group(1).strip()
                        break
        
        # Extract items (simplified)
        items = self._extract_items_from_text(text)
        if items:
            extracted_data['items'] = items
        
        return extracted_data
    
    def _extract_generic(self, text: str) -> Dict[str, Any]:
        """Generic extraction without template"""
        extracted_data = {}
        
        # Use AI if available
        if self.openai_client:
            try:
                prompt = f"""
                Extract invoice information from this text and return as JSON:
                
                {text}
                
                Extract: invoice_number, company_name, customer_name, total_amount, invoice_date, currency, items (array).
                Return only valid JSON.
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Extract invoice data as JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1500
                )
                
                result = response.choices[0].message.content
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    json_match = re.search(r'\{.*\}', result, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass
                    
            except Exception as e:
                print(f"Generic AI extraction failed: {e}")
        
        # Fallback to basic pattern extraction
        basic_patterns = {
            'invoice_number': r'(?:INV|HD|Invoice)[:\s#]*([A-Z0-9\-/]+)',
            'total_amount': r'([0-9,]+\.?\d*)\s*(?:VND|đ|VNĐ|USD|\$)',
            'invoice_date': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        }
        
        for field, pattern in basic_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_data[field] = match.group(1).strip()
        
        return extracted_data
    
    def _extract_items_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items from invoice text"""
        items = []
        
        # Look for table-like structures
        lines = text.split('\n')
        
        # Simple heuristic: lines with numbers that look like quantities and prices
        item_pattern = r'(.+?)\s+(\d+(?:\.\d+)?)\s+([0-9,]+(?:\.\d+)?)\s+([0-9,]+(?:\.\d+)?)'
        
        for line in lines:
            match = re.search(item_pattern, line.strip())
            if match:
                try:
                    description = match.group(1).strip()
                    quantity = float(match.group(2))
                    unit_price = float(match.group(3).replace(',', ''))
                    total_price = float(match.group(4).replace(',', ''))
                    
                    if description and quantity > 0:
                        items.append({
                            'description': description,
                            'quantity': quantity,
                            'unit_price': unit_price,
                            'total_price': total_price
                        })
                except ValueError:
                    continue
        
        return items[:10]  # Limit to 10 items
    
    def _validate_and_format_data(self, data: Dict[str, Any], field_mappings: Dict) -> Dict[str, Any]:
        """Validate and format extracted data according to field mappings"""
        formatted_data = {}
        
        for field_name, field_config in field_mappings.items():
            if field_name in data:
                value = data[field_name]
                field_type = field_config.get('type', 'string')
                
                try:
                    if field_type == 'decimal' and value:
                        # Clean and convert to decimal
                        clean_value = re.sub(r'[,\s]', '', str(value))
                        formatted_data[field_name] = float(clean_value)
                    elif field_type == 'date' and value:
                        # Try to parse date
                        date_value = self._parse_date(str(value))
                        if date_value:
                            formatted_data[field_name] = date_value.strftime('%Y-%m-%d')
                    elif field_type == 'string' and value:
                        formatted_data[field_name] = str(value).strip()
                    else:
                        formatted_data[field_name] = value
                except (ValueError, TypeError):
                    # Keep original value if formatting fails
                    formatted_data[field_name] = value
        
        # Include items if present
        if 'items' in data:
            formatted_data['items'] = data['items']
        
        return formatted_data
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string into datetime object"""
        date_formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%d.%m.%Y',
            '%m/%d/%Y',
            '%Y-%m-%d',
            '%d/%m/%y',
            '%d-%m-%y',
        ]
        
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str.strip(), date_format)
            except ValueError:
                continue
        
        return None
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any], template=None) -> float:
        """Calculate confidence score for extracted data"""
        if not extracted_data:
            return 0.0
        
        score = 0.0
        total_fields = 0
        
        # Required fields for basic invoice
        required_fields = ['invoice_number', 'company_name', 'total_amount']
        
        if template:
            # Use template field mappings
            field_mappings = template.get_field_mappings()
            template_required = [f for f, config in field_mappings.items() if config.get('required', False)]
            if template_required:
                required_fields = template_required
        
        # Check required fields
        for field in required_fields:
            total_fields += 1
            if field in extracted_data and extracted_data[field]:
                score += 1.0
        
        # Bonus for additional fields
        optional_fields = ['customer_name', 'invoice_date', 'items', 'company_address']
        for field in optional_fields:
            if field in extracted_data and extracted_data[field]:
                score += 0.2
                total_fields += 0.2
        
        # Penalty for empty or invalid data
        for field, value in extracted_data.items():
            if not value or (isinstance(value, str) and len(value.strip()) < 2):
                score -= 0.1
        
        # Normalize score
        if total_fields > 0:
            confidence = max(0.0, min(1.0, score / total_fields))
        else:
            confidence = 0.0
        
        return round(confidence, 2)