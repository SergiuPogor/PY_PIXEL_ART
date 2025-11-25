"""
Main generation pipeline orchestration.
"""

import logging
from pathlib import Path
from typing import List, Optional

from PIL import Image

from pixel_factory.config import get_config
from pixel_factory.generator import PixelArtGenerator, PlaceholderGenerator
from pixel_factory.metadata import (
    create_creature_metadata,
    create_pack_metadata,
    save_metadata,
    save_readme,
)
from pixel_factory.models import AnimationType, GenerationConfig, PackMetadata
from pixel_factory.packaging import export_pack
from pixel_factory.preview import create_pack_preview
from pixel_factory.spritesheet import (
    apply_color_variant,
    create_animation_sprite_sheet,
    create_combined_sprite_sheet,
    save_frames_to_disk,
    save_sprite_sheet,
)

logger = logging.getLogger(__name__)


class CreaturePackPipeline:
    """Main pipeline for generating creature asset packs."""

    def __init__(
        self,
        config: GenerationConfig,
        generator: Optional[PixelArtGenerator] = None,
    ) -> None:
        """
        Initialize the pipeline.

        Args:
            config: Generation configuration
            generator: Optional custom generator (defaults to PlaceholderGenerator)
        """
        self.config = config
        self.generator = generator or PlaceholderGenerator(config.resolution)
        self.theme_config = get_config().get_theme(config.theme_name)

    def generate_creature(
        self,
        creature_index: int,
        variant_index: int = 0,
    ) -> tuple[str, dict[AnimationType, List[Image.Image]]]:
        """
        Generate all animation frames for a single creature.

        Args:
            creature_index: Index of the creature
            variant_index: Color variant index (0 = base)

        Returns:
            Tuple of (creature_id, animation_frames_dict)
        """
        creature_id = f"creature_{creature_index + 1:03d}"
        logger.info(f"Generating {creature_id} (variant {variant_index})")

        animation_frames = {}

        for anim_type in self.config.animation_types:
            logger.debug(f"  Generating {anim_type.value} animation")

            # Generate base frames
            frames = self.generator.generate_animation_frames(
                self.theme_config,
                creature_index,
                anim_type,
                self.config.frames_per_animation,
            )

            # Apply color variant if not base
            if variant_index > 0:
                hue_shift = variant_index * 60  # Shift hue by 60 degrees per variant
                saturation_factor = 0.8 + (variant_index * 0.2)  # Adjust saturation
                frames = [apply_color_variant(frame, hue_shift, saturation_factor) for frame in frames]

            animation_frames[anim_type] = frames

        return creature_id, animation_frames

    def save_creature_assets(
        self,
        creature_id: str,
        animation_frames: dict[AnimationType, List[Image.Image]],
        variant_index: int = 0,
    ) -> dict[str, str]:
        """
        Save all assets for a creature to disk.

        Args:
            creature_id: Creature identifier
            animation_frames: Dictionary of animation frames
            variant_index: Color variant index

        Returns:
            Dictionary mapping animation types to sprite sheet paths
        """
        pack_dir = self.config.output_dir / self.config.pack_name / "creatures"
        sprite_sheet_paths = {}

        # Save individual frames and sprite sheets
        for anim_type, frames in animation_frames.items():
            # Save individual frames
            save_frames_to_disk(
                frames,
                pack_dir,
                creature_id,
                anim_type,
                variant_index,
            )

            # Create and save animation sprite sheet
            sprite_sheet = create_animation_sprite_sheet(frames, spacing=2)
            sheet_path = save_sprite_sheet(
                sprite_sheet,
                pack_dir,
                creature_id,
                anim_type,
                variant_index,
            )
            sprite_sheet_paths[anim_type.value] = str(sheet_path.relative_to(self.config.output_dir))

        # Create and save combined sprite sheet
        combined_sheet = create_combined_sprite_sheet(animation_frames, spacing=2)
        combined_path = save_sprite_sheet(
            combined_sheet,
            pack_dir,
            creature_id,
            AnimationType.IDLE,  # Unused for combined
            variant_index,
            is_combined=True,
        )
        sprite_sheet_paths["combined"] = str(combined_path.relative_to(self.config.output_dir))

        return sprite_sheet_paths

    def generate_pack(self) -> PackMetadata:
        """
        Generate a complete creature pack.

        Returns:
            PackMetadata for the generated pack
        """
        logger.info(f"Starting pack generation: {self.config.pack_name}")
        logger.info(f"Theme: {self.config.theme_name}, Resolution: {self.config.resolution}")
        logger.info(f"Creatures: {self.config.num_creatures}, Variants: {self.config.num_variants}")

        # Create pack metadata
        pack_metadata = create_pack_metadata(
            pack_id=f"pack_{self.config.pack_name}",
            pack_name=self.config.pack_name,
            theme_name=self.config.theme_name,
            resolution=self.config.resolution,
            num_creatures=self.config.num_creatures,
            num_variants=self.config.num_variants,
        )

        # Generate creatures
        all_sprite_sheets = []

        for creature_idx in range(self.config.num_creatures):
            for variant_idx in range(self.config.num_variants):
                # Generate creature
                creature_id, animation_frames = self.generate_creature(creature_idx, variant_idx)

                # Save assets
                sprite_sheet_paths = self.save_creature_assets(
                    creature_id,
                    animation_frames,
                    variant_idx,
                )

                # Create creature metadata
                creature_meta = create_creature_metadata(
                    creature_id=f"{creature_id}_v{variant_idx}",
                    theme=self.config.theme_name,
                    base_color="#000000",  # Placeholder
                    variant_index=variant_idx,
                    resolution=self.config.resolution,
                    sprite_sheet_paths=sprite_sheet_paths,
                    frames_per_animation=self.config.frames_per_animation,
                )
                pack_metadata.creatures.append(creature_meta)

                # Collect combined sprite sheet for preview (base variants only)
                if variant_idx == 0:
                    combined_path = (
                        self.config.output_dir
                        / self.config.pack_name
                        / "creatures"
                        / creature_id
                        / "sprite_sheets"
                        / "idle.png"
                    )
                    if combined_path.exists():
                        all_sprite_sheets.append(Image.open(combined_path))

        # Save metadata
        pack_dir = self.config.output_dir / self.config.pack_name
        metadata_path = pack_dir / "metadata.json"
        save_metadata(pack_metadata, metadata_path)
        logger.info(f"Metadata saved: {metadata_path}")

        # Save README
        readme_path = pack_dir / "README.txt"
        save_readme(pack_metadata, readme_path)
        logger.info(f"README saved: {readme_path}")

        # Generate preview
        if all_sprite_sheets:
            preview_dir = pack_dir / "previews"
            preview_dir.mkdir(parents=True, exist_ok=True)
            preview_path = preview_dir / "pack_preview.png"

            logger.info("Generating pack preview...")
            create_pack_preview(
                all_sprite_sheets[:20],  # Limit to 20 for preview
                pack_metadata,
                scale=8,
                output_path=preview_path,
            )
            logger.info(f"Preview saved: {preview_path}")

        logger.info(f"Pack generation complete: {pack_dir}")
        return pack_metadata

    def generate_and_export(self, create_archive: bool = True, cleanup: bool = False) -> dict:
        """
        Generate pack and export as ZIP archive.

        Args:
            create_archive: Whether to create ZIP archive
            cleanup: Whether to clean up temporary files

        Returns:
            Export information dictionary
        """
        # Generate pack
        pack_metadata = self.generate_pack()

        # Export
        pack_dir = self.config.output_dir / self.config.pack_name
        export_info = export_pack(
            pack_dir,
            self.config.output_dir,
            pack_metadata,
            create_archive=create_archive,
            cleanup=cleanup,
        )

        return export_info
