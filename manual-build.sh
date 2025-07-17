#!/bin/bash
# Manual release build script for Key Replacer
# Run this locally to create release binaries

set -e

echo "🏗️  Building Key Replacer Release Binaries"
echo "========================================="

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Get the current version
VERSION=$(git describe --tags --exact-match 2>/dev/null || echo "dev")
echo "📦 Version: $VERSION"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist build *.spec

# Activate virtual environment if it exists
if [ -d "env" ]; then
    echo "🐍 Activating virtual environment..."
    source env/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install keyboard pyautogui pillow appdirs pyinstaller

# Build the executable
echo "🔨 Building executable..."
python -m PyInstaller keyreplacer/main.py \
    --name=key-replacer \
    --onefile \
    --windowed \
    --noconfirm \
    --hidden-import=keyreplacer \
    --hidden-import=keyboard \
    --hidden-import=pyautogui \
    --hidden-import=tkinter \
    --hidden-import=PIL

# Check if build was successful
if [ -f "dist/key-replacer" ]; then
    echo "✅ Build successful!"
    ls -la dist/
    
    # Test the executable
    echo "🧪 Testing executable..."
    ./dist/key-replacer --version || echo "⚠️  Version check failed (but executable exists)"
    
    # Create release directory
    RELEASE_DIR="release-$VERSION"
    mkdir -p "$RELEASE_DIR"
    
    # Copy executable with platform suffix
    PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
    cp dist/key-replacer "$RELEASE_DIR/key-replacer-$PLATFORM"
    
    echo "📦 Release file created: $RELEASE_DIR/key-replacer-$PLATFORM"
    echo "💾 Size: $(du -h "$RELEASE_DIR/key-replacer-$PLATFORM" | cut -f1)"
    
    echo ""
    echo "🎉 Manual build complete!"
    echo "📁 Release file: $RELEASE_DIR/key-replacer-$PLATFORM"
    echo "📤 Upload this file to GitHub releases manually"
    
else
    echo "❌ Build failed - no executable created"
    exit 1
fi
