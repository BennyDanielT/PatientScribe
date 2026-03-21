# 🚀 GETTING STARTED - 5 MINUTE SETUP

## Step 1: Start Your App (30 seconds)

```bash
cd c:\Users\benny\OneDrive\Desktop\Projects\PatientScribe
python -m uvicorn app.main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Step 2: Test with curl (1 minute)

### Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{ "status": "healthy", "service": "PatientScribe API" }
```

### Process Report (with correlation ID)

```bash
curl -X POST http://localhost:8000/patients/process-report \
  -H "X-Correlation-ID: my-test-123" \
  -H "Content-Type: application/json"
```

Response includes:

```json
{
  "status": "success",
  "correlation_id": "my-test-123",
  ...
}
```

### Check Response Headers

```bash
curl -i http://localhost:8000/health
```

Look for:

```
X-Correlation-ID: <some-uuid>
```

## Step 3: View Logs (1 minute)

### Console Logs (Real-time, colorized)

```
Watch the terminal where you started the app
```

### JSON Logs (For aggregation)

```bash
# View in human-readable format
cat logs/app.json.log | python -m json.tool | head -50

# Tail in real-time
tail -f logs/app.json.log
```

Look for `"extra": {"correlation_id": "..."}` in JSON logs.

## Step 4: Understand the Flow (2 minutes)

When you make a request:

1. **Request arrives** with or without `X-Correlation-ID` header
2. **Middleware** generates correlation ID (or uses provided one)
3. **Logger** automatically includes it in all logs
4. **Services** access it without needing to pass it around
5. **Response** includes correlation ID in headers and body

All without any extra code! Magic ✨

## Step 5: Use in Your Code (1 minute)

### In a Route

```python
from app.config.logger import get_logger
from app.middleware.correlation_middleware import get_correlation_id

logger = get_logger()

@router.post("/my-endpoint")
async def my_endpoint(request: Request):
    logger.info("Processing request")  # ← CID auto-included

    # Get CID if needed
    cid = get_correlation_id()

    return {"status": "ok", "cid": cid}
```

### In a Service

```python
from app.config.logger import get_logger

logger = get_logger()

async def my_service():
    logger.info("Doing work")  # ← CID auto-included
    # ... rest of code
```

That's it! No configuration needed per route/service.

---

## 📖 What to Read Next

### Quick Learning Path (20 minutes)

1. **This file** (5 min) - You're doing it! ✅
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (5 min) - See patterns
3. [VISUAL_GUIDE.md](VISUAL_GUIDE.md) (5 min) - Understand architecture
4. Look at [app/api/routes/patient_routes.py](app/api/routes/patient_routes.py) (5 min) - Working example

### Deep Dive (45 minutes)

1. [CORRELATION_LOGGING.md](CORRELATION_LOGGING.md) - Complete guide
2. Browse `app/services/` - See examples
3. Check `app/config/logger.py` - Understand configuration

### For Specific Tasks

**Want to add a new route?**
→ Copy pattern from `app/api/routes/patient_routes.py`

**Want to add a new service?**
→ Copy pattern from `app/services/parser.py`

**Want to customize logging?**
→ Edit `app/config/logger.py`

**Want to integrate with ELK/Datadog?**
→ See [CORRELATION_LOGGING.md](CORRELATION_LOGGING.md) Integration section

---

## 🎯 Common Tasks

### Add a New Route

```python
# In app/api/routes/patient_routes.py (or new file)

@router.get("/my-endpoint")
async def my_endpoint(request: Request):
    logger.info("Endpoint called")  # CID auto-included

    try:
        result = await some_operation()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)  # CID included
        return {"status": "error"}
```

### Add a New Service

```python
# In app/services/my_service.py

from app.config.logger import get_logger
from app.middleware.correlation_middleware import get_correlation_id

logger = get_logger()

async def my_function(data: str):
    logger.info(f"Processing {data}")  # CID auto-included

    cid = get_correlation_id()  # Get when needed

    # Do work...

    return result
```

### Add Logging to Existing Code

Simply import and use:

```python
from app.config.logger import get_logger

logger = get_logger()
logger.info("Your message")  # CID automatically included
```

---

## 🔍 Debugging Tips

### Find Logs for a Specific Request

```bash
# If you know the correlation ID (e.g., from response)
grep "my-test-123" logs/app.json.log

# If you need to find it
tail -f logs/app.json.log
# Make a request, look for the CID in the logs
```

### View a Specific Service's Logs

```bash
grep '"name": "parser"' logs/app.json.log | python -m json.tool
```

### Check Log Format

```bash
# First JSON log entry
head -1 logs/app.json.log | python -m json.tool
```

---

## 🎓 Key Concepts (Quick Explanation)

### Correlation ID

A unique identifier that travels with your request.

- **Generated** by middleware
- **Stored** in contextvars (special Python storage for async)
- **Accessed** by all services automatically
- **Logged** in every log message

### Contextvars

Special Python storage that works with async code.
Think of it as: "Request-local storage that survives across async calls"

### Patcher

A function that injects correlation ID into every log message.
You don't need to do anything - it happens automatically!

### RichHandler

Beautiful, colorized console output for logs.
Makes logs easy to read during development.

---

## 🆘 Troubleshooting

### Logs Not Showing in Console?

- [x] Make sure app is running
- [x] Check log level (set to DEBUG in logger.py)
- [x] Restart app after changes

### Can't Find logs/app.json.log?

- [x] Create `logs/` directory manually
- [x] Ensure write permissions
- [x] Restart app

### Correlation ID Not in Logs?

- [x] Ensure CorrelationIDMiddleware is registered (it is)
- [x] Use `from app.config.logger import get_logger`
- [x] Don't import logger directly from loguru

### JSON Logs Hard to Read?

```bash
tail -f logs/app.json.log | python -m json.tool
```

---

## 📊 What's Running

### Main App

- **File**: `app/main.py`
- **Port**: 8000
- **Middleware**: CorrelationIDMiddleware (handles all requests)
- **Logger**: Configured with Loguru and RichHandler

### Routes

- **Health Check**: `GET /health`
- **Process Report**: `POST /patients/process-report`
- **Record Retrieval**: `GET /patients/reports/{report_id}`

### Services

- **Parser** - Document parsing with logging
- **Embeddings** - Vector embedding generation with logging
- **LLM** - Report simplification with logging

All log their operations with automatic correlation ID!

---

## 📝 Example Request Flow

```
1. curl -X POST http://localhost:8000/patients/process-report \
        -H "X-Correlation-ID: request-001"

2. Middleware intercepts, stores: correlation_id = "request-001"

3. Route handler logs: logger.info("Processing...")
   → Creates log with CID=request-001

4. Route calls parser service

5. Parser logs: logger.info("Starting parse...")
   → Creates log with CID=request-001 (same!)

6. Parser calls other services

7. All logs have CID=request-001

8. Response sent back with X-Correlation-ID header

9. You can search logs by: grep "request-001" logs/app.json.log
   → Get ALL logs for that request!
```

---

## ✨ That's It!

You now have a production-grade correlation ID logging system working!

### Next Steps

1. [x] Start the app
2. [x] Test with curl
3. [x] View logs
4. [ ] Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
5. [ ] Add your own routes/services
6. [ ] Integrate with log aggregation (optional)

---

## 🎉 You're Ready!

Your PatientScribe backend now has:

- ✅ Automatic request tracing
- ✅ Beautiful structured logs
- ✅ Zero-configuration logging per route
- ✅ Production-ready setup

**Questions?**
→ Check [CORRELATION_LOGGING.md](CORRELATION_LOGGING.md) (Comprehensive guide)
→ See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (Patterns)
→ Review [VISUAL_GUIDE.md](VISUAL_GUIDE.md) (Diagrams)

Happy coding! 🚀
