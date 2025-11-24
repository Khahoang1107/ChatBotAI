# Quick Start Guide - Enterprise ChatBotAI v2.0

## Prerequisites
- Python 3.10+
- Node.js 18.15+
- PostgreSQL 12+ (optional, for development can use SQLite)
- Git

---

## Backend Setup

### 1. Navigate to backend
```bash
cd backend
```

### 2. Create virtual environment (if not exists)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install alembic
```

### 4. Configure environment variables
Create `.env` file in backend directory:
```env
# Database
DATABASE_URL=sqlite:///./chatbot.db
# Or PostgreSQL: postgresql://user:password@localhost/chatbot

# Security
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# APIs
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_AI_API_KEY=your_google_ai_key_here

# Application
DEBUG=True
ENVIRONMENT=development
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080

# File Upload
MAX_UPLOAD_SIZE=10
ALLOWED_FILE_TYPES=jpg,jpeg,png,pdf

# Logging
LOG_LEVEL=INFO
```

### 5. Run database migrations (if using PostgreSQL)
```bash
cd backend
alembic upgrade head
```

### 6. Start backend server
```bash
# Using new refactored version
python main_refactored.py

# Or with uvicorn directly
uvicorn main_refactored:app --reload --port 8000
```

Server will run at: **http://localhost:8000**

Check health: http://localhost:8000/health
API docs: http://localhost:8000/docs

---

## Frontend Setup

### 1. Navigate to frontend
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure environment variables
Create `.env` file in frontend directory:
```env
VITE_API_URL=http://localhost:8000
```

### 4. Start development server
```bash
npm run dev
```

Frontend will run at: **http://localhost:5173**

---

## Testing the Application

### 1. Register User
Open http://localhost:5173 and fill the registration form:
- Email: `test@example.com`
- Password: `Test123!` (must have uppercase, number)
- Name: `Test User`

Click "Register"

### 2. Login
After registration, use same credentials to login

### 3. Chat with AI
- Type a message in the chat interface
- Press Send
- AI will respond with Groq integration

### 4. Upload Files
- Go to "Upload" tab
- Drag and drop or select a JPG/PNG/PDF file
- Wait for upload completion
- Click "Process OCR" to extract text

### 5. View API Documentation
Visit http://localhost:8000/docs for interactive Swagger UI

---

## API Endpoints

### Authentication
```
POST   /api/v1/auth/register          Register new user
POST   /api/v1/auth/login             Login and get JWT token
POST   /api/v1/auth/refresh           Refresh JWT token
GET    /api/v1/auth/me                Get current user info
```

### Chat
```
POST   /api/v1/chat/send              Send message to AI
GET    /api/v1/chat/history/{id}      Get conversation history
DELETE /api/v1/chat/conversation/{id} Delete conversation
```

### Files & OCR
```
POST   /api/v1/upload/file            Upload file
POST   /api/v1/upload/ocr/{id}        Process file with OCR
GET    /api/v1/upload/ocr/{id}        Get OCR results
DELETE /api/v1/upload/file/{id}       Delete file
```

### System
```
GET    /                               API information
GET    /health                         Health check
```

---

## Project Structure

```
ChatBotAI/
├── backend/                  # FastAPI application
│   ├── config/              # Settings and configuration
│   ├── core/                # Core infrastructure (DI, logging, exceptions)
│   ├── models/              # SQLAlchemy ORM models
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic services
│   ├── schemas/             # Pydantic validation models
│   ├── middleware/          # Request/response middleware
│   ├── alembic/             # Database migrations
│   ├── main_refactored.py   # NEW: Refactored FastAPI app
│   ├── main.py              # Legacy app (still available)
│   └── requirements.txt     # Python dependencies
│
└── frontend/                # React + Vite application
    ├── src/
    │   ├── api/            # API client
    │   ├── stores/         # Zustand state stores
    │   ├── components/     # React components
    │   ├── App.jsx         # Main app component
    │   └── index.css       # Global styles
    ├── package.json        # Node dependencies
    └── .env                # Environment variables
```

---

## Key Features

### Backend v2.0
✅ Service-oriented architecture
✅ Dependency injection container
✅ Structured exception handling
✅ JSON structured logging
✅ Type hints throughout
✅ Pydantic validation
✅ SQLAlchemy ORM
✅ Alembic migrations
✅ JWT authentication
✅ Token refresh mechanism
✅ Health check endpoint
✅ CORS configured
✅ Request tracing

### Frontend v2.0
✅ Zustand state management
✅ Auth store (login, register, persist)
✅ Chat store (messages, history, cache)
✅ Upload store (files, OCR results, progress)
✅ Axios API client with interceptors
✅ Token refresh on 401
✅ Automatic logout on auth failure
✅ Optimistic UI updates
✅ Error handling and display
✅ Conversation caching
✅ File upload progress
✅ Drag-drop interface
✅ Responsive design (Tailwind CSS)

---

## Troubleshooting

### Backend won't start
1. Check Python version: `python --version` (need 3.10+)
2. Check dependencies: `pip list | grep fastapi`
3. Check .env file exists and has DATABASE_URL
4. Check port 8000 is not in use: `netstat -ano | findstr :8000`

### Database connection error
1. If using PostgreSQL, ensure it's running
2. Check DATABASE_URL in .env is correct
3. Try SQLite for development: `sqlite:///./chatbot.db`
4. Run migrations: `alembic upgrade head`

### Frontend won't start
1. Check Node version: `node --version` (need 18.15+)
2. Clear cache: `rm -rf node_modules && npm install`
3. Check .env has VITE_API_URL
4. Check port 5173 is not in use

### API connection error (frontend → backend)
1. Backend must be running on http://localhost:8000
2. Check CORS origins in backend .env include frontend URL
3. Check browser console for specific error message
4. Try `curl http://localhost:8000/health` from terminal

### Can't login
1. Make sure you registered first
2. Password must have uppercase letter and number
3. Email must be unique
4. Check backend logs for detailed error message

---

## Development Commands

### Backend
```bash
cd backend

# Run application
python main_refactored.py

# Run with auto-reload
uvicorn main_refactored:app --reload

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Run tests (when implemented)
pytest tests/ -v
```

### Frontend
```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview build
npm run preview

# Run tests (when implemented)
npm run test
```

---

## Database

### Using SQLite (Development)
```env
DATABASE_URL=sqlite:///./chatbot.db
```
No setup needed, file created automatically.

### Using PostgreSQL (Production)
```bash
# Create database
createdb chatbot

# Update .env
DATABASE_URL=postgresql://user:password@localhost/chatbot

# Run migrations
alembic upgrade head
```

---

## Next Steps

1. **Run complete setup** (follow Quick Start above)
2. **Test all features** (register → login → chat → upload)
3. **Review code** (check out the refactored architecture)
4. **Add tests** (pytest for backend, vitest for frontend)
5. **Setup Docker** (for containerization)
6. **Configure CI/CD** (GitHub Actions)
7. **Deploy** (to staging, then production)

---

## Support & Documentation

- API Docs: http://localhost:8000/docs (Swagger UI)
- Project Upgrade: See `UPGRADE_COMPLETE.md`
- Architecture: See `docs/ARCHITECTURE_DIAGRAM.md`
- Issues: Check GitHub issues or project documentation

---

**Happy coding! 🚀**

*ChatBotAI v2.0 - Enterprise Ready*
