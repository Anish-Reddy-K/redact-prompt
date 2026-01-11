"""OpenAI integration with redact-prompt."""

from openai import OpenAI
from redact_prompt import redact, unredact

client = OpenAI()

# User input with sensitive data
user_input = "My email is sarah@acme.com and my API key is sk-proj-abc123xyz789def456."

# Redact → Send → Unredact
result = redact(user_input)

response = client.responses.create(
    model="gpt-4o-mini",
    input=result.text,  # Includes instruction to preserve placeholders
)

print(unredact(response.output_text))
