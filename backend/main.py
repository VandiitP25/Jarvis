
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.ai_brain import router as ai_router
from backend.workspace_tools import router as tools_router
from backend.background_tasks import router as background_tasks_router


app = FastAPI(title="JARVIS AI Assistant")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register each router exactly once.
app.include_router(ai_router)
app.include_router(tools_router)
app.include_router(background_tasks_router)


@app.get("/")
def home():
    return {
        "message": "Hackathon backend is working!",
        "status": "online",
    }
