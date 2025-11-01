# Quick Setup Guide - Phase 7 & 8

## 🚀 Phase 7: WebRTC Signaling

### 1. Configure TURN Server

**Add to `.env`:**
```env
# Generate secret: openssl rand -hex 32
TURN_SECRET=your-secret-here
TURN_HOST=localhost
TURN_PORT=3478
TURN_PORT_TLS=5349
TURN_TTL=86400

STUN_SERVERS=stun:stun.l.google.com:19302,stun:stun1.l.google.com:19302
```

### 2. Install Coturn (Optional)

**Using Docker:**
```bash
docker run -d --name coturn \
  -p 3478:3478/tcp -p 3478:3478/udp \
  -p 5349:5349/tcp -p 5349:5349/udp \
  -p 49152-65535:49152-65535/udp \
  -e TURN_SECRET=your-secret-here \
  coturn/coturn:latest
```

**Or Docker Compose:** (already in your docker-compose.yml)
```bash
docker-compose up coturn
```

### 3. Test WebRTC Endpoints

```bash
# Test TURN credentials
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/webrtc/turn-credentials

# Test ICE servers
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/webrtc/ice-servers
```

---

## 🔒 Phase 8: Final Polish

### 1. Enable Encryption

**Generate encryption key:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Add to `.env`:**
```env
ENCRYPTION_KEY=your-generated-key-here
```

### 2. Configure Data Retention

**Add to `.env`:**
```env
# Keep messages for 1 year
DATA_RETENTION_DAYS=365

# Check daily
DATA_RETENTION_CHECK_HOURS=24
```

### 3. Optional: Enable Health Checks

**Add to `.env`:**
```env
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL_MINUTES=30
```

### 4. Optional: Enable File Cleanup

**Add to `.env`:**
```env
FILE_CLEANUP_ENABLED=true
FILE_CLEANUP_INTERVAL_HOURS=168
```

### 5. Optional: Configure Licensing

**Add to `.env`:**
```env
# Leave empty for open-source mode
# Or generate: python -m app.core.security generate_license
LICENSE_KEY=
```

### 6. Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### 7. Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific tests
pytest tests/api/test_auth.py -v
```

---

## 🎯 Verification Checklist

### Phase 7 - WebRTC
- [ ] TURN server configured and running
- [ ] `/api/webrtc/turn-credentials` returns credentials
- [ ] `/api/webrtc/ice-servers` returns ICE configuration
- [ ] WebSocket accepts `webrtc_offer`, `webrtc_answer`, `webrtc_ice_candidate`

### Phase 8 - Final Polish
- [ ] Encryption key generated and configured
- [ ] Background tasks start on server launch
- [ ] Data retention logs appear in console
- [ ] Tests run successfully
- [ ] License validation works (if enabled)

---

## 📊 Complete Environment Variables

```env
# ============================================================================
# Database
# ============================================================================
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# ============================================================================
# Security
# ============================================================================
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================================================
# WebRTC / TURN
# ============================================================================
TURN_SECRET=your-turn-secret
TURN_HOST=localhost
TURN_PORT=3478
TURN_PORT_TLS=5349
TURN_TTL=86400
STUN_SERVERS=stun:stun.l.google.com:19302,stun:stun1.l.google.com:19302

# ============================================================================
# Encryption
# ============================================================================
ENCRYPTION_KEY=your-fernet-key

# ============================================================================
# Data Retention
# ============================================================================
DATA_RETENTION_DAYS=365
DATA_RETENTION_CHECK_HOURS=24

# ============================================================================
# Optional Features
# ============================================================================
FILE_CLEANUP_ENABLED=false
FILE_CLEANUP_INTERVAL_HOURS=168
HEALTH_CHECK_ENABLED=false
HEALTH_CHECK_INTERVAL_MINUTES=30
LICENSE_KEY=

# ============================================================================
# AI Services (from Phase 6)
# ============================================================================
OLLAMA_HOST=http://localhost:11434
CHROMADB_HOST=http://localhost:8000
EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200

# ============================================================================
# Redis
# ============================================================================
REDIS_URL=redis://localhost:6379

# ============================================================================
# File Storage
# ============================================================================
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# ============================================================================
# CORS
# ============================================================================
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🚀 Start All Services

```bash
# 1. Start PostgreSQL
docker-compose up -d db

# 2. Start Redis
docker-compose up -d redis

# 3. Start Ollama (Phase 6)
docker-compose up -d ollama

# 4. Start ChromaDB (Phase 6)
docker-compose up -d chromadb

# 5. Start Coturn (Phase 7)
docker-compose up -d coturn

# 6. Start Backend
cd backend
uvicorn main:app --reload --port 8000

# 7. Start Frontend
cd ../frontend
npm run dev
```

---

## 📝 Testing Quick Start

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run health tests
pytest tests/api/test_health.py -v

# Run auth tests
pytest tests/api/test_auth.py -v

# All tests with coverage
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html
# Open: htmlcov/index.html
```

---

## 🎉 Success Indicators

**Server Startup Logs:**
```
🚀 Application startup
✅ Database tables created
✅ Upload directories created
🔄 Starting background tasks...
  ✓ Data retention task started
  ✓ File cleanup task started
  ✓ Health check task started
✅ All background tasks started
INFO:     Application startup complete.
```

**Test Output:**
```
tests/api/test_health.py::test_health_check PASSED
tests/api/test_health.py::test_root_endpoint PASSED
tests/api/test_auth.py::test_register_user PASSED
tests/api/test_auth.py::test_login_success PASSED

=========== 4 passed in 2.34s ===========
```

**API Endpoints Available:**
- http://localhost:8000/docs - API Documentation
- http://localhost:8000/admin - Admin Panel
- http://localhost:8000/health - Health Check
- http://localhost:8000/api/webrtc/turn-credentials - TURN Credentials
- http://localhost:8000/api/webrtc/ice-servers - ICE Configuration

---

## 🐛 Common Issues

**"ENCRYPTION_KEY not set" warning:**
```bash
# Generate and add to .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**"TURN server not configured":**
```bash
# Add TURN_SECRET to .env
echo "TURN_SECRET=$(openssl rand -hex 32)" >> .env
```

**Background tasks not starting:**
```bash
# Check for import errors
python -c "from app.core.tasks import run_periodic_data_retention"
```

**Tests failing:**
```bash
# Ensure test database isolated
pip install aiosqlite
pytest --verbose
```

---

## 📚 Documentation

- **PHASE7_8_COMPLETE.md** - Full documentation with examples
- **API_REFERENCE.md** - All API endpoints
- **SETUP_PHASE5_6.md** - AI services setup
- **README.md** - Project overview
- **docker-compose.yml** - Service orchestration

---

## 🎯 Next Steps

1. Configure production secrets (JWT, encryption keys)
2. Set up HTTPS/TLS for production
3. Configure Coturn with real domain and certificates
4. Implement remaining tests (groups, channels, AI)
5. Set up CI/CD pipeline
6. Configure monitoring and logging
7. Perform load testing

**Your backend is now complete with all 8 phases! 🎊**
