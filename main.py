import logging
import os
from functools import lru_cache

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google import genai
from google.auth.exceptions import DefaultCredentialsError
from google.genai import errors, types

logger = logging.getLogger("hello_api")

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
MAX_OUTPUT_TOKENS = 100

HAIKU_PROMPT = "Write a short haiku about DevOps. Reply with only the haiku."
FORTUNE_PROMPT = (
    "Write a one-sentence, software-themed fortune-cookie message. "
    "Reply with only the fortune."
)

ASK_MAX_QUESTION_CHARS = 200
ASK_MAX_OUTPUT_TOKENS = 200
ASK_SYSTEM_INSTRUCTION = (
    "Answer the user's question in three sentences or fewer. Be concise and plain."
)

app = FastAPI()


class ApiError(Exception):
    """An error that maps to a clean JSON response: {"error": message}."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


@app.exception_handler(ApiError)
def handle_api_error(request, exc: ApiError):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    """Create the Vertex AI client on first use, using Application Default Credentials."""
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise ApiError(
            500, "Gemini is not configured: GOOGLE_CLOUD_PROJECT is not set"
        )
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    return genai.Client(vertexai=True, project=project, location=location)


def ask_gemini(
    prompt: str,
    max_output_tokens: int = MAX_OUTPUT_TOKENS,
    system_instruction: str | None = None,
) -> str:
    try:
        response = get_client().models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_output_tokens,
                system_instruction=system_instruction,
                # Keep thinking minimal so it doesn't use up the output token budget.
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                ),
            ),
        )
    except ApiError:
        raise
    except DefaultCredentialsError:
        logger.exception("No Application Default Credentials found")
        raise ApiError(500, "Gemini credentials are not available")
    except errors.APIError as exc:
        logger.error("Gemini API error %s: %s", exc.code, exc.message)
        if exc.code == 429:
            raise ApiError(503, "Gemini is busy right now, try again later")
        raise ApiError(502, "Gemini request failed")
    except Exception:
        logger.exception("Unexpected error calling Gemini")
        raise ApiError(502, "Gemini request failed")

    text = (response.text or "").strip()
    if not text:
        logger.error("Gemini returned an empty response: %s", response)
        raise ApiError(502, "Gemini request failed")
    return text


@app.get("/hello")
def hello():
    return {"message": "Hey there! 👋 How's it going?"}


@app.get("/goodbye")
def goodbye():
    return {"message": "Catch you later! Take it easy. ✌️"}


@app.get("/haiku")
def haiku():
    return {"haiku": ask_gemini(HAIKU_PROMPT)}


@app.get("/fortune")
def fortune():
    return {"fortune": ask_gemini(FORTUNE_PROMPT)}



@app.get("/ask")
def ask(q: str | None = None):
    question = (q or "").strip()
    if not question:
        raise ApiError(400, "Query parameter 'q' is required and cannot be empty")
    if len(question) > ASK_MAX_QUESTION_CHARS:
        raise ApiError(
            400,
            f"Query parameter 'q' must be {ASK_MAX_QUESTION_CHARS} characters or fewer",
        )
    answer = ask_gemini(
        question,
        max_output_tokens=ASK_MAX_OUTPUT_TOKENS,
        system_instruction=ASK_SYSTEM_INSTRUCTION,
    )
    return {"question": question, "answer": answer}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
