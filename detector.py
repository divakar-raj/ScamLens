"""detector.py - multilingual, rule-based scam detection.

Languages: English, Hindi (Devanagari), Tamil (Tamil script), plus romanised
Hinglish / Tanglish keywords. analyze(text) returns findings with evidence.
NOTE: Hindi/Tamil/romanised keywords should be reviewed by native speakers.
"""
import re
from url_check import url_findings

DEVANAGARI = re.compile(r"[\u0900-\u097F]")
TAMIL = re.compile(r"[\u0B80-\u0BFF]")
HINGLISH = re.compile(r"\b(aapka|aapke|apka|turant|kijiye|bhejiye|bhejo|jayega|khata|inaam|paisa)\b", re.I)
TANGLISH = re.compile(r"\b(anuppunga|anupunga|pannunga|panunga|ungal|ungalukku|udane|udanae|parisu|panam|kudunga|mudakk\w*)\b", re.I)

SAFE_CONTEXT = re.compile(
    r"(do not|don't|never)\s+share|न\s*बताएं|साझा\s*न\s*करें|किसी\s*को\s*न\s*दें|பகிர\s*வேண்டாம்",
    re.I,
)

RULES = [
    {
        "name": "Urgency or threats",
        "patterns": [
            r"act now", r"immediately", r"within \d+ (hours?|minutes?)", r"urgent", r"last warning",
            r"account (will be )?(blocked|suspended|closed)", r"expires? (today|soon)",
            r"तुरंत", r"जल्द से जल्द", r"\d+\s*घंटे", r"बंद हो जाएगा", r"ब्लॉक",
            r"உடனடியாக", r"அவசரம்", r"மணி நேரத்தில்", r"முடக்க", r"தடை செய்ய",
            r"\bturant\b", r"\bjaldi\b", r"(band|block) ho jayega", r"\budane\b", r"\budanae\b",
            r"mudakk\w*",
        ],
        "severity": 2,
        "why": "Scammers rush you so you don't stop to think or verify.",
    },
    {
        "name": "Request for sensitive data",
        "patterns": [
            r"\botp\b", r"one[- ]time password", r"\bpin\b", r"\bcvv\b", r"password", r"card number",
            r"aadhaar", r"verify your (account|identity|details)",
            r"ओटीपी", r"पासवर्ड", r"पिन नंबर", r"कार्ड नंबर", r"आधार", r"केवाईसी",
            r"ஓடிபி", r"கடவுச்சொல்", r"பின் எண்", r"கார்டு எண்", r"ஆதார்", r"கேஒய்சி",
            r"\bkyc\b", r"otp (bhejiye|bhejo|batao|share)", r"otp (anuppunga|anupunga|kudunga)",
        ],
        "severity": 3,
        "why": "Real banks and companies never ask for OTPs, PINs or passwords by message.",
    },
    {
        "name": "Payment pressure",
        "patterns": [
            r"pay (a )?(fee|fine|charge)", r"processing fee", r"gift cards?",
            r"transfer (the )?(money|amount)", r"\bupi\b", r"crypto", r"wire transfer",
            r"शुल्क", r"पैसे भेज", r"भुगतान", r"यूपीआई",
            r"கட்டணம்", r"பணம் அனுப்ப", r"யுபிஐ",
            r"paisa bhej\w*", r"panam anuppu\w*",
        ],
        "severity": 3,
        "why": "Being pushed to pay or transfer money quickly is a classic fraud sign.",
    },
    {
        "name": "Suspicious link",
        "patterns": [
            r"https?://\S+", r"\bbit\.ly/\S+", r"\btinyurl\.com/\S+", r"click (here|the link|below)",
            r"यहाँ क्लिक", r"यहां क्लिक", r"लिंक पर क्लिक",
            r"கிளிக் செய்", r"லிங்க்",
            r"link (par )?click", r"link click pannunga",
        ],
        "severity": 2,
        "why": "Links in unexpected messages can lead to fake sites that steal your data.",
    },
    {
        "name": "Too-good-to-be-true offer",
        "patterns": [
            r"you(('ve| have) )?won", r"lottery", r"prize", r"free (gift|iphone|money)",
            r"guaranteed (returns?|profit)", r"claim your",
            r"इनाम", r"लॉटरी", r"मुफ्त", r"जीत",
            r"பரிசு", r"லாட்டரி", r"இலவசம்", r"வென்றுள்ளீர்கள்",
            r"\binaam\b", r"\bparisu\b",
        ],
        "severity": 2,
        "why": "Unexpected rewards are used as bait to collect your details or money.",
    },
    {
        "name": "Impersonation of an authority",
        "patterns": [
            r"\b(bank|rbi|income tax|customs|police|cbi|courier)\b", r"official (team|department)", r"customer care",
            r"बैंक", r"पुलिस", r"आयकर", r"कस्टमर केयर",
            r"வங்கி", r"போலீஸ்", r"வாடிக்கையாளர் சேவை",
        ],
        "severity": 1,
        "why": "Scammers pretend to be banks or government bodies to seem trustworthy.",
    },
]

URL_RULE_NAME = "Risky link pattern"
URL_RULE_SEVERITY = 3
MAX_SCORE = sum(r["severity"] for r in RULES) + URL_RULE_SEVERITY


def detect_language(text: str) -> str:
    """Script-based detection, plus keyword hints for romanised text."""
    dev = len(DEVANAGARI.findall(text))
    tam = len(TAMIL.findall(text))
    if dev or tam:
        return "Hindi" if dev >= tam else "Tamil"
    if HINGLISH.search(text):
        return "Hinglish"
    if TANGLISH.search(text):
        return "Tanglish"
    return "English"


def analyze(text: str) -> dict:
    findings = []
    for rule in RULES:
        matches = []
        for pattern in rule["patterns"]:
            for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                matches.append({"text": m.group(0), "start": m.start(), "end": m.end()})
        if matches:
            findings.append({
                "rule": rule["name"], "severity": rule["severity"],
                "why": rule["why"], "evidence": matches,
            })

    urls = url_findings(text)
    if urls:
        findings.append({
            "rule": URL_RULE_NAME, "severity": URL_RULE_SEVERITY,
            "why": "; ".join(sorted({r for u in urls for r in u["reasons"]})).capitalize() + ".",
            "evidence": [{"text": u["text"], "start": u["start"], "end": u["end"]} for u in urls],
        })

    if SAFE_CONTEXT.search(text) and [f["rule"] for f in findings] == ["Request for sensitive data"]:
        findings = []

    raw = sum(f["severity"] for f in findings)
    score = min(100, round(100 * raw / MAX_SCORE * 1.8))
    level = "High" if score >= 60 else "Medium" if score >= 30 else "Low"
    return {"score": score, "level": level, "findings": findings, "language": detect_language(text)}
