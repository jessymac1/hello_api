# Plan: Public /ask endpoint backed by Gemini

## Context
You want a public `GET /ask?q=...` endpoint that sends the user's question to Gemini and returns the answer. Because it's public and every call costs money, it has to:
- reject bad input before spending anything,
- cap the answer at about 200 output tokens,
- tell the model to answer in three sentences or fewer.

The working tree is currently on `main`, which only has `CLAUDE.md`. The Gemini code is committed on `add_gemini_endpoints` (00c1161, pushed). The new work builds on that branch.

## Steps
1. **Branch.** `git checkout add_gemini_endpoints`, then `git checkout -b add_ask_endpoint`. Never `main`.
2. **Log the prompt** in `PROMPTS.md`, which exists on that branch, with a timestamp.
3. **Save the plan** as `plans/03_ask_endpoint.md`.
4. **[main.py](main.py)**:
   - **Generalize `ask_gemini`** to `ask_gemini(prompt, max_output_tokens=100, system_instruction=None)` and pass both into `GenerateContentConfig`. It keeps the same client (`get_client()`), model, minimal-thinking setting, and error mapping, so `/haiku` and `/fortune` behave exactly as before.
   - **New constants:**
     - `ASK_MAX_QUESTION_CHARS = 200`
     - `ASK_MAX_OUTPUT_TOKENS = 200`
     - `ASK_SYSTEM_INSTRUCTION`: "Answer the user's question in three sentences or fewer. Be concise and plain."
   - **`GET /ask` with `q: str | None = None`.** It checks `q` itself rather than relying on FastAPI's built-in check. That check returns a 422 with a verbose `detail` array, and the other endpoints use the simpler `{"error": ...}` format. The input is stripped of whitespace first, so a question of only spaces counts as empty.

     | Input | Response |
     |---|---|
     | Missing or empty `q` | 400, `{"error": "Query parameter 'q' is required and cannot be empty"}` |
     | Longer than 200 characters | 400, `{"error": "Query parameter 'q' must be 200 characters or fewer"}` |
     | Valid | `ask_gemini(q, max_output_tokens=200, system_instruction=ASK_SYSTEM_INSTRUCTION)`, then `{"question": q, "answer": "..."}` |

     Gemini failures reuse the existing 500/502/503 JSON errors.
   - **Handler.** Raise a small `HTTPException`-style error. The simplest way is to reuse the existing `GeminiError` handler, renamed to a general `ApiError` so 400s don't read as Gemini errors. The JSON shape stays the same.
5. **README.md.** Add:
   - `/ask` to the endpoint table, with a curl example (`curl "http://localhost:8080/ask?q=What+is+DevOps"`)
   - the 400 rows in the errors table
   - a short "Cost and abuse" note covering the limits

   I'll leave your existing README content as it is.

## Not included (worth considering before going public)
The input limits and the token cap only bound the cost of each call. They don't limit how many calls come in. Before going live, consider:
- setting `--max-instances` on the Cloud Run service
- a budget alert in Google Cloud billing
- later, rate limiting or auth

These need no code or new packages, and I'll mention them in the README. Also note that the system instruction makes short answers very likely, but it can't fully stop someone from steering the model. The 200-token cap is the hard limit.

## Files
Modified: `main.py`, `README.md`, `PROMPTS.md`. New: `plans/03_ask_endpoint.md`. No new packages, so `requirements.txt` stays the same.

## Verification
Run with `GOOGLE_CLOUD_PROJECT=oe-2-514017` and curl:
- `/ask?q=What+is+DevOps` returns 200 with a short answer of three sentences or fewer
- `/ask` (no `q`), `/ask?q=`, and `/ask?q=%20%20` each return 400 with the empty error
- `/ask?q=` with 201 characters returns 400 with the length error and makes no Gemini call
- `/ask?q=` with exactly 200 characters returns 200
- `/haiku` and `/fortune` still return 200 (regression check)
- Bad model name: `/ask?q=hi` returns 502 JSON
