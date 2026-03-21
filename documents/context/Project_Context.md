Good thinking. If your VS Code agent understands the **long-term goal (PatientScribe)** instead of just the logging demo, it can help you evolve the project naturally instead of generating throwaway code. Think of the prompt as giving the agent a **mental map of the system** 🧭

Below is a **clean “project context prompt”** you can paste into your VS Code AI agent so it understands:

• the **logging demo**
• the **future PatientScribe GenAI architecture**
• the **tech stack**
• how the project should grow over time

---

# Prompt for VS Code Agent (Project Context)

You are helping me build a Python project called **PatientScribe**. The goal is to gradually build a **production-style GenAI backend application** while demonstrating best practices such as logging, API design, and modular architecture.

The project will evolve step by step, so please keep the architecture clean, extensible, and easy to explain in demos.

---

# Project Vision: PatientScribe

PatientScribe is a **GenAI-powered application** where users upload medical reports and receive simplified explanations, summaries, and insights.

The system will eventually include:

* document ingestion
* text extraction
* LLM explanation
* retrieval augmentation
* API endpoints
* observability and logging
* optional visualization generation

This project is also used for **educational and demo purposes**, so clarity and modular design are important.

---

# Target Architecture (High Level)

Frontend
↓
FastAPI Backend
↓
Application Layer
↓
LLM Orchestration (LangChain)
↓
Data Sources

* Vector DB (future)
* Document store
* External APIs

Logging and observability should be integrated throughout the stack.

---

# Technology Stack

Backend framework
FastAPI

LLM orchestration
LangChain

API serving for chains
LangServe (future step)

Logging
Native Python logging (for comparison)
Loguru + RichHandler (preferred production option)

Vector database (future)
Qdrant

Embedding model
Open-source embedding model (TBD)

LLM
Initially OpenAI or Mistral API

---

# Current Development Phase

Right now I am implementing a **logging demonstration module** that will later be integrated into the PatientScribe backend.

The goal is to demonstrate the difference between:

1. Native Python logging
2. Loguru with Rich console output

This will be used in a presentation to show the value of structured logging in production systems.

---

# Initial Project Structure

The agent should generate a structure similar to:

```
patientscribe/

app/
    main.py
    config.py

    logging/
        native_logger.py
        loguru_logger.py

    services/
        data_pipeline.py
        report_generator.py

    api/
        routes.py

demo/
    native_logging_demo.py
    loguru_logging_demo.py

README.md
```

---

# Logging Demonstration Requirements

Create two demo scripts that simulate a simple backend workflow.

Workflow example:

Application start
Connect to mock database
Fetch data records
Process records
Generate report
Simulate error
Shutdown

Each step should log using different severity levels:

DEBUG
INFO
WARNING
ERROR
CRITICAL

One script should use **native Python logging**, the other should use **Loguru with RichHandler**.

The logs should clearly show the difference in:

* configuration complexity
* formatting
* readability
* colored output

---

# Design Principles

When generating code, prioritize:

* readability
* modular architecture
* clear separation of concerns
* production-style structure
* minimal unnecessary complexity

Code should be easy to extend later when we add:

* FastAPI endpoints
* document processing
* LangChain pipelines
* LangServe routes
* vector search

---

# Future Steps (Important Context)

This project will later include:

1. FastAPI API endpoints
2. document upload endpoint
3. PDF text extraction
4. LangChain explanation pipeline
5. LangServe integration
6. RAG with vector database
7. cloud deployment
8. observability improvements

Design the project so these additions can be implemented cleanly.

---

# Expected Behavior from the Agent

When generating code:

* keep the project consistent with the architecture above
* prefer modular services instead of monolithic scripts
* write clear logging statements
* keep demo code simple but realistic

---
