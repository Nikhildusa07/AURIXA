from fastapi import APIRouter

from app.ai.agents.orchestrator import orchestrate_request


router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/orchestrate")
async def orchestrate(
    title: str,
    content: str,
) -> dict:
    result = orchestrate_request(
        title=title,
        content=content,
    )

    return {
        "request_type": result.request_type,
        "classification_confidence": result.classification_confidence,
        "action": result.action,
        "tool_name": result.tool_name,
        "requires_approval": result.requires_approval,
        "validation": result.validation,
    }