"""explainer.py - plain-language explanations in the user's language (Groq).

AI mode if GROQ_API_KEY works, otherwise a template (in English, Hindi or Tamil).
The demo NEVER breaks because of the AI.
"""
import os
from i18n import AI_LANG, FALLBACK, LEVELS, RULE_NAMES, text_lang

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MODEL_CANDIDATES = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]


def _ask_llm(prompt: str):
    """Return model text, or None if anything fails."""
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=key, timeout=15)
    except Exception:
        return None
    models = [m for m in [os.environ.get("LLM_MODEL")] if m] + MODEL_CANDIDATES
    for model in models:
        try:
            reply = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": prompt}], max_tokens=700)
            content = (reply.choices[0].message.content or "").strip()
            if content:
                return content
        except Exception:
            continue
    return None


def _fallback(result: dict, language: str) -> str:
    tl = text_lang(language)
    if tl == "English":
        if not result["findings"]:
            return "No common scam signs were found in this message, but stay careful with unexpected requests."
        names = ", ".join(f["rule"].lower() for f in result["findings"])
        top = max(result["findings"], key=lambda f: f["severity"])
        return (f"This message is rated **{result['level']} risk**. It shows these warning signs: {names}. "
                f"The most serious one: {top['why']}")
    if not result["findings"]:
        return FALLBACK[tl]["none"]
    names = ", ".join(RULE_NAMES[tl].get(f["rule"], f["rule"]) for f in result["findings"])
    return FALLBACK[tl]["some"].format(level=LEVELS[tl][result["level"]], names=names)


def explain(text: str, result: dict, language: str = "English") -> tuple:
    """Return (explanation, source) where source is 'AI' or 'template'."""
    if not result["findings"]:
        return _fallback(result, language), "template"
    signs = "\n".join(f"- {f['rule']}: {', '.join(e['text'] for e in f['evidence'])}" for f in result["findings"])
    prompt = (
        f"Explain in 3 short sentences, in {AI_LANG.get(language, 'simple English')}, why this message may be a scam. "
        "Use ONLY the warning signs listed. Do not claim certainty; say 'may' or 'likely'.\n\n"
        f"Message:\n{text}\n\nWarning signs found:\n{signs}"
    )
    out = _ask_llm(prompt)
    return (out, "AI") if out else (_fallback(result, language), "template")


def explain_logs(incidents: list, language: str = "English") -> tuple:
    """Short incident-report summary for the log analysis tab."""
    if not incidents:
        return "No suspicious activity was found in these logs.", "template"
    lines = "\n".join(
        f"- {i['type']} from {i['ip']} (severity {i['severity']}/3): {i['evidence']}" for i in incidents[:8])
    prompt = (
        f"You are a security assistant for a small organisation. In {AI_LANG.get(language, 'simple English')}, "
        "write a 4-sentence incident summary for a non-expert, then name the single most urgent action. "
        f"Use ONLY these detected incidents:\n{lines}"
    )
    out = _ask_llm(prompt)
    if out:
        return out, "AI"
    top = incidents[0]
    return (f"{len(incidents)} suspicious activities were found. The most serious is **{top['type']}** from "
            f"{top['ip']}: {top['evidence']}. Recommended action: {top['action']}"), "template"
