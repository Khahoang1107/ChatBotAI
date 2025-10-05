# 🤖 RAG + GPT Integration Flow

## 🎯 Mục đích

Kết hợp **RAG (Retrieval-Augmented Generation)** với **Google AI (Gemini)** để trả lời câu hỏi dựa trên **dữ liệu thực tế** từ hóa đơn đã upload.

## 📊 Workflow Chi Tiết

### 1️⃣ User hỏi câu hỏi

```
User: "Có bao nhiêu hóa đơn của CÔNG TY ABC?"
```

### 2️⃣ Chatbot detect intent

```python
Intent: data_query
Pattern matched: r'(có bao nhiêu|bao nhiêu)'
Handler: handle_data_query()
```

### 3️⃣ RAG Semantic Search

```http
POST http://localhost:8000/chat/rag-search
Content-Type: application/json

{
  "query": "Có bao nhiêu hóa đơn của CÔNG TY ABC?",
  "top_k": 5
}
```

**RAG Service:**

- Embed query thành vector (sentence-transformers)
- Search trong ChromaDB
- Tìm top 5 documents tương tự nhất
- Return với score + metadata

**Response:**

```json
{
  "success": true,
  "results": [
    {
      "content": "Invoice: MTT-001\nBuyer: CÔNG TY ABC\nAmount: 1,500,000 VND",
      "score": 0.95,
      "metadata": {
        "invoice_code": "MTT-001",
        "buyer_name": "CÔNG TY ABC",
        "total_amount": "1,500,000 VND"
      }
    },
    {
      "content": "Invoice: MTT-003\nBuyer: CÔNG TY ABC\nAmount: 2,300,000 VND",
      "score": 0.88,
      "metadata": {
        "invoice_code": "MTT-003",
        "buyer_name": "CÔNG TY ABC",
        "total_amount": "2,300,000 VND"
      }
    }
  ]
}
```

### 4️⃣ Chuẩn bị Context cho GPT

```python
rag_context = """THÔNG TIN TỪ HỆ THỐNG:

Tài liệu 1 (độ phù hợp: 0.95):
Invoice: MTT-001
Buyer: CÔNG TY ABC
Seller: CÔNG TY ĐIỆN LỰC
Amount: 1,500,000 VND
Type: Hóa đơn tiền điện
Mã hóa đơn: MTT-001
Khách hàng: CÔNG TY ABC
Tổng tiền: 1,500,000 VND

---

Tài liệu 2 (độ phù hợp: 0.88):
Invoice: MTT-003
Buyer: CÔNG TY ABC
Seller: CÔNG TY NƯỚC SẠCH
Amount: 2,300,000 VND
Type: Hóa đơn tiền nước
Mã hóa đơn: MTT-003
Khách hàng: CÔNG TY ABC
Tổng tiền: 2,300,000 VND

---
"""
```

### 5️⃣ Tạo Prompt cho Google AI

```python
prompt = f"""Bạn là trợ lý AI thông minh. Dựa trên thông tin dưới đây, hãy trả lời câu hỏi của người dùng một cách chính xác và chi tiết.

{rag_context}

CÂU HỎI: Có bao nhiêu hóa đơn của CÔNG TY ABC?

Hãy trả lời dựa trên dữ liệu thực tế ở trên. Nếu có nhiều hóa đơn, hãy liệt kê rõ ràng. Sử dụng emoji và format markdown để dễ đọc."""
```

### 6️⃣ Google AI phân tích & trả lời

**Google AI (Gemini-Pro) response:**

```markdown
📊 **Kết quả tìm kiếm cho CÔNG TY ABC:**

Hệ thống tìm thấy **2 hóa đơn** của CÔNG TY ABC:

**1. Hóa đơn tiền điện (MTT-001)**
• Nhà cung cấp: CÔNG TY ĐIỆN LỰC
• Số tiền: 1,500,000 VND
• Độ phù hợp: 95%

**2. Hóa đơn tiền nước (MTT-003)**
• Nhà cung cấp: CÔNG TY NƯỚC SẠCH
• Số tiền: 2,300,000 VND
• Độ phù hợp: 88%

💰 **Tổng chi phí:** 3,800,000 VND

📈 **Phân tích:**
CÔNG TY ABC có 2 loại chi phí dịch vụ công cộng:

- Tiền điện: 1.5 triệu (39%)
- Tiền nước: 2.3 triệu (61%)

💡 **Gợi ý:** Bạn có thể hỏi thêm về chi tiết từng hóa đơn hoặc upload thêm hóa đơn mới!
```

### 7️⃣ Chatbot trả về User

```json
{
  "message": "🤖 **Trả lời từ AI (dựa trên 2 tài liệu):**\n\n📊 Kết quả tìm kiếm...",
  "type": "ai_rag_response",
  "data": [...],
  "suggestions": [
    "Hỏi thêm",
    "Xem chi tiết",
    "Upload thêm",
    "Thống kê"
  ]
}
```

## 🔑 Key Components

### 1. RAG Service (`rag_service.py`)

```python
def search_similar_documents(query: str, top_k: int = 5):
    """
    Semantic search in vector database
    - Embed query với sentence-transformers
    - Search trong ChromaDB
    - Return top_k results với scores
    """
```

### 2. Google AI Service (`google_ai_service.py`)

```python
def generate_response(prompt: str) -> str:
    """
    Generate response từ Google AI
    - Input: Full prompt với RAG context
    - Model: gemini-pro
    - Output: Natural language response
    """
```

### 3. Chat Handler (`chat_handler.py`)

```python
def handle_data_query(message: str, context: Dict):
    """
    1. Call RAG search endpoint
    2. Get documents + metadata
    3. Build context từ RAG results
    4. Create prompt với context
    5. Call Google AI
    6. Return AI response
    """
```

## 💡 Ví dụ thực tế

### Example 1: Đếm số lượng

**User:** "Có bao nhiêu hóa đơn?"

**RAG Search:** Tìm tất cả documents
**Result:** 5 documents

**GPT Prompt:**

```
THÔNG TIN: 5 tài liệu (MTT-001, MTT-002, MTT-003, MTT-004, MTT-005)
CÂU HỎI: Có bao nhiêu hóa đơn?
```

**AI Response:**

```
📊 Hệ thống có **5 hóa đơn**:
1. MTT-001 - CÔNG TY ABC
2. MTT-002 - CÔNG TY XYZ
...
```

### Example 2: Tìm theo khách hàng

**User:** "Tìm hóa đơn của CÔNG TY ABC"

**RAG Search:** Semantic search "CÔNG TY ABC"
**Result:** 2 documents (score: 0.95, 0.88)

**GPT Prompt:**

```
THÔNG TIN:
- MTT-001: CÔNG TY ABC, 1.5M
- MTT-003: CÔNG TY ABC, 2.3M
CÂU HỎI: Tìm hóa đơn của CÔNG TY ABC
```

**AI Response:**

```
🔍 Tìm thấy 2 hóa đơn của CÔNG TY ABC:
1. MTT-001: Điện - 1.5M
2. MTT-003: Nước - 2.3M
Tổng: 3.8M
```

### Example 3: So sánh

**User:** "So sánh chi phí điện và nước"

**RAG Search:** Tìm documents liên quan "điện" và "nước"
**Result:** 4 documents

**GPT Prompt:**

```
THÔNG TIN:
- MTT-001: Điện, 1.5M
- MTT-002: Nước, 2.0M
- MTT-005: Điện, 1.8M
- MTT-007: Nước, 2.2M
CÂU HỎI: So sánh chi phí điện và nước
```

**AI Response:**

```
📊 So sánh chi phí:

💡 **Điện:**
- Số lượng: 2 hóa đơn
- Tổng: 3.3M
- Trung bình: 1.65M

💧 **Nước:**
- Số lượng: 2 hóa đơn
- Tổng: 4.2M
- Trung bình: 2.1M

📈 Chi phí nước cao hơn điện 27%
```

## 🎨 Response Format

### Success (có Google AI):

```json
{
  "message": "🤖 **Trả lời từ AI (dựa trên N tài liệu):**\n\n[AI response]",
  "type": "ai_rag_response",
  "data": [...],
  "suggestions": [...]
}
```

### Fallback (không có Google AI):

```json
{
  "message": "🔍 **Tìm thấy N kết quả:**\n\n[Raw data list]",
  "type": "rag_search_results",
  "data": [...],
  "suggestions": [...]
}
```

## ⚙️ Configuration

### Environment Variables

```env
# Google AI
GOOGLE_AI_API_KEY=AIzaSyAatyIQf08xSSuBzR9u_Eb9uwPUbq3D0OA

# RAG
CHROMA_PERSIST_DIRECTORY=./chroma_db
SENTENCE_TRANSFORMERS_MODEL=all-MiniLM-L6-v2
```

### Dependencies

```txt
# Google AI
google-generativeai>=0.3.0

# RAG
sentence-transformers>=2.2.0
chromadb>=0.4.0
```

## 🔍 Debugging

### Enable logging

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"RAG found {len(documents)} docs")
logger.info(f"Google AI response: {ai_response[:100]}...")
```

### Check RAG results

```python
print(f"RAG Results: {len(documents)}")
for doc in documents:
    print(f"- {doc['metadata']['invoice_code']}: {doc['score']:.2f}")
```

### Test Google AI

```python
if self.google_ai.is_available():
    test_prompt = "Hello, test response"
    response = self.google_ai.generate_response(test_prompt)
    print(f"Google AI working: {response}")
```

## 🚀 Performance

| Operation  | Time        | Notes               |
| ---------- | ----------- | ------------------- |
| RAG Search | ~0.2-0.5s   | Depends on DB size  |
| Google AI  | ~1-3s       | Network latency     |
| **Total**  | **~1.5-4s** | Acceptable for chat |

## 📈 Advantages

1. ✅ **Trả lời dựa trên data thực:** Không hallucinate
2. ✅ **Semantic search:** Hiểu ý nghĩa, không chỉ keyword
3. ✅ **Natural response:** GPT format đẹp, dễ đọc
4. ✅ **Context-aware:** GPT phân tích data thông minh
5. ✅ **Scalable:** Thêm documents → tự động search được

## ⚠️ Limitations

1. ⏱️ **Latency:** Tổng ~1.5-4s (RAG + GPT)
2. 💰 **Cost:** Google AI API có giới hạn free tier
3. 🔒 **Dependency:** Cần internet cho Google AI
4. 📦 **Model size:** sentence-transformers ~90MB

## 🎯 Best Practices

1. **Limit context:** Chỉ gửi top 5 documents cho GPT
2. **Cache results:** Cache RAG results nếu query giống nhau
3. **Fallback:** Có raw data display nếu GPT fail
4. **Error handling:** Graceful degradation nếu RAG/GPT down
5. **Prompt engineering:** Optimize prompt để GPT trả lời tốt hơn

---

**Version:** 3.0 (RAG + GPT Integration)
**Last Updated:** 2025-10-01
