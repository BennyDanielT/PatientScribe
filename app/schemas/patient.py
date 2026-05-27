from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """
    Request payload containing the patient ID and the raw medical report text.
    """

    patient_id: str = Field(
        ..., description="The unique identifier for the patient.", examples=["P001"]
    )
    report_text: str = Field(
        ...,
        description="The raw medical report text containing jargon to simplify.",
        examples=["MRI shows mild disc bulge at L4-L5."],
    )


class ReportResponse(BaseModel):
    """
    Response payload containing the simplified medical report and execution status.
    """

    status: str = Field(
        ...,
        description="The status of the simplification operation (e.g., 'success' or 'mock_success').",
        examples=["success"],
    )
    patient_id: str = Field(
        ..., description="The unique identifier for the patient.", examples=["P001"]
    )
    simplified_text: str = Field(
        ...,
        description="The simplified explanation of the medical report in plain English.",
        examples=["There is a small bulging disc in the lower back..."],
    )
