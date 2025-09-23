from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
from flask import current_app

from models.training_data import InvoiceTrainingData, FieldExtractor
from models.template import InvoiceTemplate

logger = logging.getLogger(__name__)

class TrainingDataService:
    """
    Service để quản lý việc lưu trữ và xử lý training data cho AI
    """
    
    def __init__(self):
        self.training_data = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """
        Khởi tạo kết nối MongoDB
        """
        try:
            mongodb_url = current_app.config.get('MONGODB_URL', 'mongodb://localhost:27017/')
            db_name = current_app.config.get('MONGODB_DB_NAME', 'invoice_ai_training')
            
            self.training_data = InvoiceTrainingData(mongodb_url, db_name)
            logger.info(f"Đã kết nối thành công tới MongoDB: {db_name}")
            
        except Exception as e:
            logger.error(f"Lỗi kết nối MongoDB: {str(e)}")
            self.training_data = None
    
    def save_template_training_data(self, 
                                  template: InvoiceTemplate, 
                                  additional_metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Lưu training data từ InvoiceTemplate
        
        Args:
            template: InvoiceTemplate object
            additional_metadata: Metadata bổ sung
            
        Returns:
            str: ID của training record đã tạo, None nếu thất bại
        """
        if not self.training_data:
            logger.error("MongoDB chưa được kết nối")
            return None
        
        try:
            # Extract fields từ template content
            extracted_fields = FieldExtractor.extract_fields_from_template(
                template.content, 
                template.template_type.value
            )
            
            # Tạo field patterns để AI học
            field_patterns = self._generate_field_patterns(extracted_fields, template.content)
            
            # Tạo metadata
            metadata = {
                "original_template_id": template.id,
                "extraction_method": "auto",
                "field_count": len(extracted_fields),
                "content_length": len(template.content),
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            
            if additional_metadata:
                metadata.update(additional_metadata)
            
            # Lưu training data
            training_id = self.training_data.create_training_record(
                template_id=str(template.id),
                template_name=template.name,
                template_type=template.template_type.value,
                template_content=template.content,
                extracted_fields=extracted_fields,
                field_patterns=field_patterns,
                metadata=metadata
            )
            
            logger.info(f"Đã lưu training data cho template {template.name}, ID: {training_id}")
            return training_id
            
        except Exception as e:
            logger.error(f"Lỗi khi lưu training data cho template {template.id}: {str(e)}")
            return None
    
    def get_training_data_for_chatbot(self, 
                                    template_type: Optional[str] = None,
                                    limit: int = 100) -> Dict[str, Any]:
        """
        Lấy training data đã được format để chatbot sử dụng
        
        Args:
            template_type: Loại template cần lấy (word, pdf, excel)
            limit: Số lượng records tối đa
            
        Returns:
            Dict chứa training data đã được format
        """
        if not self.training_data:
            return {"error": "MongoDB chưa được kết nối"}
        
        try:
            if template_type:
                raw_data = self.training_data.get_training_data_by_type(template_type, limit)
            else:
                # Lấy tất cả field patterns
                all_patterns = self.training_data.get_all_field_patterns()
                raw_data = []
                for type_patterns in all_patterns.values():
                    raw_data.extend(type_patterns[:limit//len(all_patterns)] if all_patterns else [])
            
            # Format data cho chatbot
            formatted_data = self._format_for_chatbot(raw_data)
            
            return {
                "success": True,
                "data": formatted_data,
                "total_records": len(raw_data),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy training data cho chatbot: {str(e)}")
            return {"error": str(e)}
    
    def search_similar_templates(self, field_names: List[str]) -> List[Dict[str, Any]]:
        """
        Tìm các template tương tự dựa trên tên field
        
        Args:
            field_names: Danh sách tên field cần tìm
            
        Returns:
            List các template tương tự
        """
        if not self.training_data:
            return []
        
        try:
            similar_templates = []
            
            for field_name in field_names:
                results = self.training_data.search_similar_fields(field_name)
                similar_templates.extend(results)
            
            # Loại bỏ duplicate và sort theo điểm tương đồng
            unique_templates = {template["template_id"]: template for template in similar_templates}
            
            return list(unique_templates.values())
            
        except Exception as e:
            logger.error(f"Lỗi khi tìm template tương tự: {str(e)}")
            return []
    
    def get_training_statistics(self) -> Dict[str, Any]:
        """
        Lấy thống kê về training data
        """
        if not self.training_data:
            return {"error": "MongoDB chưa được kết nối"}
        
        try:
            stats = self.training_data.get_training_summary()
            return stats
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy thống kê training data: {str(e)}")
            return {"error": str(e)}
    
    def validate_and_score_training_data(self, training_id: str, is_valid: bool, score: float = None):
        """
        Validate và chấm điểm training data
        """
        if not self.training_data:
            logger.error("MongoDB chưa được kết nối")
            return False
        
        try:
            self.training_data.validate_training_record(training_id, is_valid, score)
            logger.info(f"Đã validate training record {training_id}: valid={is_valid}, score={score}")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi khi validate training data {training_id}: {str(e)}")
            return False
    
    def _generate_field_patterns(self, fields: List[Dict[str, Any]], content: str) -> Dict[str, Any]:
        """
        Tạo patterns từ các field đã extract để AI học
        """
        patterns = {
            "extraction_patterns": {},
            "validation_patterns": {},
            "field_relationships": [],
            "content_structure": self._analyze_content_structure(content)
        }
        
        for field in fields:
            field_name = field.get("field_name", "")
            field_type = field.get("field_type", "")
            pattern = field.get("pattern", "")
            
            # Pattern để extract field này
            patterns["extraction_patterns"][field_name] = {
                "regex_pattern": pattern,
                "field_type": field_type,
                "data_type": field.get("data_type", "string"),
                "is_required": field.get("is_required", False)
            }
            
            # Pattern để validate field này
            validation_pattern = self._generate_validation_pattern(field)
            if validation_pattern:
                patterns["validation_patterns"][field_name] = validation_pattern
        
        # Phân tích mối quan hệ giữa các field
        patterns["field_relationships"] = self._analyze_field_relationships(fields)
        
        return patterns
    
    def _generate_validation_pattern(self, field: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Tạo pattern validation cho field
        """
        data_type = field.get("data_type", "string")
        
        validation_patterns = {
            "date": {
                "pattern": r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
                "message": "Định dạng ngày không hợp lệ"
            },
            "number": {
                "pattern": r"^[0-9,.-]+$",
                "message": "Phải là số"
            },
            "email": {
                "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "message": "Email không hợp lệ"
            },
            "code": {
                "pattern": r"^[A-Z0-9-]+$",
                "message": "Mã không hợp lệ"
            }
        }
        
        return validation_patterns.get(data_type)
    
    def _analyze_field_relationships(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Phân tích mối quan hệ giữa các field
        """
        relationships = []
        
        # Tìm các field liên quan đến nhau
        field_groups = {
            "invoice_info": ["invoice_number", "invoice_date", "due_date"],
            "company_info": ["company_name", "company_address", "tax_code"],
            "customer_info": ["customer_name", "customer_address", "customer_phone"],
            "amount_info": ["subtotal", "tax_amount", "total_amount", "amount"]
        }
        
        field_names = [field.get("field_name", "") for field in fields]
        
        for group_name, group_fields in field_groups.items():
            found_fields = [field for field in group_fields if field in field_names]
            if len(found_fields) >= 2:
                relationships.append({
                    "group": group_name,
                    "fields": found_fields,
                    "relationship_type": "semantic_group"
                })
        
        return relationships
    
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """
        Phân tích cấu trúc của content
        """
        structure = {
            "content_type": "unknown",
            "has_tables": False,
            "has_forms": False,
            "estimated_fields": 0,
            "complexity_score": 0
        }
        
        content_lower = content.lower()
        
        # Xác định loại content
        if "<html" in content_lower or "<body" in content_lower:
            structure["content_type"] = "html"
        elif "<?xml" in content_lower or "<root" in content_lower:
            structure["content_type"] = "xml"
        elif "{" in content and "}" in content:
            structure["content_type"] = "template"
        
        # Kiểm tra có table không
        structure["has_tables"] = "<table" in content_lower or "table" in content_lower
        
        # Kiểm tra có form không
        structure["has_forms"] = "<form" in content_lower or "<input" in content_lower
        
        # Ước tính số field
        structure["estimated_fields"] = content.count("{{") + content.count("<input")
        
        # Điểm phức tạp (0-10)
        complexity_score = 0
        complexity_score += min(len(content) // 1000, 3)  # Độ dài content
        complexity_score += min(content.count("\n") // 10, 2)  # Số dòng
        complexity_score += min(structure["estimated_fields"], 3)  # Số field
        complexity_score += 1 if structure["has_tables"] else 0
        complexity_score += 1 if structure["has_forms"] else 0
        
        structure["complexity_score"] = min(complexity_score, 10)
        
        return structure
    
    def _format_for_chatbot(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format training data để chatbot dễ sử dụng
        """
        formatted = {
            "templates": [],
            "field_patterns": {},
            "common_fields": [],
            "validation_rules": {}
        }
        
        all_fields = []
        
        for record in raw_data:
            # Format template info
            template_info = {
                "name": record.get("template_name", ""),
                "type": record.get("template_type", ""),
                "fields": record.get("fields", []),
                "created_at": record.get("created_at", "")
            }
            formatted["templates"].append(template_info)
            
            # Collect field patterns
            field_patterns = record.get("field_patterns", {})
            extraction_patterns = field_patterns.get("extraction_patterns", {})
            
            for field_name, pattern_info in extraction_patterns.items():
                if field_name not in formatted["field_patterns"]:
                    formatted["field_patterns"][field_name] = []
                
                formatted["field_patterns"][field_name].append({
                    "pattern": pattern_info.get("regex_pattern", ""),
                    "data_type": pattern_info.get("data_type", "string"),
                    "template_type": record.get("template_type", ""),
                    "is_required": pattern_info.get("is_required", False)
                })
            
            # Collect all fields
            all_fields.extend([field.get("field_name", "") for field in record.get("fields", [])])
        
        # Tìm common fields
        from collections import Counter
        field_counter = Counter(all_fields)
        formatted["common_fields"] = [
            {"name": field, "frequency": count} 
            for field, count in field_counter.most_common(20)
        ]
        
        return formatted
    
    def close_connection(self):
        """
        Đóng kết nối MongoDB
        """
        if self.training_data:
            self.training_data.close_connection()