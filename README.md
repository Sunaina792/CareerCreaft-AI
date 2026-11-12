# CareerCraft AI

CareerCraft AI is an AI-powered resume analyzer and builder. It uses FastAPI for the backend, a static HTML/CSS/JavaScript frontend, and Groq models for resume analysis and writing assistance.

## Features

- Analyze a resume and receive a score, feedback, and improvement suggestions.
- Compare resume content with a job description.
- Generate or improve resume summaries, bullet points, and skills.
- Tailor an uploaded resume to a job description and download the result as DOCX or PDF.
- Create interview preparation questions from a resume and optional job description.
- Export a resume as DOCX or PDF.

## Requirements

- Python 3.11 or newer
- A Groq API key

## Setup on Windows

Open PowerShell in the project directory:

```powershell
cd "C:\path\to\CareerCraft_AI"
```

Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -e .
```

Create the root `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Keep the real API key private. Do not commit `.env` files; they are excluded by `.gitignore`.

## Run the application

From the project directory, with the virtual environment activated, start the server:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open the app at [http://localhost:8000](http://localhost:8000). API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs), and the health endpoint is [http://localhost:8000/api/health](http://localhost:8000/api/health).

## Deploy on Render

The FastAPI server hosts both the frontend and API, so deploy it as a single web service:

1. Push the project to GitHub and create a **Web Service** on [Render](https://render.com/) connected to the repository.
2. Set the **Root Directory** to the directory containing `pyproject.toml` (leave it blank if that is the repository root).
3. Use these commands:

   - **Build Command:** `pip install .`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

4. Add `GROQ_API_KEY` under the service's **Environment Variables** in Render. Use your actual Groq API key; never put it in frontend code or commit it to GitHub.
5. Deploy. Open the Render service URL and check `/api/health`; the app is available at the same URL.

The frontend calls `/api` on the same host, so the API and pages work together on the deployed domain. Uploaded resumes are processed in memory and are not stored by the app.

## API endpoints

All application API endpoints are served under `/api`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check that the server is running |
| `POST` | `/api/analyze` | Upload a PDF or DOCX resume for analysis |
| `POST` | `/api/match` | Compare resume text with a job description |
| `POST` | `/api/builder/summary` | Generate a professional summary |
| `POST` | `/api/builder/rewrite-bullet` | Rewrite a resume bullet point |
| `POST` | `/api/builder/suggest-skills` | Suggest skills for a target role |
| `POST` | `/api/builder/improve-section` | Improve resume section content |
| `POST` | `/api/builder/tailor` | Tailor an uploaded PDF or DOCX resume to a job description |
| `POST` | `/api/interview-prep` | Generate interview questions and tips |
| `POST` | `/api/export` | Generate a DOCX or PDF resume |

Interactive request schemas and responses are documented at `/docs` while the server is running.

## Project structure

```text
backend/
  core/       Resume parsing, Groq integration, prompts, and document export
  routers/    FastAPI endpoint modules
  main.py     Application entry point and frontend hosting
frontend/     HTML pages, stylesheets, and browser-side JavaScript
```
