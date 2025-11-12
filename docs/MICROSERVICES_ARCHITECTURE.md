# Microservices Architecture Design

## Current Monolithic Structure

```
┌─────────────────┐
│   FastAPI App   │
│                 │
│ - Auth Routes   │
│ - Chat Routes   │
│ - OCR Routes    │
│ - DB Models     │
│ - Business Logic│
└─────────────────┘
```

## Proposed Microservices Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │────│   Auth Service  │    │  Chat Service   │
│                 │    │                 │    │                 │
│ - Request       │    │ - JWT Auth      │    │ - AI Chat       │
│   Routing       │    │ - User Mgmt     │    │ - Conversation  │
│ - Auth          │    │ - Sessions      │    │   Memory        │
│   Middleware    │    └─────────────────┘    └─────────────────┘
└─────────────────┘                                 │
          │                                        │
          │                            ┌─────────────────┐
          │                            │   OCR Service   │
          └────────────────────────────│                 │
                                       │ - Image Proc    │
                                       │ - Async Jobs    │
                                       │ - OCR Engine    │
                                       └─────────────────┘
```

## Service Boundaries

### 1. API Gateway Service

- **Port**: 8000
- **Responsibilities**:
  - Request routing to appropriate services
  - Authentication middleware
  - Rate limiting
  - Request/response transformation
  - CORS handling

### 2. Auth Service

- **Port**: 8001
- **Responsibilities**:
  - User registration/login
  - JWT token generation/validation
  - User profile management
  - Session management
- **Database**: users, user_sessions tables

### 3. Chat Service

- **Port**: 8002
- **Responsibilities**:
  - AI chat processing (Groq integration)
  - Conversation memory management
  - Sentiment analysis
  - Chat history storage
- **Database**: chat_history, sentiment_analysis tables

### 4. OCR Service

- **Port**: 8003
- **Responsibilities**:
  - Image upload and processing
  - OCR text extraction
  - Async job management
  - File storage handling
- **Database**: ocr_jobs, invoices tables

## Communication Patterns

### Synchronous Communication

- REST APIs between services
- API Gateway → Auth Service (token validation)
- API Gateway → Chat/OCR Services (business logic)

### Asynchronous Communication

- WebSocket for real-time chat
- Message queues for OCR job processing

## Database Strategy

### Option 1: Database per Service

```
Auth Service → auth_db (users, sessions)
Chat Service → chat_db (chat_history, sentiment)
OCR Service → ocr_db (ocr_jobs, invoices)
```

### Option 2: Shared Database with Schema Separation

```
Shared PostgreSQL Database
├── auth_schema (users, sessions)
├── chat_schema (chat_history, sentiment)
└── ocr_schema (ocr_jobs, invoices)
```

## Technology Stack

- **Framework**: FastAPI for all services
- **Database**: PostgreSQL with async SQLAlchemy
- **Message Queue**: Redis (optional for async processing)
- **Container**: Docker + Docker Compose
- **API Documentation**: OpenAPI/Swagger
- **Monitoring**: Basic logging + health checks

## Implementation Plan

1. **Phase 1**: Extract Auth Service
2. **Phase 2**: Extract Chat Service
3. **Phase 3**: Extract OCR Service
4. **Phase 4**: Create API Gateway
5. **Phase 5**: Docker orchestration
6. **Phase 6**: Testing & integration
