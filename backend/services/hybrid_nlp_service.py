"""
🧠 Hybrid NLP Service: BERT + Rasa + OpenAI
Intelligent invoice processing with multi-layer AI understanding
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
import json
import requests
from datetime import datetime
import openai
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class HybridNLPService:
    """
    🚀 Hybrid NLP Service combining:
    - BERT: Deep semantic understanding
    - Rasa: Dialog management & business logic  
    - OpenAI: Advanced reasoning & generation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # BERT Configuration
        self.bert_model_path = config.get("bert_model_path", "models/phobert-invoice")
        self.bert_tokenizer = None
        self.bert_model = None
        self.bert_confidence_threshold = config.get("bert_confidence_threshold", 0.7)
        
        # Rasa Configuration  
        self.rasa_endpoint = config.get("rasa_endpoint", "http://rasa:5005")
        self.rasa_confidence_threshold = config.get("rasa_confidence_threshold", 0.6)
        
        # OpenAI Configuration
        self.openai_api_key = config.get("openai_api_key", "")
        self.openai_model = config.get("openai_model", "gpt-4")
        self.openai_confidence_threshold = config.get("openai_confidence_threshold", 0.8)
        
        # Domain Knowledge
        self.invoice_intents = {
            "upload_invoice", "search_invoice", "invoice_status", 
            "create_template", "statistics", "export_data", "train_ai"
        }
        
        self.setup_components()
    
    def setup_components(self):
        """Initialize all NLP components"""
        logger.info("🚀 Initializing Hybrid NLP Service...")
        
        # Setup OpenAI
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            logger.info("✅ OpenAI configured")
        
        # Load BERT model
        try:
            self.load_bert_model()
            logger.info("✅ BERT model loaded")
        except Exception as e:
            logger.warning(f"⚠️ BERT model not available: {e}")
        
        logger.info("🎯 Hybrid NLP Service ready!")
    
    def load_bert_model(self):
        """Load fine-tuned BERT model"""
        try:
            self.bert_tokenizer = AutoTokenizer.from_pretrained(self.bert_model_path)
            self.bert_model = AutoModelForSequenceClassification.from_pretrained(self.bert_model_path)
            self.bert_model.eval()
            
            # Load label mappings
            with open(f"{self.bert_model_path}/label_mappings.json", "r", encoding="utf-8") as f:
                mappings = json.load(f)
                self.id_to_label = mappings["id_to_label"]
                self.label_to_id = mappings["label_to_id"]
                
        except Exception as e:
            logger.error(f"Failed to load BERT model: {e}")
            raise
    
    async def process_message(self, message: str, user_id: str = None, context: Dict = None) -> Dict[str, Any]:
        """
        🧠 Main processing pipeline: BERT → Rasa → OpenAI
        """
        processing_start = datetime.now()
        results = {
            "message": message,
            "user_id": user_id,
            "timestamp": processing_start.isoformat(),
            "processing_pipeline": [],
            "final_response": None,
            "confidence_scores": {},
            "metadata": {}
        }
        
        logger.info(f"🔄 Processing: '{message}' for user {user_id}")
        
        # Step 1: BERT Intent Classification
        bert_result = await self.process_with_bert(message)
        results["processing_pipeline"].append("BERT")
        results["confidence_scores"]["bert"] = bert_result.get("confidence", 0.0)
        results["metadata"]["bert"] = bert_result
        
        # Step 2: Rasa Dialog Management
        rasa_result = await self.process_with_rasa(message, user_id, context)
        results["processing_pipeline"].append("Rasa")
        results["confidence_scores"]["rasa"] = rasa_result.get("confidence", 0.0)
        results["metadata"]["rasa"] = rasa_result
        
        # Step 3: Decision Logic - Which response to use?
        final_response = await self.decide_final_response(message, bert_result, rasa_result, context)
        results["final_response"] = final_response
        
        # Step 4: OpenAI Enhancement (if needed)
        if final_response.get("use_openai", False):
            openai_result = await self.enhance_with_openai(message, final_response, context)
            results["processing_pipeline"].append("OpenAI")
            results["confidence_scores"]["openai"] = openai_result.get("confidence", 0.0)
            results["metadata"]["openai"] = openai_result
            results["final_response"] = openai_result
        
        # Calculate processing time
        processing_time = (datetime.now() - processing_start).total_seconds()
        results["processing_time"] = processing_time
        
        logger.info(f"✅ Processed in {processing_time:.2f}s with pipeline: {' → '.join(results['processing_pipeline'])}")
        
        return results
    
    async def process_with_bert(self, message: str) -> Dict[str, Any]:
        """🧠 BERT-based intent classification"""
        if not self.bert_model or not self.bert_tokenizer:
            return {"intent": None, "confidence": 0.0, "error": "BERT model not available"}
        
        try:
            # Tokenize and encode
            inputs = self.bert_tokenizer(
                message,
                return_tensors="pt",
                max_length=256,
                truncation=True,
                padding=True
            )
            
            # Get predictions
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0][predicted_class].item()
            
            # Get predicted intent
            predicted_intent = self.id_to_label.get(str(predicted_class), "unknown")
            
            return {
                "intent": predicted_intent,
                "confidence": confidence,
                "model": "PhoBERT",
                "is_invoice_related": predicted_intent in self.invoice_intents,
                "all_probabilities": {
                    self.id_to_label.get(str(i), f"class_{i}"): float(prob) 
                    for i, prob in enumerate(probabilities[0])
                }
            }
            
        except Exception as e:
            logger.error(f"BERT processing error: {e}")
            return {"intent": None, "confidence": 0.0, "error": str(e)}
    
    async def process_with_rasa(self, message: str, user_id: str, context: Dict) -> Dict[str, Any]:
        """🤖 Rasa dialog management"""
        try:
            # Prepare Rasa request
            rasa_payload = {
                "sender": user_id or "default_user",
                "message": message
            }
            
            # Add context if available
            if context:
                rasa_payload["metadata"] = context
            
            # Send to Rasa
            response = requests.post(
                f"{self.rasa_endpoint}/webhooks/rest/webhook",
                json=rasa_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                rasa_responses = response.json()
                
                if rasa_responses:
                    # Get first response
                    rasa_response = rasa_responses[0]
                    
                    # Get intent info from Rasa NLU
                    nlu_response = requests.post(
                        f"{self.rasa_endpoint}/model/parse",
                        json={"text": message},
                        timeout=5
                    )
                    
                    intent_info = {}
                    if nlu_response.status_code == 200:
                        nlu_data = nlu_response.json()
                        intent_info = nlu_data.get("intent", {})
                    
                    return {
                        "response": rasa_response.get("text", ""),
                        "intent": intent_info.get("name"),
                        "confidence": intent_info.get("confidence", 0.0),
                        "entities": nlu_data.get("entities", []) if 'nlu_data' in locals() else [],
                        "buttons": rasa_response.get("buttons", []),
                        "custom": rasa_response.get("custom", {}),
                        "model": "Rasa"
                    }
                else:
                    return {"response": "", "confidence": 0.0, "model": "Rasa", "error": "No response from Rasa"}
            else:
                return {"response": "", "confidence": 0.0, "model": "Rasa", "error": f"Rasa HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Rasa processing error: {e}")
            return {"response": "", "confidence": 0.0, "model": "Rasa", "error": str(e)}
    
    async def decide_final_response(self, message: str, bert_result: Dict, rasa_result: Dict, context: Dict) -> Dict[str, Any]:
        """
        🎯 Intelligent decision logic for choosing the best response
        """
        
        # Get confidence scores
        bert_confidence = bert_result.get("confidence", 0.0)
        rasa_confidence = rasa_result.get("confidence", 0.0)
        
        # Get intents
        bert_intent = bert_result.get("intent")
        rasa_intent = rasa_result.get("intent")
        
        # Decision rules
        decision_logic = {
            "chosen_model": None,
            "reason": "",
            "confidence": 0.0,
            "response": "",
            "use_openai": False
        }
        
        # Rule 1: Both models agree with high confidence
        if (bert_intent == rasa_intent and 
            bert_confidence > self.bert_confidence_threshold and 
            rasa_confidence > self.rasa_confidence_threshold):
            
            decision_logic.update({
                "chosen_model": "Rasa (BERT confirmed)",
                "reason": "Both models agree with high confidence",
                "confidence": min(bert_confidence, rasa_confidence),
                "response": rasa_result.get("response", ""),
                "intent": rasa_intent
            })
        
        # Rule 2: BERT has very high confidence on invoice-related intent
        elif (bert_confidence > 0.9 and 
              bert_result.get("is_invoice_related", False)):
            
            decision_logic.update({
                "chosen_model": "BERT (high confidence)",
                "reason": "BERT very confident on invoice domain",
                "confidence": bert_confidence,
                "response": f"Tôi hiểu bạn muốn {bert_intent}. Tôi sẽ hỗ trợ bạn với điều đó.",
                "intent": bert_intent,
                "use_openai": True  # Use OpenAI to generate better response
            })
        
        # Rule 3: Rasa has good response and reasonable confidence
        elif (rasa_confidence > self.rasa_confidence_threshold and 
              rasa_result.get("response", "").strip()):
            
            decision_logic.update({
                "chosen_model": "Rasa",
                "reason": "Rasa has good confidence and response",
                "confidence": rasa_confidence,
                "response": rasa_result.get("response", ""),
                "intent": rasa_intent
            })
        
        # Rule 4: Neither model is confident - use OpenAI
        elif max(bert_confidence, rasa_confidence) < 0.5:
            
            decision_logic.update({
                "chosen_model": "OpenAI (fallback)",
                "reason": "Low confidence from both models",
                "confidence": 0.3,
                "response": "Tôi cần suy nghĩ về câu hỏi này...",
                "use_openai": True
            })
        
        # Rule 5: Default to best confidence
        else:
            if bert_confidence > rasa_confidence:
                decision_logic.update({
                    "chosen_model": "BERT",
                    "reason": "BERT has higher confidence",
                    "confidence": bert_confidence,
                    "response": f"Dựa trên hiểu biết của tôi, bạn đang {bert_intent}.",
                    "intent": bert_intent,
                    "use_openai": True
                })
            else:
                decision_logic.update({
                    "chosen_model": "Rasa",
                    "reason": "Rasa has higher confidence",
                    "confidence": rasa_confidence,
                    "response": rasa_result.get("response", ""),
                    "intent": rasa_intent
                })
        
        return decision_logic
    
    async def enhance_with_openai(self, message: str, current_response: Dict, context: Dict) -> Dict[str, Any]:
        """
        🤖 OpenAI enhancement for complex responses
        """
        if not self.openai_api_key:
            return current_response
        
        try:
            # Prepare context for OpenAI
            system_prompt = """
            Bạn là trợ lý AI chuyên về xử lý hóa đơn và tài liệu kế toán tiếng Việt.
            
            Khả năng của bạn:
            - Xử lý OCR hóa đơn
            - Tìm kiếm và phân tích hóa đơn
            - Tạo báo cáo thống kê
            - Hướng dẫn sử dụng hệ thống
            
            Hãy trả lời một cách thân thiện, chuyên nghiệp và hữu ích.
            """
            
            # Create messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Add context if available
            if context and current_response.get("intent"):
                context_message = f"Intent được nhận diện: {current_response.get('intent')}"
                messages.append({"role": "assistant", "content": context_message})
            
            # Call OpenAI
            response = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            openai_response = response.choices[0].message.content
            
            # Update response
            enhanced_response = current_response.copy()
            enhanced_response.update({
                "response": openai_response,
                "model": f"{current_response.get('chosen_model')} + OpenAI",
                "confidence": 0.85,  # High confidence for OpenAI
                "enhanced": True
            })
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"OpenAI enhancement error: {e}")
            return current_response
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "service": "Hybrid NLP (BERT + Rasa + OpenAI)",
            "components": {
                "bert_available": self.bert_model is not None,
                "rasa_endpoint": self.rasa_endpoint,
                "openai_available": bool(self.openai_api_key)
            },
            "confidence_thresholds": {
                "bert": self.bert_confidence_threshold,
                "rasa": self.rasa_confidence_threshold,
                "openai": self.openai_confidence_threshold
            },
            "supported_intents": list(self.invoice_intents)
        }


# Example usage and testing
async def test_hybrid_service():
    """Test the hybrid NLP service"""
    
    config = {
        "bert_model_path": "models/phobert-invoice",
        "rasa_endpoint": "http://localhost:5005",
        "openai_api_key": "",  # Add your OpenAI key
        "bert_confidence_threshold": 0.7,
        "rasa_confidence_threshold": 0.6
    }
    
    service = HybridNLPService(config)
    
    # Test messages
    test_messages = [
        "Tôi muốn upload hóa đơn",
        "Tìm hóa đơn của công ty ABC tháng 3",
        "Thống kê doanh thu tháng này",
        "Bạn có thể giúp tôi tạo template không?",
        "Hôm nay trời đẹp quá"  # Out of scope
    ]
    
    for message in test_messages:
        print(f"\n🧪 Testing: '{message}'")
        result = await service.process_message(message, "test_user")
        print(f"🎯 Response: {result['final_response']['response']}")
        print(f"📊 Pipeline: {' → '.join(result['processing_pipeline'])}")
        print(f"⏱️ Time: {result['processing_time']:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_hybrid_service())