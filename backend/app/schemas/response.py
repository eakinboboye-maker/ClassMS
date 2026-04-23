from pydantic import BaseModel, model_validator


class ResponseSave(BaseModel):
    question_id: int
    response: dict

    @model_validator(mode="after")
    def ensure_not_empty(self):
        if not self.response:
            raise ValueError("response cannot be empty")
        return self


class AutosavePayload(BaseModel):
    responses: list[ResponseSave]


class FinalSubmitRequest(BaseModel):
    submitted_payload: dict | None = None
