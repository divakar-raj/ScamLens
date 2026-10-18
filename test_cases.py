"""test_cases.py - sample messages and expected outcomes. Run: pytest"""
from detector import analyze

SAMPLES = [
    {
        "name": "Bank OTP scam",
        "text": "Dear customer, your bank account will be blocked within 24 hours. "
                "Share the OTP sent to your phone to verify your account immediately.",
        "expected": "High",
    },
    {
        "name": "Lottery prize scam",
        "text": "Congratulations! You have won a prize. Click here https://bit.ly/claim123 "
                "and pay a small processing fee to claim your reward.",
        "expected": "High",
    },
    {
        "name": "Legitimate delivery update",
        "text": "Hi, your order #4521 has been shipped and will arrive on Friday. Thanks for shopping with us.",
        "expected": "Low",
    },
    {
        "name": "Friend chatting",
        "text": "Hey, are we still meeting for lunch tomorrow at 1?",
        "expected": "Low",
    },
]


def test_expected_levels():
    for s in SAMPLES:
        assert analyze(s["text"])["level"] == s["expected"], s["name"]
