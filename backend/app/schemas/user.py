from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    matric_no: str | None = None
    role: str = "student"


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    matric_no: str | None = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RosterUserCreate(BaseModel):
    email: EmailStr
    full_name: str
    matric_no: str | None = None
    role: str = "student"
    password: str | None = None


class BulkRosterImportRequest(BaseModel):
    users: list[RosterUserCreate]
    default_password: str = "changeme123"
    skip_existing: bool = True


class BulkRosterImportResult(BaseModel):
    created_count: int
    skipped_count: int
    created_users: list[UserRead]


class RosterRowInput(BaseModel):
    email: str
    full_name: str
    matric_no: str | None = None
    role: str = "student"
    password: str | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str):
        return value.strip().lower()

    @field_validator("full_name")
    @classmethod
    def normalize_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("full_name cannot be blank")
        return value


class ParsedRosterResponse(BaseModel):
    parsed_count: int
    rows: list[RosterUserCreate]
    errors: list[dict] = []
