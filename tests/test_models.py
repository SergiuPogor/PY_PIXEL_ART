"""Tests for data models."""

import pytest

from pixel_factory.models import (
    AnimationType,
    CreatureMetadata,
    GenerationConfig,
    PackMetadata,
    ThemeConfig,
)


def test_animation_type_enum():
    """Test AnimationType enum."""
    assert AnimationType.IDLE.value == "idle"
    assert AnimationType.WALK.value == "walk"
    assert AnimationType.ATTACK.value == "attack"


def test_theme_config_build_prompt():
    """Test theme prompt building."""
    theme = ThemeConfig(
        name="test_theme",
        description="Test theme",
        base_description="test creature",
        mood_adjectives=["happy", "sad"],
        color_palette_hints=["red", "blue"],
    )

    prompt_0 = theme.build_prompt(0)
    assert "test creature" in prompt_0
    assert "happy" in prompt_0
    assert "red" in prompt_0

    prompt_1 = theme.build_prompt(1)
    assert "sad" in prompt_1
    assert "blue" in prompt_1


def test_creature_metadata_to_dict():
    """Test CreatureMetadata serialization."""
    metadata = CreatureMetadata(
        creature_id="creature_001",
        theme="test_theme",
        base_color="#ff0000",
        variant_index=0,
        resolution=(32, 32),
        animations={"idle": 4, "walk": 4},
        sprite_sheet_paths={"idle": "path/to/idle.png"},
    )

    data = metadata.to_dict()
    assert data["creature_id"] == "creature_001"
    assert data["resolution"] == [32, 32]
    assert data["animations"]["idle"] == 4


def test_pack_metadata_to_dict():
    """Test PackMetadata serialization."""
    creature = CreatureMetadata(
        creature_id="creature_001",
        theme="test_theme",
        base_color="#ff0000",
        variant_index=0,
        resolution=(32, 32),
        animations={"idle": 4},
        sprite_sheet_paths={"idle": "path/to/idle.png"},
    )

    pack = PackMetadata(
        pack_id="test_pack",
        pack_name="Test Pack",
        theme_name="test_theme",
        generation_date="2024-01-01T00:00:00",
        resolution=(32, 32),
        num_creatures=1,
        num_variants=1,
        animation_types=["idle", "walk", "attack"],
        creatures=[creature],
    )

    data = pack.to_dict()
    assert data["pack_id"] == "test_pack"
    assert len(data["creatures"]) == 1
    assert data["resolution"] == [32, 32]


def test_generation_config_animation_types():
    """Test GenerationConfig animation types property."""
    from pathlib import Path

    config = GenerationConfig(
        pack_name="test_pack",
        theme_name="test_theme",
        resolution=(32, 32),
        num_creatures=10,
        num_variants=2,
        output_dir=Path("output"),
    )

    anim_types = config.animation_types
    assert len(anim_types) == 3
    assert AnimationType.IDLE in anim_types
    assert AnimationType.WALK in anim_types
    assert AnimationType.ATTACK in anim_types
