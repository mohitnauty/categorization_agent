import json

from llm.factory import LLMFactory
from services.rules_engine import apply_rules
from services.sensitive_data_guard import sanitize_for_llm


class CategorizationService:

    def __init__(self, llm_client=None):
        self.llm = llm_client or LLMFactory.get_client("groq")

    def categorize(self, transaction, company):

        if isinstance(transaction, dict):
            safe_transaction = sanitize_for_llm(transaction)
            description = safe_transaction.get("description", "")
            vendor = safe_transaction.get("vendor", "")
            transaction_text = f"{description} {vendor}".strip()
        else:
            transaction_text = sanitize_for_llm(str(transaction))
            description = transaction_text
            vendor = ""

        if not transaction_text:
            return {
                "category": "Uncategorized",
                "confidence": 0,
                "reason": "Empty transaction"
            }

        rule_result = apply_rules(transaction_text)
        if rule_result:
            return rule_result

        safe_company = sanitize_for_llm(company or {})
        safe_company_text = json.dumps(safe_company, ensure_ascii=True)

        # LLM Prompt
        prompt = f"""
Categorize this transaction:

Description: {description}
Vendor: {vendor}
Company: {safe_company_text}

Return ONLY JSON:
{{
  "category": "...",
  "confidence": 0-1,
  "reason": "..."
}}
"""

        try:
            raw_output = self.llm.generate(prompt)

            # Try parsing JSON directly
            return json.loads(raw_output)

        except Exception:
            # Fallback if parsing fails
            return {
                "category": "Uncategorized",
                "confidence": 0.5,
                "reason": "LLM parsing failed"
            }
