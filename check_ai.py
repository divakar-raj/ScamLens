"""check_ai.py - run once to test your Groq key: python check_ai.py"""
import os
from dotenv import load_dotenv
load_dotenv()

key = os.environ.get("GROQ_API_KEY")
print("Key found:", bool(key))
if key:
    from groq import Groq
    client = Groq(api_key=key, timeout=15)
    try:
        models = sorted(m.id for m in client.models.list().data)
        print("Models available to your key:")
        for m in models:
            print("  ", m)
    except Exception as e:
        print("Could not reach Groq:", e)
