from fastapi import APIRouter, HTTPException

from app.workflows.background_jobs import background_job_manager
from app.workflows.scheduler import workflow_scheduler


router = APIRouter(
    prefix="/background-jobs",
    tags=["Background Jobs"],
)


@router.post("/schedule")
async def schedule_background_job(
    name: str,
    priority: int = 5,
    duplicate_key: str | None = None,
):
    job = workflow_scheduler.schedule_job(
        name=name,
        priority=priority,
        duplicate_key=duplicate_key,
    )

    return {
        "job_id": job.id,
        "name": job.name,
        "priority": job.priority,
        "status": job.status,
        "duplicate_key": job.duplicate_key,
    }


@router.get("/")
async def get_background_jobs():
    return workflow_scheduler.get_scheduled_jobs()


@router.post("/run-next")
async def run_next_background_job():
    job = workflow_scheduler.run_next_job()

    if job is None:
        return {
            "message": "No pending jobs available.",
        }

    return {
        "job_id": job.id,
        "name": job.name,
        "status": job.status,
    }


@router.post("/{job_id}/complete")
async def complete_background_job(job_id: str):
    try:
        job = workflow_scheduler.complete_scheduled_job(job_id)

        return {
            "job_id": job.id,
            "status": job.status,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post("/{job_id}/fail")
async def fail_background_job(
    job_id: str,
    error_message: str,
):
    try:
        job = workflow_scheduler.fail_scheduled_job(
            job_id=job_id,
            error_message=error_message,
        )

        return {
            "job_id": job.id,
            "status": job.status,
            "error_message": job.error_message,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post("/{job_id}/retry")
async def retry_background_job(job_id: str):
    try:
        job = background_job_manager.retry_job(job_id)

        return {
            "job_id": job.id,
            "status": job.status,
            "message": "Job moved back to pending queue.",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/pause")
async def pause_background_jobs():
    workflow_scheduler.pause_scheduler()

    return {
        "status": "paused",
        "message": "Background job processing paused.",
    }


@router.post("/resume")
async def resume_background_jobs():
    workflow_scheduler.resume_scheduler()

    return {
        "status": "running",
        "message": "Background job processing resumed.",
    }


@router.get("/dead-letter")
async def get_dead_letter_jobs():
    return [
        {
            "job_id": job.id,
            "name": job.name,
            "priority": job.priority,
            "status": job.status,
            "error_message": job.error_message,
        }
        for job in background_job_manager.dead_letter_jobs
    ]