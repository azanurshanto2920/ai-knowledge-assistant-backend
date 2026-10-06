
import os
import shutil
from typing import List

from auth import hash_password, verify_password, create_access_token, decode_access_token
from database import Message, SessionLocal, User
from fastapi import Header, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel
from sqlalchemy.orm import Session
import chromadb
from pypdf import PdfReader

from database import Message, SessionLocal

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL_NAME = "openai/gpt-oss-120b"
HISTORY_LIMIT = 10

SYSTEM_PROMPT = (
    "You are a helpful AI assistant. "
    "Reply briefly and clearly in the same language as the user. "
    "If context from a document is provided, answer using that context. "
    "If the answer is not in the context, say you don't have that information."
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ChromaDB setup for RAG
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="handbook")


def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload["sub"]


class ChatRequest(BaseModel):
    message: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str

    class Config:
        from_attributes = True


@app.get("/")
def home():
    return {"message": "My AI backend is running successfully with Groq and RAG!"}

@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        return {"error": "Username already taken"}

    new_user = User(
        username=request.username,
        hashed_password=hash_password(request.password)
    )
    db.add(new_user)
    db.commit()

    return {"message": f"User '{request.username}' registered successfully"}


@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not verify_password(request.password, user.hashed_password):
        return {"error": "Invalid username or password"}

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    print(f"\n--- Received file upload: {file.filename} ---")

    # Save the uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text from the PDF
    reader = PdfReader(temp_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    # Chunk the text
    chunks = chunk_text(full_text, chunk_size=500, overlap=50)

    # Clear old data from this collection before adding new document
    # (simple approach for learning — later we can support multiple documents)
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    # Add new chunks to ChromaDB
    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

    os.remove(temp_path)

    print(f"✅ Uploaded and indexed {len(chunks)} chunks from {file.filename}")
    return {"message": f"Uploaded and indexed {len(chunks)} chunks from {file.filename}"}


@app.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    user_message = request.message
    print(f"\n--- New request received: '{user_message}' ---")

    # Get conversation history
    try:
        recent = (
            db.query(Message)
            .order_by(Message.timestamp.desc())
            .limit(HISTORY_LIMIT)
            .all()
        )
        recent.reverse()
        history = [{"role": m.role, "content": m.content} for m in recent]
    except Exception as e:
        print(f"❌ Error fetching history: {e}")
        db.rollback()
        history = []

    # Save user message to database
    try:
        db.add(Message(role="user", content=user_message))
        db.commit()
    except Exception as e:
        print(f"❌ Error saving user message: {e}")
        db.rollback()

    # Search ChromaDB for relevant document context
    doc_context = ""
    try:
        results = collection.query(query_texts=[user_message], n_results=2)
        if results["documents"] and results["documents"][0]:
            doc_context = "\n\n".join(results["documents"][0])
    except Exception as e:
        print(f"❌ Error querying ChromaDB: {e}")

    # Build the final message sent to the LLM
    if doc_context:
        user_turn = (
            f"Context from uploaded document:\n{doc_context}\n\n"
            f"Question: {user_message}"
        )
    else:
        user_turn = user_message

    ai_reply = None
    try:
        messages = (
            [{"role": "system", "content": SYSTEM_PROMPT}]
            + history
            + [{"role": "user", "content": user_turn}]
        )

        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODEL_NAME,
            temperature=0.7,
            max_tokens=1024,
        )
        ai_reply = chat_completion.choices[0].message.content
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return {"reply": f"Sorry, there was a problem generating a response: {e}"}

    try:
        db.add(Message(role="assistant", content=ai_reply))
        db.commit()
    except Exception as e:
        print(f"❌ Error saving AI reply: {e}")
        db.rollback()

    return {"reply": ai_reply}


@app.get("/history", response_model=List[MessageResponse])
def get_history(db: Session = Depends(get_db)):
    messages = db.query(Message).order_by(Message.timestamp.desc()).all()
    return messages

