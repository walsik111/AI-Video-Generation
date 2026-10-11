#!/usr/bin/env python3
"""
Test script to run the full video generation pipeline with placeholder frames.
Useful for testing the API flow without downloading heavy ML models.

Usage:
  python3 test_pipeline.py
  
This will create a sample video in ./test_output/test_video.mp4
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from services import text_to_image, image_to_video


def test_full_pipeline():
    """Run a complete video generation pipeline with placeholder frames."""
    print("[TEST] Starting full pipeline test...")

    # Create temp working directory
    work_dir = Path("test_output")
    work_dir.mkdir(exist_ok=True)
    frames_dir = work_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    # Test parameters
    prompt = "A serene landscape at sunrise with mountains and a lake"
    duration = 3
    fps = 8
    num_frames = duration * fps
    resolution = (512, 512)
    style = "cinematic"

    try:
        # Step 1: Generate frames
        print(f"[TEST] Step 1: Generating {num_frames} placeholder frames...")
        img_paths = text_to_image.generate_images(
            prompt=prompt,
            out_dir=str(frames_dir),
            num_images=num_frames,
            resolution=resolution,
            style=style,
            device="cpu",
        )
        print(f"[TEST] ✓ Generated {len(img_paths)} frames")
        for p in img_paths[:2]:
            print(f"       {p}")
        if len(img_paths) > 2:
            print(f"       ... and {len(img_paths) - 2} more")

        # Step 2: Combine frames into video
        print("\n[TEST] Step 2: Combining frames into video with ffmpeg...")
        out_video = work_dir / "test_video.mp4"
        image_to_video.create_video_from_frames(
            str(frames_dir), str(out_video), fps=fps
        )
        print(f"[TEST] ✓ Video created: {out_video}")

        # Check file size
        if out_video.exists():
            size_mb = out_video.stat().st_size / (1024 * 1024)
            print(f"[TEST] Video size: {size_mb:.1f} MB")
        else:
            print("[TEST] ✗ Video file not created!")
            return False

        print("\n[TEST] ✓ All steps completed successfully!")
        print(f"[TEST] Output: {out_video.absolute()}")
        return True

    except Exception as e:
        print(f"[TEST] ✗ Pipeline failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_pipeline()
    sys.exit(0 if success else 1)
