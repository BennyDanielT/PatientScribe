# Visual Guide: Correlation ID Request Flow

## Request Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT REQUEST                               │
│  GET /patients/process-report                                       │
│  X-Correlation-ID: 3f91d2e3-1234-5678-abcd (optional)              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              CORRELATION ID MIDDLEWARE                              │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ 1. Check request headers for X-Correlation-ID               │ │
│  │    ├─ Found? ✓ Use it                                        │ │
│  │    └─ Not found? Generate new UUID                           │ │
│  │                                                              │ │
│  │ 2. Store in contextvars (async-safe)                        │ │
│  │    correlation_id_var.set("3f91d2e3-...")                   │ │
│  │                                                              │ │
│  │ 3. Call next middleware/route                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ROUTE HANDLER                                  │
│  @router.post("/process-report")                                    │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ logger.info("Processing medical report")                     │ │
│  │ ↓ Logs with CID=3f91d2e3 automatically                        │ │
│  │                                                              │ │
│  │ 1. Parse document ─┐                                         │ │
│  │ 2. Validate       │                                          │ │
│  │ 3. Generate embeddings                                       │ │
│  │ 4. Simplify with LLM                                         │ │
│  │ 5. Extract key points                                        │ │
│  └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                    ┌────────┴────────┬─────────┬─────────┐
                    ▼                ▼         ▼         ▼
        ┌──────────────────┐  ┌────────────┐ ┌────────────────┐
        │  Parser Service  │  │ Embeddings │ │  LLM Service   │
        ├──────────────────┤  │  Service   │ └────────────────┘
        │ logger.info(...) │  ├────────────┤
        │ CID auto-inc!    │  │log.inf(...) │ logger.info(...)
        │                  │  │CID auto-inc │ CID auto-inc!
        └──────────────────┘  └────────────┘
                    │                │         │
                    └────────────────┴─────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LOGGER (Loguru)                                  │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ Logs with correlation ID injected by patcher                │ │
│  │                                                              │ │
│  │ INFO     | parser     | CID=3f91d2e3 | Starting parse...   │ │
│  │ DEBUG    | parser     | CID=3f91d2e3 | Reading file...     │ │
│  │ INFO     | parser     | CID=3f91d2e3 | Parse complete      │ │
│  │ INFO     | embeddings | CID=3f91d2e3 | Generating embed... │ │
│  │ INFO     | llm        | CID=3f91d2e3 | Simplifying...      │ │
│  │                                                              │ │
│  │ Outputs to:                                                 │ │
│  │ ├─ Console (colorized with RichHandler)                    │ │
│  │ └─ logs/app.json.log (for aggregation)                     │ │
│  └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   HTTP RESPONSE                                     │
│  HTTP 200 OK                                                        │
│  X-Correlation-ID: 3f91d2e3-1234-5678-abcd                         │
│  Content-Type: application/json                                    │
│                                                                     │
│  {                                                                  │
│    "status": "success",                                             │
│    "correlation_id": "3f91d2e3-1234-5678-abcd",                   │
│    "...": "other data"                                              │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Code Flow in Services

```python
# app/services/parser.py
async def parse_document(path: str):
    logger.info(f"Parsing {path}")  # ← CID=3f91d2e3 injected here
    # ↓
    # ↓ Loguru patcher adds correlation ID from contextvars
    # ↓
    # Output: INFO | parser | CID=3f91d2e3 | Parsing medical_report.pdf

    logger.debug("Reading file")   # ← CID=3f91d2e3 injected here
    logger.info("Done")             # ← CID=3f91d2e3 injected here

    return result  # Same CID throughout lifecycle
```

## Correlation ID Flow Across Services

```
Request → [CID: 3f91d2e3]
  │
  ├─→ Parser Service
  │   └─ logger.info() → CID=3f91d2e3 ✓
  │
  ├─→ Embeddings Service
  │   └─ logger.info() → CID=3f91d2e3 ✓
  │
  ├─→ LLM Service
  │   ├─ logger.info() → CID=3f91d2e3 ✓
  │   └─ External API call
  │       headers: {"X-Correlation-ID": "3f91d2e3"} ✓
  │
  └─→ Response
      headers: {"X-Correlation-ID": "3f91d2e3"} ✓
      body: {"correlation_id": "3f91d2e3"} ✓
```

## Contextvar Lifecycle

```
Request Arrives
    │
    ▼
Middleware.dispatch() starts
    │
    ├─ correlation_id = get from header or generate UUID
    │
    ├─ correlation_id_var.set(correlation_id)
    │   └─ Stored in contextvars
    │      (async-safe, request-scoped)
    │
    ▼
Route Handler Called
    │
    ├─ All async functions spawned from here
    │  inherit the same contextvars context
    │
    ├─ logger.info() calls patcher
    │  └─ patcher calls get_correlation_id()
    │     └─ Returns the stored correlation ID
    │
    ▼
All services called
    │
    ├─ parser.parse_document()
    │  ├─ logger.info() → CID injected ✓
    │  └─ await validate() → CID still available ✓
    │
    ├─ embeddings.generate()
    │  ├─ logger.info() → CID injected ✓
    │  └─ async operations → CID still available ✓
    │
    └─ llm.simplify()
       ├─ logger.info() → CID injected ✓
       └─ external API → CID available for passing ✓
    │
    ▼
Response returned
    │
    └─ Middleware adds CID to response headers
```

## Log Aggregation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ Your FastAPI App                                                │
│                                                                 │
│ logger.info("message") → CID=3f91d2e3 injected                │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
   Console                      JSON File
   (RichHandler)           (logs/app.json.log)

   Colorized output:        Structured JSON:
   INFO | parser            {
   CID=3f91d2e3            "name": "parser",
   Message                 "level": "INFO",
                           "message": "...",
                           "extra": {
                              "correlation_id": "3f91d2e3"
                           }
                        }
                           │
                           ▼
                    (Optional)
                    Log Aggregation
                    ELK / Datadog / Better Stack
                    │
                    ▼
                    Search by CID:
                    Query: correlation_id = "3f91d2e3"
                    ↓
                    All logs for that request
```

## No Manual CID Passing Needed

### ❌ WITHOUT Contextvars (Old Way)

```python
@router.post("/process")
async def process(request: Request):
    cid = request.headers.get("X-Request-ID")

    # Must pass CID manually to every service
    result1 = await service1(data, correlation_id=cid)
    result2 = await service2(data, correlation_id=cid)
    result3 = await service3(data, correlation_id=cid)

    # Must manually add CID to log
    logger.info(f"CID={cid} | Processing done")

    return {"cid": cid}  # Must manually return it
```

### ✅ WITH Contextvars (Modern Way - PatientScribe)

```python
@router.post("/process")
async def process(request: Request):
    # CID automatically stored by middleware

    # No need to pass CID, services get it from contextvars
    result1 = await service1(data)
    result2 = await service2(data)
    result3 = await service3(data)

    # CID automatically in log
    logger.info("Processing done")

    # Get CID when needed
    return {"correlation_id": get_correlation_id()}
```

## Error Handling with Correlation ID

```
Request arrives with CID=abc123
    │
    ▼
Service processes → logger.info() with CID=abc123
    │
    ▼
Error occurs → logger.error() with CID=abc123
    │
    ▼
Stack trace captured with CID in context
    │
    ▼
Response: {"error": "...", "correlation_id": "abc123"}
    │
    ▼
Search logs: correlation_id = "abc123"
    ↓
Find all logs for this request, including
  - entry point
  - all services called
  - exact point of failure
  - full stack trace
```

## Summary: Why Correlation IDs Matter

### Without Correlation IDs

```
[2024-03-07 10:30:45] INFO Processing medical report
[2024-03-07 10:30:46] INFO Parsing document
[2024-03-07 10:30:47] INFO Generating embeddings
[2024-03-07 10:30:48] ERROR File not found

Question: Which request errored? 🤷
Multiple requests happening concurrently = log confusion
```

### With Correlation IDs

```
[2024-03-07 10:30:45] CID=abc Processing medical report
[2024-03-07 10:30:46] CID=abc Parsing document
[2024-03-07 10:30:47] CID=def Processing lab results
[2024-03-07 10:30:48] CID=def Generating embeddings
[2024-03-07 10:30:49] CID=abc File not found

Question: Which request errored?
Answer: The one with CID=abc

Search logs: "CID=abc"
↓ Get complete trace:
  - Request entry
  - All operations (parsing, embedding, etc.)
  - Exact failure point
```

That's the power of correlation IDs! 🎉
