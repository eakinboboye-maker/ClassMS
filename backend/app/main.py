from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, users, courses, questions, mock_exams, formal_exams, grading, admin, health
from app.core.config import settings
import os

app = FastAPI(title=settings.APP_NAME)

raw_origins = os.getenv("CORS_ORIGINS", "")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(mock_exams.router, prefix="/api/mock-exams", tags=["mock-exams"])
app.include_router(formal_exams.router, prefix="/api/formal-exams", tags=["formal-exams"])
app.include_router(grading.router, prefix="/api/grading", tags=["grading"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
