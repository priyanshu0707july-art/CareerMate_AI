# CareerForge AI

Your AI-powered career and interview preparation assistant.

## Purpose
CareerForge AI is a Generative AI-powered career and interview preparation platform that analyzes a candidate's resume against a job description, identifies skill gaps, performs semantic matching using embeddings, and conducts personalized AI mock interviews using RAG.

## Features
- **Authentication**: JWT-based secure authentication with bcrypt password hashing.
- **Resumes & Jobs**: Securely upload PDF/DOCX resumes with automatic text parsing and Gemini-powered structured data extraction. Users can also add job descriptions for AI processing.
- **Match Engine**: AI-powered gap analysis and match scoring (coming soon).
- **Mock Interviews**: Interactive AI mock interviews tailored to jobs (coming soon).

## Architecture
This project is built using a modern full-stack architecture:
- **Frontend**: Next.js, TypeScript, and Tailwind CSS. Hosted on Vercel.
- **Backend**: Python FastAPI, Pydantic, SQLAlchemy. Hosted on Render.
- **Database**: PostgreSQL with pgvector for vector search. Hosted on Neon or Render.
- **AI**: Gemini API for generative capabilities and embeddings.

## Tech Stack
- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: Python 3.11+, FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL, pgvector
- AI: Gemini API

## Local Setup

### Prerequisites
- Node.js
- Python 3.11+
- PostgreSQL

### Backend
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```
5. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## License
MIT
