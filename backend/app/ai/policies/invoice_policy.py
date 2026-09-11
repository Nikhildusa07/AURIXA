from __future__ import annotations

from dataclasses import dataclass


HIGH_VALUE_INVOICE_THRESHOLD = 100000.0


@dataclass
class InvoicePolicyDecision:
    invoice_number: str | None
    total: float
    threshold: float
    requires_approval: bool
    action: str
    reason: str


def evaluate_invoice_policy(
    extracted_fields: dict,
) -> InvoicePolicyDecision:
    invoice_number = extracted_fields.get(
        "invoice_number"
    )

    total = extracted_fields.get("total")

    if total is None:
        return InvoicePolicyDecision(
            invoice_number=invoice_number,
            total=0.0,
            threshold=HIGH_VALUE_INVOICE_THRESHOLD,
            requires_approval=True,
            action="request_human_review",
            reason=(
                "Invoice total could not be determined. "
                "Human review is required."
            ),
        )

    try:
        total_amount = float(total)
    except (TypeError, ValueError):
        return InvoicePolicyDecision(
            invoice_number=invoice_number,
            total=0.0,
            threshold=HIGH_VALUE_INVOICE_THRESHOLD,
            requires_approval=True,
            action="request_human_review",
            reason=(
                "Invoice total is invalid. "
                "Human review is required."
            ),
        )

    if total_amount > HIGH_VALUE_INVOICE_THRESHOLD:
        return InvoicePolicyDecision(
            invoice_number=invoice_number,
            total=total_amount,
            threshold=HIGH_VALUE_INVOICE_THRESHOLD,
            requires_approval=True,
            action="request_human_approval",
            reason=(
                f"Invoice total {total_amount:.2f} exceeds "
                f"the approval threshold of "
                f"{HIGH_VALUE_INVOICE_THRESHOLD:.2f}."
            ),
        )

    return InvoicePolicyDecision(
        invoice_number=invoice_number,
        total=total_amount,
        threshold=HIGH_VALUE_INVOICE_THRESHOLD,
        requires_approval=False,
        action="continue_automatic_processing",
        reason=(
            f"Invoice total {total_amount:.2f} is within "
            f"the automatic processing threshold."
        ),
    )