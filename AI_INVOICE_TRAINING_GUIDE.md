# Hướng dẫn Huấn luyện AI cho Invoice OCR Recognition

## 1. Thu thập và Chuẩn bị Training Data

### A. Loại dữ liệu cần thu thập:

- **Hình ảnh hóa đơn**: PDF, JPG, PNG từ nhiều công ty khác nhau
- **Ground truth data**: Annotation chính xác các trường thông tin
- **Template variations**: Các loại template khác nhau (A4, A5, landscape, portrait)

### B. Structure Training Data:

```
training_data/
├── images/
│   ├── invoice_001.pdf
│   ├── invoice_002.jpg
│   └── ...
├── annotations/
│   ├── invoice_001.json
│   ├── invoice_002.json
│   └── ...
└── templates/
    ├── template_A.json
    ├── template_B.json
    └── ...
```

### C. Annotation Format (JSON):

```json
{
  "image_id": "invoice_001",
  "image_path": "images/invoice_001.pdf",
  "width": 1240,
  "height": 1754,
  "fields": [
    {
      "field_name": "invoice_number",
      "field_value": "INV-2024-001",
      "bounding_box": [100, 150, 300, 180],
      "confidence": 1.0,
      "field_type": "text"
    },
    {
      "field_name": "total_amount",
      "field_value": "1,250,000",
      "bounding_box": [800, 900, 1000, 930],
      "confidence": 1.0,
      "field_type": "currency"
    }
  ]
}
```

## 2. Model Architecture

### A. Computer Vision Pipeline:

1. **Document Layout Analysis**: Phát hiện các khu vực text
2. **Text Recognition (OCR)**: Trích xuất text từ image
3. **Information Extraction (IE)**: Nhận diện và phân loại fields
4. **Template Matching**: So sánh với templates đã biết

### B. Recommended Tech Stack:

- **OCR Engine**: Tesseract, PaddleOCR, hoặc Google Vision API
- **Deep Learning**: PyTorch/TensorFlow với BERT/RoBERTa cho NER
- **Document AI**: LayoutLM, DocFormer cho document understanding
- **Template Matching**: Similarity algorithms (cosine, jaccard)

## 3. Training Process

### A. Data Preprocessing:

```python
def preprocess_invoice_image(image_path):
    # 1. Image enhancement
    image = cv2.imread(image_path)
    image = improve_image_quality(image)

    # 2. OCR text extraction
    ocr_results = pytesseract.image_to_data(image, output_type=Output.DICT)

    # 3. Text cleaning and normalization
    cleaned_text = clean_and_normalize_text(ocr_results)

    return cleaned_text, ocr_results
```

### B. Named Entity Recognition (NER) Training:

```python
# Training data format for NER
training_data = [
    ("Hóa đơn số: INV-2024-001", {"entities": [(13, 26, "INVOICE_NUMBER")]}),
    ("Tổng tiền: 1,250,000 VND", {"entities": [(11, 21, "TOTAL_AMOUNT")]}),
    ("Công ty: ABC Corporation", {"entities": [(9, 24, "COMPANY_NAME")]}),
]

# Train spaCy NER model
nlp = spacy.blank("vi")
ner = nlp.create_pipe("ner")
for _, annotations in training_data:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])
```

### C. Template Learning:

```python
def learn_template_patterns(training_invoices):
    patterns = {}
    for invoice in training_invoices:
        # Analyze field positions
        field_positions = analyze_field_positions(invoice)

        # Extract layout features
        layout_features = extract_layout_features(invoice)

        # Build template signature
        template_signature = create_template_signature(field_positions, layout_features)

        patterns[invoice.template_id] = template_signature

    return patterns
```

## 4. Integration với Existing System

### A. Update OCR Service:

```python
# backend/services/ocr_service.py
class EnhancedOCRService:
    def __init__(self):
        self.nlp_model = load_trained_ner_model()
        self.template_matcher = TemplatePatternMatcher()
        self.confidence_threshold = 0.8

    def process_invoice_with_ai(self, image_path):
        # 1. OCR extraction
        raw_text, ocr_data = self.extract_text(image_path)

        # 2. AI-powered field extraction
        extracted_fields = self.nlp_model(raw_text)

        # 3. Template matching
        best_template = self.template_matcher.find_best_match(extracted_fields)

        # 4. Confidence scoring
        confidence_scores = self.calculate_confidence(extracted_fields, best_template)

        return {
            "extracted_fields": extracted_fields,
            "matched_template": best_template,
            "confidence_scores": confidence_scores,
            "needs_review": any(score < self.confidence_threshold for score in confidence_scores.values())
        }
```

### B. Training Data Collection Hook:

```python
# backend/routes/templates.py - Update existing
@bp.route('/', methods=['POST'])
@jwt_required()
def create_template():
    # ... existing code ...

    # Save training data for AI
    training_data = {
        "template_id": new_template.id,
        "field_mappings": request.json.get('field_mappings', {}),
        "layout_info": analyze_template_layout(new_template),
        "created_at": datetime.utcnow()
    }

    # Store in MongoDB for AI training
    training_service.save_template_training_data(training_data)

    return jsonify(new_template.to_dict()), 201
```

## 5. Continuous Learning

### A. Feedback Loop:

- User corrections → Training data
- Template usage patterns → Model improvement
- OCR confidence scores → Quality assessment

### B. Model Retraining:

```python
# Scheduled retraining process
def retrain_model_weekly():
    # 1. Collect new training data
    new_data = collect_user_corrections_and_new_templates()

    # 2. Augment existing dataset
    augmented_dataset = merge_training_data(existing_data, new_data)

    # 3. Retrain models
    retrain_ner_model(augmented_dataset)
    retrain_template_matcher(augmented_dataset)

    # 4. Evaluate and deploy
    if model_performance_improved():
        deploy_new_model()
```

## 6. Performance Monitoring

### A. Metrics to Track:

- **Field Extraction Accuracy**: Per field type accuracy
- **Template Matching Accuracy**: Correct template identification rate
- **OCR Quality Score**: Text recognition confidence
- **User Correction Rate**: How often users fix AI predictions

### B. A/B Testing:

- Test different OCR engines
- Compare template matching algorithms
- Evaluate field extraction confidence thresholds

## 7. Deployment Strategy

### A. Model Serving:

```python
# chatbot/models/ai_model.py
class InvoiceAIModel:
    def __init__(self):
        self.ner_model = load_model("models/invoice_ner.pkl")
        self.template_matcher = load_model("models/template_matcher.pkl")

    def predict(self, ocr_text, image_features=None):
        # AI prediction logic
        fields = self.ner_model.predict(ocr_text)
        template = self.template_matcher.predict(fields, image_features)

        return {
            "predicted_fields": fields,
            "matched_template": template,
            "confidence": self.calculate_overall_confidence(fields, template)
        }
```

### B. API Integration:

```python
# New endpoint for AI-powered OCR
@bp.route('/ocr/ai-extract', methods=['POST'])
@jwt_required()
def ai_extract_invoice():
    file = request.files['file']

    # Traditional OCR
    ocr_result = ocr_service.process_file(file)

    # AI Enhancement
    ai_result = ai_model.predict(ocr_result.text)

    # Merge results
    enhanced_result = merge_ocr_and_ai_results(ocr_result, ai_result)

    return jsonify(enhanced_result)
```

## Kết luận

Hệ thống AI này sẽ:

1. **Tự động học** từ mỗi template mới
2. **Cải thiện accuracy** theo thời gian
3. **Giảm manual work** cho users
4. **Hỗ trợ multiple formats** (PDF, image, scan)
5. **Adaptable** cho different invoice layouts

Training data và model sẽ được lưu trữ trong MongoDB cluster để chatbot có thể access và continuously learn!
