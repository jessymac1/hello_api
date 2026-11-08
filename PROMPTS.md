# Prompt log

## 2026-11-07 16:45 UTC

Create a Python API using FastAPI and Poetry with two GET endpoints.
/hello responds with a casual hello message as JSON.
/goodbye responds with a casual goodbye message of your choice as JSON.

The app will later be deployed to Google Cloud Run from a GitHub repository,
so it must read its port from the PORT environment variable (default 8080),
and it needs a requirements.txt exported from Poetry.

This folder is already a Git repository. Follow the rules in CLAUDE.md.

## 2026-11-07 17:05 UTC

Add two more GET endpoints that call Google's Gemini model through Vertex AI,
using the google-genai Python SDK.
- /haiku returns a short haiku about DevOps, written by Gemini, as JSON.
- /fortune returns a one-sentence, software-themed fortune-cookie message,
  written by Gemini, as JSON.

Requirements:
- Create the client with genai.Client(vertexai=True, project=..., location=...).
  Authenticate with Application Default Credentials only: no API keys and no key files.
- Read these settings from environment variables: GOOGLE_CLOUD_PROJECT (required),
  GOOGLE_CLOUD_LOCATION (default "global"), and GEMINI_MODEL
  (default "gemini-3.1-flash-lite").
- The prompts are fixed in the code. These endpoints take no input from the user.
- Limit each response to about 100 output tokens.
- If the Gemini call fails, return a clear JSON error with a sensible status code
  instead of crashing.
- Update requirements.txt and the README.

## 2026-11-07 17:29 UTC

My google api call is returing a 500 error. What could I be missing?

## 2026-11-08 00:02 UTC

Add a GET endpoint /ask that takes a query parameter q, sends it to Gemini
using the same client and settings as /haiku and /fortune, and returns the
answer as JSON.

This endpoint will be public on the internet, and every call costs money, so:
- Reject q if it's missing, empty, or longer than 200 characters, with a 4xx
  status code and a clear JSON error message.
- Limit the answer to about 200 output tokens.
- Use a system instruction that tells the model to answer in three sentences
  or fewer.

Update the README. Follow the rules in CLAUDE.md.
