from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, users, courses, questions, mock_exams, formal_exams, grading, admin, health
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
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
