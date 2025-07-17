"""
Configuration management for Key Replacer application.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import appdirs

logger = logging.getLogger(__name__)


class Config:
    """Manages application configuration and user settings."""

    def __init__(self, app_name: str = "KeyReplacer"):
        self.app_name = app_name
        self.config_dir = Path(appdirs.user_config_dir(app_name))
        self.data_dir = Path(appdirs.user_data_dir(app_name))
        self.cache_dir = Path(appdirs.user_cache_dir(app_name))
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration files
        self.config_file = self.config_dir / "config.json"
        self.mappings_file = self.data_dir / "mappings.json"
        self.log_file = self.cache_dir / "keyreplacer.log"
        
        # Default configuration
        self.default_config = {
            "version": "1.0.0",
            "settings": {
                "startup_with_system": False,
                "minimize_to_tray": True,
                "show_notifications": True,
                "case_sensitive": False,
                "typing_delay": 0.01,
                "backspace_delay": 0.05,
                "expansion_delay": 0.1,
                "max_key_length": 50,
                "max_value_length": 5000,
                "hotkey_toggle": "ctrl+alt+k",
                "theme": "system",
                "window_position": {"x": 100, "y": 100},
                "window_size": {"width": 500, "height": 400}
            },
            "advanced": {
                "enable_logging": True,
                "log_level": "INFO",
                "auto_backup": True,
                "backup_interval_days": 7,
                "max_backup_files": 10
            }
        }
        
        self._config = self.load_config()
        self._mappings = self.load_mappings()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_config(self.default_config, config)
            else:
                logger.info("Config file not found, creating default configuration")
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self.default_config.copy()

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Save configuration to file."""
        try:
            config_to_save = config or self._config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False

    def load_mappings(self) -> Dict[str, str]:
        """Load text expansion mappings from file."""
        try:
            if self.mappings_file.exists():
                with open(self.mappings_file, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
                    if isinstance(mappings, dict):
                        logger.info(f"Loaded {len(mappings)} mappings")
                        return mappings
            logger.info("No mappings file found, starting with empty mappings")
            return {}
        except Exception as e:
            logger.error(f"Error loading mappings: {e}")
            return {}

    def save_mappings(self, mappings: Optional[Dict[str, str]] = None) -> bool:
        """Save text expansion mappings to file."""
        try:
            mappings_to_save = mappings or self._mappings
            
            # Create backup if auto_backup is enabled
            if self.get_setting("advanced.auto_backup", True):
                self._create_backup()
            
            with open(self.mappings_file, 'w', encoding='utf-8') as f:
                json.dump(mappings_to_save, f, indent=2, ensure_ascii=False)
            
            if mappings is not None:
                self._mappings = mappings
            
            logger.info(f"Saved {len(mappings_to_save)} mappings")
            return True
        except Exception as e:
            logger.error(f"Error saving mappings: {e}")
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value using dot notation (e.g., 'settings.typing_delay')."""
        try:
            keys = key.split('.')
            value = self._config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set_setting(self, key: str, value: Any) -> bool:
        """Set a setting value using dot notation."""
        try:
            keys = key.split('.')
            config = self._config
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
            return self.save_config()
        except Exception as e:
            logger.error(f"Error setting config key {key}: {e}")
            return False

    def add_mapping(self, key: str, value: str) -> bool:
        """Add a new text expansion mapping."""
        if not key or not value:
            return False
        
        # Validate key length
        max_key_length = self.get_setting("settings.max_key_length", 50)
        if len(key) > max_key_length:
            logger.warning(f"Key too long: {len(key)} > {max_key_length}")
            return False
        
        # Validate value length
        max_value_length = self.get_setting("settings.max_value_length", 5000)
        if len(value) > max_value_length:
            logger.warning(f"Value too long: {len(value)} > {max_value_length}")
            return False
        
        # Handle case sensitivity
        if not self.get_setting("settings.case_sensitive", False):
            key = key.lower()
        
        self._mappings[key] = value
        return self.save_mappings()

    def remove_mapping(self, key: str) -> bool:
        """Remove a text expansion mapping."""
        if not self.get_setting("settings.case_sensitive", False):
            key = key.lower()
        
        if key in self._mappings:
            del self._mappings[key]
            return self.save_mappings()
        return False

    def get_mappings(self) -> Dict[str, str]:
        """Get all text expansion mappings."""
        return self._mappings.copy()

    def clear_mappings(self) -> bool:
        """Clear all text expansion mappings."""
        self._mappings.clear()
        return self.save_mappings()

    def export_mappings(self, file_path: str) -> bool:
        """Export mappings to a JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._mappings, f, indent=2, ensure_ascii=False)
            logger.info(f"Mappings exported to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting mappings: {e}")
            return False

    def import_mappings(self, file_path: str, merge: bool = True) -> bool:
        """Import mappings from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_mappings = json.load(f)
            
            if not isinstance(imported_mappings, dict):
                logger.error("Invalid mappings file format")
                return False
            
            if merge:
                self._mappings.update(imported_mappings)
            else:
                self._mappings = imported_mappings
            
            success = self.save_mappings()
            if success:
                logger.info(f"Imported {len(imported_mappings)} mappings from {file_path}")
            return success
        except Exception as e:
            logger.error(f"Error importing mappings: {e}")
            return False

    def _create_backup(self) -> bool:
        """Create a backup of current mappings."""
        try:
            backup_dir = self.data_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"mappings_backup_{timestamp}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self._mappings, f, indent=2, ensure_ascii=False)
            
            # Clean up old backups
            self._cleanup_old_backups(backup_dir)
            
            logger.info(f"Backup created: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False

    def _cleanup_old_backups(self, backup_dir: Path) -> None:
        """Remove old backup files."""
        try:
            max_backups = self.get_setting("advanced.max_backup_files", 10)
            backup_files = sorted(backup_dir.glob("mappings_backup_*.json"))
            
            if len(backup_files) > max_backups:
                for file_to_remove in backup_files[:-max_backups]:
                    file_to_remove.unlink()
                    logger.info(f"Removed old backup: {file_to_remove}")
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")

    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with default config."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def get_app_dirs(self) -> Dict[str, Path]:
        """Get application directories."""
        return {
            "config": self.config_dir,
            "data": self.data_dir,
            "cache": self.cache_dir
        }

    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        try:
            self._config = self.default_config.copy()
            return self.save_config()
        except Exception as e:
            logger.error(f"Error resetting config: {e}")
            return False
