import os
import uuid
import shutil
import logging
import sys
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

# Handle imports for both module and direct execution
try:
    from models.job import Job, JobStatus
    from services import text_to_image, image_to_video
except ImportError:
    from ..models.job import Job, JobStatus
    from ..services import text_to_image, image_to_video

router = APIRouter()

# Use OS_specific work directory: /tmp for Unix/Mac, /data for Docker
import tempfile
default_work_dir = os.path.join(tempfile.gettempdir(), "ai-video-gen") if os.name != "nt" else os.getenv("WORK_DIR", "C:\\data")
BASE_DIR = Path(os.getenv("WORK_DIR", default_work_dir))
JOBS_DIR = BASE_DIR / "jobs"
try:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
except OSError as e:
    logging.warning("Could not create JOBS_DIR %s: %s; using temp dir", JOBS_DIR, e)
    JOBS_DIR = Path(tempfile.gettempdir()) / "ai-video-gen" / "jobs"
    JOBS_DIR.mkdir(parents=True, exist_ok=True)

# Simple in-memory registry; lightweight and beginner-friendly
JOB_REGISTRY = {}


class GenerateRequest(BaseModel):
    prompt: str
    duration: int = 3
    resolution: str = "512x512"
    style: Optional[str] = "realistic"


@router.post("/generate-video")
async def generate_video(req: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    job = Job(
        job_id=job_id,
        prompt=req.prompt,
        duration=req.duration,
        resolution=req.resolution,
        style=req.style,
        status=JobStatus.PENDING,
    )
    JOB_REGISTRY[job_id] = job

    # Schedule background task
    background_tasks.add_task(_run_generation, job_id, str(job_dir), req.dict())

    return {"job_id": job_id}


@router.get("/status/{job_id}")
async def status(job_id: str):
    job = JOB_REGISTRY.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job.dict()


@router.get("/download/{job_id}")
async def download(job_id: str):
    job = JOB_REGISTRY.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job.status != JobStatus.COMPLETED or not job.output_path:
        raise HTTPException(status_code=400, detail="job not ready for download")
    return FileResponse(job.output_path, media_type="video/mp4", filename=f"{job_id}.mp4")


def _run_generation(job_id: str, job_dir: str, req: dict):
    """Background generation pipeline orchestration."""
    logging.info("Starting job %s", job_id)
    job: Job = JOB_REGISTRY[job_id]
    job.status = JobStatus.RUNNING
    try:
        prompt = req.get("prompt")
        duration = int(req.get("duration", 3))
        resolution = req.get("resolution", "512x512")
        style = req.get("style", "realistic")

        width, height = [int(x) for x in resolution.split("x")]
        fps = int(os.getenv("FPS", "8"))
        num_frames = max(4, duration * fps)

        frames_dir = Path(job_dir) / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        # 1) Text -> image frames
        imgs = text_to_image.generate_images(
            prompt=prompt,
            out_dir=str(frames_dir),
            num_images=num_frames,
            resolution=(width, height),
            style=style,
            device=os.getenv("DEVICE", "cpu"),
        )

        # 2) Image frames -> short video
        out_video = Path(job_dir) / f"{job_id}.mp4"
        image_to_video.create_video_from_frames(str(frames_dir), str(out_video), fps=fps)

        job.status = JobStatus.COMPLETED
        job.output_path = str(out_video)
        logging.info("Job %s completed: %s", job_id, job.output_path)
    except Exception as e:
        logging.exception("Job %s failed", job_id)
        job.status = JobStatus.FAILED
        job.error = str(e)
