# No Brainers Project

Python + SQLAlchemy (SQLite) with a CustomTkinter front end. Run everything from the **project root** (the folder that contains `main.py` and `requirements.txt`).

## Requirements

- Python 3.10+ recommended  
- Dependencies: `pip install -r requirements.txt`

## How to run

### 1. Virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (cmd):** `.venv\Scripts\activate.bat`  
**Windows (PowerShell):** `.venv\Scripts\Activate.ps1`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize the database

```bash
python main.py
```

Creates `data/app.db` and tables if needed.

### 4. Start the app

```bash
python -m frontend.app
```

Use the project root for these commands so `backend` imports work. If the folder path has spaces, quote it in `cd`.
