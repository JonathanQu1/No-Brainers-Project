# No-Brainers-Project

## How to run this project

Follow these steps from your machine. Run commands from the **project root** (the folder that contains `main.py` and `requirements.txt`). If your folder name has spaces, put the path in quotes when you `cd`.

### 1. Open a terminal in the project folder

Example (adjust the path to where you cloned the repo):

```bash
cd "/Users/you/Documents/GitHub/No-Brainers-Project/No Brainers Project"
```

### 2. Use Python 3

Check that Python 3 is available:

```bash
python3 --version
```

Use `python3` in the commands below if `python` on your system is not Python 3.

### 3. (Recommended) Create and activate a virtual environment

This keeps dependencies isolated from other projects.

```bash
python3 -m venv .venv
```

Activate it:

- **macOS / Linux:** `source .venv/bin/activate`
- **Windows (Command Prompt):** `.venv\Scripts\activate.bat`
- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`

Your prompt will usually show `(.venv)` when it is active.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

This installs packages listed in `requirements.txt` (for example SQLAlchemy and CustomTkinter).

### 5. Run the app

Still in the project root:

```bash
python main.py
```

Or, if you use `python3` only:

```bash
python3 main.py
```

### 6. What you should see

Running `main.py` creates the SQLite database under `data/` (if needed), creates tables, and prints a short confirmation in the terminal.

---

**Note:** Always start the app from the project root so imports like `backend.database` resolve correctly. If you move the project, use the new folder path in step 1.
