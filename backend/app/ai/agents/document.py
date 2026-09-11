from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class DocumentAnalysisResult:
    document_type: str
    extracted_fields: dict
    confidence: float
    missing_fields: list[str]
    valid: bool


def analyze_document(
    text: str,
    document_type: str = "invoice",
) -> DocumentAnalysisResult:
    if not text or not text.strip():
        return DocumentAnalysisResult(
            document_type=document_type,
            extracted_fields={},
            confidence=0.0,
            missing_fields=["document_text"],
            valid=False,
        )

    if document_type != "invoice":
        return DocumentAnalysisResult(
            document_type=document_type,
            extracted_fields={},
            confidence=0.50,
            missing_fields=[],
            valid=True,
        )

    fields = extract_invoice_fields(text)

    required_fields = [
        "invoice_number",
        "vendor_name",
        "total",
    ]

    missing_fields = [
        field
        for field in required_fields
        if fields.get(field) is None
    ]

    confidence = calculate_confidence(
        fields=fields,
        required_fields=required_fields,
    )

    valid = len(missing_fields) == 0

    return DocumentAnalysisResult(
        document_type="invoice",
        extracted_fields=fields,
        confidence=confidence,
        missing_fields=missing_fields,
        valid=valid,
    )


def extract_invoice_fields(text: str) -> dict:
    fields: dict = {
        "document_type": "invoice",
    }

    invoice_number = extract_invoice_number(text)
    if invoice_number:
        fields["invoice_number"] = invoice_number

    vendor_name = extract_vendor_name(text)
    if vendor_name:
        fields["vendor_name"] = vendor_name

    invoice_date = extract_date(
        text,
        labels=[
            "invoice date",
        ],
    )

    if invoice_date:
        fields["invoice_date"] = invoice_date

    due_date = extract_date(
        text,
        labels=[
            "due date",
            "payment due",
        ],
    )

    if due_date:
        fields["due_date"] = due_date

    total_data = extract_total(text)
    if total_data:
        fields.update(total_data)

    purchase_order = extract_purchase_order(text)
    if purchase_order:
        fields["purchase_order"] = purchase_order

    return fields


def extract_invoice_number(text: str) -> str | None:
    patterns = [
        r"invoice\s+(?:number|no\.?|#)\s*[:\-]?\s*"
        r"([A-Z0-9][A-Z0-9\-\/]+)",

        r"invoice\s*[:\-]\s*"
        r"([A-Z0-9][A-Z0-9\-\/]+)",

        r"\binv\s*[:#]?\s*"
        r"([A-Z0-9][A-Z0-9\-\/]+)",
    ]

    return find_first_match(text, patterns)


def extract_vendor_name(text: str) -> str | None:
    patterns = [
        r"(?:vendor|supplier|company)\s*[:\-]\s*"
        r"([^\n]+)",

        r"(?:from)\s*[:\-]?\s*"
        r"([^\n]+)",
    ]

    value = find_first_match(text, patterns)

    if value:
        return value.strip()

    return None


def extract_date(
    text: str,
    labels: list[str],
) -> str | None:
    date_pattern = (
        r"(\d{4}-\d{2}-\d{2}"
        r"|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
        r"|\d{1,2}\s+[A-Za-z]+\s+\d{4})"
    )

    for label in labels:
        pattern = (
            rf"{re.escape(label)}"
            rf"\s*[:\-]?\s*{date_pattern}"
        )

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

    return None


def extract_total(text: str) -> dict | None:
    patterns = [
        r"(?:grand\s+total|total\s+amount|amount\s+due|total)"
        r"\s*[:\-]?\s*"
        r"((?:INR|USD|EUR|GBP)\s*"
        r"[\d,]+(?:\.\d{1,2})?)",

        r"(?:grand\s+total|total\s+amount|amount\s+due|total)"
        r"\s*[:\-]?\s*"
        r"([₹$€£]\s*[\d,]+(?:\.\d{1,2})?)",

        r"(?:grand\s+total|total\s+amount|amount\s+due|total)"
        r"\s*[:\-]?\s*"
        r"([\d,]+(?:\.\d{1,2})?)",
    ]

    value = find_first_match(text, patterns)

    if not value:
        return None

    currency = detect_currency(value)

    numeric_value = re.sub(
        r"[^\d.]",
        "",
        value,
    )

    try:
        amount = float(numeric_value)
    except ValueError:
        return None

    return {
        "total": amount,
        "currency": currency,
    }


def extract_purchase_order(text: str) -> str | None:
    patterns = [
        r"(?:purchase\s+order|po\s+number|po\s*#)"
        r"\s*[:\-]?\s*"
        r"([A-Z0-9\-\/]+)",
    ]

    return find_first_match(text, patterns)


def detect_currency(value: str) -> str:
    upper_value = value.upper()

    if "INR" in upper_value or "₹" in value:
        return "INR"

    if "USD" in upper_value or "$" in value:
        return "USD"

    if "EUR" in upper_value or "€" in value:
        return "EUR"

    if "GBP" in upper_value or "£" in value:
        return "GBP"

    return "UNKNOWN"


def find_first_match(
    text: str,
    patterns: list[str],
) -> str | None:
    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

    return None


def calculate_confidence(
    fields: dict,
    required_fields: list[str],
) -> float:
    extracted_count = sum(
        1
        for field in required_fields
        if fields.get(field) is not None
    )

    if not required_fields:
        return 1.0

    confidence = (
        extracted_count / len(required_fields)
    )

    optional_fields = [
        "invoice_date",
        "due_date",
        "purchase_order",
        "currency",
    ]

    optional_count = sum(
        1
        for field in optional_fields
        if fields.get(field) is not None
    )

    bonus = min(
        optional_count * 0.05,
        0.20,
    )

    return round(
        min(confidence + bonus, 1.0),
        2,
    )