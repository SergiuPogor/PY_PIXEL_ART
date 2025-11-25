"""
Configuration management for Pixel Factory.
"""

import os
from pathlib import Path
from typing import Dict, Optional

import yaml

from pixel_factory.models import ThemeConfig


DEFAULT_THEMES = {
    "cute_forest": ThemeConfig(
        name="cute_forest",
        description="Adorable forest creatures",
        base_description="cute small forest animal creature",
        mood_adjectives=["friendly", "cheerful", "playful", "curious", "happy"],
        color_palette_hints=["green and brown", "orange and yellow", "blue and white", "pink and purple", "red and brown"],
        background_color="#2d5016",
    ),
    "dark_dungeon": ThemeConfig(
        name="dark_dungeon",
        description="Menacing dungeon monsters",
        base_description="dark dungeon monster creature",
        mood_adjectives=["menacing", "sinister", "aggressive", "fierce", "intimidating"],
        color_palette_hints=["dark purple and black", "red and black", "green and brown", "gray and dark blue", "brown and orange"],
        background_color="#1a0d1a",
    ),
    "robot_aliens": ThemeConfig(
        name="robot_aliens",
        description="Robotic alien beings",
        base_description="small robot alien creature",
        mood_adjectives=["mechanical", "futuristic", "sleek", "advanced", "technological"],
        color_palette_hints=["silver and blue", "gold and red", "green and black", "cyan and white", "purple and pink"],
        background_color="#0d1a26",
    ),
    "ocean_creatures": ThemeConfig(
        name="ocean_creatures",
        description="Aquatic sea creatures",
        base_description="small sea creature ocean animal",
        mood_adjectives=["flowing", "graceful", "mysterious", "colorful", "peaceful"],
        color_palette_hints=["blue and cyan", "orange and yellow", "purple and pink", "green and teal", "red and orange"],
        background_color="#0a2463",
    ),
}


class Config:
    """Main configuration class for Pixel Factory."""

    def __init__(self, config_file: Optional[Path] = None) -> None:
        """
        Initialize configuration.

        Args:
            config_file: Optional path to YAML config file
        """
        self.themes: Dict[str, ThemeConfig] = DEFAULT_THEMES.copy()
        self.default_output_dir = Path(os.getenv("PIXEL_FACTORY_OUTPUT_DIR", "output"))
        self.default_resolution = (32, 32)
        self.default_theme = "cute_forest"
        self.default_num_creatures = 10
        self.default_num_variants = 2

        if config_file and config_file.exists():
            self._load_config_file(config_file)

    def _load_config_file(self, config_file: Path) -> None:
        """
        Load configuration from YAML file.

        Args:
            config_file: Path to YAML config file
        """
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)

        if "defaults" in data:
            defaults = data["defaults"]
            self.default_output_dir = Path(defaults.get("output_dir", self.default_output_dir))
            self.default_resolution = tuple(defaults.get("resolution", self.default_resolution))
            self.default_theme = defaults.get("theme", self.default_theme)
            self.default_num_creatures = defaults.get("num_creatures", self.default_num_creatures)
            self.default_num_variants = defaults.get("num_variants", self.default_num_variants)

        if "themes" in data:
            for theme_name, theme_data in data["themes"].items():
                self.themes[theme_name] = ThemeConfig(
                    name=theme_name,
                    description=theme_data.get("description", ""),
                    base_description=theme_data["base_description"],
                    mood_adjectives=theme_data["mood_adjectives"],
                    color_palette_hints=theme_data["color_palette_hints"],
                    background_color=theme_data.get("background_color", "#1a1a1a"),
                )

    def get_theme(self, theme_name: str) -> ThemeConfig:
        """
        Get theme configuration by name.

        Args:
            theme_name: Name of the theme

        Returns:
            ThemeConfig object

        Raises:
            ValueError: If theme not found
        """
        if theme_name not in self.themes:
            raise ValueError(
                f"Theme '{theme_name}' not found. Available themes: {list(self.themes.keys())}"
            )
        return self.themes[theme_name]


# Global config instance
_config: Optional[Config] = None


def get_config(config_file: Optional[Path] = None) -> Config:
    """
    Get or create global config instance.

    Args:
        config_file: Optional path to config file

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_file)
    return _config
