"""
Image generation backends for pixel creatures.
"""

import random
from abc import ABC, abstractmethod
from typing import List, Tuple

from PIL import Image, ImageDraw

from pixel_factory.models import AnimationType, ThemeConfig


class PixelArtGenerator(ABC):
    """Abstract base class for pixel art generation backends."""

    def __init__(self, resolution: Tuple[int, int]) -> None:
        """
        Initialize generator.

        Args:
            resolution: Target resolution (width, height) for generated images
        """
        self.resolution = resolution

    @abstractmethod
    def generate_single_creature(
        self,
        theme: ThemeConfig,
        creature_index: int,
        animation_type: AnimationType,
        frame_index: int,
    ) -> Image.Image:
        """
        Generate a single frame for a creature animation.

        Args:
            theme: Theme configuration
            creature_index: Index of the creature
            animation_type: Type of animation
            frame_index: Frame number in the animation

        Returns:
            PIL Image object with RGBA mode
        """
        pass

    def generate_animation_frames(
        self,
        theme: ThemeConfig,
        creature_index: int,
        animation_type: AnimationType,
        num_frames: int,
    ) -> List[Image.Image]:
        """
        Generate all frames for a single animation.

        Args:
            theme: Theme configuration
            creature_index: Index of the creature
            animation_type: Type of animation
            num_frames: Number of frames to generate

        Returns:
            List of PIL Images
        """
        return [
            self.generate_single_creature(theme, creature_index, animation_type, i)
            for i in range(num_frames)
        ]


class PlaceholderGenerator(PixelArtGenerator):
    """
    Placeholder generator that creates simple geometric creatures.

    This implementation focuses on project structure and creates
    simple but distinct pixel art creatures using basic shapes.
    """

    def __init__(self, resolution: Tuple[int, int]) -> None:
        """
        Initialize placeholder generator.

        Args:
            resolution: Target resolution for generated images
        """
        super().__init__(resolution)
        # Seed based on resolution for reproducibility
        self._rng = random.Random(resolution[0] * 1000 + resolution[1])

    def _get_creature_colors(self, theme: ThemeConfig, creature_index: int) -> Tuple[str, str, str]:
        """
        Generate consistent colors for a creature.

        Args:
            theme: Theme configuration
            creature_index: Index of the creature

        Returns:
            Tuple of (primary_color, secondary_color, accent_color)
        """
        # Deterministic random based on theme and creature index
        rng = random.Random(hash(theme.name) + creature_index)

        color_schemes = {
            "cute_forest": [
                ("#8bc34a", "#4caf50", "#cddc39"),
                ("#ff9800", "#ff5722", "#ffc107"),
                ("#2196f3", "#03a9f4", "#00bcd4"),
                ("#e91e63", "#9c27b0", "#f06292"),
                ("#795548", "#8d6e63", "#a1887f"),
            ],
            "dark_dungeon": [
                ("#4a148c", "#6a1b9a", "#7b1fa2"),
                ("#b71c1c", "#c62828", "#d32f2f"),
                ("#1b5e20", "#2e7d32", "#388e3c"),
                ("#263238", "#37474f", "#455a64"),
                ("#e65100", "#ef6c00", "#f57c00"),
            ],
            "robot_aliens": [
                ("#0277bd", "#0288d1", "#03a9f4"),
                ("#f57f17", "#f9a825", "#fbc02d"),
                ("#00695c", "#00796b", "#00897b"),
                ("#4a148c", "#6a1b9a", "#7b1fa2"),
                ("#c2185b", "#d81b60", "#e91e63"),
            ],
            "ocean_creatures": [
                ("#01579b", "#0277bd", "#0288d1"),
                ("#e65100", "#ef6c00", "#f57c00"),
                ("#4a148c", "#6a1b9a", "#7b1fa2"),
                ("#00695c", "#00796b", "#00897b"),
                ("#c62828", "#d32f2f", "#e53935"),
            ],
        }

        theme_colors = color_schemes.get(theme.name, color_schemes["cute_forest"])
        return rng.choice(theme_colors)

    def _get_creature_shape(self, creature_index: int) -> str:
        """
        Determine shape type for a creature.

        Args:
            creature_index: Index of the creature

        Returns:
            Shape type identifier
        """
        shapes = ["blob", "quadruped", "biped", "flying", "serpent"]
        return shapes[creature_index % len(shapes)]

    def generate_single_creature(
        self,
        theme: ThemeConfig,
        creature_index: int,
        animation_type: AnimationType,
        frame_index: int,
    ) -> Image.Image:
        """
        Generate a simple geometric pixel creature.

        Args:
            theme: Theme configuration
            creature_index: Index of the creature
            animation_type: Type of animation
            frame_index: Frame number in the animation

        Returns:
            PIL Image with transparent background
        """
        img = Image.new("RGBA", self.resolution, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        width, height = self.resolution
        colors = self._get_creature_colors(theme, creature_index)
        shape = self._get_creature_shape(creature_index)

        # Animation offset
        offset = self._get_animation_offset(animation_type, frame_index)

        # Draw creature based on shape
        if shape == "blob":
            self._draw_blob_creature(draw, width, height, colors, offset)
        elif shape == "quadruped":
            self._draw_quadruped_creature(draw, width, height, colors, offset)
        elif shape == "biped":
            self._draw_biped_creature(draw, width, height, colors, offset)
        elif shape == "flying":
            self._draw_flying_creature(draw, width, height, colors, offset)
        else:  # serpent
            self._draw_serpent_creature(draw, width, height, colors, offset)

        return img

    def _get_animation_offset(self, animation_type: AnimationType, frame_index: int) -> int:
        """Calculate pixel offset for animation frame."""
        if animation_type == AnimationType.IDLE:
            # Gentle bobbing
            return (frame_index % 2) * 1
        elif animation_type == AnimationType.WALK:
            # Up and down motion
            return [0, 1, 0, -1][frame_index % 4]
        else:  # ATTACK
            # Forward thrust
            return [0, 2, 1, 0][frame_index % 4]

    def _draw_blob_creature(
        self, draw: ImageDraw.ImageDraw, w: int, h: int, colors: Tuple[str, str, str], offset: int
    ) -> None:
        """Draw a blob-shaped creature."""
        primary, secondary, accent = colors
        center_x, center_y = w // 2, h // 2 + offset

        # Body
        body_size = min(w, h) // 3
        draw.ellipse(
            [center_x - body_size, center_y - body_size, center_x + body_size, center_y + body_size],
            fill=primary,
            outline=secondary,
        )

        # Eyes
        eye_y = center_y - body_size // 3
        draw.rectangle([center_x - body_size // 2, eye_y, center_x - body_size // 3, eye_y + 2], fill=accent)
        draw.rectangle([center_x + body_size // 3, eye_y, center_x + body_size // 2, eye_y + 2], fill=accent)

    def _draw_quadruped_creature(
        self, draw: ImageDraw.ImageDraw, w: int, h: int, colors: Tuple[str, str, str], offset: int
    ) -> None:
        """Draw a four-legged creature."""
        primary, secondary, accent = colors
        center_x, center_y = w // 2, h // 2 + offset

        # Body
        body_w, body_h = w // 2, h // 3
        draw.rectangle(
            [center_x - body_w // 2, center_y - body_h // 2, center_x + body_w // 2, center_y + body_h // 2],
            fill=primary,
            outline=secondary,
        )

        # Legs
        leg_h = h // 4
        for leg_x in [center_x - body_w // 2, center_x + body_w // 2 - 2]:
            draw.rectangle(
                [leg_x, center_y + body_h // 2, leg_x + 2, center_y + body_h // 2 + leg_h],
                fill=secondary,
            )

        # Head
        head_size = body_h
        draw.ellipse(
            [center_x + body_w // 2 - 2, center_y - head_size, center_x + body_w // 2 + head_size, center_y],
            fill=primary,
            outline=accent,
        )

    def _draw_biped_creature(
        self, draw: ImageDraw.ImageDraw, w: int, h: int, colors: Tuple[str, str, str], offset: int
    ) -> None:
        """Draw a two-legged creature."""
        primary, secondary, accent = colors
        center_x, center_y = w // 2, h // 2 + offset

        # Body
        body_w, body_h = w // 4, h // 2
        draw.rectangle(
            [center_x - body_w // 2, center_y - body_h // 2, center_x + body_w // 2, center_y + body_h // 2],
            fill=primary,
            outline=secondary,
        )

        # Head
        head_size = body_w + 2
        draw.ellipse(
            [center_x - head_size // 2, center_y - body_h // 2 - head_size,
             center_x + head_size // 2, center_y - body_h // 2],
            fill=primary,
            outline=accent,
        )

        # Legs
        leg_w, leg_h = 2, h // 4
        draw.rectangle(
            [center_x - body_w // 2, center_y + body_h // 2,
             center_x - body_w // 2 + leg_w, center_y + body_h // 2 + leg_h],
            fill=secondary,
        )
        draw.rectangle(
            [center_x + body_w // 2 - leg_w, center_y + body_h // 2,
             center_x + body_w // 2, center_y + body_h // 2 + leg_h],
            fill=secondary,
        )

    def _draw_flying_creature(
        self, draw: ImageDraw.ImageDraw, w: int, h: int, colors: Tuple[str, str, str], offset: int
    ) -> None:
        """Draw a flying creature."""
        primary, secondary, accent = colors
        center_x, center_y = w // 2, h // 2 + offset

        # Body
        body_size = min(w, h) // 4
        draw.ellipse(
            [center_x - body_size, center_y - body_size // 2,
             center_x + body_size, center_y + body_size // 2],
            fill=primary,
            outline=secondary,
        )

        # Wings
        wing_size = body_size + 4
        draw.polygon(
            [
                (center_x - body_size, center_y),
                (center_x - body_size - wing_size, center_y - wing_size // 2),
                (center_x - body_size - wing_size, center_y + wing_size // 2),
            ],
            fill=secondary,
            outline=accent,
        )
        draw.polygon(
            [
                (center_x + body_size, center_y),
                (center_x + body_size + wing_size, center_y - wing_size // 2),
                (center_x + body_size + wing_size, center_y + wing_size // 2),
            ],
            fill=secondary,
            outline=accent,
        )

    def _draw_serpent_creature(
        self, draw: ImageDraw.ImageDraw, w: int, h: int, colors: Tuple[str, str, str], offset: int
    ) -> None:
        """Draw a serpentine creature."""
        primary, secondary, accent = colors
        center_y = h // 2 + offset

        # Segmented body
        segment_size = min(w, h) // 8
        num_segments = 5
        for i in range(num_segments):
            x = w // 4 + (i * w // (num_segments + 2))
            y_wave = center_y + int((i % 2) * segment_size // 2)
            draw.ellipse(
                [x - segment_size, y_wave - segment_size, x + segment_size, y_wave + segment_size],
                fill=primary if i % 2 == 0 else secondary,
                outline=accent,
            )
