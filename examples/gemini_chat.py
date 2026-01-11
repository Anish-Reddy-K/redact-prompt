"""Google Gemini integration with redact-prompt."""

from google import genai
from redact_prompt import redact, unredact

client = genai.Client()

# User input with sensitive data
user_input = "Contact me at 555-123-4567 or jane.doe@company.com for details."

# Redact → Send → Unredact
result = redact(user_input)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=result.text,
)

print(unredact(response.text))
