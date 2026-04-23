from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import (
    UserRead,
    UserCreate,
    BulkRosterImportRequest,
    BulkRosterImportResult,
    ParsedRosterResponse,
)
from app.services.roster_import_service import parse_csv_roster, parse_xlsx_roster_rows

router = APIRouter()


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    return db.query(User).all()


@router.post("/", response_model=UserRead)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        matric_no=payload.matric_no,
        role=payload.role,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/bulk-import", response_model=BulkRosterImportResult)
def bulk_import_roster(
    payload: BulkRosterImportRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "instructor")),
):
    created_users: list[User] = []
    created_count = 0
    skipped_count = 0

    for item in payload.users:
        existing = db.query(User).filter(User.email == item.email).first()
        if existing:
            if payload.skip_existing:
                skipped_count += 1
                continue
            raise HTTPException(status_code=400, detail=f"User already exists: {item.email}")

        password = item.password or payload.default_password

        user = User(
            email=item.email,
            full_name=item.full_name,
            matric_no=item.matric_no,
            role=item.role,
            hashed_password=hash_password(password),
        )
        db.add(user)
        db.flush()

        created_users.append(user)
        created_count += 1

    db.commit()

    return BulkRosterImportResult(
        created_count=created_count,
        skipped_count=skipped_count,
        created_users=created_users,
    )


@router.post("/parse-csv", response_model=ParsedRosterResponse)
def parse_csv_roster_endpoint(
    csv_content: str = Body(..., embed=True),
    _: User = Depends(require_role("admin", "instructor")),
):
    rows, errors = parse_csv_roster(csv_content)
    return ParsedRosterResponse(parsed_count=len(rows), rows=rows, errors=errors)


@router.post("/parse-xlsx-rows", response_model=ParsedRosterResponse)
def parse_xlsx_rows_endpoint(
    rows: list[dict] = Body(..., embed=True),
    _: User = Depends(require_role("admin", "instructor")),
):
    parsed_rows, errors = parse_xlsx_roster_rows(rows)
    return ParsedRosterResponse(parsed_count=len(parsed_rows), rows=parsed_rows, errors=errors)
