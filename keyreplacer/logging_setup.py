"""
Logging configuration for Key Replacer application.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import sys


def setup_logging(
    log_file: Optional[Path] = None,
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_file: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """
    Setup logging configuration for the application.
    
    Args:
        log_file: Path to log file. If None, logs to user cache directory.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        enable_console: Whether to log to console.
        enable_file: Whether to log to file.
        max_file_size: Maximum size of log file before rotation.
        backup_count: Number of backup log files to keep.
    """
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file and log_file:
        try:
            # Ensure log directory exists
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            # If file logging fails, at least log the error to console
            if enable_console:
                logger.error(f"Failed to setup file logging: {e}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)
