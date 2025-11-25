"""Tests for packaging functionality."""

import zipfile
from pathlib import Path

import pytest

from pixel_factory.metadata import create_pack_metadata
from pixel_factory.packaging import (
    create_pack_archive,
    generate_pack_filename,
    get_pack_statistics,
    validate_pack_structure,
)


@pytest.fixture
def test_pack_dir(tmp_path):
    """Create a test pack directory structure."""
    pack_dir = tmp_path / "test_pack"

    # Create directory structure
    creatures_dir = pack_dir / "creatures" / "creature_001"
    (creatures_dir / "idle").mkdir(parents=True)
    (creatures_dir / "walk").mkdir(parents=True)
    (creatures_dir / "attack").mkdir(parents=True)
    (creatures_dir / "sprite_sheets").mkdir(parents=True)

    # Create dummy files
    (creatures_dir / "idle" / "frame_01.png").write_text("dummy")
    (creatures_dir / "walk" / "frame_01.png").write_text("dummy")
    (creatures_dir / "attack" / "frame_01.png").write_text("dummy")
    (creatures_dir / "sprite_sheets" / "idle.png").write_text("dummy")

    (pack_dir / "metadata.json").write_text('{"test": "data"}')
    (pack_dir / "README.txt").write_text("Test README")

    return pack_dir


def test_validate_pack_structure(test_pack_dir):
    """Test pack structure validation."""
    assert validate_pack_structure(test_pack_dir) is True


def test_validate_pack_structure_missing_metadata(tmp_path):
    """Test validation fails with missing metadata."""
    pack_dir = tmp_path / "incomplete_pack"
    (pack_dir / "creatures").mkdir(parents=True)

    assert validate_pack_structure(pack_dir) is False


def test_get_pack_statistics(test_pack_dir):
    """Test pack statistics calculation."""
    stats = get_pack_statistics(test_pack_dir)

    assert stats["num_creatures"] == 1
    assert stats["total_files"] > 0
    assert stats["num_frames"] == 3  # 3 frame files
    assert stats["num_sprite_sheets"] == 1


def test_get_pack_statistics_nonexistent():
    """Test statistics for nonexistent pack."""
    stats = get_pack_statistics(Path("/nonexistent"))

    assert stats["total_files"] == 0
    assert stats["num_creatures"] == 0


def test_generate_pack_filename():
    """Test pack filename generation."""
    filename = generate_pack_filename(
        pack_name="My Test Pack",
        theme_name="Cute Forest",
        resolution=(32, 32),
        pack_id="001",
    )

    assert "pixel_creatures" in filename
    assert "001" in filename
    assert "cute_forest" in filename
    assert "32x32" in filename
    assert " " not in filename  # No spaces


def test_create_pack_archive(test_pack_dir, tmp_path):
    """Test ZIP archive creation."""
    output_path = tmp_path / "test_pack.zip"

    created_path = create_pack_archive(test_pack_dir, output_path)

    assert created_path == output_path
    assert output_path.exists()

    # Verify archive contents
    with zipfile.ZipFile(output_path, "r") as zipf:
        names = zipf.namelist()
        assert any("metadata.json" in name for name in names)
        assert any("README.txt" in name for name in names)
        assert any("creature_001" in name for name in names)


def test_create_pack_archive_default_path(test_pack_dir):
    """Test archive creation with default path."""
    created_path = create_pack_archive(test_pack_dir)

    assert created_path.exists()
    assert created_path.suffix == ".zip"
    assert "test_pack" in created_path.name

    # Cleanup
    created_path.unlink()
