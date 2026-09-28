import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

models_to_try = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]

for name in models_to_try:
    print(f"Trying {name} ...")
    start = time.time()
    try:
        model = genai.GenerativeModel(name)
        response = model.generate_content(
            "Say hello in one sentence.",
            request_options={"timeout": 25},
        )
        print("  WORKED:", response.text.strip())
    except Exception as e:
        print("  FAILED:", str(e)[:150])
    print(f"  ({round(time.time() - start)} seconds)")
    print()