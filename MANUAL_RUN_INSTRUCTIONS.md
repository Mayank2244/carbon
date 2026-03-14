# Manual Run Instructions

Follow these step-by-step instructions to run the CarbonSense AI project manually on your local machine.

## Prerequisites

Ensure you have the following installed:
- **Python 3.10+**: Verify with `python --version`
- **Node.js (LTS)**: Verify with `node --version`
- **PostgreSQL**: Verify service is running.
- **Redis**: Verify service is running.

## 1. Backend Setup

The backend is built with FastAPI and Python.

### Step 1.1: Navigate to Backend Directory
Open your terminal and navigate to the `backend` folder:
```bash
cd backend
```

### Step 1.2: Create Virtual Environment
Create an isolated Python environment to manage dependencies:
```bash
python -m venv venv
```

### Step 1.3: Activate Virtual Environment
- **Mac/Linux**:
  ```bash
  source venv/bin/activate
  ```
- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

### Step 1.4: Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```

### Step 1.5: Configure Environment Variables
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in a text editor and fill in the required values:
   - **Database**: `DATABASE_URL` (e.g., `postgresql://user:password@localhost:5432/carbonsense_db`)
   - **Redis**: `REDIS_URL`
   - **API Keys**: `GROQ_API_KEY`, `HUGGINGFACE_API_KEY`, etc.

### Step 1.6: Initialize Database (Optional)
If running for the first time, you might need to initialize the database tables. The application attempts to do this on startup, but ensure your Postgres server is running and the database exists.

### Step 1.7: Run the Backend Server
Start the FastAPI server with hot-reloading enabled:
```bash
uvicorn app.main:app --reload
```
*The backend will be available at `http://localhost:8000`.*
*API Documentation: `http://localhost:8000/docs`*

---

## 2. Frontend Setup

The frontend is built with React, Vite, and Tailwind CSS.

### Step 2.1: Navigate to Frontend Directory
Open a **new terminal window** and navigate to the `frontend` folder:
```bash
cd frontend
```

### Step 2.2: Install Dependencies
Install all required Node.js packages:
```bash
npm install
```

### Step 2.3: Run Development Server
Start the frontend development server:
```bash
npm run dev
```
*The frontend will typically be available at `http://localhost:5173` (check terminal output).*

---

## 3. Verification

1. **Backend Health Check**:
   Open `http://localhost:8000/health` in your browser. You should see `{"status": "healthy", ...}`.

2. **Frontend Access**:
   Open the frontend URL (e.g., `http://localhost:5173`). You should see the CarbonSense AI dashboard.

## Troubleshooting

- **Database Connection Error**: Ensure PostgreSQL is running and the credentials in `backend/.env` are correct.
- **Redis Error**: Ensure Redis server is running (`redis-cli ping` should return `PONG`).
- **Module Not Found**: Ensure you activated the virtual environment before running the backend.
- **Port Conflicts**: If ports 8000 or 5173 are in use, modify `.env` (backend) or `vite.config.ts` (frontend) / check running processes.
