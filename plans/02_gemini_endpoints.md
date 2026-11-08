# Plan: Gemini-powered /haiku and /fortune endpoints

## Context
The app has `/hello` and `/goodbye` in [main.py](main.py). The previous work is committed on branch `add_hello_goodbye_api`. We're adding two GET endpoints whose text comes from Gemini on Vertex AI, using the `google-genai` SDK. They authenticate with Application Default Credentials only (no API keys, no key files) so they work both locally (`gcloud auth application-default login`, which already exists on this machine) and on Cloud Run (through the service account).

## Steps
1. **Log the prompt** in `PROMPTS.md` with a timestamp.
2. **Branch.** Create `add_gemini_endpoints` from the current branch. Not `main`.
3. **Save the plan** as `plans/02_gemini_endpoints.md`.
4. **Dependency.** `poetry add google-genai`. This is the only new package.
5. **[main.py](main.py)**:
   - **Settings, read from env:** `GOOGLE_CLOUD_PROJECT` (required, no default), `GOOGLE_CLOUD_LOCATION` (default `"global"`), `GEMINI_MODEL` (default `"gemini-3.1-flash-lite"`).
   - **Lazy, cached client.** A `get_client()` helper creates `genai.Client(vertexai=True, project=..., location=...)` on first use and caches it. This lets the app start and keep serving `/hello` and `/goodbye` even if Gemini isn't configured. If `GOOGLE_CLOUD_PROJECT` is missing, it raises a config error.
   - **Fixed prompts as module constants:**
     - `HAIKU_PROMPT`: "Write a short haiku about DevOps. Reply with only the haiku."
     - `FORTUNE_PROMPT`: "Write a one-sentence, software-themed fortune-cookie message. Reply with only the fortune."
   - **One shared `ask_gemini(prompt)` helper.** It calls `client.models.generate_content(model=..., contents=prompt, config=types.GenerateContentConfig(max_output_tokens=100, ...))` and returns `response.text.strip()`.
     - Gemini 3 models "think" by default, and that thinking counts against the 100-token limit, so the answer could come back cut off or empty. To avoid this, set thinking to the minimum level, then check during verification that the model accepts the setting and gives complete answers.
   - **Endpoints:**
     - `GET /haiku` returns `{"haiku": "..."}`
     - `GET /fortune` returns `{"fortune": "..."}`
     - Both are plain `def` (not `async`), so FastAPI runs the blocking SDK call in a threadpool.
   - **Errors.** Each case returns JSON `{"error": "..."}` with a short, clear message and no stack trace. Details are logged on the server.

     | Situation | Status |
     |---|---|
     | `GOOGLE_CLOUD_PROJECT` not set | 500, "Gemini is not configured: GOOGLE_CLOUD_PROJECT is not set" |
     | No ADC found (`google.auth.exceptions.DefaultCredentialsError`) | 500, "Gemini credentials are not available" |
     | Gemini rate limit (`errors.APIError` with code 429) | 503, with "try again later" |
     | Any other Gemini/API error, or an empty response | 502, "Gemini request failed" |

6. **requirements.txt.** Re-export with `poetry export -f requirements.txt --output requirements.txt --without-hashes`.
7. **README.md.** Document:
   - The two new endpoints
   - The three environment variables
   - Local auth: `gcloud auth application-default login`
   - The Cloud Run notes:
     - Set `GOOGLE_CLOUD_PROJECT` on the service.
     - The service account needs the `roles/aiplatform.user` role.
     - The Vertex AI API must be enabled.
     - No keys are needed.
   - The error responses

   I'll keep your other README edits as they are. One problem, though: `poetry run python main.py --reload` doesn't actually turn on reload, because `main.py` ignores command-line arguments. I'll point this out rather than change it.

## Files
Modified: `main.py`, `pyproject.toml`, `poetry.lock`, `requirements.txt`, `README.md`, `PROMPTS.md`. New: `plans/02_gemini_endpoints.md`.

## Verification
- **Live calls.** Start the app with `GOOGLE_CLOUD_PROJECT=oe-2-514017 poetry run python main.py` (the project from your gcloud config) and curl `/haiku` and `/fortune`. Expect complete text. This makes two small, real Vertex AI calls.
- **Missing project.** Start without `GOOGLE_CLOUD_PROJECT`. `/haiku` should return 500 with the config error, and `/hello` should still work.
- **Bad model.** Use `GEMINI_MODEL=does-not-exist`. `/fortune` should return 502 with a JSON error, and the server shouldn't crash.
- **Exports.** `requirements.txt` includes `google-genai`.
- **Secrets.** `grep` shows no keys or secrets in the repo.
