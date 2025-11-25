# Installation & Setup

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- git (optional, for cloning)

## Step-by-Step Installation

### 1. Clone or Download the Project

```bash
git clone https://github.com/yourusername/pixel-factory.git
cd pixel-factory
```

Or download and extract the ZIP file.

### 2. Create Virtual Environment

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Package

```bash
pip install -e ".[dev]"
```

This installs:
- pixel-factory package in editable mode
- All runtime dependencies (Pillow, PyYAML, Click)
- Development dependencies (pytest, black, mypy)

### 4. Verify Installation

```bash
# Check CLI is available
pixel-factory --help

# List themes
pixel-factory list-themes

# Run tests
pytest
```

## Quick Test Run

Generate a small test pack:

```bash
pixel-factory generate --count 3 --variants 2
```

This creates a pack in the `output/` directory.

## Configuration (Optional)

Create a custom config file:

```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your preferences
```

Use custom config:

```bash
pixel-factory generate --config config.yaml
```

## Troubleshooting

### "pixel-factory: command not found"

Make sure your virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Import Errors

Reinstall the package:
```bash
pip install -e ".[dev]" --force-reinstall
```

### Permission Errors on Linux

If you get permission errors for font files:
```bash
sudo apt-get install fonts-dejavu
```

## Uninstallation

```bash
pip uninstall pixel-factory
deactivate
rm -rf venv
```

## Next Steps

- Read [QUICKSTART.md](QUICKSTART.md) for usage examples
- Read [README.md](README.md) for full documentation
- Explore [config.example.yaml](config.example.yaml) for customization options
