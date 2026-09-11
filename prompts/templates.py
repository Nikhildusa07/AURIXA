from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    version: str
    system_prompt: str
    user_template: str


CLASSIFIER_PROMPT = PromptTemplate(
    name="classifier",
    version="v1",
    system_prompt=(
        "You are the AURIXA Classification Agent. "
        "Classify enterprise requests accurately and safely."
    ),
    user_template=(
        "Title: {title}\n"
        "Content: {content}\n\n"
        "Classify the request and provide confidence."
    ),
)


AUTOMATION_PROMPT = PromptTemplate(
    name="automation",
    version="v1",
    system_prompt=(
        "You are the AURIXA Automation Agent. "
        "Decide whether a request should be automated "
        "or require human approval."
    ),
    user_template=(
        "Request Type: {request_type}\n"
        "Confidence: {confidence}\n\n"
        "Determine the appropriate automation action."
    ),
)


RESEARCH_PROMPT = PromptTemplate(
    name="research",
    version="v1",
    system_prompt=(
        "You are the AURIXA Research Agent. "
        "Answer questions using retrieved knowledge context. "
        "Do not invent information outside the available context."
    ),
    user_template=(
        "Query: {query}\n\n"
        "Context:\n{context}\n\n"
        "Provide a grounded answer."
    ),
)


DOCUMENT_PROMPT = PromptTemplate(
    name="document",
    version="v1",
    system_prompt=(
        "You are the AURIXA Document Analysis Agent. "
        "Extract relevant structured information accurately."
    ),
    user_template=(
        "Document Type: {document_type}\n\n"
        "Document Content:\n{content}"
    ),
)


VALIDATION_PROMPT = PromptTemplate(
    name="validation",
    version="v1",
    system_prompt=(
        "You are the AURIXA Validation Agent. "
        "Validate workflow results and identify issues "
        "that require human review."
    ),
    user_template=(
        "Result:\n{result}\n\n"
        "Confidence: {confidence}\n\n"
        "Validate the result."
    ),
)


PROMPT_TEMPLATES = {
    "classifier": CLASSIFIER_PROMPT,
    "automation": AUTOMATION_PROMPT,
    "research": RESEARCH_PROMPT,
    "document": DOCUMENT_PROMPT,
    "validation": VALIDATION_PROMPT,
}


def get_prompt_template(name: str) -> PromptTemplate:
    template = PROMPT_TEMPLATES.get(name)

    if template is None:
        raise ValueError(f"Prompt template not found: {name}")

    return template


def render_prompt(
    name: str,
    **kwargs,
) -> str:
    template = get_prompt_template(name)

    return template.user_template.format(**kwargs)