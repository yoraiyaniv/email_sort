import os
import json
from typing import List, Optional
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()


genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

MODEL = genai.GenerativeModel(
    model_name="gemini-2.0-flash-lite",
    system_instruction=(
        "You classify emails into exactly one label from allowed_labels. "
        "If the email does not clearly match any label, return 'None'. "
        'Output JSON only like {"label": "..."}'
    ),
    generation_config={
        "temperature": 0.1,
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "object",
            "properties": {"label": {"type": "string"}},
            "required": ["label"],
        },
    },
)

def classify_email(email_text: str, allowed_labels: list[str]) -> str | None:
    extended = list(allowed_labels) + ["None"]
    prompt = (
        f"allowed_labels = {json.dumps(extended, ensure_ascii=False)}\n\n"
        f"email:\n{email_text}"
    )
    try:
        resp = MODEL.generate_content(prompt)
        data = json.loads(resp.text)
        label = data.get("label", "None")
        return None if label == "None" else label
    except Exception:
        # On any error, be safe and return None
        return None