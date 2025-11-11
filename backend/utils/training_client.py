import requests
import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TrainingDataClient:
    """
    Client để kết nối với backend API và lấy training data cho chatbot
    """
    
    def __init__(self, base_url: str = None):
        # Use Docker service name in container, localhost for development
        if base_url is None:
            base_url = os.getenv('BACKEND_URL', 'http://localhost:8000/api/ai-training')
        
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'InvoiceBot-TrainingClient/1.0'
        })
        
        # Cache để tránh gọi API liên tục
        self._cache = {}
        self._cache_timeout = 300  # 5 phút
        self._last_cache_update = {}
    
    def get_training_data(self, 
                         template_type: Optional[str] = None,
                         limit: int = 100,
                         include_patterns: bool = True,
                         use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Lấy training data từ backend
        
        Args:
            template_type: Loại template (word, pdf, excel, html, xml)
            limit: Số lượng records tối đa
            include_patterns: Có bao gồm field patterns không
            use_cache: Có sử dụng cache không
            
        Returns:
            Dict chứa training data hoặc None nếu lỗi
        """
        cache_key = f"training_data_{template_type}_{limit}_{include_patterns}"
        
        # Kiểm tra cache
        if use_cache and self._is_cache_valid(cache_key):
            logger.info(f"Sử dụng cached training data: {cache_key}")
            return self._cache[cache_key]
        
        try:
            params = {
                'limit': limit,
                'include_patterns': str(include_patterns).lower()
            }
            
            if template_type:
                params['template_type'] = template_type
            
            response = self.session.get(
                f"{self.base_url}/training-data",
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                # Cache kết quả
                self._cache[cache_key] = data
                self._last_cache_update[cache_key] = datetime.now()
                
                logger.info(f"Đã lấy training data thành công: {data.get('total_records', 0)} records")
                return data
            else:
                logger.error(f"API trả về lỗi: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi gọi API training data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Lỗi không xác định khi lấy training data: {str(e)}")
            return None
    
    def search_similar_templates(self, field_names: List[str], limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """
        Tìm các template tương tự dựa trên field names
        """
        cache_key = f"similar_templates_{hash(tuple(sorted(field_names)))}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            payload = {
                'field_names': field_names,
                'limit': limit
            }
            
            response = self.session.post(
                f"{self.base_url}/search-similar",
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                results = data.get('results', [])
                self._cache[cache_key] = results
                self._last_cache_update[cache_key] = datetime.now()
                
                logger.info(f"Tìm thấy {len(results)} template tương tự")
                return results
            else:
                logger.error(f"API search similar trả về lỗi: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi search similar templates: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Lỗi không xác định khi search similar: {str(e)}")
            return None
    
    def get_field_patterns(self, 
                          template_type: Optional[str] = None,
                          field_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Lấy field patterns để nhận dạng và extract thông tin
        """
        cache_key = f"field_patterns_{template_type}_{field_name}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            params = {}
            if template_type:
                params['template_type'] = template_type
            if field_name:
                params['field_name'] = field_name
            
            response = self.session.get(
                f"{self.base_url}/field-patterns",
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                patterns = data.get('patterns', {})
                self._cache[cache_key] = patterns
                self._last_cache_update[cache_key] = datetime.now()
                
                logger.info(f"Đã lấy field patterns thành công")
                return patterns
            else:
                logger.error(f"API field patterns trả về lỗi: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi lấy field patterns: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Lỗi không xác định khi lấy field patterns: {str(e)}")
            return None
    
    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Lấy thống kê về training data
        """
        try:
            response = self.session.get(
                f"{self.base_url}/statistics",
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                return data.get('statistics', {})
            else:
                logger.error(f"API statistics trả về lỗi: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi lấy statistics: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Lỗi không xác định khi lấy statistics: {str(e)}")
            return None
    
    def check_health(self) -> bool:
        """
        Kiểm tra tình trạng kết nối với backend
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            return data.get('status') == 'healthy'
            
        except Exception as e:
            logger.error(f"Health check thất bại: {str(e)}")
            return False
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Kiểm tra cache có còn hợp lệ không
        """
        if cache_key not in self._cache:
            return False
        
        if cache_key not in self._last_cache_update:
            return False
        
        time_diff = datetime.now() - self._last_cache_update[cache_key]
        return time_diff.total_seconds() < self._cache_timeout
    
    def get_training_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Lấy thống kê training data từ backend
        """
        try:
            # Try public endpoint first (no auth required)
            response = self.session.get(
                f"{self.base_url}/public-statistics",
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info("Đã lấy thành công public training statistics")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi kết nối khi lấy statistics: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Lỗi không xác định khi lấy statistics: {str(e)}")
            return None
    
    def clear_cache(self):
        """
        Xóa cache
        """
        self._cache.clear()
        self._last_cache_update.clear()
        logger.info("Đã xóa cache training data")
    
    def submit_user_correction(self, 
                              original_text: str, 
                              corrected_amount: str, 
                              invoice_type: str = "general",
                              user_id: str = "anonymous") -> bool:
        """
        Submit user correction for amount recognition to improve AI training
        
        Args:
            original_text: The OCR text where the amount was found
            corrected_amount: The correct amount the user specified
            invoice_type: Type of invoice (momo, electricity, traditional)
            user_id: ID of the user making the correction
            
        Returns:
            bool: True if correction was submitted successfully
        """
        try:
            payload = {
                'original_text': original_text,
                'corrected_amount': corrected_amount,
                'invoice_type': invoice_type,
                'user_id': user_id,
                'correction_type': 'dash_amount_recognition',
                'timestamp': datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}/user-corrections",
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                logger.info(f"✅ User correction submitted successfully for amount: {corrected_amount}")
                # Clear cache to force refresh of patterns
                self.clear_cache()
                return True
            else:
                logger.error(f"❌ Failed to submit user correction: {data}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error submitting user correction: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Error submitting user correction: {str(e)}")
            return False
    
    def get_dash_patterns(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get learned dash amount patterns from training data
        
        Returns:
            List of dash pattern objects with confidence scores
        """
        try:
            response = self.session.get(
                f"{self.base_url}/dash-patterns",
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                patterns = data.get('patterns', [])
                logger.info(f"✅ Retrieved {len(patterns)} dash patterns")
                return patterns
            else:
                logger.error(f"❌ Failed to get dash patterns: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error getting dash patterns: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting dash patterns: {str(e)}")
            return None
        

class InvoicePatternMatcher:
    """
    Class để match patterns từ training data với input của user
    """
    
    def __init__(self, training_client: TrainingDataClient):
        self.training_client = training_client
        self.field_patterns = {}
        self.common_fields = []
        self._load_patterns()
    
    def _load_patterns(self):
        """
        Load patterns từ training data
        """
        try:
            training_data = self.training_client.get_training_data(limit=500)
            
            if training_data and training_data.get('success'):
                data = training_data.get('data', {})
                
                # Load field patterns
                self.field_patterns = data.get('field_patterns', {})
                
                # Load common fields
                self.common_fields = [
                    field['name'] for field in data.get('common_fields', [])
                ]
                
                logger.info(f"Đã load {len(self.field_patterns)} field patterns và {len(self.common_fields)} common fields")
            else:
                logger.warning("Không thể load training data patterns")
                
        except Exception as e:
            logger.error(f"Lỗi khi load patterns: {str(e)}")
    
    def extract_invoice_info(self, text: str) -> Dict[str, Any]:
        """
        Extract thông tin hóa đơn từ text dựa trên patterns đã học
        Enhanced with dash amount recognition
        """
        extracted_info = {}
        
        # ⭐ HIGH PRIORITY: Check for dash-indicated amounts first
        dash_amount = self._extract_dash_amount(text)
        if dash_amount:
            extracted_info['total_amount'] = {
                'values': [dash_amount['amount']],
                'best_match': dash_amount['amount'],
                'confidence': dash_amount['confidence'],
                'pattern_type': 'dash_recognition'
            }
            logger.info(f"✅ Found dash-indicated amount: {dash_amount['amount']} (confidence: {dash_amount['confidence']})")
        
        # Duyệt qua tất cả field patterns đã học
        for field_name, patterns in self.field_patterns.items():
            # Skip total_amount if we already found it via dash recognition
            if field_name == 'total_amount' and 'total_amount' in extracted_info:
                continue
                
            values = []
            
            for pattern_info in patterns:
                pattern = pattern_info.get('pattern', '')
                if pattern:
                    try:
                        import re
                        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                        values.extend(matches)
                    except re.error:
                        continue
            
            if values:
                # Loại bỏ duplicate và lấy giá trị tốt nhất
                unique_values = list(set(values))
                extracted_info[field_name] = {
                    'values': unique_values,
                    'best_match': unique_values[0] if unique_values else None,
                    'confidence': min(len(unique_values) / len(patterns), 1.0) if patterns else 0.0
                }
        
        return extracted_info
    
    def _extract_dash_amount(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract amount from dash-indicated patterns with learned corrections
        
        Returns:
            Dict with amount, confidence, and pattern info, or None if not found
        """
        import re
        
        # Get learned dash patterns from training data
        dash_patterns = self.training_client.get_dash_patterns()
        
        # Default dash patterns if no learned patterns available
        if not dash_patterns:
            dash_patterns = [
                {
                    'pattern': r'(?:^\s*-\s*|-\s+)([0-9,\.]+)(?:\s*(?:vnd|đ|vnđ))?',
                    'confidence': 0.9,
                    'description': 'Line starting with dash'
                },
                {
                    'pattern': r'(\d+(?:,\d{3})*(?:\.\d{2})?)(?:\s*(?:vnd|đ|vnđ))?\s*$',
                    'confidence': 0.7,
                    'description': 'Amount at end of line'
                }
            ]
        
        best_match = None
        highest_confidence = 0.0
        
        for pattern_info in dash_patterns:
            pattern = pattern_info.get('pattern', '')
            base_confidence = pattern_info.get('confidence', 0.5)
            
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    amount_str = match.group(1).strip()
                    
                    # Clean up the amount string
                    amount_str = amount_str.replace(' ', '').replace('_', '')
                    
                    # Parse amount
                    try:
                        if ',' in amount_str and '.' in amount_str:
                            numeric_value = float(amount_str.replace(',', ''))
                        else:
                            numeric_value = float(amount_str.replace(',', '').replace('.', ''))
                        
                        # Validate reasonable amount
                        if 100 <= numeric_value <= 100000000:
                            # Boost confidence if this matches a learned correction
                            final_confidence = base_confidence
                            
                            # Check if this pattern has been validated by user corrections
                            if pattern_info.get('validated_by_corrections', 0) > 0:
                                final_confidence = min(final_confidence + 0.2, 1.0)
                            
                            if final_confidence > highest_confidence:
                                highest_confidence = final_confidence
                                best_match = {
                                    'amount': f"{numeric_value:,.0f} VND",
                                    'numeric_value': numeric_value,
                                    'confidence': final_confidence,
                                    'pattern': pattern,
                                    'description': pattern_info.get('description', 'Dash pattern')
                                }
                                
                    except (ValueError, OverflowError):
                        continue
                        
            except re.error:
                continue
        
        return best_match