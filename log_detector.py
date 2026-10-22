import re
from urllib.parse import unquote_plus
import pandas as pd
from sklearn.ensemble import IsolationForest

SQLI = re.compile(r"(?:\bor\b|\band\b)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+|union\s+select|drop\s+table|sleep\(\d+\)|'\s*(?:--|#)", re.I)
XSS = re.compile(r"<script|javascript:|onerror\s*=", re.I)
TRAVERSAL = re.compile(r"\.\./|/etc/passwd|\\windows\\system32", re.I)

INFO = {
    "Brute-force login attack": ("Many failed logins in a short time suggest password guessing.",
                                 "Block this IP, force a password reset for the targeted account, and enable 2-step login."),
    "SQL injection attempt": ("Attackers insert database commands into web requests to steal or change data.",
                              "Block this IP and make sure the application uses parameterised queries."),
    "Cross-site scripting (XSS) attempt": ("Malicious scripts in requests can run in other users' browsers.",
                                           "Block this IP and sanitise or escape user input."),
    "Path traversal attempt": ("Requests like ../ try to read files outside the web folder.",
                               "Block this IP and restrict file access on the server."),
    "Scanning for hidden pages": ("Many requests for pages that do not exist suggest an attacker mapping your site.",
                                  "Rate-limit or block this IP and review exposed admin pages."),
    "Request flood": ("A very high request rate can be a denial-of-service attempt.",
                      "Enable rate limiting and block this IP if it continues."),
    "Unusual-hour login": ("A successful login at night can mean a stolen account.",
                           "Confirm with the user that this login was theirs."),
    "Statistical anomaly": ("This source behaves very differently from the rest of the traffic (machine-learning check).",
                            "Review this IP's activity manually."),
}
SEVERITY = {"Brute-force login attack": 2, "SQL injection attempt": 3, "Cross-site scripting (XSS) attempt": 3,
            "Path traversal attempt": 3, "Scanning for hidden pages": 2, "Request flood": 2,
            "Unusual-hour login": 1, "Statistical anomaly": 1}


def _max_window(times, seconds):
    """Largest number of events inside any window of `seconds`; returns (count, start, end)."""
    t = list(times)
    best = (0, None, None)
    j = 0
    for i in range(len(t)):
        while (t[i] - t[j]).total_seconds() > seconds:
            j += 1
        if i - j + 1 > best[0]:
            best = (i - j + 1, t[j], t[i])
    return best


def _incident(kind, ip, count, first, last, evidence, severity=None):
    why, action = INFO[kind]
    return {"type": kind, "severity": severity or SEVERITY[kind], "ip": ip, "count": count,
            "first_seen": first, "last_seen": last, "evidence": evidence, "why": why, "action": action}


def analyze_logs(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for col in ("user", "url", "status"):
        if col not in df.columns:
            df[col] = ""
    df["status"] = pd.to_numeric(df["status"], errors="coerce").fillna(0).astype(int)
    df = df.sort_values("timestamp").reset_index(drop=True)
    incidents = []

    for ip, g in df[df.event == "login_failed"].groupby("ip"):
        count, start, end = _max_window(g.timestamp, 300)
        if count >= 5:
            users = ", ".join(sorted(set(g.user.astype(str))))
            later_ok = df[(df.ip == ip) & (df.event == "login_success") & (df.timestamp >= start)]
            note = " A successful login followed, so the account may be compromised." if len(later_ok) else ""
            incidents.append(_incident("Brute-force login attack", ip, count, start, end,
                                       f"{count} failed logins within 5 minutes (accounts tried: {users}).{note}",
                                       3 if len(later_ok) else 2))

    reqs = df[df.event == "http_request"].copy()
    reqs["decoded"] = reqs.url.astype(str).map(unquote_plus)
    for kind, pattern in (("SQL injection attempt", SQLI), ("Cross-site scripting (XSS) attempt", XSS),
                          ("Path traversal attempt", TRAVERSAL)):
        hit = reqs[reqs.decoded.str.contains(pattern)]
        for ip, g in hit.groupby("ip"):
            incidents.append(_incident(kind, ip, len(g), g.timestamp.min(), g.timestamp.max(),
                                       f"{len(g)} malicious request(s), e.g. {g.decoded.iloc[0][:70]}"))

    for ip, g in reqs.groupby("ip"):
        missing = g[g.status == 404]
        if missing.url.nunique() >= 10:
            incidents.append(_incident("Scanning for hidden pages", ip, missing.url.nunique(),
                                       missing.timestamp.min(), missing.timestamp.max(),
                                       f"{missing.url.nunique()} different non-existent pages requested"))
        count, start, end = _max_window(g.timestamp, 60)
        if count >= 100:
            incidents.append(_incident("Request flood", ip, count, start, end, f"{count} requests within 60 seconds"))

    night = df[(df.event == "login_success") & (df.timestamp.dt.hour < 5)]
    for (ip, user), g in night.groupby(["ip", "user"]):
        incidents.append(_incident("Unusual-hour login", ip, len(g), g.timestamp.min(), g.timestamp.max(),
                                   f"Successful login by '{user}' at {g.timestamp.min():%H:%M}"))

    flagged = {i["ip"] for i in incidents}
    feats = df.groupby("ip").agg(
        events=("event", "size"),
        fails=("event", lambda s: (s == "login_failed").sum()),
        urls=("url", "nunique"),
        not_found=("status", lambda s: (s == 404).sum()),
        users=("user", "nunique"),
    )
    if len(feats) >= 10:
        model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
        feats["flag"] = model.fit_predict(feats) == -1
        for ip, row in feats[feats.flag].iterrows():
            if ip not in flagged:
                g = df[df.ip == ip]
                incidents.append(_incident("Statistical anomaly", ip, int(row.events), g.timestamp.min(), g.timestamp.max(),
                                           f"{int(row.events)} events, {int(row.urls)} distinct URLs, {int(row.fails)} failed logins"))

    incidents.sort(key=lambda i: (-i["severity"], -i["count"]))
    return {"incidents": incidents, "events": len(df), "ips": int(df.ip.nunique())}
