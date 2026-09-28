
from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(min_length=3, max_length=120)
    parties: str = Field(min_length=3, max_length=3000)
    terms: str = Field(min_length=3, max_length=12000)
    dates: str = Field(min_length=3, max_length=200)
    jurisdiction: str = Field(default="Not specified", max_length=200)
    additional_instructions: str = Field(default="", max_length=3000)

    @field_validator("document_type", "parties", "terms", "dates")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be blank")
        return value.strip()


class DocumentResponse(BaseModel):
    document: str
    disclaimer: str = (
        "AI-generated draft. Have a qualified lawyer review it "
        "for your jurisdiction before signing or relying on it."
    )