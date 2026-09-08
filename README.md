# CareerMate AI 🚀

CareerMate AI is a cutting-edge Generative AI-powered career and interview preparation platform. It helps candidates land jobs by analyzing their resumes against job descriptions, mathematically calculating skill gaps, and putting them through adaptive, AI-driven mock interviews.

## 🌟 Key Features

1. **Smart Resume Extraction:** Upload your PDF/DOCX resume and Gemini AI mathematically extracts your skills, experience, and education into a structured JSON schema.
2. **Algorithmic Job Matching:** Paste a Job Description and receive a 100% deterministic, weighted percentage score (40% Skills, 20% Projects, 15% Experience, etc.) alongside visual Matched/Missing grids.
3. **Adaptive Mock Interviews:** Practice technical and behavioral questions in an interactive chat. The AI evaluates your responses across 4 distinct pillars (Technical Accuracy, Completeness, Clarity, Communication).
4. **Dynamic Difficulty Scaling:** If you score `> 8.0/10` on a question, the state engine dynamically ramps up the difficulty of the next question. If you struggle (`< 5.0`), it eases up.
5. **Retrieval-Augmented Generation (RAG):** Uses `pgvector` to store 768-dimensional embeddings of all knowledge chunks to perfectly ground the AI interviewer and prevent hallucinations.

## 🏗 Architecture

**Backend:**
- Python 3.11+
- FastAPI (High-performance Async API)
- PostgreSQL & SQLAlchemy ORM
- `pgvector` for Vector Similarity Search (Cosine distance)
- Google Gemini API (`text-embedding-004`, `gemini-1.5-flash`)
- `slowapi` (IP-based Rate Limiting)
- Pytest (Robust Mocking and Fixtures)

**Frontend:**
- Next.js 14+ (App Router)
- React, TypeScript
- Tailwind CSS (Utility-first styling)
- Axios/Fetch Abstraction (JWT Bearer injection)

## 🔒 Security Posture

- **Rate Limiting:** Protects expensive LLM routes (`10 requests / min`).
- **BOLA / IDOR Prevention:** Strict SQLAlchemy queries (`user_id == current_user.id`) ensuring no lateral data access.
- **Strict File Validation:** Prevents execution of malicious payloads by hard-checking `application/pdf` and `docx` MIME types.
- **Safe RAG Extraction:** Encapsulates untrusted user text inside isolated XML blocks `<RESUME_TEXT>` to defeat prompt injection techniques.

## 🚀 Getting Started

### 1. Database
Provision a Postgres instance (e.g. Neon.tech).
```bash
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. Backend
```bash
cd careerforge-ai/backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
# Ensure .env is populated (DATABASE_URL, GEMINI_API_KEY, JWT_SECRET)
uvicorn app.main:app --reload
```

### 3. Frontend
```bash
cd careerforge-ai/frontend
npm install
npm run dev
```
