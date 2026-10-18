"""detector.py - rule-based scam detection (v1).

Design: analyze(text) takes ANY text and returns a list of findings.
Each finding = rule name, evidence found, severity, and why it matters.
To adapt to a new problem statement, change the RULES list (or the input
type) - the rest of the app keeps working.
"""
import re

# Each rule: name, regex patterns, severity (1-3), explanation
RULES = [
    {
        "name": "Urgency or threats",
        "patterns": [
            r"act now", r"immediately", r"within \d+ (hours?|minutes?)",
            r"urgent", r"last warning", r"account (will be )?(blocked|suspended|closed)",
            r"expires? (today|soon)",
        ],
        "severity": 2,
        "why": "Scammers rush you so you don't stop to think or verify.",
    },
    {
        "name": "Request for sensitive data",
        "patterns": [
            r"\botp\b", r"one[- ]time password", r"\bpin\b", r"\bcvv\b",
            r"password", r"card number", r"aadhaar", r"verify your (account|identity|details)",
        ],
        "severity": 3,
        "why": "Real banks and companies never ask for OTPs, PINs or passwords by message.",
    },
    {
        "name": "Payment pressure",
        "patterns": [
            r"pay (a )?(fee|fine|charge)", r"processing fee", r"gift cards?",
            r"transfer (the )?(money|amount)", r"upi", r"crypto", r"wire transfer",
        ],
        "severity": 3,
        "why": "Being pushed to pay or transfer money quickly is a classic fraud sign.",
    },
    {
        "name": "Suspicious link",
        "patterns": [
            r"https?://\S+", r"\bbit\.ly/\S+", r"\btinyurl\.com/\S+",
            r"click (here|the link|below)",
        ],
        "severity": 2,
        "why": "Links in unexpected messages can lead to fake sites that steal your data.",
    },
    {
        "name": "Too-good-to-be-true offer",
        "patterns": [
            r"you(('ve| have) )?won", r"lottery", r"prize", r"free (gift|iphone|money)",
            r"guaranteed (returns?|profit)", r"claim your",
        ],
        "severity": 2,
        "why": "Unexpected rewards are used as bait to collect your details or money.",
    },
    {
        "name": "Impersonation of an authority",
        "patterns": [
            r"\b(bank|rbi|income tax|customs|police|cbi|courier)\b",
            r"official (team|department)", r"customer care",
        ],
        "severity": 1,
        "why": "Scammers pretend to be banks or government bodies to seem trustworthy.",
    },
]


def analyze(text: str) -> dict:
    """Return findings, a 0-100 risk score, and a risk level."""
    findings = []
    for rule in RULES:
        matches = []
        for pattern in rule["patterns"]:
            for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                matches.append({"text": m.group(0), "start": m.start(), "end": m.end()})
        if matches:
            findings.append({
                "rule": rule["name"],
                "severity": rule["severity"],
                "why": rule["why"],
                "evidence": matches,
            })

    # Simple, explainable score: sum of severities for the rules that fired
    max_score = sum(r["severity"] for r in RULES)
    raw = sum(f["severity"] for f in findings)
    score = round(100 * raw / max_score * 1.6)  # boosted so 3-4 rules is clearly high
    score = min(score, 100)

    if score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"

    return {"score": score, "level": level, "findings": findings}
