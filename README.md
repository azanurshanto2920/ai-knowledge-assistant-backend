# AI Knowledge Assistant — Backend

A full-stack AI chatbot backend that can answer questions based on uploaded PDF documents, using Retrieval-Augmented Generation (RAG).

## Features

- **Chat with AI** — powered by Groq API (LLaMA/GPT-OSS models)
- **RAG (Retrieval-Augmented Generation)** — upload a PDF and ask questions about its content
- **Persistent Chat History** — stored in PostgreSQL
- **JWT Authentication** — secure register/login system with hashed passwords
- **Vector Search** — ChromaDB for semantic document search
- **Dockerized** — ready to deploy anywhere

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL + SQLAlchemy
- **Vector DB:** ChromaDB
- **LLM:** Groq API
- **Auth:** JWT (python-jose) + bcrypt password hashing
- **Containerization:** Docker

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|--------------|
| POST | `/register` | Create a new user account |
| POST | `/login` | Log in and receive a JWT token |
| POST | `/upload` | Upload a PDF to be indexed for RAG |
| POST | `/chat` | Send a message and get an AI response (protected) |
| GET | `/history` | Get full conversation history (protected) |

## Running Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Running with Docker

```bash
docker build -t ai-knowledge-assistant .
docker run -p 8000:8000 --env-file .env ai-knowledge-assistant
```

## Frontend

The React frontend for this project is available at: [link পরে যোগ হবে]