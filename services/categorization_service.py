import json
import re

from llm.factory import LLMFactory
from services.rules_engine import apply_rules
from services.sensitive_data_guard import sanitize_for_llm


class CategorizationService:

    def __init__(self, llm_client=None):
        self.llm = llm_client or LLMFactory.get_client("groq")

    def _extract_json(self, text):
        """
        Safely extract JSON from LLM response
        """
        if not text:
            raise ValueError("Empty LLM response")

        # Remove markdown/code blocks
        text = re.sub(r"```json|```", "", text).strip()

        # Extract JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in response")

        return match.group(0)

    def categorize(self, transaction, company):

        # ---- Normalize input ----
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

        # ---- Rule Engine (fast path) ----
        rule_result = apply_rules(transaction_text)
        if rule_result:
            return rule_result

        # ---- Prepare company context ----
        safe_company = sanitize_for_llm(company or {})
        safe_company_text = json.dumps(safe_company, ensure_ascii=True)

        # ---- Prompt ----
        prompt = f"""
Categorize this transaction:

Description: {description}
Vendor: {vendor}
Company: {safe_company_text}

STRICT RULES:
- Return ONLY valid JSON
- No explanation
- No markdown
- No extra text

Format:
{{
  "category": "...",
  "confidence": 0-1,
  "reason": "..."
}}
"""

        try:
            raw_output = self.llm.generate(prompt)

            # Debug logs (Render logs)
            print("RAW OUTPUT:", raw_output)

            clean_json = self._extract_json(raw_output)

            parsed = json.loads(clean_json)

            return {
                "category": parsed.get("category", "Uncategorized"),
                "confidence": float(parsed.get("confidence", 0.5)),
                "reason": parsed.get("reason", "No reason provided")
            }

        except Exception as e:
            print("ERROR:", str(e))

            return {
                "category": "Uncategorized",
                "confidence": 0.5,
                "reason": f"LLM parsing failed: {str(e)}"
            }
