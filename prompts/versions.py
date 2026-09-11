from __future__ import annotations

from prompts.templates import PROMPT_TEMPLATES, PromptTemplate


PROMPT_VERSIONS: dict[str, dict[str, PromptTemplate]] = {
    "classifier": {
        "v1": PROMPT_TEMPLATES["classifier"],
    },
    "automation": {
        "v1": PROMPT_TEMPLATES["automation"],
    },
    "research": {
        "v1": PROMPT_TEMPLATES["research"],
    },
    "document": {
        "v1": PROMPT_TEMPLATES["document"],
    },
    "validation": {
        "v1": PROMPT_TEMPLATES["validation"],
    },
}


ACTIVE_PROMPT_VERSIONS = {
    "classifier": "v1",
    "automation": "v1",
    "research": "v1",
    "document": "v1",
    "validation": "v1",
}


def get_prompt_version(
    name: str,
    version: str | None = None,
) -> PromptTemplate:
    if name not in PROMPT_VERSIONS:
        raise ValueError(f"Unknown prompt: {name}")

    selected_version = (
        version
        or ACTIVE_PROMPT_VERSIONS.get(name)
    )

    prompt = PROMPT_VERSIONS[name].get(
        selected_version
    )

    if prompt is None:
        raise ValueError(
            f"Prompt version not found: "
            f"{name}:{selected_version}"
        )

    return prompt


def get_active_prompt(
    name: str,
) -> PromptTemplate:
    return get_prompt_version(name)