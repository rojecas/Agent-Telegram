---
description: Instructions to set up the development environment from scratch
---

# Development Environment Setup

## 1. Prerequisites
- Python 3.10+
- Git

## 2. Installation Steps

### Step 1: Clone and Enter
```bash
git clone <repo_url>
cd Agent-Telegram
```

### Step 2: Create Virtual Environment
Isolate dependencies to avoid conflicts.
```bash
python -m venv .venv
```

### Step 3: Activate Environment
*   **Windows (Git Bash)**:
    ```bash
    source .venv/Scripts/activate
    ```
*   **Linux/Mac**:
    ```bash
    source .venv/bin/activate
    ```

### Step 4: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Configuration (.env)
Copy the template and fill in your secrets.
```bash
cp .env.template .env
```
Edit `.env` and add:
- `DEEPSEEK_API_KEY`
- `TELEGRAM_BOT_TOKEN`

## 3. Verification
Run the main entry point to ensure everything loads correctly.
```bash
python main.py
```
