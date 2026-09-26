"""The validated, immutable contract for triage decisions."""

from __future__ import annotations

import json
import re
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


class Category(StrEnum):
    BILLING = "billing"
    BUG = "bug"
    ACCESS = "access"
    PERFORMANCE = "performance"
    HOW_TO = "how-to"


class Priority(StrEnum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class Route(StrEnum):
    BILLING_TEAM = "billing-team"
    BUG_TEAM = "bug-team"
    ACCESS_TEAM = "access-team"
    PERFORMANCE_TEAM = "performance-team"
    HOW_TO_TEAM = "how-to-team"


class TriageValidationError(ValueError):
    """Raised when a triage decision cannot satisfy the public contract."""


class TriageDecision(BaseModel):
    """An immutable, strictly shaped triage decision."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    category: Category
    priority: Priority
    route: Route
    rationale: str

    @field_validator("rationale")
    @classmethod
    def validate_rationale(cls, value: str) -> str:
        if not value:
            raise ValueError("rationale must not be empty")

        # A sentence may have one optional final terminator. Any terminator
        # before the end indicates that the rationale contains another
        # sentence, including when that second sentence has no terminator.
        terminators = list(re.finditer(r"[.!?]", value))
        if len(terminators) > 1 or (
            terminators and value[terminators[0].end() :].strip()
        ):
            raise ValueError("rationale must contain exactly one sentence")

        return value


def validate_decision(payload: dict[str, Any] | str) -> TriageDecision:
    """Validate a decision dictionary or a JSON object and return its model."""

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise TriageValidationError(f"Invalid JSON decision: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise TriageValidationError("Decision must be a dictionary or JSON object")

    try:
        return TriageDecision.model_validate(payload)
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        )
        raise TriageValidationError(f"Invalid triage decision: {problems}") from exc
