"""
Metadata generation and management for asset packs.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from pixel_factory.models import AnimationType, CreatureMetadata, PackMetadata


def create_pack_metadata(
    pack_id: str,
    pack_name: str,
    theme_name: str,
    resolution: tuple[int, int],
    num_creatures: int,
    num_variants: int,
) -> PackMetadata:
    """
    Create metadata for a new pack.

    Args:
        pack_id: Unique identifier for the pack
        pack_name: Display name for the pack
        theme_name: Theme used for generation
        resolution: Creature resolution (width, height)
        num_creatures: Number of base creatures
        num_variants: Number of color variants per creature

    Returns:
        PackMetadata object
    """
    return PackMetadata(
        pack_id=pack_id,
        pack_name=pack_name,
        theme_name=theme_name,
        generation_date=datetime.utcnow().isoformat(),
        resolution=resolution,
        num_creatures=num_creatures,
        num_variants=num_variants,
        animation_types=[anim.value for anim in AnimationType],
    )


def create_creature_metadata(
    creature_id: str,
    theme: str,
    base_color: str,
    variant_index: int,
    resolution: tuple[int, int],
    sprite_sheet_paths: Dict[str, str],
    frames_per_animation: int = 4,
) -> CreatureMetadata:
    """
    Create metadata for a creature.

    Args:
        creature_id: Unique identifier for the creature
        theme: Theme name
        base_color: Primary color hex code
        variant_index: Color variant index (0 = base)
        resolution: Creature resolution
        sprite_sheet_paths: Dictionary mapping animation types to file paths
        frames_per_animation: Number of frames per animation

    Returns:
        CreatureMetadata object
    """
    animations = {anim.value: frames_per_animation for anim in AnimationType}

    return CreatureMetadata(
        creature_id=creature_id,
        theme=theme,
        base_color=base_color,
        variant_index=variant_index,
        resolution=resolution,
        animations=animations,
        sprite_sheet_paths=sprite_sheet_paths,
    )


def save_metadata(metadata: PackMetadata, output_path: Path) -> None:
    """
    Save pack metadata to JSON file.

    Args:
        metadata: PackMetadata object
        output_path: Path to save JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(metadata.to_dict(), f, indent=2)


def load_metadata(metadata_path: Path) -> PackMetadata:
    """
    Load pack metadata from JSON file.

    Args:
        metadata_path: Path to metadata JSON file

    Returns:
        PackMetadata object
    """
    with open(metadata_path, "r") as f:
        data = json.load(f)

    creatures = []
    for creature_data in data.get("creatures", []):
        creatures.append(
            CreatureMetadata(
                creature_id=creature_data["creature_id"],
                theme=creature_data["theme"],
                base_color=creature_data["base_color"],
                variant_index=creature_data["variant_index"],
                resolution=tuple(creature_data["resolution"]),
                animations=creature_data["animations"],
                sprite_sheet_paths=creature_data["sprite_sheet_paths"],
                generation_time=creature_data.get("generation_time", ""),
            )
        )

    return PackMetadata(
        pack_id=data["pack_id"],
        pack_name=data["pack_name"],
        theme_name=data["theme_name"],
        generation_date=data["generation_date"],
        resolution=tuple(data["resolution"]),
        num_creatures=data["num_creatures"],
        num_variants=data["num_variants"],
        animation_types=data["animation_types"],
        creatures=creatures,
    )


def generate_readme(pack_metadata: PackMetadata) -> str:
    """
    Generate README content for the pack.

    Args:
        pack_metadata: Metadata for the pack

    Returns:
        README content as string
    """
    readme = f"""# {pack_metadata.pack_name}

## Pack Information

- **Theme**: {pack_metadata.theme_name}
- **Resolution**: {pack_metadata.resolution[0]}x{pack_metadata.resolution[1]} pixels
- **Creatures**: {pack_metadata.num_creatures}
- **Color Variants**: {pack_metadata.num_variants} per creature
- **Generated**: {pack_metadata.generation_date}

## Animations Included

Each creature includes the following animations:
"""

    for anim_type in pack_metadata.animation_types:
        readme += f"- **{anim_type.capitalize()}**: 4 frames\n"

    readme += """
## File Structure

```
{pack_name}/
├── creatures/
│   ├── creature_001/
│   │   ├── idle/
│   │   │   ├── frame_01.png
│   │   │   ├── frame_02.png
│   │   │   ├── frame_03.png
│   │   │   └── frame_04.png
│   │   ├── walk/
│   │   │   └── ...
│   │   ├── attack/
│   │   │   └── ...
│   │   └── sprite_sheets/
│   │       ├── idle.png
│   │       ├── walk.png
│   │       ├── attack.png
│   │       └── combined.png
│   └── creature_002/
│       └── ...
├── previews/
│   └── pack_preview.png
├── metadata.json
└── README.txt
```

## Sprite Sheets

Each creature has individual sprite sheets for each animation type, plus a combined sprite sheet:

- **Individual sheets** (e.g., `idle.png`): Single row of frames for one animation
- **Combined sheet** (`combined.png`): All animations stacked vertically in order: idle, walk, attack

## Color Variants

Color variants are generated programmatically from the base creature. Variant files include `_variant_N` in their filename.

## Usage in Game Engines

### Unity
1. Import sprite sheets into your project
2. Use the Sprite Editor to slice the sprite sheet
3. Set pixels per unit to match your game's scale
4. Create animation clips using the sliced sprites

### Godot
1. Import sprite sheets as Texture
2. Create AnimatedSprite node
3. Add frames from sprite sheet
4. Configure animation speed and looping

### Pygame
```python
sprite_sheet = pygame.image.load('combined.png')
frame_width = {pack_metadata.resolution[0]}
frame_height = {pack_metadata.resolution[1]}
# Extract frames and animate
```

## License

This asset pack was generated using Pixel Factory.
Use these assets freely in your commercial or non-commercial projects.

## Credits

Generated with Pixel Factory - https://github.com/yourusername/pixel-factory
"""

    return readme


def save_readme(pack_metadata: PackMetadata, output_path: Path) -> None:
    """
    Save README file for the pack.

    Args:
        pack_metadata: Metadata for the pack
        output_path: Path to save README
    """
    readme_content = generate_readme(pack_metadata)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(readme_content)
