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
        """
        extracted_info = {}
        
        # Duyệt qua tất cả field patterns đã học
        for field_name, patterns in self.field_patterns.items():
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
    
    def suggest_template_type(self, extracted_info: Dict[str, Any]) -> str:
        """
        Gợi ý loại template dựa trên thông tin đã extract
        """
        field_names = list(extracted_info.keys())
        
        # Tìm templates tương tự
        similar_templates = self.training_client.search_similar_templates(field_names)
        
        if similar_templates:
            # Đếm loại template phổ biến nhất
            template_types = {}
            for template in similar_templates:
                template_type = template.get('template_type', 'unknown')
                template_types[template_type] = template_types.get(template_type, 0) + 1
            
            # Trả về loại phổ biến nhất
            return max(template_types.items(), key=lambda x: x[1])[0]
        
        return 'unknown'
    
    def get_field_suggestions(self, partial_field_name: str) -> List[str]:
        """
        Gợi ý field names dựa trên input từng phần
        """
        suggestions = []
        
        for field_name in self.common_fields:
            if partial_field_name.lower() in field_name.lower():
                suggestions.append(field_name)
        
        return suggestions[:10]  # Giới hạn 10 gợi ý
    
    def refresh_patterns(self):
        """
        Refresh patterns từ backend
        """
        self.training_client.clear_cache()
        self._load_patterns()