"""
Test configuration for pytest.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_config_dir(temp_dir, monkeypatch):
    """Mock the configuration directory for testing."""
    config_dir = temp_dir / "config"
    data_dir = temp_dir / "data"
    cache_dir = temp_dir / "cache"
    
    config_dir.mkdir()
    data_dir.mkdir()
    cache_dir.mkdir()
    
    # Mock appdirs functions
    monkeypatch.setattr("appdirs.user_config_dir", lambda app: str(config_dir))
    monkeypatch.setattr("appdirs.user_data_dir", lambda app: str(data_dir))
    monkeypatch.setattr("appdirs.user_cache_dir", lambda app: str(cache_dir))
    
    return {
        "config": config_dir,
        "data": data_dir,
        "cache": cache_dir
    }


@pytest.fixture
def sample_mappings():
    """Sample mappings for testing."""
    return {
        "email": "john.doe@example.com",
        "addr": "123 Main Street, City, State 12345",
        "sig": "Best regards,\\nJohn Doe\\nSoftware Engineer",
        "phone": "+1-234-567-8900"
    }
