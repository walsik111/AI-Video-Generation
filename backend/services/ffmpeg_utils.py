import subprocess
import shlex
import logging
from pathlib import Path


def run_ffmpeg_command(cmd: str):
    logging.info("Running ffmpeg: %s", cmd)
    proc = subprocess.run(shlex.split(cmd), capture_output=True)
    if proc.returncode != 0:
        logging.error("ffmpeg failed: %s", proc.stderr.decode(errors='ignore'))
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.decode(errors='ignore')}")
    return proc.stdout


def images_to_video(image_pattern: str, out_path: str, fps: int = 8, add_transition: bool = True):
    """Combine frames into a video. image_pattern e.g. "frame_%04d.png""" 
    out_dir = str(Path(out_path).parent)
    # Basic command: use image sequence pattern
    if add_transition:
        # For simplicity add a fade in/out across whole video using filter_complex
        cmd = (
            f"ffmpeg -y -framerate {fps} -i {image_pattern} "
            f"-vf \"format=yuv420p,fade=t=in:st=0:d=1,fade=t=out:st=\"( \"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\" )\"\"\"\"\"\"\"\"\"\"\"\"\"\":d=1\" -movflags +faststart {out_path}"
        )
        # The above attempt to craft nested quotes can be fragile; use a simple command instead
    cmd = f"ffmpeg -y -framerate {fps} -i {image_pattern} -c:v libx264 -pix_fmt yuv420p {out_path}"
    return run_ffmpeg_command(cmd)


def concatenate_videos(video_files: list, out_path: str):
    # Create a temporary text file listing inputs
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
        for v in video_files:
            f.write(f"file '{Path(v).as_posix()}'\n")
        listfile = f.name
    cmd = f"ffmpeg -y -f concat -safe 0 -i {listfile} -c copy {out_path}"
    try:
        return run_ffmpeg_command(cmd)
    finally:
        Path(listfile).unlink(missing_ok=True)
