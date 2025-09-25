# 🚀 Local Development Guide

Run the application locally without Docker for faster development and testing.

## Quick Start

```powershell
# First time setup
.\main.ps1 setup

# Start all services
.\main.ps1 start

# Test services
.\main.ps1 test

# Stop services when done
.\main.ps1 stop
```

## 🛠️ Manual Setup

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 20+** with npm
- **Git** (for version control)

### Install Dependencies

```powershell
# Backend
cd backend
pip install -r requirements.txt

# Chatbot
cd chatbot
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## 🚀 Running Services

### Option 1: All at once (Recommended)

```powershell
.\start_local_services.ps1
```

### Option 2: Individual services

**Backend (Port 5000):**

```powershell
cd backend
python -m flask run --host=0.0.0.0 --port=5000
```

**Chatbot (Port 5001):**

```powershell
cd chatbot
python -m flask run --host=0.0.0.0 --port=5001
```

**Frontend (Port 5174):**

```powershell
cd frontend
npm run dev
```

## 🌐 Access URLs

| Service  | URL                   | Description     |
| -------- | --------------------- | --------------- |
| Frontend | http://localhost:5174 | React UI        |
| Backend  | http://localhost:5000 | API & Templates |
| Chatbot  | http://localhost:5001 | AI Chat Service |

## 🔧 Configuration

### Environment Variables

The setup script automatically creates `.env` files:

**backend/.env:**

```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///invoice.db
OPENAI_API_KEY=your-openai-api-key-here
```

**chatbot/.env:**

```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=sqlite:///chatbot.db
BACKEND_URL=http://localhost:5000
```

### Important: Set Your API Keys

1. Get OpenAI API key from https://platform.openai.com/
2. Update `OPENAI_API_KEY` in both `.env` files

## 🧪 Testing

### Health Check

```powershell
.\test_local_services.ps1
```

### Individual Service Tests

```powershell
# Test specific service
.\test_local_services.ps1 -Service backend
.\test_local_services.ps1 -Service chatbot
.\test_local_services.ps1 -Service frontend
```

### Manual Testing

```powershell
# Backend API
curl http://localhost:5000/api/templates

# Chatbot API
curl http://localhost:5001/chat -X POST -H "Content-Type: application/json" -d '{"message": "hello"}'

# Frontend
# Open http://localhost:5174 in browser
```

## 🛑 Stopping Services

```powershell
# Stop all services
.\stop_local_services.ps1

# Or use main script
.\main.ps1 stop
```

## 🐛 Troubleshooting

### Port Conflicts

```powershell
# Check what's using the ports
netstat -ano | findstr ":5000 :5001 :5174"

# Kill specific processes
taskkill /PID <PID_NUMBER> /F
```

### Service Not Starting

1. Check console output for errors
2. Verify dependencies installed: `pip list` or `npm list`
3. Check `.env` files exist and have correct values
4. Ensure ports are not in use

### Common Issues

**Python Module Not Found:**

```powershell
pip install -r requirements.txt
```

**Node Module Not Found:**

```powershell
npm install
```

**CORS Errors:**

- Make sure backend is running on port 5000
- Check frontend is configured to use correct backend URL

**OpenAI API Errors:**

- Verify `OPENAI_API_KEY` is set in `.env` files
- Check API key has credits available

## 📝 Development Tips

### Hot Reloading

- **Backend**: Flask auto-reloads on file changes (debug mode)
- **Chatbot**: Flask auto-reloads on file changes (debug mode)
- **Frontend**: Vite auto-reloads on file changes

### Logs

- Backend: Check console output or enable logging
- Chatbot: Check console output or `logs/chatbot.log`
- Frontend: Check browser developer console

### Database

- SQLite databases are created automatically
- Located in service directories: `backend/invoice.db`, `chatbot/chatbot.db`

## 🔄 Development Workflow

```powershell
# 1. First time setup
.\main.ps1 setup

# 2. Start development
.\main.ps1 start

# 3. Develop... (services auto-reload on changes)

# 4. Test your changes
.\main.ps1 test

# 5. When done
.\main.ps1 stop
```

## 📦 vs Docker

| Aspect           | Local                  | Docker              |
| ---------------- | ---------------------- | ------------------- |
| **Speed**        | ⚡ Fast startup        | 🐌 Slower startup   |
| **Dependencies** | Manual install         | Auto included       |
| **Hot Reload**   | ✅ Native              | ❌ Complex setup    |
| **Debugging**    | ✅ Easy                | 🔍 More complex     |
| **Production**   | ❌ Not recommended     | ✅ Production ready |
| **Isolation**    | ❌ System dependencies | ✅ Isolated         |

**Use Local for:** Development, testing, debugging
**Use Docker for:** Production, deployment, team consistency
