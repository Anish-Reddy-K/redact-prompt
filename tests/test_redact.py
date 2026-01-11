"""Tests for redact-prompt."""

import pytest
from redact_prompt import Redactor


class TestRedactor:
    def test_email(self):
        r = Redactor()
        result = r.redact("Email john@example.com")
        assert "[EMAIL_1]" in result.redacted
        assert "john@example.com" not in result.redacted
    
    def test_phone(self):
        r = Redactor()
        result = r.redact("Call 555-123-4567")
        assert "[PHONE_1]" in result.redacted
    
    def test_api_key_partial_mask(self):
        r = Redactor()
        result = r.redact("Key: sk-proj-abc123def456ghi789")
        assert "[API_KEY_1:sk-pro" in result.redacted
        assert "***" in result.redacted
    
    def test_person_name(self):
        r = Redactor()
        result = r.redact("Meeting with John Smith")
        assert "[PERSON_1]" in result.redacted
    
    def test_unredact(self):
        r = Redactor()
        result = r.redact("Email john@example.com")
        response = f"Got it, {result.entities[0].placeholder}"
        restored = r.unredact(response)
        assert "john@example.com" in restored
    
    def test_deterministic(self):
        r = Redactor()
        result = r.redact("a@b.com and a@b.com")
        assert result.redacted.count("[EMAIL_1]") == 2
    
    def test_text_includes_instruction(self):
        r = Redactor()
        result = r.redact("john@example.com")
        assert "IMPORTANT:" in result.text
        assert "[EMAIL_1]" in result.text
    
    def test_clear(self):
        r = Redactor()
        r.redact("john@example.com")
        r.clear()
        result = r.redact("jane@example.com")
        assert "[EMAIL_1]" in result.redacted  # counter reset
    
    def test_multiple_types(self):
        r = Redactor()
        result = r.redact("Email john@test.com, call 555-123-4567, key sk-proj-abc123xyz789012")
        assert "[EMAIL_1]" in result.redacted
        assert "[PHONE_1]" in result.redacted
        assert "[API_KEY_1:" in result.redacted
