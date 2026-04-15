from django.test import TestCase

from services.categorization_service import CategorizationService
from services.sensitive_data_guard import sanitize_for_llm


class CapturingLLM:
    def __init__(self):
        self.prompt = ""

    def generate(self, prompt):
        self.prompt = prompt
        return '{"category": "Office Supplies", "confidence": 0.8, "reason": "Test"}'


class SensitiveDataGuardTests(TestCase):
    def test_sanitize_removes_sensitive_keys_and_redacts_patterns(self):
        payload = {
            "industry": "Retail",
            "chart_of_accounts": ["Sales", "Office Supplies"],
            "email": "owner@example.com",
            "pan": "ABCDE1234F",
            "notes": "Call +91 9876543210 for approval",
            "nested": {"api_key": "secret-value", "category": "Sales"},
        }

        safe_payload = sanitize_for_llm(payload)

        self.assertNotIn("email", safe_payload)
        self.assertNotIn("pan", safe_payload)
        self.assertNotIn("api_key", safe_payload["nested"])
        self.assertEqual(safe_payload["chart_of_accounts"], ["Sales", "Office Supplies"])
        self.assertEqual(safe_payload["notes"], "Call [REDACTED] for approval")
        self.assertEqual(safe_payload["nested"]["category"], "Sales")

    def test_categorization_prompt_does_not_include_sensitive_company_data(self):
        llm = CapturingLLM()
        service = CategorizationService(llm_client=llm)

        service.categorize(
            {
                "description": "Printer paper bought by owner@example.com",
                "vendor": "Stationery Hub",
            },
            {
                "industry": "Retail",
                "chart_of_accounts": ["Office Supplies"],
                "historical_transactions": [],
                "api_key": "secret-value",
                "phone": "9876543210",
            },
        )

        self.assertNotIn("secret-value", llm.prompt)
        self.assertNotIn("api_key", llm.prompt)
        self.assertNotIn("9876543210", llm.prompt)
        self.assertNotIn("owner@example.com", llm.prompt)
        self.assertIn("[REDACTED]", llm.prompt)
