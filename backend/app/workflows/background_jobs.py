from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class BackgroundJob:
    id: str
    name: str
    priority: int
    status: str
    payload: dict[str, Any] = field(default_factory=dict)
    duplicate_key: str | None = None
    error_message: str | None = None
    created_at: datetime | None = None


class BackgroundJobManager:
    def __init__(self) -> None:
        self.jobs: list[BackgroundJob] = []
        self.dead_letter_jobs: list[BackgroundJob] = []

    def create_job(
        self,
        name: str,
        payload: dict[str, Any] | None = None,
        priority: int = 5,
        duplicate_key: str | None = None,
    ) -> BackgroundJob:
        if duplicate_key:
            for job in self.jobs:
                if (
                    job.duplicate_key == duplicate_key
                    and job.status in {"pending", "running"}
                ):
                    raise ValueError(
                        "Duplicate job already exists."
                    )

        job = BackgroundJob(
            id=str(uuid4()),
            name=name,
            priority=priority,
            status="pending",
            payload=payload or {},
            duplicate_key=duplicate_key,
            created_at=datetime.now(timezone.utc),
        )

        self.jobs.append(job)

        return job

    def get_jobs(self) -> list[BackgroundJob]:
        return sorted(
            self.jobs,
            key=lambda job: (
                job.status != "pending",
                job.priority,
            ),
        )

    def get_job(
        self,
        job_id: str,
    ) -> BackgroundJob | None:
        for job in self.jobs:
            if job.id == job_id:
                return job

        return None

    def retry_job(
        self,
        job_id: str,
    ) -> BackgroundJob:
        job = self.get_job(job_id)

        if job is None:
            raise ValueError("Background job not found.")

        if job.status != "failed":
            raise ValueError(
                "Only failed jobs can be retried."
            )

        job.status = "pending"
        job.error_message = None

        if job in self.dead_letter_jobs:
            self.dead_letter_jobs.remove(job)

        return job

    def fail_job(
        self,
        job_id: str,
        error_message: str,
    ) -> BackgroundJob:
        job = self.get_job(job_id)

        if job is None:
            raise ValueError("Background job not found.")

        job.status = "failed"
        job.error_message = error_message

        if job not in self.dead_letter_jobs:
            self.dead_letter_jobs.append(job)

        return job


background_job_manager = BackgroundJobManager()