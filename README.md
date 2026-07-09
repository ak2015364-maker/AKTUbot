# //-- AKTUbot --//

An AI-powered academic assistant built specifically for AKTU students.

AKTUbot uses Retrieval-Augmented Generation (RAG) with Google's Gemini API to answer subject-specific questions using Notes, PYQs, and Syllabus PDFs.

---

##  Features

- AI-powered academic chatbot
- Retrieval-Augmented Generation (RAG)
- PDF-based knowledge retrieval
- User Login & Signup
- Search History
- Download Source PDFs
- Semantic Search using ChromaDB
- Responsive React UI

---

## 🛠 Tech Stack

### Frontend
- React.js
- Axios
- CSS

### Backend
- FastAPI
- Python
- SQLAlchemy
- SQLite

### AI & ML
- Google Gemini API
- ChromaDB
- Sentence Transformers
- all-MiniLM-L6-v2

---

## 📂 Project Structure

```
AKTUbot
│
├── backend
│   ├── services
│   ├── utils
│   ├── AKTU_data
│   ├── uploads
│   ├── chroma_db
│   └── main.py
│
├── frontend
│   ├── src
│   └── public
│
└── README.md
```

---

##  Installation

### Clone Repository

```bash
git clone https://github.com/ak2015364-maker/AKTUbot.git
```

### Backend

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

##  How It Works

1. PDFs are uploaded into the knowledge base.
2. PDFs are converted into embeddings.
3. ChromaDB stores the embeddings.
4. User asks a question.
5. Relevant chunks are retrieved.
6. Gemini generates an answer using retrieved context.

---

## 🌐 Live Demo

Frontend:
AKTUbot.netlify.app

Backend API:
https://aktubot-production.up.railway.app/docs

---

## 🔮 Future Improvements

- Voice Assistant
- OCR Support
- Multi-Subject Support
- Admin Dashboard
- Mobile Application

---

⭐ If you found this project useful, please consider giving it a star.