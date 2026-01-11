"""OpenAI integration with redact-prompt."""

from openai import OpenAI
from redact_prompt import redact, unredact

client = OpenAI()

# user input with sensitive data
user_input = "My email is sarah@acme.com and my API key is sk-proj-abc123xyz789def456."

# redact → send → unredact
result = redact(user_input)

response = client.responses.create(
    model="gpt-4o-mini",
    input=result.text,  # includes instruction to preserve placeholders
)

print(unredact(response.output_text))
