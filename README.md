# Key Replacer

A powerful, cross-platform text expansion tool that helps boost your productivity by automatically replacing short text snippets with longer predefined text.

## Features

- 🚀 **Real-time text expansion**: Type shortcuts and watch them expand instantly
- 🖥️ **Cross-platform support**: Works on Windows, macOS, and Linux
- 🎯 **Simple GUI**: Easy-to-use interface for managing your text expansions
- 💾 **Persistent storage**: Your mappings are automatically saved and restored
- ⚡ **Low resource usage**: Minimal system impact with efficient background monitoring
- 🔧 **Customizable**: Add, edit, and remove text expansions on the fly
- 🛡️ **Safe and secure**: No data collection, everything stored locally

## Installation

### Download Pre-built Binaries

Visit our [releases page](https://github.com/kumar10248/key_replacer/releases) and download the appropriate version for your operating system:

- **Windows**: `key-replacer-windows.exe`
- **macOS**: `key-replacer-macos`
- **Linux**: `key-replacer-linux`

### Install from Source

```bash
# Clone the repository
git clone https://github.com/kumar10248/key_replacer.git
cd key_replacer

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m keyreplacer
```

## Usage

1. **Launch the application**: Double-click the executable or run from command line
2. **Add text expansions**: 
   - Enter a short key (e.g., "myemail")
   - Enter the replacement text (e.g., "john.doe@example.com")
   - Click "Add Mapping"
3. **Use your expansions**: Type your key followed by space or enter, and watch it expand!

### Example Use Cases

- **Email signatures**: `sig` → `Best regards,\nJohn Doe\nSoftware Engineer`
- **Common phrases**: `addr` → `123 Main Street, City, State 12345`
- **Code snippets**: `func` → `function functionName() {\n    // code here\n}`
- **Personal information**: `phone` → `+1-234-567-8900`

## Configuration

The application stores your text expansions in a local `mappings.json` file. You can:

- **Backup your mappings**: Copy the `mappings.json` file
- **Share mappings**: Send your `mappings.json` file to colleagues
- **Import mappings**: Replace your `mappings.json` file with another one

## System Requirements

- **Windows**: Windows 10 or later
- **macOS**: macOS 10.14 or later
- **Linux**: Most modern distributions with X11 or Wayland support

## Privacy & Security

- **No data collection**: Your text expansions never leave your device
- **Local storage only**: All data is stored locally on your machine
- **Open source**: Full source code available for inspection
- **No network access**: The application doesn't connect to the internet

## Building from Source

### Prerequisites

- Python 3.8 or later
- pip package manager

### Build Instructions

```bash
# Clone and setup
git clone https://github.com/kumar10248/key_replacer.git
cd key_replacer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Build executable
python build_scripts/build.py

# The executable will be in the dist/ directory
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/kumar10248/key_replacer.git
cd key_replacer

# Create development environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## Troubleshooting

### Common Issues

**Linux: Permission errors**
```bash
sudo apt-get install python3-tk python3-dev
```

**macOS: Accessibility permissions**
1. Go to System Preferences → Security & Privacy → Privacy
2. Add Key Replacer to "Accessibility" and "Input Monitoring"

**Windows: Antivirus false positives**
- Add the executable to your antivirus whitelist
- This is common with PyInstaller-built applications

### Getting Help

- **Issues**: Report bugs on our [GitHub Issues](https://github.com/kumar10248/key_replacer/issues)
- **Discussions**: Join our [GitHub Discussions](https://github.com/kumar10248/key_replacer/discussions)
- **Wiki**: Check our [Wiki](https://github.com/kumar10248/key_replacer/wiki) for detailed guides

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0
- Initial release
- Cross-platform text expansion
- GUI for managing mappings
- Automatic persistence
- System tray integration

---

**Made with ❤️ by Kumar Devashish**
