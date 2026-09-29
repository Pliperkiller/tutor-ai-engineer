"""The contract for one intake: what an extraction must produce.

Shared by the three demos. The LLM never sees this Python class: it sees the
JSON Schema that Pydantic generates from it.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

CaseType = Literal["personal_injury", "contract_dispute", "employment", "other"]
Urgency = Literal["low", "medium", "high"]


class Intake(BaseModel):
    """Structured data extracted from a prospective client's free-text message."""

    client_name: str = Field(description="Full name of the person writing, as they wrote it.")
    case_type: CaseType = Field(description="Legal area of the problem. Use 'other' if none fits.")
    incident_date: date | None = Field(
        description="Date of the incident (YYYY-MM-DD), or null if the message gives no date."
    )
    summary: str = Field(
        max_length=160, description="One English sentence describing what happened."
    )
    urgency: Urgency = Field(
        description="high if a deadline or ongoing harm is mentioned, low if purely informational, else medium."
    )

    @field_validator("incident_date")
    @classmethod
    def reject_future_dates(cls, value: date | None) -> date | None:
        """An incident cannot have happened after today."""
        if value is not None and value > date.today():
            raise ValueError("incident_date cannot be in the future")
        return value
