"""Tests for sprite sheet composition."""

import pytest
from PIL import Image

from pixel_factory.models import AnimationType
from pixel_factory.spritesheet import (
    apply_color_variant,
    create_animation_sprite_sheet,
    create_combined_sprite_sheet,
    create_grid_layout,
    upscale_nearest_neighbor,
)


@pytest.fixture
def test_frames():
    """Create test frames."""
    return [
        Image.new("RGBA", (32, 32), (255, 0, 0, 255)),
        Image.new("RGBA", (32, 32), (0, 255, 0, 255)),
        Image.new("RGBA", (32, 32), (0, 0, 255, 255)),
        Image.new("RGBA", (32, 32), (255, 255, 0, 255)),
    ]


def test_create_animation_sprite_sheet(test_frames):
    """Test creating an animation sprite sheet."""
    sprite_sheet = create_animation_sprite_sheet(test_frames, spacing=0)

    assert isinstance(sprite_sheet, Image.Image)
    # 4 frames * 32 pixels each = 128 pixels wide
    assert sprite_sheet.size == (128, 32)
    assert sprite_sheet.mode == "RGBA"


def test_create_animation_sprite_sheet_with_spacing(test_frames):
    """Test sprite sheet with spacing."""
    sprite_sheet = create_animation_sprite_sheet(test_frames, spacing=2)

    # 4 frames * 32 pixels + 3 spacings * 2 pixels = 134 pixels
    assert sprite_sheet.size == (134, 32)


def test_create_animation_sprite_sheet_empty():
    """Test that empty frame list raises error."""
    with pytest.raises(ValueError):
        create_animation_sprite_sheet([])


def test_create_combined_sprite_sheet(test_frames):
    """Test creating combined sprite sheet."""
    animation_frames = {
        AnimationType.IDLE: test_frames,
        AnimationType.WALK: test_frames,
        AnimationType.ATTACK: test_frames,
    }

    combined = create_combined_sprite_sheet(animation_frames, spacing=2)

    assert isinstance(combined, Image.Image)
    # Width: 4 frames * 32 + 3 spacings = 134
    # Height: 3 animations * 32 + 2 spacings = 100
    assert combined.size == (134, 100)


def test_apply_color_variant():
    """Test color variant application."""
    base_image = Image.new("RGBA", (32, 32), (255, 0, 0, 255))

    variant = apply_color_variant(base_image, hue_shift=60, saturation_factor=1.2)

    assert isinstance(variant, Image.Image)
    assert variant.size == base_image.size
    assert variant.mode == "RGBA"


def test_upscale_nearest_neighbor():
    """Test pixel art upscaling."""
    image = Image.new("RGBA", (16, 16), (255, 0, 0, 255))

    upscaled = upscale_nearest_neighbor(image, scale=4)

    assert upscaled.size == (64, 64)


def test_create_grid_layout():
    """Test grid layout creation."""
    images = [
        Image.new("RGBA", (32, 32), (255, 0, 0, 255)),
        Image.new("RGBA", (32, 32), (0, 255, 0, 255)),
        Image.new("RGBA", (32, 32), (0, 0, 255, 255)),
    ]

    grid = create_grid_layout(images, cols=2, spacing=4)

    assert isinstance(grid, Image.Image)
    # 2 columns: 2*32 + 3*4 spacing = 76 width
    # 2 rows (3 images, 2 cols): 2*32 + 3*4 spacing = 76 height
    assert grid.size == (76, 76)


def test_create_grid_layout_empty():
    """Test that empty image list raises error."""
    with pytest.raises(ValueError):
        create_grid_layout([], cols=2)
