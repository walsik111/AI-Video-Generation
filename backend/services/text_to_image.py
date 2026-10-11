import os
import logging
from pathlib import Path
from typing import List, Tuple

from PIL import Image

# Optional heavy imports are lazy-loaded to avoid failing on systems without them
sd_pipeline = None


def _load_sd_pipeline(device: str = "cpu"):
    global sd_pipeline
    if sd_pipeline is not None:
        return sd_pipeline
    try:
        from diffusers import StableDiffusionPipeline
        import torch
    except Exception as e:
        logging.warning("diffusers or torch not installed: %s", e)
        raise

    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float32 if device == "cpu" else torch.float16,
    )
    pipe = pipe.to(device)
    sd_pipeline = pipe
    return sd_pipeline


def prompt_for_style(prompt: str, style: str) -> str:
    style_map = {
        "cinematic": "cinematic, 35mm, dramatic lighting",
        "anime": "anime style, vibrant colors, cel shading",
        "realistic": "photo-realistic, high detail",
    }
    addition = style_map.get(style, style_map["realistic"])
    return f"{prompt}, {addition}"


def generate_images(
    prompt: str,
    out_dir: str,
    num_images: int = 8,
    resolution: Tuple[int, int] = (512, 512),
    style: str = "realistic",
    device: str = "cpu",
) -> List[str]:
    """Generate a sequence of images from the prompt and save them to out_dir.

    Falls back to placeholder images if diffusers/torch are not available.
    When using actual models, falls back to placeholder frames on any error.
    """
    os.makedirs(out_dir, exist_ok=True)
    images_paths = []
    full_prompt = prompt_for_style(prompt, style)

    # Try to load the Stable Diffusion pipeline
    pipe = None
    try:
        pipe = _load_sd_pipeline(device=device)
    except Exception as e:
        logging.warning(
            "Stable Diffusion unavailable (%s); using placeholder frames. "
            "To enable model generation, install: pip install diffusers transformers torch",
            e,
        )

    width, height = resolution
    for i in range(num_images):
        # Slight prompt jitter for variation
        this_prompt = f"{full_prompt}, variation {i}"
        img = None

        # Attempt to use the model if available
        if pipe is not None:
            try:
                import torch
                result = pipe(this_prompt, height=height, width=width, num_inference_steps=20)
                img = result.images[0]
            except Exception as e:
                logging.error("Generation failed for frame %d: %s", i, e)
                img = None

        # Fallback: create colored placeholder with gradient for visual variety
        if img is None:
            # Create a simple gradient image with color based on frame index
            # This gives visual feedback without needing ML models
            hue_shift = int((i / num_images) * 360)
            r = int(100 + (i * 155 / num_images)) % 256
            g = int(80 + ((i + 3) * 175 / num_images)) % 256
            b = int(120 + ((i + 6) * 135 / num_images)) % 256
            img = Image.new("RGB", resolution, color=(r, g, b))

        path = Path(out_dir) / f"frame_{i:04d}.png"
        img.save(path)
        images_paths.append(str(path))

    return images_paths
