import json

from services.sensitive_data_guard import sanitize_for_llm


class ContextBuilder:
    def build(self, transaction, company):
        safe_company = sanitize_for_llm(company)
        safe_transaction = sanitize_for_llm(transaction)

        return {
            "categories": safe_company["chart_of_accounts"],
            "examples": safe_company["historical_transactions"],
            "industry": safe_company["industry"],
            "transaction": safe_transaction
        }

    def to_prompt(self, context):
        safe_context = sanitize_for_llm(context)

        return f"""
Categorize the following transaction.

Industry: {safe_context['industry']}

Allowed Categories:
{json.dumps(safe_context['categories'], ensure_ascii=True)}

Examples:
{json.dumps(safe_context['examples'], ensure_ascii=True)}

Transaction:
{json.dumps(safe_context['transaction'], ensure_ascii=True)}

Return ONLY JSON:
{{
  "category": "...",
  "confidence": 0-1,
  "reason": "..."
}}
"""
