"""Basic usage without API calls."""

from redact_prompt import redact, unredact, clear

# reset state (in case of previous runs)
clear()

# user input with sensitive data (including api key)
user_input = "Hi, I'm Sarah Johnson. Email: sarah@acme.com, API key: sk-proj-abc123xyz789def456ghi."

# redact pii
result = redact(user_input)
print("Redacted:", result.redacted)
print("Entities:", [e.placeholder for e in result.entities])

# result.text includes instruction for llm
print("\nPrompt to send (result.text):")
print(result.text)

# simulate llm response and restore pii
llm_response = "Got it [PERSON_1], I see your API key [API_KEY_1:sk-pro***6ghi] has expired. So here is the new code: ..."
print("\nRestored:", unredact(llm_response))
