"""i18n.py - texts shown to the user in English, Hindi and Tamil.
Romanised languages (Hinglish/Tanglish) reuse English screen texts, while the AI
explanation is written in the matching romanised style.
NOTE: have a native speaker review these before the demo.
"""

UI_LANGS = ["Auto", "English", "Hindi", "Tamil"]

def text_lang(lang: str) -> str:
    return lang if lang in ("Hindi", "Tamil") else "English"

AI_LANG = {
    "English": "simple English",
    "Hindi": "simple Hindi in Devanagari script",
    "Tamil": "simple Tamil in Tamil script",
    "Hinglish": "Hinglish (Hindi written in English letters)",
    "Tanglish": "Tanglish (Tamil written in English letters)",
}

NEXT_STEPS = {
    "English": [
        "**Do not** share any OTP, PIN or password with anyone.",
        "**Do not** click links or reply to the message.",
        "Contact the organisation using the **official number or website**, not the one in the message.",
        "Block the sender.",
        "Report scams (India: cybercrime.gov.in or call 1930).",
    ],
    "Hindi": [
        "किसी के साथ भी OTP, PIN या पासवर्ड **साझा न करें**।",
        "संदेश में दिए लिंक पर **क्लिक न करें** और जवाब न दें।",
        "संस्था से उसके **आधिकारिक नंबर या वेबसाइट** पर ही संपर्क करें, संदेश वाले नंबर पर नहीं।",
        "भेजने वाले को ब्लॉक करें।",
        "शिकायत दर्ज करें: cybercrime.gov.in या 1930।",
    ],
    "Tamil": [
        "OTP, PIN அல்லது கடவுச்சொல்லை யாருடனும் **பகிர வேண்டாம்**.",
        "செய்தியில் உள்ள லிங்கை **கிளிக் செய்யவோ** பதிலளிக்கவோ வேண்டாம்.",
        "அந்த நிறுவனத்தின் **அதிகாரப்பூர்வ எண் அல்லது இணையதளம்** மூலமாக மட்டுமே தொடர்பு கொள்ளுங்கள்.",
        "அனுப்பியவரை பிளாக் செய்யுங்கள்.",
        "புகார் செய்ய: cybercrime.gov.in அல்லது 1930.",
    ],
}

TITLES = {
    "English": {"steps": "Do this now", "why": "Why it matters"},
    "Hindi": {"steps": "अभी यह करें", "why": "यह क्यों ज़रूरी है"},
    "Tamil": {"steps": "இப்போது இதைச் செய்யுங்கள்", "why": "ஏன் முக்கியம்"},
}

RULE_NAMES = {
    "Hindi": {
        "Urgency or threats": "जल्दबाज़ी या धमकी",
        "Request for sensitive data": "संवेदनशील जानकारी की मांग",
        "Payment pressure": "पैसे देने का दबाव",
        "Suspicious link": "संदिग्ध लिंक",
        "Risky link pattern": "जोखिम भरा लिंक",
        "Too-good-to-be-true offer": "लालच भरा इनाम या ऑफ़र",
        "Impersonation of an authority": "बैंक या अधिकारी बनकर संपर्क",
    },
    "Tamil": {
        "Urgency or threats": "அவசரம் அல்லது மிரட்டல்",
        "Request for sensitive data": "முக்கிய தகவல் கேட்பு",
        "Payment pressure": "பணம் செலுத்த அழுத்தம்",
        "Suspicious link": "சந்தேகத்திற்குரிய லிங்க்",
        "Risky link pattern": "ஆபத்தான லிங்க்",
        "Too-good-to-be-true offer": "நம்பமுடியாத பரிசு அல்லது சலுகை",
        "Impersonation of an authority": "வங்கி/அதிகாரி போல நடிப்பு",
    },
}

LEVELS = {
    "Hindi": {"Low": "कम", "Medium": "मध्यम", "High": "उच्च"},
    "Tamil": {"Low": "குறைவு", "Medium": "நடுத்தரம்", "High": "அதிகம்"},
}

FALLBACK = {
    "Hindi": {
        "none": "इस संदेश में आम स्कैम के संकेत नहीं मिले, फिर भी अनजान अनुरोधों से सावधान रहें।",
        "some": "इस संदेश का जोखिम स्तर **{level}** है। इसमें ये चेतावनी संकेत मिले: {names}। OTP, पासवर्ड या पैसे की मांग पर कभी जवाब न दें।",
    },
    "Tamil": {
        "none": "இந்த செய்தியில் பொதுவான மோசடி அறிகுறிகள் இல்லை, ஆனாலும் தெரியாத கோரிக்கைகளில் கவனமாக இருங்கள்.",
        "some": "இந்த செய்தியின் ஆபத்து நிலை **{level}**. கண்டறிந்த எச்சரிக்கை அறிகுறிகள்: {names}. OTP, கடவுச்சொல் அல்லது பணம் கேட்டால் ஒருபோதும் பதிலளிக்க வேண்டாம்.",
    },
}
