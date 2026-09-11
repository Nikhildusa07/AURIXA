from fastapi import APIRouter, HTTPException

from app.ai.feedback.service import feedback_service


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


@router.post("/")
async def submit_feedback(
    rating: int,
    feedback: str,
    workflow_id: str | None = None,
    request_id: str | None = None,
    correction: str | None = None,
):
    try:
        record = feedback_service.submit_feedback(
            rating=rating,
            feedback=feedback,
            workflow_id=workflow_id,
            request_id=request_id,
            correction=correction,
        )

        return {
            "id": record.id,
            "rating": record.rating,
            "feedback": record.feedback,
            "correction": record.correction,
            "message": "Feedback submitted successfully.",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("/summary")
async def get_feedback_summary():
    return feedback_service.get_feedback_summary()


@router.get("/failure-patterns")
async def get_failure_patterns():
    return feedback_service.get_failure_patterns()


@router.get("/improvement-history")
async def get_improvement_history():
    return feedback_service.get_improvement_history()