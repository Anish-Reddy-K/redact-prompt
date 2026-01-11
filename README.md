# redact-prompt

Redact PII from prompts before sending to LLMs. Restore original values in responses.

## Install

```bash
pip install redact-prompt
```

The spaCy language model downloads automatically on first use.

## Quick Start

```python
from redact_prompt import redact, unredact

result = redact("Email john@acme.com about the project")
# Send result.text to LLM (includes instruction to preserve placeholders)
restored = unredact(llm_response)  # Restore original values
```

## Examples

```python
# OpenAI
from openai import OpenAI
from redact_prompt import redact, unredact

client = OpenAI()
result = redact("My email is sarah@acme.com and API key is sk-proj-abc123xyz.")

response = client.responses.create(
    model="gpt-4o-mini",
    input=result.text,
)
print(unredact(response.output_text))
```

```python
# Anthropic
import anthropic
from redact_prompt import redact, unredact

client = anthropic.Anthropic()
result = redact("Hi, I'm John Smith. Email: john@acme.com")

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": result.text}],
)
print(unredact(message.content[0].text))
```

```python
# Google Gemini
from google import genai
from redact_prompt import redact, unredact

client = genai.Client()
result = redact("Contact me at 555-123-4567 or jane@company.com")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=result.text,
)
print(unredact(response.text))
```

See [`examples/`](examples/) for OpenRouter and more.

## What It Detects

**Regex-based:**
- **Email** — `john@example.com` → `[EMAIL_1]`
- **Phone** — `555-123-4567` → `[PHONE_1]`
- **SSN** — `123-45-6789` → `[SSN_1]`
- **Credit Card** — `4111-1111-1111-1111` → `[CREDIT_CARD_1]`
- **IP Address** — `192.168.1.1` → `[IP_1]`
- **API Keys** — OpenAI, Anthropic, AWS, GitHub, Stripe, Slack, Google

**NER-based (via spaCy):**
- **Person** — `John Smith` → `[PERSON_1]`
- **Organization** — `Acme Corp` → `[ORG_1]`
- **Location** — `New York` → `[LOCATION_1]`

## API

```python
from redact_prompt import redact, unredact, clear

result = redact("text")        # Returns RedactionResult
result.text                    # Redacted + instruction (send to LLM)
result.redacted                # Just redacted text (for debugging)
result.entities                # List of detected entities

unredact(llm_response)         # Restore original values
clear()                        # Reset mappings between conversations
```

### Options

```python
# Disable NER (faster, regex only)
result = redact("text", use_ner=False)

# Multiple conversations (use class API)
from redact_prompt import Redactor
r = Redactor()
result = r.redact("text")
r.clear()  # Reset for new conversation
```

## License

MIT
