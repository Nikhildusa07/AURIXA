from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class FeedbackRecord:
    id: str
    workflow_id: str | None
    request_id: str | None
    rating: int
    feedback: str
    correction: str | None
    created_at: datetime


@dataclass
class FailurePattern:
    pattern: str
    count: int = 0
    last_seen: datetime | None = None


class FeedbackService:
    def __init__(self) -> None:
        self.feedback_records: list[FeedbackRecord] = []
        self.failure_patterns: dict[str, FailurePattern] = {}
        self.improvement_history: list[dict[str, Any]] = []

    def submit_feedback(
        self,
        rating: int,
        feedback: str,
        workflow_id: str | None = None,
        request_id: str | None = None,
        correction: str | None = None,
    ) -> FeedbackRecord:
        if rating < 1 or rating > 5:
            raise ValueError(
                "Rating must be between 1 and 5."
            )

        record = FeedbackRecord(
            id=str(uuid4()),
            workflow_id=workflow_id,
            request_id=request_id,
            rating=rating,
            feedback=feedback,
            correction=correction,
            created_at=datetime.now(timezone.utc),
        )

        self.feedback_records.append(record)

        if correction:
            self.improvement_history.append(
                {
                    "id": str(uuid4()),
                    "type": "ai_correction",
                    "feedback_id": record.id,
                    "correction": correction,
                    "created_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                }
            )

        if rating <= 2:
            self.track_failure_pattern(
                pattern=feedback
            )

        return record

    def track_failure_pattern(
        self,
        pattern: str,
    ) -> FailurePattern:
        normalized_pattern = pattern.strip().lower()

        if normalized_pattern not in self.failure_patterns:
            self.failure_patterns[
                normalized_pattern
            ] = FailurePattern(
                pattern=normalized_pattern
            )

        failure = self.failure_patterns[
            normalized_pattern
        ]

        failure.count += 1
        failure.last_seen = datetime.now(
            timezone.utc
        )

        return failure

    def get_feedback_summary(self) -> dict[str, Any]:
        total = len(self.feedback_records)

        if total == 0:
            average_rating = 0.0
        else:
            average_rating = round(
                sum(
                    record.rating
                    for record in self.feedback_records
                )
                / total,
                2,
            )

        corrections = sum(
            1
            for record in self.feedback_records
            if record.correction
        )

        return {
            "total_feedback": total,
            "average_rating": average_rating,
            "ai_corrections": corrections,
            "failure_patterns": len(
                self.failure_patterns
            ),
            "improvement_history": len(
                self.improvement_history
            ),
        }

    def get_failure_patterns(
        self,
    ) -> list[dict[str, Any]]:
        patterns = sorted(
            self.failure_patterns.values(),
            key=lambda item: item.count,
            reverse=True,
        )

        return [
            {
                "pattern": pattern.pattern,
                "count": pattern.count,
                "last_seen": (
                    pattern.last_seen.isoformat()
                    if pattern.last_seen
                    else None
                ),
            }
            for pattern in patterns
        ]

    def get_improvement_history(
        self,
    ) -> list[dict[str, Any]]:
        return self.improvement_history


feedback_service = FeedbackService()