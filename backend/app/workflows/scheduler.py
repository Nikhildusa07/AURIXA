from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.workflows.background_jobs import (
    BackgroundJob,
    background_job_manager,
)


class WorkflowScheduler:
    def __init__(self) -> None:
        self.scheduled_jobs: dict[str, dict[str, Any]] = {}

    def schedule_job(
        self,
        name: str,
        payload: dict[str, Any] | None = None,
        priority: int = 5,
        duplicate_key: str | None = None,
    ) -> BackgroundJob:
        job = background_job_manager.create_job(
            name=name,
            payload=payload,
            priority=priority,
            duplicate_key=duplicate_key,
        )

        self.scheduled_jobs[job.id] = {
            "job_id": job.id,
            "name": job.name,
            "scheduled_at": datetime.now(timezone.utc),
            "status": job.status,
        }

        return job

    def run_next_job(self) -> BackgroundJob | None:
        job = background_job_manager.get_next_job()

        if job is None:
            return None

        return background_job_manager.start_job(job.id)

    def complete_scheduled_job(
        self,
        job_id: str,
    ) -> BackgroundJob:
        job = background_job_manager.complete_job(job_id)

        if job_id in self.scheduled_jobs:
            self.scheduled_jobs[job_id]["status"] = job.status

        return job

    def fail_scheduled_job(
        self,
        job_id: str,
        error_message: str,
    ) -> BackgroundJob:
        job = background_job_manager.fail_job(
            job_id=job_id,
            error_message=error_message,
        )

        if job_id in self.scheduled_jobs:
            self.scheduled_jobs[job_id]["status"] = job.status

        return job

    def pause_scheduler(self) -> None:
        background_job_manager.pause()

    def resume_scheduler(self) -> None:
        background_job_manager.resume()

    def get_scheduled_jobs(self) -> list[dict[str, Any]]:
        jobs = []

        for job in background_job_manager.get_jobs():
            jobs.append(
                {
                    "job_id": job.id,
                    "name": job.name,
                    "priority": job.priority,
                    "status": job.status,
                    "payload": job.payload,
                    "duplicate_key": job.duplicate_key,
                    "created_at": job.created_at,
                    "started_at": job.started_at,
                    "completed_at": job.completed_at,
                    "error_message": job.error_message,
                }
            )

        return jobs


workflow_scheduler = WorkflowScheduler()