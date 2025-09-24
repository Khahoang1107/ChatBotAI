"""
Fine-tune PhoBERT for Vietnamese Invoice Domain
"""
import os
import json
import logging
from typing import List, Dict, Tuple
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvoiceIntentDataset(Dataset):
    """Dataset for invoice intent classification"""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class InvoiceBERTFineTuner:
    """Fine-tune BERT model for Vietnamese invoice processing"""
    
    def __init__(self, model_name: str = "vinai/phobert-base"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.label_to_id = {}
        self.id_to_label = {}
        
    def load_training_data(self, data_path: str = "data/nlu_bert.yml") -> Tuple[List[str], List[str]]:
        """Load training data from Rasa NLU file"""
        texts = []
        labels = []
        
        # Sample invoice-specific training data
        training_samples = {
            "upload_invoice": [
                "Tôi muốn upload hóa đơn này",
                "Xử lý hóa đơn giúp tôi",
                "OCR hóa đơn này",
                "Đọc thông tin từ hóa đơn",
                "Trích xuất dữ liệu hóa đơn",
                "Tôi có ảnh hóa đơn cần xử lý",
                "Scan hóa đơn và lấy thông tin",
                "Nhận diện text trong hóa đơn",
                "Chuyển đổi hóa đơn thành dữ liệu",
                "Phân tích nội dung hóa đơn"
            ],
            "search_invoice": [
                "Tìm hóa đơn của công ty ABC",
                "Tìm hóa đơn số INV-001", 
                "Tìm hóa đơn tháng 3",
                "Tìm hóa đơn có số tiền 1 triệu",
                "Hiển thị hóa đơn gần đây",
                "Lọc hóa đơn theo điều kiện",
                "Tìm kiếm hóa đơn Samsung",
                "Tìm hóa đơn từ ngày 1 đến 30",
                "Danh sách hóa đơn tháng này",
                "Tìm hóa đơn chứa từ khóa điện thoại"
            ],
            "invoice_status": [
                "Trạng thái hóa đơn INV-123",
                "Hóa đơn đã xử lý chưa",
                "Kiểm tra tình trạng hóa đơn",
                "OCR thành công chưa",
                "Kết quả xử lý hóa đơn",
                "Độ tin cậy của hóa đơn",
                "Hóa đơn có lỗi không",
                "Chi tiết hóa đơn đã upload",
                "Thông tin xử lý hóa đơn",
                "Tình trạng OCR"
            ],
            "statistics": [
                "Thống kê hóa đơn tháng này",
                "Báo cáo tổng kết",
                "Phân tích dữ liệu hóa đơn", 
                "Tổng số hóa đơn đã xử lý",
                "Doanh thu từ hóa đơn",
                "Thống kê theo thời gian",
                "Xu hướng hóa đơn",
                "Dashboard hóa đơn",
                "Số liệu thống kê",
                "Báo cáo tài chính"
            ],
            "create_template": [
                "Tạo template hóa đơn mới",
                "Tạo mẫu hóa đơn",
                "Định nghĩa template",
                "Thiết kế mẫu hóa đơn",
                "Tôi muốn tạo template",
                "Thêm template mới",
                "Định dạng hóa đơn mới",
                "Template cho loại hóa đơn này",
                "Tạo form hóa đơn",
                "Layout hóa đơn mới"
            ],
            "greet": [
                "Xin chào",
                "Chào bạn",
                "Hello",
                "Hi",
                "Tôi cần hỗ trợ",
                "Bot ơi",
                "Trợ lý ảo ơi",
                "Chúc buổi sáng tốt lành",
                "Bạn có thể giúp tôi không",
                "Xin chào bạn"
            ],
            "ask_for_help": [
                "Tôi không biết làm gì",
                "Bạn có thể hướng dẫn không",
                "Giúp tôi",
                "Tôi cần hỗ trợ",
                "Hướng dẫn chi tiết",
                "Tôi bị lỗi",
                "Không thể upload file",
                "OCR không hoạt động",
                "Có vấn đề gì đó",
                "Không hiểu cách sử dụng"
            ]
        }
        
        # Convert to texts and labels
        for intent, examples in training_samples.items():
            for example in examples:
                texts.append(example)
                labels.append(intent)
        
        logger.info(f"Loaded {len(texts)} training examples for {len(set(labels))} intents")
        return texts, labels
    
    def prepare_data(self, texts: List[str], labels: List[str]) -> Tuple[Dataset, Dataset]:
        """Prepare training and validation datasets"""
        
        # Create label mappings
        unique_labels = sorted(list(set(labels)))
        self.label_to_id = {label: idx for idx, label in enumerate(unique_labels)}
        self.id_to_label = {idx: label for label, idx in self.label_to_id.items()}
        
        # Convert labels to IDs
        label_ids = [self.label_to_id[label] for label in labels]
        
        # Split data
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, label_ids, test_size=0.2, random_state=42, stratify=label_ids
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Create datasets
        train_dataset = InvoiceIntentDataset(train_texts, train_labels, self.tokenizer)
        val_dataset = InvoiceIntentDataset(val_texts, val_labels, self.tokenizer)
        
        logger.info(f"Training set: {len(train_dataset)} examples")
        logger.info(f"Validation set: {len(val_dataset)} examples")
        
        return train_dataset, val_dataset
    
    def fine_tune_model(self, train_dataset: Dataset, val_dataset: Dataset, output_dir: str = "./models/phobert-invoice"):
        """Fine-tune PhoBERT model"""
        
        # Load model
        num_labels = len(self.label_to_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=num_labels
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=50,
            save_strategy="steps",
            save_steps=100,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            save_total_limit=3,
            dataloader_num_workers=4,
            fp16=torch.cuda.is_available(),  # Use mixed precision if GPU available
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        # Train model
        logger.info("Starting fine-tuning...")
        trainer.train()
        
        # Save model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        # Save label mappings
        with open(os.path.join(output_dir, "label_mappings.json"), "w", encoding="utf-8") as f:
            json.dump({
                "label_to_id": self.label_to_id,
                "id_to_label": self.id_to_label
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Model saved to {output_dir}")
        
        return trainer
    
    def evaluate_model(self, val_dataset: Dataset, trainer: Trainer):
        """Evaluate fine-tuned model"""
        
        logger.info("Evaluating model...")
        
        # Get predictions
        predictions = trainer.predict(val_dataset)
        pred_labels = np.argmax(predictions.predictions, axis=1)
        true_labels = predictions.label_ids
        
        # Calculate metrics
        accuracy = accuracy_score(true_labels, pred_labels)
        
        # Classification report
        label_names = [self.id_to_label[i] for i in range(len(self.id_to_label))]
        report = classification_report(
            true_labels, 
            pred_labels, 
            target_names=label_names,
            output_dict=True
        )
        
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info("Classification Report:")
        logger.info(classification_report(true_labels, pred_labels, target_names=label_names))
        
        return accuracy, report

def main():
    """Main fine-tuning process"""
    
    # Initialize fine-tuner
    fine_tuner = InvoiceBERTFineTuner()
    
    # Load training data
    texts, labels = fine_tuner.load_training_data()
    
    # Prepare datasets
    train_dataset, val_dataset = fine_tuner.prepare_data(texts, labels)
    
    # Fine-tune model
    trainer = fine_tuner.fine_tune_model(train_dataset, val_dataset)
    
    # Evaluate model
    accuracy, report = fine_tuner.evaluate_model(val_dataset, trainer)
    
    logger.info("Fine-tuning completed successfully!")
    logger.info(f"Final accuracy: {accuracy:.4f}")

if __name__ == "__main__":
    main()