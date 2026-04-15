RULES = {
    "swiggy": "Food",
    "zomato": "Food",
    "uber": "Transport",
    "ola": "Transport",
    "netflix": "Entertainment",
    "amazon": "Shopping"
}

def apply_rules(transaction):
    transaction = transaction.lower()

    for key, value in RULES.items():
        if key in transaction:
            return {
                "category": value,
                "confidence": 0.95,
                "reason": f"Matched {key}"
            }

    return None