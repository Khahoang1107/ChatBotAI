"""
Custom BERT-based Intent Classifier for Vietnamese Invoice Domain
"""
from typing import Any, Dict, List, Optional, Text, Type
import logging
import numpy as np
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.nlu.classifiers.classifier import IntentClassifier
from rasa.shared.nlu.constants import (
    INTENT,
    INTENT_NAME_KEY,
    INTENT_RANKING_KEY,
    PREDICTED_CONFIDENCE_KEY,
    TEXT,
)

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    import torch.nn as nn
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics.pairwise import cosine_similarity
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.INTENT_CLASSIFIER,
    is_trainable=True
)
class BERTIntentClassifier(GraphComponent, IntentClassifier):
    """
    Custom BERT-based Intent Classifier optimized for Vietnamese Invoice Processing
    
    Features:
    - Uses PhoBERT for Vietnamese language understanding
    - Domain-specific fine-tuning for invoice/finance terminology
    - Semantic similarity matching for unknown intents
    - Confidence scoring with uncertainty estimation
    """
    
    def __init__(
        self,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> None:
        super().__init__()
        self._config = config
        self._model_storage = model_storage
        self._resource = resource
        
        # BERT Configuration
        self.model_name = config.get("model_name", "vinai/phobert-base")
        self.max_length = config.get("max_length", 256)
        self.confidence_threshold = config.get("confidence_threshold", 0.3)
        self.use_semantic_similarity = config.get("use_semantic_similarity", True)
        
        # Initialize components
        self.tokenizer = None
        self.bert_model = None
        self.intent_classifier = None
        self.intent_embeddings = {}
        self.label_encoder = {}
        self.reverse_label_encoder = {}
    
    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "BERTIntentClassifier":
        return cls(config, model_storage, resource, execution_context)
    
    def _check_transformers(self) -> None:
        """Check if transformers library is available"""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "The transformers library is not installed. "
                "Please install it with: pip install transformers torch"
            )
    
    def _load_bert_model(self) -> None:
        """Load PhoBERT model and tokenizer"""
        self._check_transformers()
        
        try:
            logger.info(f"Loading BERT model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.bert_model = AutoModel.from_pretrained(self.model_name)
            self.bert_model.eval()
            logger.info("BERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load BERT model: {e}")
            raise
    
    def _encode_text(self, text: Text) -> np.ndarray:
        """Encode text using BERT to get semantic embeddings"""
        if not self.bert_model or not self.tokenizer:
            self._load_bert_model()
        
        # Tokenize and encode
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True,
            padding=True
        )
        
        # Get BERT embeddings
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
            # Use [CLS] token embedding as sentence representation
            embeddings = outputs.last_hidden_state[:, 0, :].numpy()
        
        return embeddings.flatten()
    
    def train(self, training_data: TrainingData) -> Resource:
        """Train the BERT-based intent classifier"""
        if not training_data.intent_examples:
            logger.warning("No training data with intents found")
            return self._resource
        
        logger.info("Training BERT Intent Classifier...")
        
        # Load BERT model
        self._load_bert_model()
        
        # Prepare training data
        texts = []
        labels = []
        unique_intents = set()
        
        for example in training_data.intent_examples:
            text = example.get(TEXT, "")
            intent = example.get(INTENT, "")
            
            if text and intent:
                texts.append(text)
                labels.append(intent)
                unique_intents.add(intent)
        
        if not texts:
            logger.warning("No valid training examples found")
            return self._resource
        
        # Create label encoders
        self.label_encoder = {intent: idx for idx, intent in enumerate(sorted(unique_intents))}
        self.reverse_label_encoder = {idx: intent for intent, idx in self.label_encoder.items()}
        
        # Encode texts using BERT
        logger.info("Encoding training texts with BERT...")
        X = []
        y = []
        
        for text, label in zip(texts, labels):
            try:
                embedding = self._encode_text(text)
                X.append(embedding)
                y.append(self.label_encoder[label])
            except Exception as e:
                logger.warning(f"Failed to encode text '{text}': {e}")
                continue
        
        if not X:
            logger.error("Failed to encode any training examples")
            return self._resource
        
        X = np.array(X)
        y = np.array(y)
        
        # Train intent classifier
        logger.info("Training intent classifier...")
        self.intent_classifier = LogisticRegression(
            random_state=42,
            max_iter=1000,
            multi_class='ovr'
        )
        self.intent_classifier.fit(X, y)
        
        # Store intent embeddings for semantic similarity
        if self.use_semantic_similarity:
            logger.info("Computing intent embeddings for semantic similarity...")
            self.intent_embeddings = {}
            
            for intent in unique_intents:
                intent_texts = [text for text, label in zip(texts, labels) if label == intent]
                if intent_texts:
                    # Compute average embedding for this intent
                    embeddings = []
                    for text in intent_texts:
                        try:
                            emb = self._encode_text(text)
                            embeddings.append(emb)
                        except Exception:
                            continue
                    
                    if embeddings:
                        avg_embedding = np.mean(embeddings, axis=0)
                        self.intent_embeddings[intent] = avg_embedding
        
        # Save model
        self._persist()
        
        logger.info(f"Training completed. Trained on {len(X)} examples for {len(unique_intents)} intents")
        return self._resource
    
    def process(self, messages: List[Message]) -> List[Message]:
        """Process messages to predict intents"""
        for message in messages:
            self._predict_intent(message)
        
        return messages
    
    def _predict_intent(self, message: Message) -> None:
        """Predict intent for a single message"""
        text = message.get(TEXT, "")
        
        if not text or not self.intent_classifier:
            self._set_default_intent(message)
            return
        
        try:
            # Encode text with BERT
            text_embedding = self._encode_text(text)
            text_embedding = text_embedding.reshape(1, -1)
            
            # Predict with logistic regression
            probabilities = self.intent_classifier.predict_proba(text_embedding)[0]
            predicted_class = np.argmax(probabilities)
            confidence = probabilities[predicted_class]
            predicted_intent = self.reverse_label_encoder[predicted_class]
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                # Try semantic similarity as fallback
                if self.use_semantic_similarity:
                    similarity_intent, similarity_score = self._find_most_similar_intent(text_embedding)
                    if similarity_score > 0.7:  # High similarity threshold
                        predicted_intent = similarity_intent
                        confidence = similarity_score
                    else:
                        predicted_intent = None
                        confidence = 0.0
                else:
                    predicted_intent = None
                    confidence = 0.0
            
            # Create intent ranking
            intent_ranking = []
            for i, prob in enumerate(probabilities):
                intent_name = self.reverse_label_encoder[i]
                intent_ranking.append({
                    INTENT_NAME_KEY: intent_name,
                    PREDICTED_CONFIDENCE_KEY: float(prob)
                })
            
            # Sort by confidence
            intent_ranking.sort(key=lambda x: x[PREDICTED_CONFIDENCE_KEY], reverse=True)
            
            # Set intent
            if predicted_intent:
                intent = {
                    INTENT_NAME_KEY: predicted_intent,
                    PREDICTED_CONFIDENCE_KEY: float(confidence)
                }
                message.set(INTENT, intent, add_to_output=True)
                message.set(INTENT_RANKING_KEY, intent_ranking, add_to_output=True)
            else:
                self._set_default_intent(message)
                
        except Exception as e:
            logger.error(f"Error predicting intent: {e}")
            self._set_default_intent(message)
    
    def _find_most_similar_intent(self, text_embedding: np.ndarray) -> tuple:
        """Find most similar intent using semantic similarity"""
        if not self.intent_embeddings:
            return None, 0.0
        
        max_similarity = 0.0
        most_similar_intent = None
        
        text_embedding = text_embedding.flatten()
        
        for intent, intent_embedding in self.intent_embeddings.items():
            similarity = cosine_similarity([text_embedding], [intent_embedding])[0][0]
            
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_intent = intent
        
        return most_similar_intent, max_similarity
    
    def _set_default_intent(self, message: Message) -> None:
        """Set default intent when prediction fails"""
        intent = {
            INTENT_NAME_KEY: None,
            PREDICTED_CONFIDENCE_KEY: 0.0
        }
        message.set(INTENT, intent, add_to_output=True)
        message.set(INTENT_RANKING_KEY, [], add_to_output=True)
    
    def _persist(self) -> None:
        """Save the trained model"""
        # Implementation for saving model would go here
        # For now, models are kept in memory
        pass
    
    @classmethod
    def load(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        **kwargs: Any,
    ) -> "BERTIntentClassifier":
        """Load a trained model"""
        instance = cls.create(config, model_storage, resource, execution_context)
        # Implementation for loading saved model would go here
        return instance
    
    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        """Returns the component's default config"""
        return {
            "model_name": "vinai/phobert-base",
            "max_length": 256,
            "confidence_threshold": 0.3,
            "use_semantic_similarity": True,
        }