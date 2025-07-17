"""
Main entry point for Key Replacer application.
"""

import sys
import argparse
import signal
import os
from pathlib import Path

# Add the parent directory to the path so we can import keyreplacer
sys.path.insert(0, str(Path(__file__).parent.parent))

from keyreplacer.config import Config
from keyreplacer.core import KeyReplacer
from keyreplacer.gui import KeyReplacerGUI
from keyreplacer.logging_setup import setup_logging, get_logger


def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    logger = get_logger(__name__)
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Key Replacer - A cross-platform text expansion tool",
        epilog="For more information, visit: https://github.com/kumar10248/key-replacer"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Key Replacer 1.0.0"
    )
    
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run without GUI (command-line mode)"
    )
    
    parser.add_argument(
        "--config-dir",
        type=str,
        help="Custom configuration directory"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--no-file-logging",
        action="store_true",
        help="Disable file logging"
    )
    
    parser.add_argument(
        "--add-mapping",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Add a mapping and exit (format: --add-mapping key 'expansion text')"
    )
    
    parser.add_argument(
        "--list-mappings",
        action="store_true",
        help="List all mappings and exit"
    )
    
    parser.add_argument(
        "--export-mappings",
        type=str,
        metavar="FILE",
        help="Export mappings to JSON file and exit"
    )
    
    parser.add_argument(
        "--import-mappings",
        type=str,
        metavar="FILE",
        help="Import mappings from JSON file and exit"
    )
    
    return parser.parse_args()


def run_cli_commands(args, config):
    """Handle command-line operations that don't require GUI."""
    logger = get_logger(__name__)
    
    if args.add_mapping:
        key, value = args.add_mapping
        if config.add_mapping(key, value):
            print(f"✓ Added mapping: {key} → {value}")
            logger.info(f"Added mapping via CLI: {key}")
            return True
        else:
            print(f"✗ Failed to add mapping: {key}")
            logger.error(f"Failed to add mapping via CLI: {key}")
            return False
    
    if args.list_mappings:
        mappings = config.get_mappings()
        if mappings:
            print(f"Found {len(mappings)} mappings:")
            print("-" * 50)
            for key, value in sorted(mappings.items()):
                # Truncate long values for display
                display_value = value[:80] + "..." if len(value) > 80 else value
                print(f"{key:20} → {display_value}")
        else:
            print("No mappings found.")
        return True
    
    if args.export_mappings:
        if config.export_mappings(args.export_mappings):
            mappings_count = len(config.get_mappings())
            print(f"✓ Exported {mappings_count} mappings to {args.export_mappings}")
            logger.info(f"Exported mappings via CLI to {args.export_mappings}")
            return True
        else:
            print(f"✗ Failed to export mappings to {args.export_mappings}")
            logger.error(f"Failed to export mappings via CLI to {args.export_mappings}")
            return False
    
    if args.import_mappings:
        if os.path.exists(args.import_mappings):
            if config.import_mappings(args.import_mappings, merge=True):
                mappings_count = len(config.get_mappings())
                print(f"✓ Imported mappings from {args.import_mappings}")
                print(f"Total mappings: {mappings_count}")
                logger.info(f"Imported mappings via CLI from {args.import_mappings}")
                return True
            else:
                print(f"✗ Failed to import mappings from {args.import_mappings}")
                logger.error(f"Failed to import mappings via CLI from {args.import_mappings}")
                return False
        else:
            print(f"✗ File not found: {args.import_mappings}")
            return False
    
    return False


def run_headless_mode(config):
    """Run in headless mode without GUI."""
    logger = get_logger(__name__)
    logger.info("Starting Key Replacer in headless mode")
    
    # Create and start key replacer
    key_replacer = KeyReplacer(config=config)
    
    # Set up callbacks
    def on_expansion(key, value):
        logger.info(f"Expanded: {key} → {value[:50]}{'...' if len(value) > 50 else ''}")
    
    def on_error(error_msg):
        logger.error(f"Key replacer error: {error_msg}")
    
    def on_status_change(status):
        logger.info(f"Status changed: {status}")
    
    key_replacer.set_callbacks(
        on_expansion=on_expansion,
        on_error=on_error,
        on_status_change=on_status_change
    )
    
    # Load mappings and start
    key_replacer.set_mappings(config.get_mappings())
    
    if not key_replacer.start():
        logger.error("Failed to start key replacer")
        return False
    
    try:
        print("Key Replacer is running in headless mode...")
        print("Press Ctrl+C to stop.")
        
        # Keep running until interrupted
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        logger.info("Received keyboard interrupt")
    finally:
        key_replacer.stop()
        logger.info("Key Replacer stopped")
    
    return True


def run_gui_mode(config):
    """Run with GUI interface."""
    logger = get_logger(__name__)
    logger.info("Starting Key Replacer with GUI")
    
    try:
        # Create key replacer engine
        key_replacer = KeyReplacer(config=config)
        
        # Create GUI
        gui = KeyReplacerGUI(config=config, key_replacer=key_replacer)
        
        # Run the GUI
        gui.run()
        
        return True
        
    except ImportError as e:
        logger.error(f"GUI dependencies not available: {e}")
        print("Error: GUI dependencies not available.")
        print("Please install the required packages or run with --no-gui flag.")
        return False
    except Exception as e:
        logger.error(f"GUI error: {e}")
        print(f"Error: {e}")
        return False


def main():
    """Main entry point."""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Initialize configuration
        if args.config_dir:
            # TODO: Pass custom config directory to Config class
            config = Config()
        else:
            config = Config()
        
        # Setup logging
        log_file = None if args.no_file_logging else config.log_file
        setup_logging(
            log_file=log_file,
            log_level=args.log_level,
            enable_file=not args.no_file_logging
        )
        
        logger = get_logger(__name__)
        logger.info("Key Replacer starting...")
        logger.info(f"Config directory: {config.config_dir}")
        logger.info(f"Data directory: {config.data_dir}")
        
        # Handle CLI commands that don't require the main application
        if run_cli_commands(args, config):
            return 0
        
        # Run in appropriate mode
        if args.no_gui:
            success = run_headless_mode(config)
        else:
            success = run_gui_mode(config)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        try:
            logger = get_logger(__name__)
            logger.critical(f"Fatal error: {e}", exc_info=True)
        except:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
