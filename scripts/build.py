#!/usr/bin/env python3
"""
Build script for Key Replacer application.
Creates executables for different platforms using PyInstaller.
"""

import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path
import argparse


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def clean_build_dirs():
    """Clean previous build artifacts."""
    project_root = get_project_root()
    
    dirs_to_clean = [
        project_root / "build",
        project_root / "dist",
        project_root / "__pycache__",
    ]
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"Cleaning {dir_path}")
            shutil.rmtree(dir_path)
    
    # Clean .spec files
    for spec_file in project_root.glob("*.spec"):
        print(f"Removing {spec_file}")
        spec_file.unlink()


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)


def get_platform_specific_args():
    """Get platform-specific PyInstaller arguments."""
    system = platform.system()
    args = []
    
    if system == "Windows":
        args.extend([
            "--hidden-import=win32api",
            "--hidden-import=win32con",
            "--hidden-import=win32gui",
            "--hidden-import=pywintypes",
        ])
    elif system == "Darwin":  # macOS
        args.extend([
            "--hidden-import=AppKit",
            "--hidden-import=Foundation",
        ])
    elif system == "Linux":
        args.extend([
            "--hidden-import=Xlib",
            "--hidden-import=Xlib.display",
        ])
    
    return args


def build_executable(debug=False, onefile=True):
    """Build the executable using PyInstaller."""
    project_root = get_project_root()
    main_script = project_root / "keyreplacer" / "main.py"
    icon_path = project_root / "assets" / "icon.png"
    
    if not main_script.exists():
        raise FileNotFoundError(f"Main script not found: {main_script}")
    
    # Base PyInstaller arguments
    args = [
        "pyinstaller",
        str(main_script),
        "--name=key-replacer",
        "--clean",
        "--noconfirm",
    ]
    
    # Add icon if available
    if icon_path.exists():
        args.extend(["--icon", str(icon_path)])
    
    # One file vs one directory
    if onefile:
        args.append("--onefile")
    else:
        args.append("--onedir")
    
    # GUI options
    if not debug:
        args.append("--windowed")  # No console window
    else:
        args.append("--console")   # Keep console for debugging
    
    # Hidden imports
    hidden_imports = [
        "keyreplacer",
        "keyreplacer.config",
        "keyreplacer.core",
        "keyreplacer.gui",
        "keyreplacer.logging_setup",
        "keyboard",
        "pyautogui",
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "tkinter.filedialog",
        "tkinter.scrolledtext",
        "PIL",
        "PIL.Image",
        "PIL.ImageTk",
        "appdirs",
        "json",
        "logging",
        "threading",
        "pathlib",
    ]
    
    for import_name in hidden_imports:
        args.append(f"--hidden-import={import_name}")
    
    # Platform-specific arguments
    args.extend(get_platform_specific_args())
    
    # Add data files
    data_files = []
    
    # Add assets directory if it exists
    assets_dir = project_root / "assets"
    if assets_dir.exists():
        data_files.append(f"{assets_dir}:assets")
    
    # Add README and LICENSE
    readme_file = project_root / "README.md"
    if readme_file.exists():
        data_files.append(f"{readme_file}:.")
    
    license_file = project_root / "LICENSE"
    if license_file.exists():
        data_files.append(f"{license_file}:.")
    
    for data_file in data_files:
        args.append(f"--add-data={data_file}")
    
    # Optimization options
    if not debug:
        args.extend([
            "--optimize", "2",
            "--strip",
        ])
    
    print(f"Building executable with command:")
    print(" ".join(args))
    print()
    
    # Run PyInstaller
    result = subprocess.run(args, cwd=project_root)
    
    if result.returncode != 0:
        print("Build failed!")
        return False
    
    print("Build completed successfully!")
    return True


def create_installer():
    """Create platform-specific installer."""
    system = platform.system()
    project_root = get_project_root()
    
    if system == "Windows":
        create_windows_installer(project_root)
    elif system == "Darwin":
        create_macos_installer(project_root)
    elif system == "Linux":
        create_linux_installer(project_root)


def create_windows_installer(project_root):
    """Create Windows installer using NSIS (if available)."""
    print("Windows installer creation not implemented yet.")
    print("You can use tools like NSIS, Inno Setup, or WiX to create an installer.")


def create_macos_installer(project_root):
    """Create macOS app bundle and DMG."""
    print("macOS installer creation not implemented yet.")
    print("You can use tools like create-dmg to create a DMG installer.")


def create_linux_installer(project_root):
    """Create Linux packages (AppImage, .deb, .rpm)."""
    print("Linux installer creation not implemented yet.")
    print("You can use tools like AppImageTool or fpm to create packages.")


def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Build Key Replacer executable")
    parser.add_argument("--debug", action="store_true", help="Build with debug console")
    parser.add_argument("--onedir", action="store_true", help="Build as directory instead of single file")
    parser.add_argument("--clean", action="store_true", help="Clean build directories before building")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies before building")
    parser.add_argument("--create-installer", action="store_true", help="Create platform-specific installer")
    
    args = parser.parse_args()
    
    try:
        project_root = get_project_root()
        os.chdir(project_root)
        
        print(f"Building Key Replacer for {platform.system()}...")
        print(f"Project root: {project_root}")
        print()
        
        if args.clean:
            clean_build_dirs()
        
        if args.install_deps:
            install_dependencies()
        
        # Build executable
        success = build_executable(
            debug=args.debug,
            onefile=not args.onedir
        )
        
        if not success:
            return 1
        
        # Show build results
        dist_dir = project_root / "dist"
        if dist_dir.exists():
            print("\nBuild artifacts:")
            for item in dist_dir.iterdir():
                size = ""
                if item.is_file():
                    size_bytes = item.stat().st_size
                    size = f" ({size_bytes / (1024*1024):.1f} MB)"
                print(f"  {item.name}{size}")
        
        if args.create_installer:
            create_installer()
        
        print("\nBuild completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Build failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
