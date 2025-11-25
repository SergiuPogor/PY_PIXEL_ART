# Pixel Factory

**Automated pixel creature asset pack generator for indie game developers**

Pixel Factory is a complete Python tool that automatically generates pixel art creature assets for game development. It creates consistent, themed creature sprites with multiple animations, color variants, sprite sheets, and packages everything into ready-to-sell asset packs.

## Features

- 🎨 **Multiple Built-in Themes**: Cute forest creatures, dark dungeon monsters, robot aliens, and ocean creatures
- 🎭 **Multiple Animations**: Idle, walk, and attack animations (4 frames each)
- 🌈 **Color Variants**: Automatic palette-shifted color variants
- 📊 **Sprite Sheets**: Individual and combined sprite sheets for easy integration
- 📦 **Complete Packages**: ZIP archives with all assets, metadata, and documentation
- 🖼️ **Preview Generation**: High-resolution preview collages for marketing
- 🔧 **Extensible Architecture**: Easy to add new generation backends (local models, APIs)
- ✨ **Production Ready**: Full CLI, logging, tests, and type hints

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/pixel-factory.git
cd pixel-factory

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Dependencies

- Python 3.8+
- Pillow (image processing)
- PyYAML (configuration)
- Click (CLI)
- pytest (testing, dev only)

## Quick Start

Generate your first asset pack:

```bash
# Generate a pack with default settings (10 creatures, 2 variants, 32x32)
pixel-factory generate

# Generate a themed pack
pixel-factory generate --theme dark_dungeon --count 20 --resolution 64

# Generate with custom settings
pixel-factory generate \
  --pack-name "MyCreatures" \
  --theme cute_forest \
  --count 50 \
  --variants 3 \
  --resolution 32 \
  --output ./my_packs
```

## Usage

### Command Line Interface

#### Generate Command

```bash
pixel-factory generate [OPTIONS]
```

**Options:**

- `--pack-name TEXT`: Name for the asset pack (default: auto-generated)
- `--theme TEXT`: Theme to use (default: cute_forest)
- `--resolution INT`: Creature resolution in pixels (default: 32)
- `--count INT`: Number of creatures to generate (default: 10)
- `--variants INT`: Number of color variants per creature (default: 2)
- `--output PATH`: Output directory (default: ./output)
- `--no-archive`: Skip creating ZIP archive
- `--cleanup`: Remove temporary files after archiving
- `--config PATH`: Path to custom config file
- `--verbose, -v`: Enable verbose logging

#### List Themes

```bash
pixel-factory list-themes
```

Shows all available themes with descriptions.

#### Version

```bash
pixel-factory version
```

### Available Themes

1. **cute_forest**: Adorable forest creatures with friendly designs
2. **dark_dungeon**: Menacing dungeon monsters with aggressive appearance
3. **robot_aliens**: Futuristic robotic alien beings
4. **ocean_creatures**: Aquatic sea creatures with flowing designs

## Output Structure

```
output/
└── pack_name/
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

## Configuration

### Custom Configuration File

Create a YAML config file to customize defaults and themes:

```yaml
# config.yaml
defaults:
  output_dir: ./my_output
  resolution: [64, 64]
  theme: robot_aliens
  num_creatures: 20
  num_variants: 3

themes:
  custom_theme:
    description: "My custom theme"
    base_description: "fantasy dragon creature"
    mood_adjectives:
      - fierce
      - majestic
      - ancient
    color_palette_hints:
      - red and gold
      - blue and silver
      - green and bronze
    background_color: "#2a1a1a"
```

Use with:

```bash
pixel-factory generate --config config.yaml --theme custom_theme
```

### Environment Variables

- `PIXEL_FACTORY_OUTPUT_DIR`: Default output directory

## Using in Game Engines

### Unity

1. Import sprite sheets into your Assets folder
2. Set Texture Type to "Sprite (2D and UI)"
3. Set Pixels Per Unit to match your game scale
4. Use the Sprite Editor to slice sprite sheets
5. Create Animator and Animation Clips

### Godot

1. Import sprite sheets as Texture resources
2. Create AnimatedSprite2D node
3. Add SpriteFrames resource
4. Add animations and frames from sprite sheet
5. Configure FPS and looping

### Pygame

```python
import pygame

# Load sprite sheet
sprite_sheet = pygame.image.load('combined.png')

# Extract frames
frame_width, frame_height = 32, 32
frames = []

for row in range(3):  # 3 animations
    for col in range(4):  # 4 frames
        frame = sprite_sheet.subsurface(
            col * frame_width,
            row * frame_height,
            frame_width,
            frame_height
        )
        frames.append(frame)
```

## Architecture

### Project Structure

```
pixel_factory/
├── __init__.py          # Package initialization
├── models.py            # Data models and structures
├── config.py            # Configuration management
├── generator.py         # Image generation backends
├── spritesheet.py       # Sprite sheet composition
├── preview.py           # Preview image generation
├── metadata.py          # Metadata and README generation
├── packaging.py         # ZIP archive creation
├── pipeline.py          # Main orchestration pipeline
└── cli.py               # Command-line interface
```

### Extending with Custom Generators

The architecture supports pluggable generation backends:

```python
from pixel_factory.generator import PixelArtGenerator
from pixel_factory.models import AnimationType, ThemeConfig
from PIL import Image

class MyCustomGenerator(PixelArtGenerator):
    """Custom generator using your preferred method."""

    def generate_single_creature(
        self,
        theme: ThemeConfig,
        creature_index: int,
        animation_type: AnimationType,
        frame_index: int,
    ) -> Image.Image:
        # Your custom generation logic
        # Could call a local model, API, or other method
        prompt = theme.build_prompt(creature_index)
        image = your_generation_function(prompt, self.resolution)
        return image

# Use in pipeline
from pixel_factory.pipeline import CreaturePackPipeline
from pixel_factory.models import GenerationConfig

config = GenerationConfig(
    pack_name="custom_pack",
    theme_name="cute_forest",
    resolution=(64, 64),
    num_creatures=10,
    num_variants=2,
    output_dir=Path("output"),
)

generator = MyCustomGenerator(resolution=(64, 64))
pipeline = CreaturePackPipeline(config, generator=generator)
pipeline.generate_and_export()
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pixel_factory

# Run specific test file
pytest tests/test_generator.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/

# Type checking
mypy src/
```

### Project Goals

- ✅ Production-ready code structure
- ✅ Comprehensive test coverage
- ✅ Clean separation of concerns
- ✅ Extensible architecture
- ✅ Type hints throughout
- ✅ Detailed documentation

## Metadata Format

Each pack includes a `metadata.json` file:

```json
{
  "pack_id": "pack_cute_forest_32x32_1234567890",
  "pack_name": "cute_forest_pack",
  "theme_name": "cute_forest",
  "generation_date": "2024-01-15T10:30:00",
  "resolution": [32, 32],
  "num_creatures": 10,
  "num_variants": 2,
  "animation_types": ["idle", "walk", "attack"],
  "creatures": [
    {
      "creature_id": "creature_001_v0",
      "theme": "cute_forest",
      "base_color": "#000000",
      "variant_index": 0,
      "resolution": [32, 32],
      "animations": {
        "idle": 4,
        "walk": 4,
        "attack": 4
      },
      "sprite_sheet_paths": {
        "idle": "creatures/creature_001/sprite_sheets/idle.png",
        "walk": "creatures/creature_001/sprite_sheets/walk.png",
        "attack": "creatures/creature_001/sprite_sheets/attack.png",
        "combined": "creatures/creature_001/sprite_sheets/combined.png"
      }
    }
  ]
}
```

## Performance

- Generates ~10 creatures with 2 variants in under 30 seconds (placeholder backend)
- Supports parallel generation (can be extended)
- Efficient sprite sheet composition using Pillow
- Minimal memory footprint

## Roadmap

Future enhancements:

- [ ] Integration with Stable Diffusion for AI-generated creatures
- [ ] API backend for cloud-based generation services
- [ ] Additional animation types (death, special attack, etc.)
- [ ] Custom frame counts per animation
- [ ] Batch generation mode
- [ ] Web interface
- [ ] More built-in themes

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Credits

Created with ❤️ for indie game developers

## Support

- **Issues**: Report bugs at https://github.com/yourusername/pixel-factory/issues
- **Discussions**: Feature requests and questions welcome

---

**Happy game development! 🎮✨**
