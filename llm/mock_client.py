class MockClient:
    def generate(self, prompt):
        return '{"category": "Uncategorized", "confidence": 0.5, "reason": "Mock fallback"}'