from app.ai.agents.document import analyze_document
from app.ai.policies.invoice_policy import (
    evaluate_invoice_policy,
)


invoice_text = """
ABC Technologies Pvt Ltd

INVOICE

Invoice Number: INV-2026-1001
Vendor: ABC Technologies Pvt Ltd
Invoice Date: 08-09-2026
Due Date: 30-09-2026
PO Number: PO-5001

Grand Total: ₹150000
"""


document_result = analyze_document(invoice_text)

print("=" * 60)
print("DOCUMENT ANALYSIS")
print("=" * 60)

print("Valid:", document_result.valid)
print("Confidence:", document_result.confidence)
print("Fields:", document_result.extracted_fields)

policy_decision = evaluate_invoice_policy(
    document_result.extracted_fields
)

print()
print("=" * 60)
print("INVOICE POLICY DECISION")
print("=" * 60)

print("Invoice Number:", policy_decision.invoice_number)
print("Total:", policy_decision.total)
print("Threshold:", policy_decision.threshold)
print("Requires Approval:", policy_decision.requires_approval)
print("Action:", policy_decision.action)
print("Reason:", policy_decision.reason)