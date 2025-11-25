"""
Packaging and export functionality for asset packs.
"""

import logging
import shutil
import zipfile
from pathlib import Path
from typing import Optional

from pixel_factory.models import PackMetadata

logger = logging.getLogger(__name__)


def create_pack_archive(
    pack_dir: Path,
    output_path: Optional[Path] = None,
    compression: int = zipfile.ZIP_DEFLATED,
) -> Path:
    """
    Create a ZIP archive of the complete asset pack.

    Args:
        pack_dir: Directory containing the pack
        output_path: Optional custom output path for the zip file
        compression: Compression method (default: ZIP_DEFLATED)

    Returns:
        Path to the created ZIP file
    """
    if output_path is None:
        output_path = pack_dir.parent / f"{pack_dir.name}.zip"

    logger.info(f"Creating archive: {output_path}")

    with zipfile.ZipFile(output_path, "w", compression) as zipf:
        for file_path in pack_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(pack_dir.parent)
                zipf.write(file_path, arcname)
                logger.debug(f"Added to archive: {arcname}")

    logger.info(f"Archive created successfully: {output_path}")
    return output_path


def generate_pack_filename(
    pack_name: str,
    theme_name: str,
    resolution: tuple[int, int],
    pack_id: Optional[str] = None,
) -> str:
    """
    Generate a standardized filename for a pack.

    Args:
        pack_name: Name of the pack
        theme_name: Theme name
        resolution: Resolution tuple
        pack_id: Optional pack ID

    Returns:
        Standardized filename (without extension)
    """
    # Sanitize names
    safe_name = pack_name.lower().replace(" ", "_")
    safe_theme = theme_name.lower().replace(" ", "_")

    parts = ["pixel_creatures"]

    if pack_id:
        parts.append(pack_id)

    parts.extend([safe_theme, f"{resolution[0]}x{resolution[1]}"])

    return "_".join(parts)


def cleanup_temporary_files(pack_dir: Path, keep_zip: bool = True) -> None:
    """
    Clean up temporary files after packaging.

    Args:
        pack_dir: Directory containing the pack
        keep_zip: Whether to keep the ZIP file
    """
    if pack_dir.exists() and pack_dir.is_dir():
        logger.info(f"Cleaning up temporary files: {pack_dir}")
        shutil.rmtree(pack_dir)

    if not keep_zip:
        zip_path = pack_dir.parent / f"{pack_dir.name}.zip"
        if zip_path.exists():
            logger.info(f"Removing ZIP file: {zip_path}")
            zip_path.unlink()


def validate_pack_structure(pack_dir: Path) -> bool:
    """
    Validate that a pack directory has the expected structure.

    Args:
        pack_dir: Directory to validate

    Returns:
        True if structure is valid, False otherwise
    """
    required_paths = [
        pack_dir / "creatures",
        pack_dir / "metadata.json",
        pack_dir / "README.txt",
    ]

    for path in required_paths:
        if not path.exists():
            logger.error(f"Missing required path: {path}")
            return False

    # Check for at least one creature
    creatures_dir = pack_dir / "creatures"
    creature_dirs = [d for d in creatures_dir.iterdir() if d.is_dir()]

    if not creature_dirs:
        logger.error("No creature directories found")
        return False

    # Validate first creature has required structure
    first_creature = creature_dirs[0]
    required_subdirs = ["idle", "walk", "attack", "sprite_sheets"]

    for subdir in required_subdirs:
        if not (first_creature / subdir).exists():
            logger.error(f"Missing required subdirectory: {first_creature / subdir}")
            return False

    logger.info("Pack structure validation passed")
    return True


def get_pack_statistics(pack_dir: Path) -> dict:
    """
    Calculate statistics about the pack.

    Args:
        pack_dir: Pack directory

    Returns:
        Dictionary with statistics
    """
    stats = {
        "total_files": 0,
        "total_size_bytes": 0,
        "num_creatures": 0,
        "num_frames": 0,
        "num_sprite_sheets": 0,
    }

    if not pack_dir.exists():
        return stats

    # Count files and sizes
    for file_path in pack_dir.rglob("*"):
        if file_path.is_file():
            stats["total_files"] += 1
            stats["total_size_bytes"] += file_path.stat().st_size

            if "frame_" in file_path.name:
                stats["num_frames"] += 1
            elif file_path.parent.name == "sprite_sheets":
                stats["num_sprite_sheets"] += 1

    # Count creatures
    creatures_dir = pack_dir / "creatures"
    if creatures_dir.exists():
        stats["num_creatures"] = len([d for d in creatures_dir.iterdir() if d.is_dir()])

    # Convert size to MB
    stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)

    return stats


def export_pack(
    pack_dir: Path,
    output_dir: Path,
    pack_metadata: PackMetadata,
    create_archive: bool = True,
    cleanup: bool = False,
) -> dict:
    """
    Export a complete pack with optional archiving and cleanup.

    Args:
        pack_dir: Source pack directory
        output_dir: Output directory for export
        pack_metadata: Pack metadata
        create_archive: Whether to create a ZIP archive
        cleanup: Whether to clean up temporary files after archiving

    Returns:
        Dictionary with export information
    """
    export_info = {
        "pack_dir": str(pack_dir),
        "success": False,
        "archive_path": None,
        "statistics": {},
    }

    try:
        # Validate structure
        if not validate_pack_structure(pack_dir):
            logger.error("Pack structure validation failed")
            return export_info

        # Get statistics
        stats = get_pack_statistics(pack_dir)
        export_info["statistics"] = stats
        logger.info(f"Pack statistics: {stats}")

        # Create archive if requested
        if create_archive:
            archive_filename = generate_pack_filename(
                pack_metadata.pack_name,
                pack_metadata.theme_name,
                pack_metadata.resolution,
                pack_metadata.pack_id,
            )
            archive_path = output_dir / f"{archive_filename}.zip"
            created_archive = create_pack_archive(pack_dir, archive_path)
            export_info["archive_path"] = str(created_archive)

            # Cleanup if requested
            if cleanup:
                cleanup_temporary_files(pack_dir, keep_zip=True)

        export_info["success"] = True
        logger.info("Pack export completed successfully")

    except Exception as e:
        logger.error(f"Error during pack export: {e}", exc_info=True)
        export_info["error"] = str(e)

    return export_info
