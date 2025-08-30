# server/groq_client.py
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

def _groq_sdk_available():
    try:
        from groq import Groq  # noqa: F401
        return True
    except Exception:
        return False

def query_groq(prompt: str, model: str = None) -> str:
    """
    Query Groq for short answers. Tries to use the groq SDK if installed,
    otherwise raises a clear error. Keep prompt concise.
    """
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set in environment (.env).")

    model = model or GROQ_MODEL

    # Prefer SDK if available
    if _groq_sdk_available():
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a concise assistant helping with game battle analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=512
        )
        return resp.choices[0].message.content

    # If SDK unavailable, use requests to Groq-compatible endpoint (fallback)
    import requests
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a concise assistant helping with game battle analysis."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6,
        "max_tokens": 512
    }
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"Groq API error {r.status_code}: {r.text}")
    j = r.json()
    return j["choices"][0]["message"]["content"]
