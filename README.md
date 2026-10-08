# AI Knowledge Assistant — Backend

A full-stack AI chatbot backend that can answer questions based on uploaded PDF documents, using Retrieval-Augmented Generation (RAG).

## Live Demo

- **Frontend:** [https://ai-knowledge-assistant-frontend-tau.vercel.app](https://ai-knowledge-assistant-frontend-tau.vercel.app)
- **Backend API docs:** [https://ai-knowledge-assistant-backend-1yuu.onrender.com/docs](https://ai-knowledge-assistant-backend-1yuu.onrender.com/docs)
- **Frontend repository:** [ai-knowledge-assistant-frontend](https://github.com/azanurshanto2920/ai-knowledge-assistant-frontend)

> Note: The backend runs on a free tier and sleeps after inactivity. The first request may take up to a minute to wake it up. Uploaded PDFs are not stored permanently on the free tier.

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
- **Hosting:** Render (backend + database), Vercel (frontend)

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