import pytest

from app.ai.tools.invoice import validate_invoice


def test_valid_invoice():
    invoice = {
        "invoice_number": "INV-001",
        "total": 1500.50,
    }

    result = validate_invoice(invoice)

    assert result["status"] == "validated"
    assert result["invoice_number"] == "INV-001"
    assert result["total"] == 1500.50


def test_invoice_input_must_be_dictionary():
    with pytest.raises(ValueError, match="Invoice input must be a dictionary"):
        validate_invoice("invalid invoice")


def test_missing_invoice_number():
    invoice = {
        "total": 500,
    }

    result = validate_invoice(invoice)

    assert result["status"] == "invalid"
    assert result["missing_fields"] == ["invoice_number"]


def test_missing_total():
    invoice = {
        "invoice_number": "INV-002",
    }

    result = validate_invoice(invoice)

    assert result["status"] == "invalid"
    assert result["missing_fields"] == ["total"]


def test_missing_multiple_fields():
    invoice = {}

    result = validate_invoice(invoice)

    assert result["status"] == "invalid"
    assert result["missing_fields"] == ["invoice_number", "total"]


@pytest.mark.parametrize(
    "total",
    [
        -100,
        -0.01,
        "100",
        None,
        [],
    ],
)
def test_invalid_invoice_total(total):
    invoice = {
        "invoice_number": "INV-003",
        "total": total,
    }

    result = validate_invoice(invoice)

    assert result["status"] == "invalid"
    assert result["issues"] == [
        "Invoice total must be a non-negative number."
    ]


@pytest.mark.parametrize("total", [0, 100, 99.99])
def test_valid_non_negative_totals(total):
    invoice = {
        "invoice_number": "INV-004",
        "total": total,
    }

    result = validate_invoice(invoice)

    assert result["status"] == "validated"
    assert result["total"] == total