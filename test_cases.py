"""test_cases.py - sample messages and expected outcomes. Run: pytest"""
from detector import analyze

SAMPLES = [
    {"name": "Bank OTP scam (English)",
     "text": "Dear customer, your bank account will be blocked within 24 hours. "
             "Share the OTP sent to your phone to verify your account immediately.",
     "expected": "High"},
    {"name": "Lottery prize scam (English)",
     "text": "Congratulations! You have won a prize. Click here https://bit.ly/claim123 "
             "and pay a small processing fee to claim your reward.",
     "expected": "High"},
    {"name": "Bank OTP scam (Hindi)",
     "text": "आपका बैंक खाता 24 घंटे में बंद हो जाएगा। तुरंत अपना ओटीपी बताएं।",
     "expected": "High"},
    {"name": "Bank OTP scam (Tamil)",
     "text": "உங்கள் வங்கி கணக்கு 24 மணி நேரத்தில் முடக்கப்படும். உடனடியாக உங்கள் ஓடிபி அனுப்புங்கள்.",
     "expected": "High"},
    {"name": "Bank scam (Hinglish)",
     "text": "Aapka bank account band ho jayega. Turant OTP bhejiye warna khata block.",
     "expected": "High"},
    {"name": "Bank scam (Tanglish)",
     "text": "Ungal bank account udane mudakkapadum. OTP anuppunga, link click pannunga https://sbi-kyc.xyz/update",
     "expected": "High"},
    {"name": "Fake bank link (English)",
     "text": "SBI alert: update KYC now at http://sbi-secure-login.xyz/verify",
     "expected": "High"},
    {"name": "Genuine OTP notice",
     "text": "123456 is your OTP for login. Do not share it with anyone.",
     "expected": "Low"},
    {"name": "Legitimate delivery update",
     "text": "Hi, your order #4521 has been shipped and will arrive on Friday. Thanks for shopping with us.",
     "expected": "Low"},
    {"name": "Friend chatting",
     "text": "Hey, are we still meeting for lunch tomorrow at 1?",
     "expected": "Low"},
    {"name": "Friend chatting (Tamil)",
     "text": "நாளை மதியம் சாப்பிட சந்திக்கலாமா?",
     "expected": "Low"},
]


def test_expected_levels():
    for s in SAMPLES:
        assert analyze(s["text"])["level"] == s["expected"], s["name"]


def test_language_detection():
    assert analyze(SAMPLES[2]["text"])["language"] == "Hindi"
    assert analyze(SAMPLES[3]["text"])["language"] == "Tamil"
    assert analyze(SAMPLES[4]["text"])["language"] == "Hinglish"
    assert analyze(SAMPLES[5]["text"])["language"] == "Tanglish"
