import json

import pytest
from pydantic import ValidationError

from triage.schema import (
    Category,
    Priority,
    Route,
    TriageDecision,
    TriageValidationError,
    validate_decision,
)


VALID = {
    "category": "billing",
    "priority": "P2",
    "route": "billing-team",
    "rationale": "A refund is covered by the money-at-stake rule.",
}


def test_validates_dictionary_and_json_object() -> None:
    decision = validate_decision(VALID)
    from_json = validate_decision(json.dumps(VALID))

    assert isinstance(decision, TriageDecision)
    assert decision == from_json
    assert decision.category is Category.BILLING
    assert decision.priority is Priority.P2
    assert decision.route is Route.BILLING_TEAM


@pytest.mark.parametrize("field", ["category", "priority", "route"])
def test_rejects_invalid_enum_values(field: str) -> None:
    payload = {**VALID, field: "unsupported"}

    with pytest.raises(TriageValidationError, match=field):
        validate_decision(payload)


@pytest.mark.parametrize("field", ["category", "priority", "route", "rationale"])
def test_rejects_missing_fields(field: str) -> None:
    payload = {key: value for key, value in VALID.items() if key != field}

    with pytest.raises(TriageValidationError, match=field):
        validate_decision(payload)


def test_rejects_extra_fields() -> None:
    with pytest.raises(TriageValidationError, match="Extra"):
        validate_decision({**VALID, "unexpected": "value"})


@pytest.mark.parametrize("rationale", ["", "First sentence. Second sentence.", "First. Second"])
def test_rejects_empty_or_multi_sentence_rationale(rationale: str) -> None:
    with pytest.raises(TriageValidationError, match="rationale"):
        validate_decision({**VALID, "rationale": rationale})


@pytest.mark.parametrize("payload", ["{not json", "[]", '"text"', "null", 42, None])
def test_rejects_malformed_json_and_non_objects(payload: object) -> None:
    with pytest.raises(TriageValidationError):
        validate_decision(payload)  # type: ignore[arg-type]


def test_decision_is_immutable() -> None:
    decision = validate_decision(VALID)

    with pytest.raises((ValidationError, TypeError)):
        decision.priority = Priority.P1
