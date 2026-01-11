"""Basic usage without API calls."""

from redact_prompt import redact, unredact, clear

# Reset state (in case of previous runs)
clear()

# User input with sensitive data
user_input = "Hi, I'm Sarah Johnson from Acme Corp. Contact me at sarah@acme.com or 555-867-5309."

# Redact PII
result = redact(user_input)
print("Redacted:", result.redacted)
print("Entities:", [e.placeholder for e in result.entities])

# result.text includes instruction for LLM
print("\nPrompt to send (result.text):")
print(result.text)

# Simulate LLM response and restore PII
llm_response = "Got it [PERSON_1], I'll contact you at [EMAIL_1]."
print("\nRestored:", unredact(llm_response))
