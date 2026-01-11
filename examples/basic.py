"""Basic usage without API calls."""

from redact_prompt import redact, unredact, clear

# Reset state (in case of previous runs)
clear()

# User input with sensitive data (including API key)
user_input = "Hi, I'm Sarah Johnson. Email: sarah@acme.com, API key: sk-proj-abc123xyz789def456ghi."

# Redact PII
result = redact(user_input)
print("Redacted:", result.redacted)
print("Entities:", [e.placeholder for e in result.entities])

# result.text includes instruction for LLM
print("\nPrompt to send (result.text):")
print(result.text)

# Simulate LLM response and restore PII
llm_response = "Got it [PERSON_1], I see your API key [API_KEY_1:sk-pro***6ghi] has expired."
print("\nRestored:", unredact(llm_response))
