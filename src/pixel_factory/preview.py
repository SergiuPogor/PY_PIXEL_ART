"""
Preview image generation for asset packs.
"""

from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageDraw, ImageFont

from pixel_factory.models import PackMetadata
from pixel_factory.spritesheet import create_grid_layout, upscale_nearest_neighbor


def create_pack_preview(
    sprite_sheets: List[Image.Image],
    pack_metadata: PackMetadata,
    scale: int = 8,
    cols: int = 5,
    output_path: Optional[Path] = None,
) -> Image.Image:
    """
    Create a preview collage showing creatures from the pack.

    Args:
        sprite_sheets: List of sprite sheet images to showcase
        pack_metadata: Metadata for the pack
        scale: Upscale factor for pixel art
        cols: Number of columns in the grid
        output_path: Optional path to save the preview

    Returns:
        Preview image
    """
    if not sprite_sheets:
        raise ValueError("Cannot create preview from empty sprite sheet list")

    # Take first frame from each sprite sheet for preview
    preview_sprites = []
    for sheet in sprite_sheets[:20]:  # Limit to 20 creatures
        # Extract first frame (assume horizontal sprite sheet)
        frame_height = sheet.height
        frame_width = frame_height  # Assuming square frames
        first_frame = sheet.crop((0, 0, frame_width, frame_height))
        # Upscale with nearest neighbor to preserve pixel art
        upscaled = upscale_nearest_neighbor(first_frame, scale)
        preview_sprites.append(upscaled)

    # Create grid
    spacing = 8 * scale
    bg_color = (26, 26, 26, 255)
    grid = create_grid_layout(preview_sprites, cols=cols, spacing=spacing, background_color=bg_color)

    # Add header with pack info
    header_height = 80 * scale
    final_width = grid.width
    final_height = grid.height + header_height

    preview = Image.new("RGBA", (final_width, final_height), bg_color)
    draw = ImageDraw.Draw(preview)

    # Try to use a default font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24 * scale // 4)
        info_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16 * scale // 4)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
        info_font = ImageFont.load_default()

    # Draw title
    title = f"{pack_metadata.pack_name}"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (final_width - title_width) // 2
    draw.text((title_x, 10 * scale), title, fill=(255, 255, 255, 255), font=title_font)

    # Draw info
    info_text = (
        f"Theme: {pack_metadata.theme_name} | "
        f"{pack_metadata.num_creatures} Creatures | "
        f"{pack_metadata.num_variants} Variants | "
        f"{pack_metadata.resolution[0]}x{pack_metadata.resolution[1]}"
    )
    info_bbox = draw.textbbox((0, 0), info_text, font=info_font)
    info_width = info_bbox[2] - info_bbox[0]
    info_x = (final_width - info_width) // 2
    draw.text((info_x, 40 * scale), info_text, fill=(200, 200, 200, 255), font=info_font)

    # Paste grid below header
    preview.paste(grid, (0, header_height), grid)

    if output_path:
        preview.save(output_path, "PNG")

    return preview


def create_creature_showcase(
    creature_dir: Path,
    output_path: Path,
    scale: int = 6,
) -> Image.Image:
    """
    Create a showcase image for a single creature showing all animations.

    Args:
        creature_dir: Directory containing creature sprite sheets
        output_path: Path to save the showcase
        scale: Upscale factor

    Returns:
        Showcase image
    """
    sprite_sheets_dir = creature_dir / "sprite_sheets"

    # Load sprite sheets
    sprite_sheets = []
    for sheet_file in sorted(sprite_sheets_dir.glob("*.png")):
        if "combined" not in sheet_file.name and "variant" not in sheet_file.name:
            sprite_sheets.append(Image.open(sheet_file))

    if not sprite_sheets:
        raise ValueError(f"No sprite sheets found in {sprite_sheets_dir}")

    # Upscale and stack
    upscaled_sheets = [upscale_nearest_neighbor(sheet, scale) for sheet in sprite_sheets]

    # Calculate dimensions
    max_width = max(sheet.width for sheet in upscaled_sheets)
    total_height = sum(sheet.height for sheet in upscaled_sheets)
    spacing = 4 * scale
    total_height += spacing * (len(upscaled_sheets) - 1)

    # Create showcase
    showcase = Image.new("RGBA", (max_width, total_height), (26, 26, 26, 255))

    y_offset = 0
    for sheet in upscaled_sheets:
        showcase.paste(sheet, (0, y_offset), sheet)
        y_offset += sheet.height + spacing

    showcase.save(output_path, "PNG")
    return showcase
