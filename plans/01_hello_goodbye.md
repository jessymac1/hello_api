# Plan: FastAPI hello/goodbye API

## Context
The repo has only `CLAUDE.md` and is on `main`. We need a small FastAPI app, managed by Poetry, with two GET endpoints (`/hello`, `/goodbye`) that return casual JSON messages. It will later be deployed to Google Cloud Run from GitHub, so it has to read its port from `PORT` (default 8080) and ship a `requirements.txt` exported from Poetry. Poetry 2.5.1 with `poetry-plugin-export` and Python 3.14 are already installed.

## Steps
1. **Log the prompt.** Create `PROMPTS.md` with a time-stamped entry (2026-11-07) holding this prompt.
2. **Branch.** `git checkout -b add_hello_goodbye_api`. Never work on `main`.
3. **Save the approved plan** as `plans/01_hello_goodbye.md`.
4. **Poetry project.** Create `pyproject.toml` with `package-mode = false` (this is an app, not a library), `requires-python = ">=3.12"`, and runtime dependencies only:
   - `fastapi`
   - `uvicorn`

   No test or dev packages. Run `poetry install` to generate `poetry.lock`.
5. **`main.py`** (project root):
   - `app = FastAPI()`
   - `GET /hello` returns `{"message": "Hey there! 👋 How's it going?"}`
   - `GET /goodbye` returns `{"message": "Catch you later! Take it easy. ✌️"}`
   - Under `if __name__ == "__main__":`, run `uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))`
6. **`Procfile`** containing `web: python main.py`. Cloud Run's Python buildpack would otherwise default to gunicorn, which isn't installed. The Procfile makes it start our app, and our app reads `PORT`.
7. **`requirements.txt`**: `poetry export -f requirements.txt --output requirements.txt --without-hashes`
8. **`.gitignore`**: `__pycache__/`, `.venv/`, `.env`, `*.pyc`
9. **`README.md`**: what the app does, the endpoints, how to install (`poetry install`), how to run (`poetry run python main.py`, with a custom `PORT` example), and how to regenerate `requirements.txt` after changing dependencies.

## Files created
`PROMPTS.md`, `plans/01_hello_goodbye.md`, `pyproject.toml`, `poetry.lock`, `main.py`, `Procfile`, `requirements.txt`, `.gitignore`, `README.md`

## Verification
- `poetry run python main.py` &, then `curl localhost:8080/hello` and `curl localhost:8080/goodbye` return the JSON messages
- `PORT=9000 poetry run python main.py` &, then `curl localhost:9000/hello` works
- `requirements.txt` lists fastapi and uvicorn
- `git status` shows we're on `add_hello_goodbye_api`, with nothing committed (you'll commit it yourself)
