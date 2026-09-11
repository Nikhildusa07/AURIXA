from __future__ import annotations

from typing import Any


def validate_invoice(invoice: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(invoice, dict):
        raise ValueError("Invoice input must be a dictionary.")

    required_fields = ["invoice_number", "total"]

    missing_fields = [
        field
        for field in required_fields
        if field not in invoice
    ]

    if missing_fields:
        return {
            "status": "invalid",
            "missing_fields": missing_fields,
        }

    total = invoice["total"]

    if not isinstance(total, (int, float)) or total < 0:
        return {
            "status": "invalid",
            "issues": ["Invoice total must be a non-negative number."],
        }

    return {
        "status": "validated",
        "invoice_number": invoice["invoice_number"],
        "total": total,
    }