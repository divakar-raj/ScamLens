"""explainer.py - turns findings into a plain-language explanation (Groq).

Two modes:
  1. AI mode  - if GROQ_API_KEY is set in .env and the call works.
  2. Fallback - a simple template (no key, no internet, or API error).
The demo NEVER breaks because of the AI.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Tried in order until one works. Check console.groq.com/docs/models for current names.
MODEL_CANDIDATES = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
]


def _fallback(result: dict) -> str:
    if not result["findings"]:
        return "No common scam signs were found in this message, but stay careful with unexpected requests."
    names = ", ".join(f["rule"].lower() for f in result["findings"])
    top = max(result["findings"], key=lambda f: f["severity"])
    return (
        f"This message is rated **{result['level']} risk**. It shows these warning signs: {names}. "
        f"The most serious one: {top['why']}"
    )


def explain(text: str, result: dict) -> tuple[str, str]:
    """Return (explanation, source) where source is 'AI' or 'template'."""
    key = os.environ.get("API_KEY")
    if not key or not result["findings"]:
        return _fallback(result), "template"

    signs = "\n".join(
        f"- {f['rule']}: {', '.join(e['text'] for e in f['evidence'])}" for f in result["findings"]
    )
    prompt = (
        "Explain in 3 short, simple sentences why this message may be a scam. "
        "Use ONLY the warning signs listed. Do not claim certainty; say 'may' or 'likely'.\n\n"
        f"Message:\n{text}\n\nWarning signs found:\n{signs}"
    )

    models = [m for m in [os.environ.get("LLM_MODEL")] if m] + MODEL_CANDIDATES
    try:
        from groq import Groq
        client = Groq(api_key=key, timeout=15)
    except Exception:
        return _fallback(result), "template"

    for model in models:
        try:
            reply = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
            )
            content = (reply.choices[0].message.content or "").strip()
            if content:
                return content, "AI"
        except Exception:
            continue  # try the next model
    return _fallback(result), "template"