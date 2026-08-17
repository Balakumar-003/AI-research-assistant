# AI Research Assistant

## Project Overview
A production-ready Enterprise AI Research Assistant. This system will eventually support PDF parsing, Retrieval-Augmented Generation (RAG), AI Chat, and literature reviews.

This milestone (Milestone 4) implements PDF Uploads & Document Management backed by MongoDB.

## Features Implemented in Milestones 3-5
- **Milestone 3**: Project management, creation, update, delete, and user ownership authorization.
- **Milestone 4**: PDF upload, storage in `backend/uploads`, paper metadata modeling in MongoDB, listing/deleting papers with strict ownership checks.
- **Milestone 5**: PDF text extraction using PyMuPDF, tracking paper processing status (`uploaded` -> `processing` -> `processed`), minimal safe text cleaning, and page-aware text storage in a `document_pages` MongoDB collection. Includes pagination support for viewing extracted content.

## Folder Structure
```text
AI-Research-Assistant/
├── backend/            # FastAPI Backend
│   ├── app/            # Application logic (api, core, database, models, schemas, services, utils)
│   ├── requirements.txt# Dependencies
│   └── .env.example    # Environment variable template
├── frontend/           # React Frontend (Future)
├── docs/               # Documentation
├── dataset/            # Data storage
└── docker/             # Docker configurations
```

## Installation Steps

### 1. Virtual Environment Setup
First, navigate to the `backend` directory and create a virtual environment:
```bash
cd backend
python -m venv venv
```

Activate the virtual environment:
- **Mac/Linux:** `source venv/bin/activate`
- **Windows:** `venv\Scripts\activate`

### 2. Package Installation
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the environment template and configure your variables:
```bash
cp .env.example .env
```
Ensure you have MongoDB running locally (default: `mongodb://localhost:27017`).

## Running FastAPI
To start the backend server, ensure you are in the `backend` directory and run:
```bash
uvicorn app.main:app --reload
```

## Authentication Flow & API Endpoints

This project uses JWT (JSON Web Tokens) for secure authentication. Passwords are hashed using bcrypt.

### Auth Endpoints
- `POST /auth/register`: Registers a new user.
- `POST /auth/login`: Authenticates user credentials (email & password) and returns a JWT.
- `GET /users/me`: Protected endpoint. Requires a valid JWT to return the current user's profile.
- `GET /health`: Public endpoint to check system health.

### Project Endpoints
All project endpoints require authentication via JWT.
- `POST /projects`: Create a new project. 
  Example request: `{"name": "NLP Research", "description": "Research on transformers"}`
- `GET /projects`: List all projects for the authenticated user.
- `GET /projects/{project_id}`: Get a specific project.
- `PUT /projects/{project_id}`: Update a specific project's name or description.
- `DELETE /projects/{project_id}`: Soft delete a project.

### Document Processing Endpoints
- `POST /papers/{paper_id}/process`: Extracts text from the uploaded PDF using PyMuPDF and stores page-aware metadata.
- `GET /papers/{paper_id}/processing-status`: Returns the current extraction status (`uploaded`, `processing`, `processed`, `failed`).
- `GET /papers/{paper_id}/content?page=1&limit=10`: Returns the paginated extracted text from the document.

## Testing with Swagger UI
Once the server is running, navigate to the Swagger Documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

**How to test the Auth & Project Flow:**
1. **Register:** Call `POST /auth/register`.
2. **Login:** Call `POST /auth/login` and copy the `access_token`.
3. **Authorize:** Click the **Authorize** button in Swagger UI and paste your token.
4. **Create Project:** Call `POST /projects` to create a new research project.
5. **List Projects:** Call `GET /projects` to verify your project was created.

## Testing with Automated Script
A python script `backend/test_projects.py` is provided to run automated tests against the APIs.
Run it using:
```bash
python test_projects.py
```

## Future Milestones (Milestone 4)
- Vector Database & Embeddings Setup
- PDF Upload and Parsing
- Text Chunking
- Frontend Integration (React Dashboard for Projects)
