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

app = FastAPI()


class GeminiError(Exception):
    """A Gemini failure that maps to a clean JSON error response."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


@app.exception_handler(GeminiError)
def handle_gemini_error(request, exc: GeminiError):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    """Create the Vertex AI client on first use, using Application Default Credentials."""
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise GeminiError(
            500, "Gemini is not configured: GOOGLE_CLOUD_PROJECT is not set"
        )
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    return genai.Client(vertexai=True, project=project, location=location)


def ask_gemini(prompt: str) -> str:
    try:
        response = get_client().models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=MAX_OUTPUT_TOKENS,
                # Keep thinking minimal so it doesn't use up the output token budget.
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                ),
            ),
        )
    except GeminiError:
        raise
    except DefaultCredentialsError:
        logger.exception("No Application Default Credentials found")
        raise GeminiError(500, "Gemini credentials are not available")
    except errors.APIError as exc:
        logger.error("Gemini API error %s: %s", exc.code, exc.message)
        if exc.code == 429:
            raise GeminiError(503, "Gemini is busy right now, try again later")
        raise GeminiError(502, "Gemini request failed")
    except Exception:
        logger.exception("Unexpected error calling Gemini")
        raise GeminiError(502, "Gemini request failed")

    text = (response.text or "").strip()
    if not text:
        logger.error("Gemini returned an empty response: %s", response)
        raise GeminiError(502, "Gemini request failed")
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
