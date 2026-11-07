# hello_api

A tiny [FastAPI](https://fastapi.tiangolo.com/) app with four endpoints. Two return fixed messages; two ask Google's Gemini model (via Vertex AI) to write something fresh each time:

| Method | Path       | Response                                              |
|--------|------------|-------------------------------------------------------|
| GET    | `/hello`   | `{"message": "Hey there! 👋 How's it going?"}`        |
| GET    | `/goodbye` | `{"message": "Catch you later! Take it easy. ✌️"}`    |
| GET    | `/haiku`   | `{"haiku": "..."}`: a short DevOps haiku by Gemini   |
| GET    | `/fortune` | `{"fortune": "..."}`: a one-sentence software fortune by Gemini |

## Requirements

- Python 3.12 or newer
- [Poetry](https://python-poetry.org/) 2.x
- For `/haiku` and `/fortune`: a Google Cloud project with the Vertex AI API enabled, and the [gcloud CLI](https://cloud.google.com/sdk/docs/install)

## Install

```bash
poetry install
```

## Configuration

The Gemini endpoints are configured with environment variables:

| Variable                | Required | Default                 | Purpose                         |
|-------------------------|----------|-------------------------|---------------------------------|
| `GOOGLE_CLOUD_PROJECT`  | Yes      | none                    | Google Cloud project to bill    |
| `GOOGLE_CLOUD_LOCATION` | No       | `global`                | Vertex AI location              |
| `GEMINI_MODEL`          | No       | `gemini-3.1-flash-lite` | Gemini model to use             |
| `PORT`                  | No       | `8080`                  | Port the server listens on      |

`/hello` and `/goodbye` work without any of these.

### Authentication

The app uses [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials) only. There are no API keys or key files. To run locally, log in once:

```bash
gcloud auth application-default login
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

To try the Gemini endpoints, set your project first:

```bash
GOOGLE_CLOUD_PROJECT=oe-2-514017 poetry run python main.py
curl http://localhost:8080/haiku
curl http://localhost:8080/fortune
```

Each Gemini reply is limited to about 100 output tokens.

### Errors

If a Gemini call fails, the endpoint returns a JSON error like `{"error": "Gemini request failed"}` instead of crashing:

| Status | When                                                       |
|--------|------------------------------------------------------------|
| 500    | `GOOGLE_CLOUD_PROJECT` isn't set, or no credentials found  |
| 503    | Gemini is rate-limiting requests; try again later          |
| 502    | Any other Gemini failure, such as a bad model name         |

Details are written to the server log.

Interactive API docs are at http://localhost:8080/docs

## Deployment (Google Cloud Run)

Cloud Run builds the app from `requirements.txt` and starts it with the command in `Procfile` (`python main.py`). Cloud Run sets `PORT` for you.

For the Gemini endpoints on Cloud Run:

- Enable the Vertex AI API in the project: `gcloud services enable aiplatform.googleapis.com`
- Set `GOOGLE_CLOUD_PROJECT` on the service (and optionally `GOOGLE_CLOUD_LOCATION` and `GEMINI_MODEL`).
- Give the service's service account the **Vertex AI User** role (`roles/aiplatform.user`). Cloud Run supplies its credentials automatically, so no keys are needed.

If you change dependencies in `pyproject.toml`, regenerate `requirements.txt`. This needs the `poetry-plugin-export` plugin.

```bash
poetry lock
poetry export -f requirements.txt --output requirements.txt --without-hashes
```
