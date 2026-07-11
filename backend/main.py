from database import SessionLocal, engine, Base
from models import User, SearchHistory
from auth import hash_password, verify_password
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from pathlib import Path

from services.gemini_service import (
    get_ai_response,
    classify_intent
)

from services.vector_store import (
    add_document,
    get_context_and_sources,
    count_documents,
    collection
)

from utils.pdf_utils import extract_text_from_pdf
from utils.text_splitter import split_text


import uuid

app = FastAPI()


UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UsernameUpdateRequest(BaseModel):
    username: str


class QuestionRequest(BaseModel):
    subject: str
    question: str
    user_id: int

# Home Route
@app.get("/")
def home():
    return {
        "message": "Welcome to AKTUbot"
    }

@app.post("/signup")
def signup(data: SignupRequest):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        db.close()

        return {
            "message": "User already exists"
        }

    new_user = User(
        username=data.username,
        email=data.email,
        password=hash_password(data.password)
    )

    db.add(new_user)
    db.commit()
    db.close()

    return {
        "message": "Signup successful"
    }


@app.post("/login", status_code=status.HTTP_200_OK)
def login(data: LoginRequest):

    db = SessionLocal()

    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No user exists for this email."
        )

    if not verify_password(
        data.password,
        user.password
    ):
        db.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email and password do not match."
        )

    db.close()

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }


@app.put("/users/{user_id}/username", status_code=status.HTTP_200_OK)
def update_username(user_id: int, data: UsernameUpdateRequest):
    new_username = data.username.strip()

    if not new_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be empty"
        )

    db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    duplicate_user = (
        db.query(User)
        .filter(User.username == new_username, User.id != user_id)
        .first()
    )

    if duplicate_user:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    user.username = new_username
    db.commit()
    db.refresh(user)
    db.close()

    return {
        "message": "Username updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }


# Normal Gemini Chat
@app.post("/ask")
def ask_question(data: QuestionRequest):

    ai_answer = get_ai_response(data.question)

    return {
        "your_question": data.question,
        "answer": ai_answer
    }


# RAG Chat
@app.post("/ask-rag")
def ask_rag(data: QuestionRequest):
    intent = classify_intent(
        data.question,
        data.subject
    )
    print("Detected Intent:", intent)

    if intent == "casual":
        prompt = f"""
You are AKTUbot.

The user has currently selected the subject:
{data.subject}

Have a short and natural conversation.

Rules:

- Be friendly.
- Keep replies under 3 sentences.
- If the user asks who you are, explain that you are an AI academic assistant.
- Mention that you can help with the selected subject ({data.subject}) whenever appropriate.
- If the user asks what you can do, explain your academic capabilities.
- Do NOT invent information.
- Do NOT answer questions outside your purpose.

User:
{data.question}
"""

        answer = get_ai_response(prompt)

        return {
            "subject": data.subject,
            "question": data.question,
            "answer": answer,
            "sources": []
        }

    if intent == "unrelated":
        prompt = f"""
You are AKTUbot.

The user has selected the subject:
{data.subject}

Politely explain that your primary purpose is to help students with the selected subject.

Be friendly and encourage them to ask questions related to {data.subject}.

User:
{data.question}
"""

        answer = get_ai_response(prompt)

        return {
            "subject": data.subject,
            "question": data.question,
            "answer": answer,
            "sources": []
        }

    context, sources = get_context_and_sources(
        data.question,
        data.subject
    )

    # Debug Output
    print("\n" + "=" * 60)
    print("QUESTION:", data.question)
    print("=" * 60)
    print(context[:2000])
    print("=" * 60 + "\n")

    prompt = f"""


You are an expert DBMS professor.

Answer the question in a clean exam-oriented format.

Rules:

1. Do not say "Based on the provided context".
2. Do not mention the context.
3. Use proper headings and bullet points.
4. If comparison is asked, create a table.
5. If the answer is not available, say:
   "I could not find this information in the uploaded documents."
6. Don't show stars (*) and underscores (_) also hash (#) in the output. Use proper formatting instead.
7. Answer in the same language in which the user asked the question.

Context:
{context}

Question:
{data.question}
"""

    answer = get_ai_response(prompt)

    # Save Search History
    db = SessionLocal()

    new_search = SearchHistory(
        user_id=data.user_id,
        question=data.question
    )

    db.add(new_search)
    db.commit()

    # Keep only latest 10 searches
    all_searches = (
        db.query(SearchHistory)
        .filter(
            SearchHistory.user_id == data.user_id
        )
        .order_by(
            SearchHistory.created_at.desc()
        )
        .all()
    )

    if len(all_searches) > 10:
        for old_search in all_searches[10:]:
            db.delete(old_search)

        db.commit()

    return {
        "subject": data.subject,
        "question": data.question,
        "answer": answer,
        "sources": sources
    }


# Upload PDF
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    extracted_text = extract_text_from_pdf(file_path)

    chunks = split_text(extracted_text)

    for chunk in chunks:
        add_document(
            doc_id=str(uuid.uuid4()),
            text=chunk,
            metadata={
                "subject": "DBMS",
                "type": "NOTES",
                "filename": file.filename
            }
        )

    return {
        "filename": file.filename,
        "characters_extracted": len(extracted_text),
        "chunks_stored": len(chunks)
    }


@app.get("/download-pdf/{filename}")
def download_pdf(filename: str):
    safe_name = Path(filename).name
    file_path = UPLOAD_DIR / safe_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        path=file_path,
        filename=safe_name,
        media_type="application/pdf"
    )


# Count Documents
@app.get("/count")
def count():

    return {
        "documents_in_db": count_documents()
    }


# Peek Metadata
@app.get("/peek")
def peek():

    data = collection.get()

    return {
        "total_docs": len(data["ids"]),
        "sample_metadata": data["metadatas"][:5]
    }

@app.get("/history/{user_id}")
def get_history(user_id: int):
        db = SessionLocal()

        history = (
            db.query(SearchHistory)
            .filter(
                SearchHistory.user_id == user_id
            )
            .order_by(
                SearchHistory.created_at.desc()
            )
            .limit(10)
            .all()
        )

        return [
            {
                "id": item.id,
                "question": item.question
            }
            for item in history
        ]

