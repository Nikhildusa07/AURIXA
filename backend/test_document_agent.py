from app.ai.agents.document import analyze_document


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


result = analyze_document(invoice_text)

print(result)
print()
print("DOCUMENT TYPE:", result.document_type)
print("FIELDS:", result.extracted_fields)
print("CONFIDENCE:", result.confidence)
print("MISSING:", result.missing_fields)
print("VALID:", result.valid)