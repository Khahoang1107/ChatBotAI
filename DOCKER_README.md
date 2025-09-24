# Docker Setup cho Invoice Management System

Hệ thống quản lý hóa đơn với AI chatbot được container hóa hoàn toàn sử dụng Docker.

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Chatbot       │
│   (React)       │◄──►│   (Flask)       │◄──►│   (Flask)       │
│   Port: 5174    │    │   Port: 5000    │    │   Port: 5001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐    ┌─────────────────┐
                    │   PostgreSQL    │    │    MongoDB      │
                    │   Port: 5432    │    │   Port: 27017   │
                    └─────────────────┘    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │   Port: 6379    │
                    └─────────────────┘
```

## 🚀 Khởi động nhanh

### 1. Clone repository và vào thư mục

```bash
git clone <repository-url>
cd DoAnCN
```

### 2. Tạo file environment (tùy chọn)

```bash
cp .env.docker .env
# Chỉnh sửa OPENAI_API_KEY trong .env nếu có
```

### 3. Khởi động tất cả services

```bash
docker-compose up -d
```

### 4. Kiểm tra trạng thái

```bash
docker-compose ps
```

### 5. Xem logs

```bash
docker-compose logs -f
```

## 🌐 Truy cập ứng dụng

- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:5000
- **Chatbot API**: http://localhost:5001
- **PgAdmin** (DB management): http://localhost:5050
- **Mongo Express** (MongoDB management): http://localhost:8081

## 📋 Chi tiết Services

### Core Services (luôn chạy)

- **mongodb**: Database cho AI training data
- **postgres**: Database chính của ứng dụng
- **redis**: Cache và session storage
- **backend**: API chính (Flask)
- **chatbot**: AI chatbot service (Flask)
- **frontend**: Giao diện người dùng (React)

### Optional Services

- **rasa**: Advanced NLP processing (`--profile rasa`)
- **pgadmin**: PostgreSQL management (`--profile dev-tools`)
- **mongo-express**: MongoDB management (`--profile dev-tools`)

## 🛠️ Lệnh Docker hữu ích

### Khởi động với dev tools

```bash
docker-compose --profile dev-tools up -d
```

### Khởi động với Rasa

```bash
docker-compose --profile rasa up -d
```

### Dừng tất cả services

```bash
docker-compose down
```

### Xây dựng lại images

```bash
docker-compose build --no-cache
```

### Xem logs của service cụ thể

```bash
docker-compose logs backend
docker-compose logs chatbot
docker-compose logs frontend
```

### Vào container để debug

```bash
docker-compose exec backend bash
docker-compose exec chatbot bash
docker-compose exec mongodb mongo
```

## 🔧 Cấu hình Database

### PostgreSQL

- **Host**: postgres
- **Port**: 5432
- **Database**: invoice_app
- **Username**: invoice_user
- **Password**: invoice_pass123

### MongoDB

- **Host**: mongodb
- **Port**: 27017
- **Database**: invoice_ai_training
- **Username**: admin
- **Password**: password123

### Redis

- **Host**: redis
- **Port**: 6379

## 📊 Health Checks

Tất cả services đều có health checks tự động. Kiểm tra trạng thái:

```bash
# Kiểm tra tất cả services
docker-compose ps

# Kiểm tra health của backend
curl http://localhost:5000/api/health

# Kiểm tra health của chatbot
curl http://localhost:5001/health

# Kiểm tra MongoDB
docker-compose exec mongodb mongo --eval "db.stats()"

# Kiểm tra PostgreSQL
docker-compose exec postgres psql -U invoice_user -d invoice_app -c "SELECT version();"
```

## 🔄 Development Workflow

### 1. Thay đổi code backend

```bash
# Code sẽ tự động reload nhờ volume mounting
docker-compose logs -f backend
```

### 2. Thay đổi code frontend

```bash
# Hot reload enabled
docker-compose logs -f frontend
```

### 3. Database migrations

```bash
# Vào container backend
docker-compose exec backend bash

# Chạy migrations
python -m flask db init
python -m flask db migrate -m "Your message"
python -m flask db upgrade
```

## 🐛 Troubleshooting

### Services không khởi động được

```bash
# Kiểm tra logs
docker-compose logs

# Restart service cụ thể
docker-compose restart backend

# Xây dựng lại
docker-compose build --no-cache backend
```

### Database connection errors

```bash
# Kiểm tra database services
docker-compose ps postgres mongodb redis

# Restart databases
docker-compose restart postgres mongodb redis
```

### Port conflicts

```bash
# Thay đổi port trong docker-compose.yml
ports:
  - "5175:5174"  # Frontend trên port 5175
  - "5002:5000"  # Backend trên port 5002
```

### Memory issues

```bash
# Thêm memory limits
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

## 📁 Cấu trúc thư mục

```
DoAnCN/
├── docker-compose.yml          # Main compose file
├── docker-compose.override.yml # Development overrides
├── .env.docker                 # Environment variables
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── Dockerfile
│   └── ...
├── chatbot/
│   ├── Dockerfile
│   └── ...
├── rasa/
│   ├── Dockerfile
│   └── ...
└── README.md
```

## 🔒 Security Notes

- **Không sử dụng passwords mặc định trong production!**
- **Thay đổi SECRET_KEY và JWT_SECRET_KEY**
- **Cấu hình firewall cho các ports cần thiết**
- **Sử dụng HTTPS trong production**
- **Regular backup databases**

## 📈 Monitoring

### Logs

```bash
# Tất cả logs
docker-compose logs -f

# Logs theo thời gian
docker-compose logs --since 1h backend
```

### Resource usage

```bash
# Kiểm tra resource usage
docker stats

# Chi tiết container
docker inspect invoice_backend
```

## 🚀 Production Deployment

### 1. Tạo production compose file

```bash
cp docker-compose.yml docker-compose.prod.yml
# Chỉnh sửa cho production environment
```

### 2. Sử dụng external databases

```yaml
services:
  backend:
    environment:
      DATABASE_URL: postgresql://user:pass@external-db:5432/prod_db
      MONGODB_URL: mongodb://user:pass@external-mongo:27017/prod_ai
```

### 3. Enable SSL/TLS

```yaml
services:
  frontend:
    environment:
      HTTPS: true
    ports:
      - "443:443"
```

## 📞 Support

Nếu gặp vấn đề:

1. Kiểm tra logs: `docker-compose logs`
2. Verify Docker và Docker Compose versions
3. Kiểm tra ports có bị conflict không
4. Restart Docker daemon nếu cần

---

**Happy Dockerizing! 🐳**
