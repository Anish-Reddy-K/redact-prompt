"""Google Gemini integration with redact-prompt."""

from google import genai
from redact_prompt import redact, unredact

client = genai.Client()

# user input with sensitive data
user_input = "Contact me at 555-123-4567 or jane.doe@company.com for details."

# redact → send → unredact
result = redact(user_input)

response = client.models.generate_content(
    model="gemini-3.0-pro-preview",
    contents=result.text,
)

print(unredact(response.text))
