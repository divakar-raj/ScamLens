import re

RULES = [
    {
        "name": "Urgency or Threats",
        "patterns": [
            r'disconnected tonight', r'blocked within', r'immediately', 
            r'illegal activity', r'urgent', r'24 hrs', r'முடக்கப்பட்டுள்ளது'
        ],
        "severity": 3,
        "explanation": "Creates artificial panic to force quick action."
    },
    {
        "name": "Impersonation of Authority",
        "patterns": [
            r'trai alert', r'update office', r'electricity power', 
            r'dear customer', r'ஐயா', r'வங்கி கணக்கு'
        ],
        "severity": 3,
        "explanation": "Pretends to be a trusted organization or authority."
    },
    {
        "name": "Payment Pressure",
        "patterns": [
            r'tax pay', r'google pay', r'bhejein', r'pay karne', 
            r'google pay par', r'பான் கார்டு'
        ],
        "severity": 3,
        "explanation": "Demands payment or sensitive KYC documents."
    },
    {
        "name": "Too Good To Be True",
        "patterns": [
            r'lottery laga', r'ka lottery', r'50,000', r'lakh', r'prize'
        ],
        "severity": 3,
        "explanation": "Offers unrealistic rewards to lure victims."
    },
    {
        "name": "Suspicious Link / Contact",
        "patterns": [
            r'call \d{10}', r'call 987', r'http[s]?://', r'click here'
        ],
        "severity": 2,
        "explanation": "Directs you to an unofficial link or number."
    }
]

def analyze(text):
    text_lower = text.lower()
    score = 0
    findings = []
    
    # Check for genuine OTPs or standard warnings to prevent false positives
    if "otp is" in text_lower and "do not share" in text_lower:
        return {"score": 10, "level": "Low", "findings": [], "language": "Auto"}
    if "recharge now" in text_lower and "expires in" in text_lower:
        return {"score": 10, "level": "Low", "findings": [], "language": "Auto"}
    
    for rule in RULES:
        rule_evidence = []
        for pattern in rule["patterns"]:
            # Find exactly where the words are for the UI highlighter
            for match in re.finditer(pattern, text_lower):
                rule_evidence.append({
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end()
                })
        
        if rule_evidence:
            score += rule["severity"] * 25  
            findings.append({
                "rule": rule["name"], 
                "why": rule["explanation"],
                "severity": rule["severity"],
                "evidence": rule_evidence
            })
                
    score = min(score, 100)
    
    if score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"
        
    return {
        "score": score,
        "level": level,
        "findings": findings,
        "language": "Auto"
    }