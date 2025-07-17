"""
Tests for the Config class.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from keyreplacer.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_config_initialization(self, mock_config_dir):
        """Test that config initializes correctly with proper directories."""
        config = Config()
        
        assert config.config_dir.exists()
        assert config.data_dir.exists()
        assert config.cache_dir.exists()
        assert config.config_file.name == "config.json"
        assert config.mappings_file.name == "mappings.json"

    def test_default_config_creation(self, mock_config_dir):
        """Test that default configuration is created when no config file exists."""
        config = Config()
        
        # Check that default configuration is loaded
        assert config.get_setting("version") == "1.0.0"
        assert config.get_setting("settings.case_sensitive") is False
        assert config.get_setting("settings.typing_delay") == 0.01

    def test_add_mapping_success(self, mock_config_dir):
        """Test successful addition of a mapping."""
        config = Config()
        result = config.add_mapping("test", "test value")
        
        assert result is True
        mappings = config.get_mappings()
        assert "test" in mappings
        assert mappings["test"] == "test value"

    def test_add_mapping_empty_key(self, mock_config_dir):
        """Test that empty keys are rejected."""
        config = Config()
        result = config.add_mapping("", "test value")
        
        assert result is False
        assert len(config.get_mappings()) == 0

    def test_add_mapping_empty_value(self, mock_config_dir):
        """Test that empty values are rejected."""
        config = Config()
        result = config.add_mapping("test", "")
        
        assert result is False
        assert len(config.get_mappings()) == 0

    def test_add_mapping_case_insensitive(self, mock_config_dir):
        """Test that keys are made lowercase when case insensitive."""
        config = Config()
        config.set_setting("settings.case_sensitive", False)
        
        result = config.add_mapping("TEST", "test value")
        
        assert result is True
        mappings = config.get_mappings()
        assert "test" in mappings
        assert "TEST" not in mappings

    def test_add_mapping_case_sensitive(self, mock_config_dir):
        """Test that keys preserve case when case sensitive."""
        config = Config()
        config.set_setting("settings.case_sensitive", True)
        
        result = config.add_mapping("TEST", "test value")
        
        assert result is True
        mappings = config.get_mappings()
        assert "TEST" in mappings
        assert "test" not in mappings

    def test_remove_mapping_success(self, mock_config_dir):
        """Test successful removal of a mapping."""
        config = Config()
        config.add_mapping("test", "test value")
        
        result = config.remove_mapping("test")
        
        assert result is True
        assert "test" not in config.get_mappings()

    def test_remove_mapping_nonexistent(self, mock_config_dir):
        """Test removal of non-existent mapping."""
        config = Config()
        
        result = config.remove_mapping("nonexistent")
        
        assert result is False

    def test_clear_mappings(self, mock_config_dir):
        """Test clearing all mappings."""
        config = Config()
        config.add_mapping("test1", "value1")
        config.add_mapping("test2", "value2")
        
        result = config.clear_mappings()
        
        assert result is True
        assert len(config.get_mappings()) == 0

    def test_get_setting_existing(self, mock_config_dir):
        """Test getting an existing setting."""
        config = Config()
        
        value = config.get_setting("settings.typing_delay")
        
        assert value == 0.01

    def test_get_setting_nonexistent(self, mock_config_dir):
        """Test getting a non-existent setting."""
        config = Config()
        
        value = config.get_setting("nonexistent.setting", "default")
        
        assert value == "default"

    def test_set_setting_success(self, mock_config_dir):
        """Test setting a configuration value."""
        config = Config()
        
        result = config.set_setting("settings.typing_delay", 0.05)
        
        assert result is True
        assert config.get_setting("settings.typing_delay") == 0.05

    def test_export_mappings_success(self, mock_config_dir, sample_mappings):
        """Test successful export of mappings."""
        config = Config()
        for key, value in sample_mappings.items():
            config.add_mapping(key, value)
        
        export_file = config.data_dir / "test_export.json"
        result = config.export_mappings(str(export_file))
        
        assert result is True
        assert export_file.exists()
        
        # Verify exported content
        with open(export_file, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
        
        assert exported_data == sample_mappings

    def test_import_mappings_merge(self, mock_config_dir, sample_mappings):
        """Test importing mappings with merge option."""
        config = Config()
        config.add_mapping("existing", "existing value")
        
        # Create import file
        import_file = config.data_dir / "test_import.json"
        with open(import_file, 'w', encoding='utf-8') as f:
            json.dump(sample_mappings, f)
        
        result = config.import_mappings(str(import_file), merge=True)
        
        assert result is True
        mappings = config.get_mappings()
        assert "existing" in mappings  # Original mapping preserved
        assert "email" in mappings     # New mapping added

    def test_import_mappings_replace(self, mock_config_dir, sample_mappings):
        """Test importing mappings with replace option."""
        config = Config()
        config.add_mapping("existing", "existing value")
        
        # Create import file
        import_file = config.data_dir / "test_import.json"
        with open(import_file, 'w', encoding='utf-8') as f:
            json.dump(sample_mappings, f)
        
        result = config.import_mappings(str(import_file), merge=False)
        
        assert result is True
        mappings = config.get_mappings()
        assert "existing" not in mappings  # Original mapping replaced
        assert "email" in mappings         # New mapping added
        assert len(mappings) == len(sample_mappings)

    def test_key_length_validation(self, mock_config_dir):
        """Test that overly long keys are rejected."""
        config = Config()
        long_key = "a" * 100  # Longer than default max of 50
        
        result = config.add_mapping(long_key, "test value")
        
        assert result is False

    def test_value_length_validation(self, mock_config_dir):
        """Test that overly long values are rejected."""
        config = Config()
        long_value = "a" * 10000  # Longer than default max of 5000
        
        result = config.add_mapping("test", long_value)
        
        assert result is False
