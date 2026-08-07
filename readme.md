# AI Research Assistant

## Project Overview
A production-ready Enterprise AI Research Assistant. This system will eventually support PDF parsing, Retrieval-Augmented Generation (RAG), AI Chat, and literature reviews.

This milestone (Milestone 2) implements a robust Authentication foundation backed by MongoDB.

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

### API Endpoints
- `POST /auth/register`: Registers a new user.
- `POST /auth/login`: Authenticates user credentials (email & password) and returns a JWT.
- `GET /users/me`: Protected endpoint. Requires a valid JWT to return the current user's profile.
- `GET /health`: Public endpoint to check system health.

## Testing with Swagger UI
Once the server is running, navigate to the Swagger Documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

**How to test the Auth Flow:**
1. **Register:** Find the `POST /auth/register` endpoint, click "Try it out", and provide your name, email, and password. Execute.
2. **Login:** Find the `POST /auth/login` endpoint, provide the same email and password. Execute and copy the `access_token` string from the response.
3. **Authorize:** Scroll to the top of Swagger UI and click the **Authorize** button. Paste your copied token (or let Swagger auto-fill if configured) and click Authorize.
4. **Call Protected Route:** Find the `GET /users/me` endpoint. Click "Try it out" and execute. Because you authorized Swagger, it will attach the token to the request and successfully return your profile data!

## Future Milestones
- Vector Database & Embeddings Setup
- PDF Upload and Parsing
- LangChain / LangGraph Integration
- Frontend integration with React/Vite
