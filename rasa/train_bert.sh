#!/bin/bash

# 🧠 BERT-Enhanced Rasa Training Script

echo "🚀 Starting BERT-Enhanced Rasa Training..."

# Set environment variables
export PYTHONPATH="/app:${PYTHONPATH}"
export TRANSFORMERS_CACHE="/app/models/transformers"
export HF_HOME="/app/models/transformers"

# Create necessary directories
mkdir -p models logs

echo "📋 Step 1: Validating training data..."
rasa data validate --config config_bert.yml --data data/nlu_bert.yml data/stories.yml data/rules.yml

if [ $? -ne 0 ]; then
    echo "❌ Training data validation failed!"
    exit 1
fi

echo "✅ Training data validation passed!"

echo "🧠 Step 2: Fine-tuning BERT model for invoice domain..."
python fine_tune_bert.py

echo "🤖 Step 3: Training Rasa model with BERT integration..."
rasa train \
    --config config_bert.yml \
    --data data/nlu_bert.yml data/stories.yml data/rules.yml \
    --out models \
    --fixed-model-name bert_invoice_model \
    --augmentation 0 \
    --debug

if [ $? -eq 0 ]; then
    echo "✅ BERT-Enhanced Rasa training completed successfully!"
    echo "📊 Model saved as: models/bert_invoice_model.tar.gz"
    
    echo "🧪 Step 4: Testing model..."
    echo "Tôi muốn upload hóa đơn" | rasa shell --model models/bert_invoice_model.tar.gz --debug
    
    echo "🎯 Training Summary:"
    echo "- Model: PhoBERT + Rasa Hybrid"
    echo "- Language: Vietnamese"
    echo "- Domain: Invoice Processing"
    echo "- Enhanced Intent Recognition: ✅"
    echo "- Semantic Understanding: ✅"
    echo "- Context Awareness: ✅"
    
else
    echo "❌ Training failed!"
    exit 1
fi