    def _merge_ocr_and_ai_results(self, traditional_result: Dict, ai_result: Dict) -> Dict:
        """
        Merge traditional OCR và AI prediction results
        """
        merged = traditional_result.copy()
        
        if 'predicted_fields' in ai_result and ai_result['predicted_fields']:
            ai_fields = ai_result['predicted_fields']
            
            # Enhance parsed_data with AI predictions
            if 'parsed_data' not in merged:
                merged['parsed_data'] = {}
            
            for field_name, field_info in ai_fields.items():
                if isinstance(field_info, dict) and 'value' in field_info:
                    # Use AI prediction if confidence is high enough
                    confidence = field_info.get('confidence', 0.0)
                    if confidence > 0.6:  # Threshold for AI predictions
                        merged['parsed_data'][field_name] = {
                            'value': field_info['value'],
                            'confidence': confidence,
                            'source': 'ai_prediction',
                            'position': {
                                'start': field_info.get('start_pos'),
                                'end': field_info.get('end_pos')
                            }
                        }
        
        # Add AI metadata
        merged['ai_predictions'] = ai_result.get('predicted_fields', {})
        merged['matched_template'] = ai_result.get('matched_template', {})
        merged['ai_confidence'] = ai_result.get('overall_confidence', 0.0)
        
        # Update overall confidence
        if merged.get('ai_confidence', 0) > merged.get('confidence_score', 0):
            merged['confidence_score'] = merged['ai_confidence']
        
        return merged
    
    def train_ai_model(self, retrain: bool = False) -> Dict[str, Any]:
        """
        Trigger AI model training/retraining
        """
        if not AI_AVAILABLE:
            return {'success': False, 'error': 'AI training not available'}
        
        try:
            if not self.ai_trainer:
                self.ai_trainer = InvoiceAITrainer()
            
            # Collect training data từ database
            training_data = self.ai_trainer.collect_training_data()
            
            if len(training_data['invoices']) < 10:
                return {
                    'success': False, 
                    'error': 'Not enough training data. Need at least 10 invoice samples.'
                }
            
            # Train NER model
            self.ai_trainer.train_ner_model(training_data)
            
            # Build template matcher
            self.ai_trainer.build_template_matcher(training_data)
            
            return {
                'success': True,
                'message': 'AI model training completed',
                'training_data_count': len(training_data['invoices']),
                'template_count': len(training_data['templates'])
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Training failed: {str(e)}'}
    
    def get_ai_status(self) -> Dict[str, Any]:
        """
        Get AI system status and capabilities
        """
        status = {
            'ai_available': AI_AVAILABLE,
            'ai_trainer_loaded': self.ai_trainer is not None,
            'models_trained': False,
            'last_training': None
        }
        
        if self.ai_trainer:
            # Check if models exist
            import os
            ner_model_exists = os.path.exists('models/invoice_ner_model')
            template_matcher_exists = os.path.exists('models/template_matcher.pkl')
            
            status['models_trained'] = ner_model_exists and template_matcher_exists
            status['ner_model_available'] = ner_model_exists
            status['template_matcher_available'] = template_matcher_exists
            
            # Get model info if available
            if status['models_trained']:
                try:
                    # Get training data stats
                    training_data = self.ai_trainer.collect_training_data()
                    status['training_data_stats'] = {
                        'invoice_count': len(training_data['invoices']),
                        'template_count': len(training_data['templates'])
                    }
                except:
                    pass
        
        return status