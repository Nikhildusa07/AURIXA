from app.ai.rag.filter import filter_results


def test_filters_valid_results():
    results = [
        {
            "text": "Valid result",
            "distance": 0.5,
            "confidence": 0.9,
        },
        {
            "text": "",
            "distance": 0.2,
            "confidence": 0.9,
        },
        {
            "text": "Too far",
            "distance": 1.5,
            "confidence": 0.9,
        },
        {
            "text": "Low confidence",
            "distance": 0.4,
            "confidence": 0.1,
        },
    ]

    filtered = filter_results(results)

    assert len(filtered) == 1
    assert filtered[0]["text"] == "Valid result"


def test_filters_whitespace_only_text():
    results = [
        {
            "text": "   ",
            "distance": 0.2,
            "confidence": 0.9,
        }
    ]

    assert filter_results(results) == []


def test_uses_default_values_for_missing_fields():
    results = [
        {"text": "Missing distance"},
        {"text": "Missing confidence", "distance": 0.5},
        {"text": "Complete", "distance": 0.5, "confidence": 0.9},
    ]

    filtered = filter_results(results)

    assert len(filtered) == 1
    assert filtered[0]["text"] == "Complete"


def test_respects_custom_max_distance():
    results = [
        {"text": "Close", "distance": 0.3, "confidence": 0.9},
        {"text": "Far", "distance": 0.8, "confidence": 0.9},
    ]

    filtered = filter_results(
        results,
        max_distance=0.5,
    )

    assert len(filtered) == 1
    assert filtered[0]["text"] == "Close"


def test_respects_custom_min_confidence():
    results = [
        {"text": "Low", "distance": 0.3, "confidence": 0.4},
        {"text": "High", "distance": 0.2, "confidence": 0.8},
    ]

    filtered = filter_results(
        results,
        min_confidence=0.5,
    )

    assert len(filtered) == 1
    assert filtered[0]["text"] == "High"


def test_boundary_values_are_included():
    results = [
        {
            "text": "Boundary",
            "distance": 1.0,
            "confidence": 0.15,
        }
    ]

    filtered = filter_results(results)

    assert len(filtered) == 1
    assert filtered[0]["text"] == "Boundary"


def test_results_are_sorted_by_distance():
    results = [
        {"text": "Third", "distance": 0.8, "confidence": 0.9},
        {"text": "First", "distance": 0.2, "confidence": 0.9},
        {"text": "Second", "distance": 0.5, "confidence": 0.9},
    ]

    filtered = filter_results(results)

    assert [item["text"] for item in filtered] == [
        "First",
        "Second",
        "Third",
    ]


def test_empty_results():
    assert filter_results([]) == []