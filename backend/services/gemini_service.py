import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

def get_ai_response(prompt: str):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini error: {str(e)}"
    
def classify_intent(question: str, subject: str):
    prompt = f"""
You are an intent classifier.

The user has currently selected the subject:
{subject}

Classify the user's message into ONLY ONE category.

Possible categories:

casual
academic
unrelated

Rules:

- casual → greetings, thanks, who are you, help, introduction, small talk.
- academic → anything asking about the selected subject.
- unrelated → anything not related to the selected subject.

Return ONLY ONE WORD.

User:
{question}
"""

    response = get_ai_response(prompt)
    return response.strip().lower()