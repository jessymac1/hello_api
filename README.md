# hello_api

A tiny [FastAPI](https://fastapi.tiangolo.com/) app with two endpoints:

| Method | Path       | Response                                              |
|--------|------------|-------------------------------------------------------|
| GET    | `/hello`   | `{"message": "Hey there! 👋 How's it going?"}`        |
| GET    | `/goodbye` | `{"message": "Catch you later! Take it easy. ✌️"}`    |

## Requirements

- Python 3.12 or newer
- [Poetry](https://python-poetry.org/) 2.x

## Install

```bash
poetry install
```

## Run

```bash
poetry run python main.py --reload
```

The app listens on the port in the `PORT` environment variable, or 8080 if `PORT` isn't set:

```bash
PORT=9000 poetry run python main.py
```

Try it:

```bash
curl http://localhost:8080/hello
curl http://localhost:8080/goodbye
```

Interactive API docs are at http://localhost:8080/docs

## Deployment (Google Cloud Run)

Cloud Run builds the app from `requirements.txt` and starts it with the command in `Procfile` (`python main.py`). Cloud Run sets `PORT` for you.

If you change dependencies in `pyproject.toml`, regenerate `requirements.txt`. This needs the `poetry-plugin-export` plugin.

```bash
poetry lock
poetry export -f requirements.txt --output requirements.txt --without-hashes
```
