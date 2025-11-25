"""Tests for metadata generation."""

import json
from pathlib import Path

import pytest

from pixel_factory.metadata import (
    create_creature_metadata,
    create_pack_metadata,
    generate_readme,
    load_metadata,
    save_metadata,
)


def test_create_pack_metadata():
    """Test pack metadata creation."""
    metadata = create_pack_metadata(
        pack_id="test_pack",
        pack_name="Test Pack",
        theme_name="test_theme",
        resolution=(32, 32),
        num_creatures=10,
        num_variants=2,
    )

    assert metadata.pack_id == "test_pack"
    assert metadata.pack_name == "Test Pack"
    assert metadata.resolution == (32, 32)
    assert metadata.num_creatures == 10
    assert len(metadata.creatures) == 0


def test_create_creature_metadata():
    """Test creature metadata creation."""
    sprite_sheet_paths = {
        "idle": "path/to/idle.png",
        "walk": "path/to/walk.png",
    }

    metadata = create_creature_metadata(
        creature_id="creature_001",
        theme="test_theme",
        base_color="#ff0000",
        variant_index=0,
        resolution=(32, 32),
        sprite_sheet_paths=sprite_sheet_paths,
        frames_per_animation=4,
    )

    assert metadata.creature_id == "creature_001"
    assert metadata.theme == "test_theme"
    assert metadata.variant_index == 0
    assert metadata.animations["idle"] == 4


def test_save_and_load_metadata(tmp_path):
    """Test saving and loading metadata."""
    # Create metadata
    metadata = create_pack_metadata(
        pack_id="test_pack",
        pack_name="Test Pack",
        theme_name="test_theme",
        resolution=(64, 64),
        num_creatures=5,
        num_variants=3,
    )

    # Add a creature
    creature = create_creature_metadata(
        creature_id="creature_001",
        theme="test_theme",
        base_color="#ff0000",
        variant_index=0,
        resolution=(64, 64),
        sprite_sheet_paths={"idle": "test.png"},
    )
    metadata.creatures.append(creature)

    # Save
    output_path = tmp_path / "metadata.json"
    save_metadata(metadata, output_path)

    assert output_path.exists()

    # Load
    loaded_metadata = load_metadata(output_path)

    assert loaded_metadata.pack_id == metadata.pack_id
    assert loaded_metadata.pack_name == metadata.pack_name
    assert len(loaded_metadata.creatures) == 1
    assert loaded_metadata.creatures[0].creature_id == "creature_001"


def test_generate_readme():
    """Test README generation."""
    metadata = create_pack_metadata(
        pack_id="test_pack",
        pack_name="Test Pack",
        theme_name="cute_forest",
        resolution=(32, 32),
        num_creatures=10,
        num_variants=2,
    )

    readme = generate_readme(metadata)

    assert "Test Pack" in readme
    assert "cute_forest" in readme
    assert "32x32" in readme
    assert "10" in readme
    assert "idle" in readme.lower()
    assert "walk" in readme.lower()


def test_metadata_json_format(tmp_path):
    """Test that saved metadata is valid JSON."""
    metadata = create_pack_metadata(
        pack_id="test_pack",
        pack_name="Test Pack",
        theme_name="test_theme",
        resolution=(32, 32),
        num_creatures=1,
        num_variants=1,
    )

    output_path = tmp_path / "metadata.json"
    save_metadata(metadata, output_path)

    # Verify it's valid JSON
    with open(output_path, "r") as f:
        data = json.load(f)

    assert data["pack_id"] == "test_pack"
    assert isinstance(data["resolution"], list)
