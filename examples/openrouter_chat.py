"""OpenRouter integration with redact-prompt."""

import os
import requests
from redact_prompt import redact, unredact

# User input with sensitive data
user_input = "My SSN is 123-45-6789 and credit card is 4111-1111-1111-1111."

# Redact → Send → Unredact
result = redact(user_input)

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
    json={
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": result.text}],
    },
)

reply = response.json()["choices"][0]["message"]["content"]
print(unredact(reply))
