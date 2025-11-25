# Quick Start Guide

## Installation

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Install package
pip install -e ".[dev]"
```

## First Generation

Generate your first pack with default settings:

```bash
pixel-factory generate
```

This creates:
- 10 creatures
- 2 color variants each
- 32x32 resolution
- cute_forest theme
- Complete ZIP archive in `output/`

## Quick Examples

### Different Theme
```bash
pixel-factory generate --theme dark_dungeon
```

### Larger Resolution
```bash
pixel-factory generate --resolution 64 --count 5
```

### Custom Pack
```bash
pixel-factory generate \
  --pack-name "MyCreatures" \
  --theme robot_aliens \
  --count 20 \
  --variants 3 \
  --resolution 48
```

### List Available Themes
```bash
pixel-factory list-themes
```

## Test Generation Results

After generation, check the output:

```bash
# List generated files
tree output/pack_*/

# View sprite sheets
ls output/pack_*/creatures/creature_001/sprite_sheets/

# Check preview
file output/pack_*/previews/pack_preview.png
```

## Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pixel_factory

# Run verbose
pytest -v
```

## What You Get

Each pack contains:
- ✅ Individual animation frames (PNG)
- ✅ Sprite sheets (idle, walk, attack)
- ✅ Combined sprite sheets
- ✅ Color variants
- ✅ High-res preview collage
- ✅ Complete metadata (JSON)
- ✅ Usage documentation (README.txt)
- ✅ ZIP archive ready to distribute

## Next Steps

1. **Customize themes**: Edit `config.example.yaml` and save as `config.yaml`
2. **Integrate custom generator**: See Architecture section in README.md
3. **Use in your game**: Import sprite sheets into Unity, Godot, or Pygame
4. **Sell as assets**: Package includes everything needed for asset marketplaces

## Need Help?

- Check the full README.md for detailed documentation
- Run `pixel-factory --help` for CLI options
- Look at the example config: `config.example.yaml`
