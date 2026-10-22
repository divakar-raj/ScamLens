import pytest
from detector import analyze

# 1. Expand the dataset with diverse, real-world examples
TEST_MESSAGES = [
    # --- TRUE POSITIVES (Should be HIGH risk) ---
    {
        "text": "Dear customer, your electricity power will be disconnected tonight at 9:30 PM from update office. Call 9876543210 immediately.",
        "expected_level": "High",
        "category": "Fake Urgency/Utility Scam"
    },
    {
        "text": "TRAI ALERT: Your mobile number will be blocked within 24 hrs due to illegal activity. Click here to complete KYC: http://trai-kyc-update.com",
        "expected_level": "High",
        "category": "Authority Impersonation"
    },
    {
        "text": "ஐயா, உங்கள் வங்கி கணக்கு முடக்கப்பட்டுள்ளது. மீண்டும் தொடங்க உங்கள் பான் கார்டு எண்ணை அனுப்பவும்.", # Tamil: Bank account locked, send PAN
        "expected_level": "High",
        "category": "Tamil Regional Scam"
    },
    {
        "text": "Bhaiya, aapka 50,000 ka lottery laga hai. Tax pay karne ke liye Google Pay par 2000 bhejein.", # Hinglish: Lottery tax fee
        "expected_level": "High",
        "category": "Hinglish Advance Fee Fraud"
    },
    
    # --- TRUE NEGATIVES (Should be LOW risk - Precision Test) ---
    {
        "text": "Your Amazon package OTP is 4920. DO NOT SHARE THIS WITH ANYONE. Amazon will never call you to ask for this code.",
        "expected_level": "Low",
        "category": "Genuine OTP with safety warning" # This tests if your engine ignores standard "do not share" warnings
    },
    {
        "text": "Reminder: Your Jio mobile plan expires in 3 days. Recharge now via the MyJio app.",
        "expected_level": "Low",
        "category": "Genuine utility reminder"
    },
    {
        "text": "Hi Divakar, are we still meeting at 10 AM for the hackathon?",
        "expected_level": "Low",
        "category": "Normal human conversation"
    }
]

# 2. Pytest loop to run all cases
@pytest.mark.parametrize("case", TEST_MESSAGES)
def test_detection_precision(case):
    result = analyze(case["text"])
    
    # Assert that the engine's output matches the expected reality
    assert result["level"] == case["expected_level"], f"Failed {case['category']}: Expected {case['expected_level']} but got {result['level']}"