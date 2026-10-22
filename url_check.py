"""url_check.py - simple, explainable checks for risky links (no internet needed)."""
import re
from urllib.parse import urlparse

URL_RE = re.compile(r"(https?://[^\s<>\"']+|www\.[^\s<>\"']+)", re.I)

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "cutt.ly", "rb.gy", "is.gd", "ow.ly", "shorturl.at"}
RISKY_TLDS = {"xyz", "top", "click", "tk", "ml", "ga", "cf", "gq", "work", "zip", "icu", "buzz", "link", "rest"}
SECOND_LEVEL = {"co", "com", "org", "gov", "net", "ac", "edu"}

BRANDS = {
    "sbi": {"sbi.co.in", "onlinesbi.sbi", "sbi.bank.in"},
    "hdfc": {"hdfcbank.com", "hdfc.com"},
    "icici": {"icicibank.com"},
    "paytm": {"paytm.com"},
    "phonepe": {"phonepe.com"},
    "npci": {"npci.org.in"},
    "amazon": {"amazon.in", "amazon.com", "amazonaws.com"},
    "google": {"google.com", "google.co.in", "googleapis.com", "googleusercontent.com"},
    "paypal": {"paypal.com"},
}


def registered_domain(host: str) -> str:
    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in SECOND_LEVEL and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def url_findings(text: str) -> list:
    """Return risky URLs as [{'text','start','end','reasons':[...]}]."""
    out = []
    for m in URL_RE.finditer(text):
        raw = m.group(0).rstrip(".,);:!?")
        end = m.start() + len(raw)
        try:
            parsed = urlparse(raw if "://" in raw else "http://" + raw)
            host = (parsed.hostname or "").lower()
            netloc = parsed.netloc
        except ValueError:
            continue
        if not host:
            continue
        reg = registered_domain(host)
        reasons = []
        if reg in SHORTENERS:
            reasons.append("shortened link hides the real destination")
        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
            reasons.append("uses a raw IP address instead of a domain name")
        if "xn--" in host:
            reasons.append("uses look-alike (punycode) characters")
        if "@" in netloc:
            reasons.append("contains '@' to disguise the real site")
        if host.count(".") >= 4:
            reasons.append("has an unusually long chain of subdomains")
        if host.rsplit(".", 1)[-1] in RISKY_TLDS:
            reasons.append("uses a domain ending often abused by scammers")
        for brand, official in BRANDS.items():
            if brand in host and reg not in official:
                reasons.append(f"mentions '{brand}' but is not the official {brand} domain")
                break
        if reasons:
            out.append({"text": raw, "start": m.start(), "end": end, "reasons": reasons})
    return out
