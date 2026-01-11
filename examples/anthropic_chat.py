"""Anthropic Claude integration with redact-prompt."""

import anthropic
from redact_prompt import redact, unredact

client = anthropic.Anthropic()

# user input with sensitive data
user_input = "Hi, I'm John Smith from Acme Corp. My email is john@acme.com."

# redact → send → unredact
result = redact(user_input)

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": result.text}],
)

print(unredact(message.content[0].text))
