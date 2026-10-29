
from __future__ import annotations

import os
import secrets
import time

from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Any

from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

from backend.workspace_tools import send_jarvis_notification


# --------------------------------------------------
# Configuration
# --------------------------------------------------

router = APIRouter(prefix="/api/tasks", tags=["JARVIS Background Tasks"])

AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama").strip().lower()
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434/v1",
)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

MAX_TASKS = 100
MAX_TASK_LENGTH = 8000

# In-memory task storage.
# Tasks are lost when the backend restarts.
TASKS: dict[str, dict[str, Any]] = {}
TASKS_LOCK = Lock()

# A small worker pool processes tasks outside the request handler.
EXECUTOR = ThreadPoolExecutor(
    max_workers=2,
    thread_name_prefix="jarvis-task",
)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class BackgroundTaskRequest(BaseModel):
    task: str = Field(min_length=1, max_length=MAX_TASK_LENGTH)


# --------------------------------------------------
# AI processing
# --------------------------------------------------

def run_ai_task(task_text: str) -> tuple[str, str]:
    """Process a user task with the configured AI provider."""

    if AI_PROVIDER == "ollama":
        client = OpenAI(
            api_key="ollama",
            base_url=OLLAMA_BASE_URL,
            timeout=180.0,
            max_retries=1,
        )
        model = OLLAMA_MODEL

    elif AI_PROVIDER == "nvidia":
        api_key = os.getenv("NVIDIA_API_KEY")

        if not api_key:
            raise RuntimeError("NVIDIA_API_KEY is not configured.")

        client = OpenAI(
            api_key=api_key,
            base_url=os.getenv(
                "NVIDIA_BASE_URL",
                "https://integrate.api.nvidia.com/v1",
            ),
            timeout=90.0,
            max_retries=1,
        )
        model = os.getenv(
            "NVIDIA_MODEL",
            "nvidia/nemotron-3.5-bolt-e4b",
        )

    else:
        raise RuntimeError(
            "Unsupported AI_PROVIDER. Use 'ollama' or 'nvidia'."
        )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are JARVIS, a helpful personal AI assistant. "
                    "Complete the user's requested reasoning or writing "
                    "task as helpfully as possible. Be honest about your "
                    "capabilities. You cannot execute computer commands, "
                    "open applications, or perform external actions through "
                    "this task processor. Never claim an external action "
                    "was performed."
                ),
            },
            {
                "role": "user",
                "content": task_text,
            },
        ],
        max_tokens=1200,
        temperature=0.4,
    )

    result = response.choices[0].message.content

    if not result or not result.strip():
        raise RuntimeError("The AI provider returned an empty response.")

    return result.strip(), model


# --------------------------------------------------
# Background worker
# --------------------------------------------------

def process_task(task_id: str) -> None:
    """Run one queued task and record its final status."""

    with TASKS_LOCK:
        item = TASKS.get(task_id)

        if item is None:
            return

        item["status"] = "running"
        item["started_at"] = time.time()

        task_text = item["task"]

    try:
        result, model = run_ai_task(task_text)

        with TASKS_LOCK:
            item = TASKS.get(task_id)

            if item is None:
                return

            item["status"] = "completed"
            item["result"] = result
            item["model"] = model
            item["finished_at"] = time.time()
            item["error"] = None

        send_jarvis_notification(
            "JARVIS - Task Completed",
            f"Your background task {task_id[:8]} has completed.",
        )

    except Exception as exc:
        error_message = f"{type(exc).__name__}: {exc}"

        print(
            f"JARVIS background task {task_id} failed: {error_message}",
            flush=True,
        )

        with TASKS_LOCK:
            item = TASKS.get(task_id)

            if item is None:
                return

            item["status"] = "failed"
            item["error"] = error_message
            item["finished_at"] = time.time()

        send_jarvis_notification(
            "JARVIS - Task Failed",
            f"Task {task_id[:8]} failed. Check the JARVIS dashboard.",
        )


# --------------------------------------------------
# Submit a background task
# POST /api/tasks
# --------------------------------------------------

@router.post("", status_code=202)
def submit_task(request: BackgroundTaskRequest):
    task_text = request.task.strip()

    if not task_text:
        raise HTTPException(
            status_code=400,
            detail="Enter a task before submitting.",
        )

    with TASKS_LOCK:
        # Remove oldest finished tasks if the storage limit is reached.
        if len(TASKS) >= MAX_TASKS:
            finished_ids = [
                task_id
                for task_id, item in TASKS.items()
                if item["status"] in {"completed", "failed"}
            ]

            for task_id in finished_ids:
                if len(TASKS) < MAX_TASKS:
                    break
                TASKS.pop(task_id, None)

        if len(TASKS) >= MAX_TASKS:
            raise HTTPException(
                status_code=503,
                detail=(
                    "The task list is full. Wait for tasks to finish "
                    "and try again."
                ),
            )

        task_id = secrets.token_urlsafe(16)

        TASKS[task_id] = {
            "task_id": task_id,
            "task": task_text,
            "status": "pending",
            "created_at": time.time(),
            "started_at": None,
            "finished_at": None,
            "result": None,
            "model": None,
            "error": None,
        }

    try:
        EXECUTOR.submit(process_task, task_id)

    except Exception as exc:
        with TASKS_LOCK:
            TASKS.pop(task_id, None)

        raise HTTPException(
            status_code=503,
            detail="JARVIS could not schedule the task.",
        ) from exc

    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Task accepted for background processing.",
    }


# --------------------------------------------------
# List tasks
# GET /api/tasks
# --------------------------------------------------

@router.get("")
def list_tasks():
    with TASKS_LOCK:
        items = [
            dict(item)
            for item in TASKS.values()
        ]

    items.sort(
        key=lambda item: item["created_at"],
        reverse=True,
    )

    return {
        "count": len(items),
        "tasks": items,
    }


# --------------------------------------------------
# Check an individual task
# GET /api/tasks/{task_id}
# --------------------------------------------------

@router.get("/{task_id}")
def get_task(task_id: str):
    with TASKS_LOCK:
        item = TASKS.get(task_id)

        if item is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found. It may have expired or the backend restarted.",
            )

        return dict(item)
