"""Check the LLM connection outside Cognee, for whichever provider is in .env.

Makes one tiny call through LiteLLM (the same library Cognee uses) and times it.
Prints only the model name, the reply and the time, never the key.

Run:  uv run python backend/check_llm.py
"""
import os
import time

import litellm
from dotenv import load_dotenv

load_dotenv()
model = os.environ["LLM_MODEL"]  # e.g. anthropic/claude-haiku-5-5
key = os.environ["LLM_API_KEY"]

print("Model:", model)
start = time.time()
try:
    resp = litellm.completion(model=model, api_key=key, timeout=120, max_tokens=20,
                              messages=[{"role": "user", "content": 'Reply with the word "test".'}])
    print(f"Reply: {resp.choices[0].message.content!r} in {time.time() - start:.1f}s")
except Exception as e:
    print(f"FAILED after {time.time() - start:.1f}s: {type(e).__name__}: {str(e)[:400]}")
