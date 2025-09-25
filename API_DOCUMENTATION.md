# Backend API Documentation

## 🚀 Invoice Management System API

Base URL: `http://localhost:5000`

### 📊 Health Check

- `GET /api/health` - Check service health
- `GET /` - Root endpoint with API overview

---

## 🔐 Authentication APIs (`/api/auth`)

### Register User

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

### Login User

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}
```

### Refresh Token

```http
POST /api/auth/refresh
Authorization: Bearer {refresh_token}
```

### Get User Profile

```http
GET /api/auth/profile
Authorization: Bearer {access_token}
```

---

## 📄 Invoice APIs (`/api/invoices`)

### Get All Invoices

```http
GET /api/invoices?page=1&per_page=20&status=pending
Authorization: Bearer {access_token}
```

### Get Invoice by ID

```http
GET /api/invoices/{invoice_id}
Authorization: Bearer {access_token}
```

### Create New Invoice

```http
POST /api/invoices
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "invoice_number": "INV-2024-001",
  "company_name": "ABC Company",
  "company_address": "123 Business St",
  "customer_name": "XYZ Client",
  "total_amount": "1000.00",
  "currency": "VND",
  "invoice_date": "2024-01-01",
  "due_date": "2024-01-31",
  "items": [
    {
      "description": "Web Development",
      "quantity": "1",
      "unit_price": "1000.00",
      "total_price": "1000.00"
    }
  ]
}
```

### Update Invoice

```http
PUT /api/invoices/{invoice_id}
Authorization: Bearer {access_token}
Content-Type: application/json
```

### Delete Invoice

```http
DELETE /api/invoices/{invoice_id}
Authorization: Bearer {access_token}
```

---

## 📋 Template APIs (`/api/templates`)

### Get All Templates

```http
GET /api/templates
Authorization: Bearer {access_token}
```

### Get Template by ID

```http
GET /api/templates/{template_id}
Authorization: Bearer {access_token}
```

### Create New Template

```http
POST /api/templates
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Standard Invoice Template",
  "description": "Default invoice template",
  "field_mappings": {
    "invoice_number": "top-right",
    "company_name": "top-left"
  },
  "ocr_zones": {
    "header": {"x": 0, "y": 0, "width": 100, "height": 20}
  }
}
```

### Update Template

```http
PUT /api/templates/{template_id}
Authorization: Bearer {access_token}
```

### Delete Template

```http
DELETE /api/templates/{template_id}
Authorization: Bearer {access_token}
```

---

## 🔍 OCR APIs (`/api/ocr`)

### Process Invoice Image

```http
POST /api/ocr/process
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: {invoice_image.jpg}
template_id: {optional_template_id}
```

### Get OCR Results

```http
GET /api/ocr/results/{result_id}
Authorization: Bearer {access_token}
```

### Async OCR Processing (`/api/ocr-async`)

```http
POST /api/ocr-async/process
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: {invoice_image.jpg}
```

---

## 🤖 AI Training APIs (`/api/ai-training`)

### Get Training Data

```http
GET /api/ai-training/training-data
Authorization: Bearer {access_token}
```

### Add Training Data

```http
POST /api/ai-training/training-data
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "image_path": "/path/to/image.jpg",
  "extracted_data": {
    "invoice_number": "INV-001",
    "total": "1000.00"
  },
  "confidence_scores": {
    "invoice_number": 0.95,
    "total": 0.88
  }
}
```

### Train Model

```http
POST /api/ai-training/train
Authorization: Bearer {access_token}
```

---

## 💬 Hybrid Chat APIs (`/api/hybrid-chat`)

### Send Chat Message

```http
POST /api/hybrid-chat/message
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "message": "Help me create a new invoice",
  "context": "invoice_creation"
}
```

### Get Chat History

```http
GET /api/hybrid-chat/history?limit=50
Authorization: Bearer {access_token}
```

---

## 📊 Analytics APIs (`/api/analytics`)

### Get Dashboard Statistics

```http
GET /api/analytics/dashboard
Authorization: Bearer {access_token}
```

### Get Revenue Analytics

```http
GET /api/analytics/revenue?period=monthly&year=2024
Authorization: Bearer {access_token}
```

### Get Invoice Status Report

```http
GET /api/analytics/invoice-status
Authorization: Bearer {access_token}
```

---

## 🔧 Error Responses

### Standard Error Format

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "code": 400
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created successfully
- `400` - Bad request / Validation error
- `401` - Unauthorized / Invalid token
- `403` - Forbidden / Access denied
- `404` - Resource not found
- `500` - Internal server error

---

## 🛡️ Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer {your_jwt_token}
```

Get tokens from the `/api/auth/login` endpoint.

---

## 📝 Notes

- All dates should be in `YYYY-MM-DD` format
- Decimal values should be sent as strings (e.g., "1000.00")
- File uploads use `multipart/form-data`
- JSON requests should set `Content-Type: application/json`
- Pagination uses `page` and `per_page` query parameters
- All responses are in JSON format
