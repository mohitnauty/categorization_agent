import json

class ResponseParser:
    def parse(self, raw_output: str):
        try:
            data = json.loads(raw_output)

            return {
                "category": data["category"],
                "confidence": float(data["confidence"]),
                "reason": data.get("reason", "")
            }
        except Exception:
            raise ValueError("Invalid LLM response format")