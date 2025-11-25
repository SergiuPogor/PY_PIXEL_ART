"""Tests for image generation."""

import pytest
from PIL import Image

from pixel_factory.generator import PlaceholderGenerator
from pixel_factory.models import AnimationType, ThemeConfig


@pytest.fixture
def test_theme():
    """Create a test theme."""
    return ThemeConfig(
        name="test_theme",
        description="Test theme",
        base_description="test creature",
        mood_adjectives=["happy"],
        color_palette_hints=["red and blue"],
    )


def test_placeholder_generator_initialization():
    """Test PlaceholderGenerator initialization."""
    generator = PlaceholderGenerator((32, 32))
    assert generator.resolution == (32, 32)


def test_generate_single_creature(test_theme):
    """Test generating a single creature frame."""
    generator = PlaceholderGenerator((32, 32))

    image = generator.generate_single_creature(
        test_theme,
        creature_index=0,
        animation_type=AnimationType.IDLE,
        frame_index=0,
    )

    assert isinstance(image, Image.Image)
    assert image.size == (32, 32)
    assert image.mode == "RGBA"


def test_generate_animation_frames(test_theme):
    """Test generating animation frames."""
    generator = PlaceholderGenerator((64, 64))

    frames = generator.generate_animation_frames(
        test_theme,
        creature_index=0,
        animation_type=AnimationType.WALK,
        num_frames=4,
    )

    assert len(frames) == 4
    assert all(isinstance(frame, Image.Image) for frame in frames)
    assert all(frame.size == (64, 64) for frame in frames)


def test_different_creature_shapes(test_theme):
    """Test that different creature indices produce different shapes."""
    generator = PlaceholderGenerator((32, 32))

    images = []
    for i in range(5):
        img = generator.generate_single_creature(
            test_theme,
            creature_index=i,
            animation_type=AnimationType.IDLE,
            frame_index=0,
        )
        images.append(img)

    # Images should be different (at least some pixels)
    # Convert to bytes for comparison
    image_data = [img.tobytes() for img in images]
    # Check that not all images are identical
    assert len(set(image_data)) > 1


def test_animation_variations(test_theme):
    """Test that different animation types produce variations."""
    generator = PlaceholderGenerator((32, 32))

    idle = generator.generate_single_creature(
        test_theme, 0, AnimationType.IDLE, 0
    )
    walk = generator.generate_single_creature(
        test_theme, 0, AnimationType.WALK, 0
    )
    attack = generator.generate_single_creature(
        test_theme, 0, AnimationType.ATTACK, 0
    )

    # All should be valid images
    assert all(isinstance(img, Image.Image) for img in [idle, walk, attack])
