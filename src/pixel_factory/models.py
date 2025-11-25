"""
Data models and structures for pixel creature generation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class AnimationType(Enum):
    """Types of animations for creatures."""

    IDLE = "idle"
    WALK = "walk"
    ATTACK = "attack"


@dataclass
class ThemeConfig:
    """Configuration for a visual theme."""

    name: str
    description: str
    base_description: str
    mood_adjectives: List[str]
    color_palette_hints: List[str]
    background_color: str = "#1a1a1a"

    def build_prompt(self, creature_index: int) -> str:
        """
        Build a generation prompt for a creature in this theme.

        Args:
            creature_index: Index of the creature being generated

        Returns:
            Formatted prompt string
        """
        mood = self.mood_adjectives[creature_index % len(self.mood_adjectives)]
        color_hint = self.color_palette_hints[creature_index % len(self.color_palette_hints)]

        return (
            f"{self.base_description}, {mood} style, "
            f"pixel art, {color_hint} color scheme, "
            f"game sprite, transparent background, simple design"
        )


@dataclass
class CreatureMetadata:
    """Metadata for a single generated creature."""

    creature_id: str
    theme: str
    base_color: str
    variant_index: int
    resolution: Tuple[int, int]
    animations: Dict[str, int]  # animation_type -> frame_count
    sprite_sheet_paths: Dict[str, str]  # animation_type -> file_path
    generation_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "creature_id": self.creature_id,
            "theme": self.theme,
            "base_color": self.base_color,
            "variant_index": self.variant_index,
            "resolution": list(self.resolution),
            "animations": self.animations,
            "sprite_sheet_paths": self.sprite_sheet_paths,
            "generation_time": self.generation_time,
        }


@dataclass
class PackMetadata:
    """Metadata for a complete asset pack."""

    pack_id: str
    pack_name: str
    theme_name: str
    generation_date: str
    resolution: Tuple[int, int]
    num_creatures: int
    num_variants: int
    animation_types: List[str]
    creatures: List[CreatureMetadata] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "pack_id": self.pack_id,
            "pack_name": self.pack_name,
            "theme_name": self.theme_name,
            "generation_date": self.generation_date,
            "resolution": list(self.resolution),
            "num_creatures": self.num_creatures,
            "num_variants": self.num_variants,
            "animation_types": self.animation_types,
            "creatures": [creature.to_dict() for creature in self.creatures],
        }


@dataclass
class GenerationConfig:
    """Configuration for a generation run."""

    pack_name: str
    theme_name: str
    resolution: Tuple[int, int]
    num_creatures: int
    num_variants: int
    output_dir: Path
    frames_per_animation: int = 4

    @property
    def animation_types(self) -> List[AnimationType]:
        """Get all animation types to generate."""
        return [AnimationType.IDLE, AnimationType.WALK, AnimationType.ATTACK]
