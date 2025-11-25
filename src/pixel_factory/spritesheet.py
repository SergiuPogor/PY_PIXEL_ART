"""
Sprite sheet composition and color variant generation.
"""

from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw

from pixel_factory.models import AnimationType


def apply_color_variant(base_image: Image.Image, hue_shift: int, saturation_factor: float) -> Image.Image:
    """
    Apply color transformation to create a variant.

    Args:
        base_image: Source image in RGBA mode
        hue_shift: Degrees to shift hue (-180 to 180)
        saturation_factor: Multiplier for saturation (0.0 to 2.0)

    Returns:
        New image with transformed colors
    """
    # Convert to HSV for color manipulation
    rgb_image = base_image.convert("RGB")
    hsv_image = rgb_image.convert("HSV")

    # Get alpha channel separately
    alpha = base_image.split()[3] if base_image.mode == "RGBA" else None

    # Apply transformations
    hsv_data = []
    for h, s, v in hsv_image.getdata():
        # Shift hue
        new_h = (h + hue_shift) % 256
        # Adjust saturation
        new_s = min(255, max(0, int(s * saturation_factor)))
        hsv_data.append((new_h, new_s, v))

    hsv_image.putdata(hsv_data)
    result = hsv_image.convert("RGB")

    # Restore alpha
    if alpha:
        result = result.convert("RGBA")
        result.putalpha(alpha)
    else:
        result = result.convert("RGBA")

    return result


def create_animation_sprite_sheet(
    frames: List[Image.Image],
    spacing: int = 0,
    background_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
) -> Image.Image:
    """
    Compose frames into a horizontal sprite sheet.

    Args:
        frames: List of frame images
        spacing: Pixels between frames
        background_color: RGBA background color

    Returns:
        Sprite sheet image
    """
    if not frames:
        raise ValueError("Cannot create sprite sheet from empty frame list")

    frame_width, frame_height = frames[0].size
    total_width = len(frames) * frame_width + (len(frames) - 1) * spacing

    sprite_sheet = Image.new("RGBA", (total_width, frame_height), background_color)

    x_offset = 0
    for frame in frames:
        sprite_sheet.paste(frame, (x_offset, 0), frame if frame.mode == "RGBA" else None)
        x_offset += frame_width + spacing

    return sprite_sheet


def create_combined_sprite_sheet(
    animation_frames: dict[AnimationType, List[Image.Image]],
    spacing: int = 2,
    background_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
) -> Image.Image:
    """
    Create a combined sprite sheet with all animations stacked vertically.

    Args:
        animation_frames: Dictionary mapping animation types to frame lists
        spacing: Pixels between rows and frames
        background_color: RGBA background color

    Returns:
        Combined sprite sheet with all animations
    """
    if not animation_frames:
        raise ValueError("Cannot create combined sprite sheet from empty animations")

    # Calculate dimensions
    animation_types = sorted(animation_frames.keys(), key=lambda x: x.value)
    first_frames = next(iter(animation_frames.values()))
    frame_width, frame_height = first_frames[0].size
    max_frames = max(len(frames) for frames in animation_frames.values())

    total_width = max_frames * frame_width + (max_frames - 1) * spacing
    total_height = len(animation_types) * frame_height + (len(animation_types) - 1) * spacing

    sprite_sheet = Image.new("RGBA", (total_width, total_height), background_color)

    y_offset = 0
    for anim_type in animation_types:
        frames = animation_frames[anim_type]
        x_offset = 0

        for frame in frames:
            sprite_sheet.paste(frame, (x_offset, y_offset), frame if frame.mode == "RGBA" else None)
            x_offset += frame_width + spacing

        y_offset += frame_height + spacing

    return sprite_sheet


def save_frames_to_disk(
    frames: List[Image.Image],
    output_dir: Path,
    creature_id: str,
    animation_type: AnimationType,
    variant_index: int = 0,
) -> List[Path]:
    """
    Save animation frames to disk.

    Args:
        frames: List of frame images
        output_dir: Base output directory
        creature_id: Identifier for the creature
        animation_type: Type of animation
        variant_index: Color variant index

    Returns:
        List of paths to saved files
    """
    # Create directory structure
    creature_dir = output_dir / creature_id / animation_type.value
    creature_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for i, frame in enumerate(frames, 1):
        if variant_index > 0:
            filename = f"frame_{i:02d}_variant_{variant_index}.png"
        else:
            filename = f"frame_{i:02d}.png"

        frame_path = creature_dir / filename
        frame.save(frame_path, "PNG")
        saved_paths.append(frame_path)

    return saved_paths


def save_sprite_sheet(
    sprite_sheet: Image.Image,
    output_dir: Path,
    creature_id: str,
    animation_type: AnimationType,
    variant_index: int = 0,
    is_combined: bool = False,
) -> Path:
    """
    Save sprite sheet to disk.

    Args:
        sprite_sheet: Sprite sheet image
        output_dir: Base output directory
        creature_id: Identifier for the creature
        animation_type: Type of animation (ignored if is_combined=True)
        variant_index: Color variant index
        is_combined: Whether this is a combined sprite sheet

    Returns:
        Path to saved file
    """
    sheets_dir = output_dir / creature_id / "sprite_sheets"
    sheets_dir.mkdir(parents=True, exist_ok=True)

    if is_combined:
        if variant_index > 0:
            filename = f"combined_variant_{variant_index}.png"
        else:
            filename = "combined.png"
    else:
        if variant_index > 0:
            filename = f"{animation_type.value}_variant_{variant_index}.png"
        else:
            filename = f"{animation_type.value}.png"

    sheet_path = sheets_dir / filename
    sprite_sheet.save(sheet_path, "PNG")
    return sheet_path


def upscale_nearest_neighbor(image: Image.Image, scale: int) -> Image.Image:
    """
    Upscale image using nearest neighbor (preserves pixel art look).

    Args:
        image: Source image
        scale: Scale factor (integer)

    Returns:
        Upscaled image
    """
    new_size = (image.width * scale, image.height * scale)
    return image.resize(new_size, Image.NEAREST)


def create_grid_layout(
    images: List[Image.Image],
    cols: int,
    spacing: int = 4,
    background_color: Tuple[int, int, int, int] = (30, 30, 30, 255),
) -> Image.Image:
    """
    Arrange images in a grid layout.

    Args:
        images: List of images to arrange
        cols: Number of columns
        spacing: Pixels between images
        background_color: RGBA background color

    Returns:
        Grid layout image
    """
    if not images:
        raise ValueError("Cannot create grid from empty image list")

    img_width, img_height = images[0].size
    rows = (len(images) + cols - 1) // cols

    total_width = cols * img_width + (cols + 1) * spacing
    total_height = rows * img_height + (rows + 1) * spacing

    grid = Image.new("RGBA", (total_width, total_height), background_color)

    for idx, img in enumerate(images):
        row = idx // cols
        col = idx % cols
        x = spacing + col * (img_width + spacing)
        y = spacing + row * (img_height + spacing)
        grid.paste(img, (x, y), img if img.mode == "RGBA" else None)

    return grid
