from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict
import uuid
from datetime import datetime

app = FastAPI()

class RenderPayload(BaseModel):
    project_id: str
    template_id: str
    parameters: Dict
    quality: str
    user_id: str
    callback_url: str

@app.post("/render")
async def render(payload: RenderPayload):
    # Simulate job id and processing time
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    estimated_duration = 5  # in seconds

    # Respond immediately, as if job is queued
    return {
        "job_id": job_id,
        "estimated_duration": estimated_duration,
        "message": f"Render job for template {payload.template_id} accepted."
    }

@app.get("/render/status/{job_id}")
async def get_status(job_id: str):
    # Always return completed with fake video
    return {
        "status": "completed",
        "video_url": f"https://dummy.video.storage/{job_id}.mp4",
        "thumbnail_url": f"https://dummy.video.storage/{job_id}.jpg",
        "duration_seconds": 30,
        "file_size_mb": 12.7
    }

@app.get("/health")
def health():
    return {"status": "render engine healthy", "timestamp": datetime.utcnow()}
