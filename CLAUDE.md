# Project rules

## Prompt log
- Keep a `PROMPTS.md` file at the root of the project. Create it if it doesn't exist.
- Before you start on any prompt I give you, log it as a time-stamped entry in `PROMPTS.md`.

## Plans
- When I approve a plan, save a copy of it in a `plans/` folder at the root of the project, numbered in order (for example, `plans/01_hello_goodbye.md`).

## Git
- Never commit to `main`. Before you change any code, create a new branch, or confirm we're already on one that isn't `main`.
- Don't commit, push, merge, or open pull requests. I'll do those myself.
- Use underscores, not hyphens, in names you choose (files, folders, branches).

## Project
- Python, managed with Poetry.
- Keep a `README.md` that explains how to install and run the app. Update it whenever the app changes.
- Don't add packages we don't need.
- Never put API keys, passwords, or other secrets in the code or in any file that gets committed.