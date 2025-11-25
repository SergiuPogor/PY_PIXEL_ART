"""
Command-line interface for Pixel Factory.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import click

from pixel_factory.config import get_config
from pixel_factory.models import GenerationConfig
from pixel_factory.pipeline import CreaturePackPipeline


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        verbose: Enable verbose (DEBUG) logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Pixel Factory - Automated pixel creature asset pack generator."""
    pass


@cli.command()
@click.option(
    "--pack-name",
    default=None,
    help="Name for the asset pack (default: auto-generated)",
)
@click.option(
    "--theme",
    default=None,
    help="Theme to use for generation (default: cute_forest)",
)
@click.option(
    "--resolution",
    type=int,
    default=32,
    help="Creature resolution in pixels (default: 32)",
)
@click.option(
    "--count",
    type=int,
    default=None,
    help="Number of creatures to generate (default: 10)",
)
@click.option(
    "--variants",
    type=int,
    default=None,
    help="Number of color variants per creature (default: 2)",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory (default: ./output)",
)
@click.option(
    "--no-archive",
    is_flag=True,
    help="Skip creating ZIP archive",
)
@click.option(
    "--cleanup",
    is_flag=True,
    help="Remove temporary files after archiving",
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to custom config file",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
def generate(
    pack_name: Optional[str],
    theme: Optional[str],
    resolution: int,
    count: Optional[int],
    variants: Optional[int],
    output: Optional[Path],
    no_archive: bool,
    cleanup: bool,
    config: Optional[Path],
    verbose: bool,
) -> None:
    """Generate a pixel creature asset pack."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        app_config = get_config(config)

        # Apply defaults from config
        theme = theme or app_config.default_theme
        count = count or app_config.default_num_creatures
        variants = variants or app_config.default_num_variants
        output = output or app_config.default_output_dir

        # Validate theme
        try:
            app_config.get_theme(theme)
        except ValueError as e:
            logger.error(str(e))
            sys.exit(1)

        # Generate pack name if not provided
        if pack_name is None:
            import time

            timestamp = int(time.time())
            pack_name = f"pack_{theme}_{resolution}x{resolution}_{timestamp}"

        # Create generation config
        gen_config = GenerationConfig(
            pack_name=pack_name,
            theme_name=theme,
            resolution=(resolution, resolution),
            num_creatures=count,
            num_variants=variants,
            output_dir=Path(output),
        )

        # Display configuration
        logger.info("=" * 60)
        logger.info("Pixel Factory - Asset Pack Generation")
        logger.info("=" * 60)
        logger.info(f"Pack Name:       {gen_config.pack_name}")
        logger.info(f"Theme:           {gen_config.theme_name}")
        logger.info(f"Resolution:      {gen_config.resolution[0]}x{gen_config.resolution[1]}")
        logger.info(f"Creatures:       {gen_config.num_creatures}")
        logger.info(f"Variants:        {gen_config.num_variants}")
        logger.info(f"Output:          {gen_config.output_dir}")
        logger.info(f"Create Archive:  {not no_archive}")
        logger.info("=" * 60)

        # Create pipeline and generate
        pipeline = CreaturePackPipeline(gen_config)
        export_info = pipeline.generate_and_export(
            create_archive=not no_archive,
            cleanup=cleanup,
        )

        # Display results
        if export_info["success"]:
            logger.info("=" * 60)
            logger.info("Generation Complete!")
            logger.info("=" * 60)

            stats = export_info.get("statistics", {})
            logger.info(f"Total Files:     {stats.get('total_files', 0)}")
            logger.info(f"Total Size:      {stats.get('total_size_mb', 0)} MB")
            logger.info(f"Creatures:       {stats.get('num_creatures', 0)}")
            logger.info(f"Frames:          {stats.get('num_frames', 0)}")
            logger.info(f"Sprite Sheets:   {stats.get('num_sprite_sheets', 0)}")

            if export_info.get("archive_path"):
                logger.info(f"Archive:         {export_info['archive_path']}")

            logger.info("=" * 60)
        else:
            logger.error("Generation failed!")
            if "error" in export_info:
                logger.error(f"Error: {export_info['error']}")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("\nGeneration interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=verbose)
        sys.exit(1)


@cli.command()
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to custom config file",
)
def list_themes(config: Optional[Path]) -> None:
    """List available themes."""
    app_config = get_config(config)

    click.echo("\nAvailable Themes:")
    click.echo("=" * 60)

    for theme_name, theme_config in app_config.themes.items():
        click.echo(f"\n{theme_name}")
        click.echo(f"  Description: {theme_config.description}")
        click.echo(f"  Base: {theme_config.base_description}")
        click.echo(f"  Moods: {', '.join(theme_config.mood_adjectives[:3])}")
        click.echo(f"  Colors: {', '.join(theme_config.color_palette_hints[:3])}")

    click.echo("\n" + "=" * 60)


@cli.command()
def version() -> None:
    """Show version information."""
    from pixel_factory import __version__

    click.echo(f"Pixel Factory v{__version__}")
    click.echo("Automated pixel creature asset pack generator")


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
