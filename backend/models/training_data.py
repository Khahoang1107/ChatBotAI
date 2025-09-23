from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import json
from typing import List, Dict, Any, Optional

class InvoiceTrainingData:
    """
    Model để lưu trữ dữ liệu training cho AI từ các mẫu hóa đơn
    """
    
    def __init__(self, db_url: str = "mongodb://localhost:27017/", db_name: str = "invoice_ai_training"):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db.invoice_training_data
        
        # Tạo index để tối ưu tìm kiếm
        self.collection.create_index([("template_id", 1)])
        self.collection.create_index([("template_type", 1)])
        self.collection.create_index([("created_at", -1)])
        self.collection.create_index([("fields.field_name", 1)])
    
    def create_training_record(self, 
                             template_id: str,
                             template_name: str,
                             template_type: str,
                             template_content: str,
                             extracted_fields: List[Dict[str, Any]],
                             field_patterns: Dict[str, Any],
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Tạo bản ghi training data mới từ mẫu hóa đơn
        
        Args:
            template_id: ID của template gốc
            template_name: Tên template
            template_type: Loại template (word, pdf, excel)
            template_content: Nội dung HTML/XML của template
            extracted_fields: Danh sách các field đã extract
            field_patterns: Patterns để nhận dạng các field
            metadata: Thông tin bổ sung
        
        Returns:
            str: ID của bản ghi vừa tạo
        """
        
        training_data = {
            "template_id": template_id,
            "template_name": template_name,
            "template_type": template_type,
            "template_content": template_content,
            "fields": extracted_fields,
            "field_patterns": field_patterns,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "version": 1,
            "is_validated": False,
            "training_score": 0.0,
            "usage_count": 0
        }
        
        result = self.collection.insert_one(training_data)
        return str(result.inserted_id)
    
    def update_training_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """
        Cập nhật bản ghi training data
        """
        updates["updated_at"] = datetime.utcnow()
        updates["version"] = {"$inc": {"version": 1}}
        
        result = self.collection.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": updates, "$inc": {"version": 1}}
        )
        
        return result.modified_count > 0
    
    def get_training_data_by_template(self, template_id: str) -> List[Dict[str, Any]]:
        """
        Lấy training data theo template ID
        """
        cursor = self.collection.find({"template_id": template_id})
        return [self._convert_objectid_to_str(doc) for doc in cursor]
    
    def get_training_data_by_type(self, template_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy training data theo loại template
        """
        cursor = self.collection.find({"template_type": template_type}).limit(limit)
        return [self._convert_objectid_to_str(doc) for doc in cursor]
    
    def get_all_field_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Lấy tất cả field patterns để training AI
        """
        pipeline = [
            {
                "$group": {
                    "_id": "$template_type",
                    "patterns": {
                        "$push": {
                            "template_name": "$template_name",
                            "fields": "$fields",
                            "field_patterns": "$field_patterns",
                            "created_at": "$created_at"
                        }
                    }
                }
            }
        ]
        
        result = {}
        for doc in self.collection.aggregate(pipeline):
            result[doc["_id"]] = doc["patterns"]
        
        return result
    
    def search_similar_fields(self, field_name: str, field_type: str = None) -> List[Dict[str, Any]]:
        """
        Tìm kiếm các field tương tự để AI học pattern
        """
        query = {"fields.field_name": {"$regex": field_name, "$options": "i"}}
        
        if field_type:
            query["fields.field_type"] = field_type
        
        cursor = self.collection.find(query)
        return [self._convert_objectid_to_str(doc) for doc in cursor]
    
    def get_training_summary(self) -> Dict[str, Any]:
        """
        Lấy thống kê tổng quan về training data
        """
        pipeline = [
            {
                "$group": {
                    "_id": "$template_type",
                    "count": {"$sum": 1},
                    "avg_fields": {"$avg": {"$size": "$fields"}},
                    "total_usage": {"$sum": "$usage_count"},
                    "latest_update": {"$max": "$updated_at"}
                }
            }
        ]
        
        stats = {}
        for doc in self.collection.aggregate(pipeline):
            stats[doc["_id"]] = {
                "count": doc["count"],
                "avg_fields": round(doc["avg_fields"], 2),
                "total_usage": doc["total_usage"],
                "latest_update": doc["latest_update"]
            }
        
        total_records = self.collection.count_documents({})
        
        return {
            "total_records": total_records,
            "by_type": stats,
            "generated_at": datetime.utcnow()
        }
    
    def increment_usage(self, record_id: str):
        """
        Tăng số lần sử dụng của training record
        """
        self.collection.update_one(
            {"_id": ObjectId(record_id)},
            {"$inc": {"usage_count": 1}, "$set": {"last_used": datetime.utcnow()}}
        )
    
    def validate_training_record(self, record_id: str, is_valid: bool, score: float = None):
        """
        Đánh dấu training record là đã được validate
        """
        update_data = {
            "is_validated": is_valid,
            "validated_at": datetime.utcnow()
        }
        
        if score is not None:
            update_data["training_score"] = score
        
        self.collection.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": update_data}
        )
    
    def _convert_objectid_to_str(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chuyển đổi ObjectId thành string để serialize JSON
        """
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    def close_connection(self):
        """
        Đóng kết nối MongoDB
        """
        self.client.close()


class FieldExtractor:
    """
    Class để extract và analyze các field từ template content
    """
    
    @staticmethod
    def extract_fields_from_template(content: str, template_type: str) -> List[Dict[str, Any]]:
        """
        Extract các field từ template content
        """
        fields = []
        
        if template_type.lower() == "html" or "html" in content.lower():
            fields = FieldExtractor._extract_html_fields(content)
        elif template_type.lower() == "xml":
            fields = FieldExtractor._extract_xml_fields(content)
        else:
            # Fallback: extract by common patterns
            fields = FieldExtractor._extract_pattern_fields(content)
        
        return fields
    
    @staticmethod
    def _extract_html_fields(content: str) -> List[Dict[str, Any]]:
        """
        Extract fields từ HTML content
        """
        import re
        fields = []
        
        # Tìm các input fields
        input_pattern = r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>'
        inputs = re.findall(input_pattern, content, re.IGNORECASE)
        
        for input_name in inputs:
            fields.append({
                "field_name": input_name,
                "field_type": "input",
                "data_type": "string",
                "is_required": "required" in content.lower(),
                "pattern": f"input[name='{input_name}']"
            })
        
        # Tìm các placeholder text
        placeholder_pattern = r'\{\{([^}]+)\}\}'
        placeholders = re.findall(placeholder_pattern, content)
        
        for placeholder in placeholders:
            fields.append({
                "field_name": placeholder.strip(),
                "field_type": "placeholder",
                "data_type": "string",
                "is_required": True,
                "pattern": f"{{{{{placeholder}}}}}"
            })
        
        return fields
    
    @staticmethod
    def _extract_xml_fields(content: str) -> List[Dict[str, Any]]:
        """
        Extract fields từ XML content
        """
        import re
        fields = []
        
        # Tìm XML tags
        tag_pattern = r'<([^/\s>]+)[^>]*>([^<]*)</\1>'
        tags = re.findall(tag_pattern, content)
        
        for tag_name, tag_value in tags:
            if tag_value.strip():
                fields.append({
                    "field_name": tag_name,
                    "field_type": "xml_element",
                    "data_type": FieldExtractor._detect_data_type(tag_value),
                    "is_required": True,
                    "pattern": f"<{tag_name}>{{value}}</{tag_name}>",
                    "sample_value": tag_value.strip()
                })
        
        return fields
    
    @staticmethod
    def _extract_pattern_fields(content: str) -> List[Dict[str, Any]]:
        """
        Extract fields bằng pattern matching
        """
        import re
        fields = []
        
        # Common invoice field patterns
        patterns = {
            "invoice_number": [r"(?:invoice|hóa đơn)[\s#:]*([A-Z0-9-]+)", r"số[\s]*:[\s]*([A-Z0-9-]+)"],
            "date": [r"(?:date|ngày)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"],
            "amount": [r"(?:total|tổng|amount)[\s:]*([0-9,.-]+)", r"([0-9,.-]+)[\s]*(?:VND|đ|USD|\$)"],
            "company_name": [r"(?:company|công ty)[\s:]*([^\n\r]+)", r"([A-Z][A-Za-z\s]+(?:JSC|LLC|Ltd|Co\.|Corporation))"],
            "tax_code": [r"(?:tax code|mã số thuế)[\s:]*([0-9-]+)", r"MST[\s:]*([0-9-]+)"]
        }
        
        for field_name, field_patterns in patterns.items():
            for pattern in field_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    fields.append({
                        "field_name": field_name,
                        "field_type": "extracted",
                        "data_type": FieldExtractor._detect_data_type(matches[0] if matches else ""),
                        "is_required": True,
                        "pattern": pattern,
                        "sample_values": matches[:3]  # Lấy 3 sample đầu tiên
                    })
                    break
        
        return fields
    
    @staticmethod
    def _detect_data_type(value: str) -> str:
        """
        Detect data type của value
        """
        import re
        
        if re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$', value.strip()):
            return "date"
        elif re.match(r'^[0-9,.-]+$', value.strip()):
            return "number"
        elif re.match(r'^[A-Z0-9-]+$', value.strip()):
            return "code"
        elif '@' in value:
            return "email"
        elif len(value.strip()) > 50:
            return "text_long"
        else:
            return "string"