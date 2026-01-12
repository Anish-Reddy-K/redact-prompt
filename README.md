# redact-prompt

Redact PII from prompts before sending to LLMs. Restore original values in responses.

## Install

```bash
pip install redact-prompt
```
https://pypi.org/project/redact-prompt/

The spaCy language model downloads automatically on first use.

## How It Works

<img width="1112" alt="How redact-prompt works" src="https://github.com/user-attachments/assets/13ad6c38-90c1-4502-841d-da008d1cc0bb" />

1. **Redact** — Regex + NER detect PII, replace with numbered placeholders
2. **Inject** — `result.text` includes instruction telling LLM to preserve placeholders
3. **Restore** — `unredact()` maps placeholders back to original values

Same values get same placeholders (deterministic), so `john@acme.com` appearing twice → `[EMAIL_1]` both times.

## Quick Start

```python
from redact_prompt import redact, unredact

result = redact("Email john@acme.com about the project")

# Send result.text to LLM (includes injected instruction to preserve placeholders)

restored = unredact(llm_response)
```

## Examples

```python
# OpenAI
from openai import OpenAI
from redact_prompt import redact, unredact

client = OpenAI()
result = redact("My email is sarah@acme.com and my API key is sk-proj-abc123xyz789def456.")

response = client.responses.create(
    model="gpt-5-mini-2025-08-07",
    input=result.text,
)
print(unredact(response.output_text))
```

```python
# Anthropic
import anthropic
from redact_prompt import redact, unredact

client = anthropic.Anthropic()
result = redact("Hi, I'm John Smith from Acme Corp. My email is john@acme.com.")

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
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
result = redact("Contact me at 555-123-4567 or jane.doe@company.com for details.")

response = client.models.generate_content(
    model="gemini-3.0-pro-preview",
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
# Exclude specific types
result = redact("text", exclude=["EMAIL", "PHONE"])

# Only include specific types
result = redact("text", include=["SSN", "CREDIT_CARD"])

# Disable NER (faster, regex only)
result = redact("text", use_ner=False)

# Multiple conversations (use class API)
from redact_prompt import Redactor
r = Redactor()
result = r.redact("text")
r.clear()  # Reset for new conversation
```

**Available types:** `EMAIL`, `PHONE`, `SSN`, `CREDIT_CARD`, `IP`, `API_KEY`, `PERSON`, `ORG`, `LOCATION`

## Contributing

PRs welcome! See [GitHub Issues](https://github.com/Anish-Reddy-K/redact-prompt/issues) for wanted features.

**Adding a new PII pattern:**

1. Add regex to `PATTERNS` in `redact_prompt/__init__.py`
2. Add test in `tests/test_redact.py`
3. Update "What It Detects" in README

**Wanted patterns:** URL, Date of Birth, Address/ZIP, Bank Account, Drivers License, Passport Number, and more. Check issues.

## License

MIT
