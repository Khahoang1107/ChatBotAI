import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import spacy
import pytesseract
import cv2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class InvoiceAITrainer:
    """
    AI Training system cho Invoice OCR Recognition
    Tích hợp với existing backend/chatbot infrastructure
    """
    
    def __init__(self):
        self.nlp = None
        self.template_patterns = {}
        self.field_extractors = {}
        self.confidence_threshold = 0.75
        
    def collect_training_data(self) -> Dict:
        """
        Thu thập training data từ existing templates và user inputs
        """
        from models import Template, Invoice, OCRResult
        
        training_data = {
            "templates": [],
            "invoices": [],
            "field_patterns": {},
            "layout_patterns": {}
        }
        
        # Collect template data
        templates = Template.query.all()
        for template in templates:
            template_data = {
                "id": template.id,
                "name": template.name,
                "field_mappings": template.get_field_mappings(),
                "layout_info": self._analyze_template_layout(template),
                "usage_count": len(template.invoices)
            }
            training_data["templates"].append(template_data)
        
        # Collect successful OCR results
        successful_ocrs = OCRResult.query.filter(
            OCRResult.confidence_score > 0.8,
            OCRResult.status == 'completed'
        ).limit(1000).all()
        
        for ocr in successful_ocrs:
            if ocr.parsed_data:
                training_data["invoices"].append({
                    "ocr_text": ocr.extracted_text,
                    "parsed_fields": ocr.parsed_data,
                    "confidence": ocr.confidence_score,
                    "template_match": self._find_template_match(ocr)
                })
        
        return training_data
    
    def _analyze_template_layout(self, template) -> Dict:
        """Phân tích layout patterns của template"""
        field_mappings = template.get_field_mappings()
        
        layout_info = {
            "field_count": len(field_mappings),
            "field_types": {},
            "common_positions": {},
            "text_patterns": {}
        }
        
        for field_name, field_config in field_mappings.items():
            field_type = field_config.get('type', 'text')
            layout_info["field_types"][field_name] = field_type
            
            # Analyze common patterns
            if field_name in ['invoice_number', 'so_hoa_don']:
                layout_info["text_patterns"][field_name] = [
                    r"(Số|Number|No\.?)\s*:?\s*([A-Z0-9\-/]+)",
                    r"Invoice\s*#?\s*:?\s*([A-Z0-9\-/]+)",
                    r"HĐ\s*:?\s*([A-Z0-9\-/]+)"
                ]
            elif field_name in ['total_amount', 'tong_tien']:
                layout_info["text_patterns"][field_name] = [
                    r"(Tổng|Total|Sum)\s*:?\s*([\d,\.]+)",
                    r"Thành\s*tiền\s*:?\s*([\d,\.]+)",
                    r"([\d,\.]+)\s*(VND|đ|₫)"
                ]
            elif field_name in ['company_name', 'ten_cong_ty']:
                layout_info["text_patterns"][field_name] = [
                    r"(Công ty|Company)\s*:?\s*(.+?)(?:\n|$)",
                    r"^([A-Z][A-Za-z\s&.,]+(?:Company|Corporation|Ltd|Co\.|JSC))",
                ]
        
        return layout_info
    
    def train_ner_model(self, training_data: Dict):
        """
        Train Named Entity Recognition model cho invoice fields
        """
        # Prepare training data for spaCy
        ner_training_data = []
        
        for invoice_data in training_data["invoices"]:
            text = invoice_data["ocr_text"]
            parsed_fields = invoice_data["parsed_fields"]
            
            entities = []
            for field_name, field_value in parsed_fields.items():
                if field_value and str(field_value).strip():
                    # Find field value position in text
                    start_pos = text.find(str(field_value))
                    if start_pos != -1:
                        end_pos = start_pos + len(str(field_value))
                        entities.append((start_pos, end_pos, field_name.upper()))
            
            if entities:
                ner_training_data.append((text, {"entities": entities}))
        
        # Train spaCy model
        if not self.nlp:
            self.nlp = spacy.blank("vi")  # Vietnamese language support
            ner = self.nlp.create_pipe("ner")
            self.nlp.add_pipe("ner", last=True)
        
        # Add labels
        ner = self.nlp.get_pipe("ner")
        for _, annotations in ner_training_data:
            for ent in annotations.get("entities"):
                ner.add_label(ent[2])
        
        # Training loop
        self.nlp.begin_training()
        for iteration in range(100):
            losses = {}
            for text, annotations in ner_training_data:
                self.nlp.update([text], [annotations], losses=losses)
            
            if iteration % 20 == 0:
                print(f"Training iteration {iteration}, Losses: {losses}")
        
        # Save model
        self.nlp.to_disk("models/invoice_ner_model")
        print("NER model saved to models/invoice_ner_model")
    
    def build_template_matcher(self, training_data: Dict):
        """
        Xây dựng template matching system
        """
        template_vectors = []
        template_ids = []
        
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words=None  # Keep all words for invoice analysis
        )
        
        # Create template signatures
        template_texts = []
        for template in training_data["templates"]:
            field_names = list(template["field_mappings"].keys())
            template_signature = " ".join(field_names + [template["name"]])
            template_texts.append(template_signature)
            template_ids.append(template["id"])
        
        if template_texts:
            template_vectors = vectorizer.fit_transform(template_texts)
            
            self.template_matcher = {
                "vectorizer": vectorizer,
                "template_vectors": template_vectors,
                "template_ids": template_ids,
                "templates": {t["id"]: t for t in training_data["templates"]}
            }
            
            # Save template matcher
            import pickle
            with open("models/template_matcher.pkl", "wb") as f:
                pickle.dump(self.template_matcher, f)
            
            print("Template matcher saved to models/template_matcher.pkl")
    
    def predict_invoice_fields(self, ocr_text: str) -> Dict:
        """
        Predict invoice fields từ OCR text sử dụng trained models
        """
        if not self.nlp:
            try:
                self.nlp = spacy.load("models/invoice_ner_model")
            except:
                return {"error": "NER model not found. Please train first."}
        
        # NER prediction
        doc = self.nlp(ocr_text)
        predicted_fields = {}
        
        for ent in doc.ents:
            field_name = ent.label_.lower()
            field_value = ent.text.strip()
            confidence = ent._.score if hasattr(ent._, 'score') else 0.8
            
            predicted_fields[field_name] = {
                "value": field_value,
                "confidence": confidence,
                "start_pos": ent.start_char,
                "end_pos": ent.end_char
            }
        
        # Template matching
        best_template = self.find_best_template_match(predicted_fields)
        
        return {
            "predicted_fields": predicted_fields,
            "matched_template": best_template,
            "overall_confidence": self._calculate_overall_confidence(predicted_fields)
        }
    
    def find_best_template_match(self, predicted_fields: Dict) -> Dict:
        """
        Tìm template phù hợp nhất dựa trên predicted fields
        """
        if not hasattr(self, 'template_matcher'):
            try:
                import pickle
                with open("models/template_matcher.pkl", "rb") as f:
                    self.template_matcher = pickle.load(f)
            except:
                return {"error": "Template matcher not found"}
        
        # Create query vector from predicted fields
        field_names = list(predicted_fields.keys())
        query_text = " ".join(field_names)
        
        vectorizer = self.template_matcher["vectorizer"]
        template_vectors = self.template_matcher["template_vectors"]
        template_ids = self.template_matcher["template_ids"]
        
        query_vector = vectorizer.transform([query_text])
        similarities = cosine_similarity(query_vector, template_vectors)[0]
        
        # Find best match
        best_idx = np.argmax(similarities)
        best_template_id = template_ids[best_idx]
        best_similarity = similarities[best_idx]
        
        if best_similarity > 0.3:  # Threshold for acceptable match
            best_template = self.template_matcher["templates"][best_template_id]
            return {
                "template_id": best_template_id,
                "template_name": best_template["name"],
                "similarity_score": float(best_similarity),
                "field_mappings": best_template["field_mappings"]
            }
        else:
            return {"template_id": None, "similarity_score": 0.0}
    
    def _calculate_overall_confidence(self, predicted_fields: Dict) -> float:
        """Tính confidence score tổng thể"""
        if not predicted_fields:
            return 0.0
        
        confidences = [
            field_data.get("confidence", 0.0) 
            for field_data in predicted_fields.values() 
            if isinstance(field_data, dict)
        ]
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def _find_template_match(self, ocr_result) -> Optional[int]:
        """Helper method để tìm template match cho OCR result"""
        # Implementation để link OCR với template
        return None

# Usage example:
def setup_ai_training_pipeline():
    """
    Setup và chạy training pipeline
    """
    trainer = InvoiceAITrainer()
    
    # 1. Collect training data
    print("Collecting training data...")
    training_data = trainer.collect_training_data()
    print(f"Collected {len(training_data['templates'])} templates and {len(training_data['invoices'])} invoices")
    
    # 2. Train NER model
    print("Training NER model...")
    trainer.train_ner_model(training_data)
    
    # 3. Build template matcher
    print("Building template matcher...")
    trainer.build_template_matcher(training_data)
    
    print("AI training pipeline setup completed!")
    
    return trainer

if __name__ == "__main__":
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    # Setup training pipeline
    trainer = setup_ai_training_pipeline()
    
    # Test prediction
    sample_text = "Hóa đơn số: INV-2024-001\nCông ty ABC\nTổng tiền: 1,250,000 VND"
    result = trainer.predict_invoice_fields(sample_text)
    print("Prediction result:", result)