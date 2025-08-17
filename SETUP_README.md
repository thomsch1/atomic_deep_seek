# Development Environment Setup

If you're getting `ModuleNotFoundError: No module named 'agent'` when running `make dev` from an external bash environment, follow these steps:

## Quick Setup (Recommended)

Run the setup script once:

```bash
make setup
```

Or directly:

```bash
./setup-dev.sh
```

This will:
- Install the `agent` package in editable mode
- Set up environment variables
- Install frontend dependencies
- Verify everything works

## Manual Setup (Alternative)

If the automatic setup doesn't work, follow these manual steps:

### 1. Install the Backend Package

```bash
cd backend
pip install -e . --user
cd ..
```

### 2. Set Environment Variables

Make sure you have a `.env` file in the project root with:

```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Verify Installation

Test that the agent module can be imported:

```bash
python3 -c "import agent; print('✅ Agent module works!')"
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Running the Development Servers

After setup, you can use:

```bash
# Start both frontend and backend
make dev

# Start only backend
make dev-backend

# Start only frontend  
make dev-frontend
```

## Troubleshooting

### Getting "ModuleNotFoundError: No module named 'fastapi'" or similar dependency errors?

This means the Python dependencies aren't installed in your environment. Try:

```bash
# Install dependencies manually
cd backend
pip install -r requirements.txt --user

# Or install individual missing packages
pip install --user fastapi uvicorn pydantic python-dotenv atomic-agents instructor google-generativeai httpx

# Then install the agent package
pip install -e . --user
```

### Still getting "ModuleNotFoundError: No module named 'agent'"?

Try setting PYTHONPATH manually:

```bash
export PYTHONPATH="$(pwd)/backend/src:$PYTHONPATH"
make dev
```

### Permission issues with pip?

Try different installation methods:

```bash
cd backend
# Method 1: User install with system packages
pip install -e . --user --break-system-packages

# Method 2: User install (older pip versions)
pip install -e . --user

# Method 3: Virtual environment (recommended for development)
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Different Python environments?

Make sure you're using the same Python/pip in your external bash:

```bash
which python3
which pip3
python3 --version
pip3 --version
```

### Frontend not starting?

Make sure Node.js and npm are installed:

```bash
node --version
npm --version
```

If not installed, visit https://nodejs.org/

## What Each Command Does

- `make setup` - Sets up the entire development environment
- `make dev` - Starts frontend (Vite) + backend (Uvicorn) concurrently
- `make dev-backend` - Starts only the backend server with auto-reload
- `make dev-frontend` - Starts only the frontend development server

## Environment Variables

The application requires:

- `GEMINI_API_KEY` - Your Google Gemini API key
- Other optional variables can be found in `backend/.env.example`

## Ports

- Backend: http://localhost:8000
- Frontend: http://localhost:5173 (or next available port)
- API Docs: http://localhost:8000/docs