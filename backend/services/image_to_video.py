import logging
import os
from pathlib import Path
from typing import List


def frames_to_video_ffmpeg(frames_dir: str, out_video: str, fps: int = 8):
    """Use ffmpeg to combine frames into a video.

    frames_dir: folder containing frame_0000.png ...
    out_video: full path to mp4
    """
    # Build image pattern relative to frames_dir
    p = Path(frames_dir)
    pattern = str(p / "frame_%04d.png")
    # Call ffmpeg via subprocess through helper to avoid duplication
    from .ffmpeg_utils import images_to_video

    logging.info("Combining frames at %s into %s", frames_dir, out_video)
    return images_to_video(pattern, out_video, fps=fps, add_transition=True)


def try_animatediff(frames_dir: str, out_video: str, fps: int = 8):
    """Placeholder for an AnimateDiff or Stable Video Diffusion integration.
    If the library is installed and a model is available, user can extend this function.
    For now we fallback to ffmpeg-based composition.
    """
    logging.info("AnimateDiff integration not implemented; using ffmpeg fallback")
    return frames_to_video_ffmpeg(frames_dir, out_video, fps=fps)


def create_video_from_frames(frames_dir: str, out_video: str, fps: int = 8):
    # Prefer advanced model-based video methods if present
    try:
        import animatediff  # type: ignore
        logging.info("animatediff detected; would call model pipeline here")
        # The actual integration would go here; since animatediff is complex,
        # we keep a simple fallback to ffmpeg for CPU-friendly behavior.
    except Exception:
        pass
    return try_animatediff(frames_dir, out_video, fps=fps)
