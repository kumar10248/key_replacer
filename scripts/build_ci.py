#!/usr/bin/env python3
"""
Simple build script for CI environments.
Creates executables using PyInstaller with minimal configuration.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path


def main():
    """Build the executable."""
    project_root = Path(__file__).parent.parent
    main_script = project_root / "keyreplacer" / "main.py"
    
    if not main_script.exists():
        print(f"ERROR: Main script not found: {main_script}")
        return 1
    
    # Ensure we're in the project directory
    os.chdir(project_root)
    
    # Basic PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(main_script),
        "--name=key-replacer",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--windowed",  # No console window
    ]
    
    # Add platform-specific hidden imports
    system = platform.system()
    if system == "Linux":
        cmd.extend([
            "--hidden-import=Xlib",
            "--hidden-import=Xlib.display",
        ])
    elif system == "Darwin":  # macOS
        cmd.extend([
            "--hidden-import=AppKit",
            "--hidden-import=Foundation",
        ])
    elif system == "Windows":
        cmd.extend([
            "--hidden-import=win32api",
            "--hidden-import=win32con",
            "--hidden-import=win32gui",
        ])
    
    # Add essential hidden imports
    cmd.extend([
        "--hidden-import=keyreplacer",
        "--hidden-import=keyreplacer.config",
        "--hidden-import=keyreplacer.core",
        "--hidden-import=keyreplacer.gui",
        "--hidden-import=keyreplacer.logging_setup",
        "--hidden-import=keyboard",
        "--hidden-import=pyautogui",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "--hidden-import=appdirs",
        "--hidden-import=json",
        "--hidden-import=logging",
        "--hidden-import=threading",
        "--hidden-import=pathlib",
        "--hidden-import=os",
        "--hidden-import=sys",
        "--hidden-import=platform",
        "--collect-submodules=keyreplacer",
    ])
    
    print(f"Building Key Replacer for {system}...")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Main script path: {main_script}")
    print(f"Main script exists: {main_script.exists()}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print("STDOUT:", result.stdout[-1000:] if result.stdout else "No stdout")
        
        # Show what was created
        dist_dir = project_root / "dist"
        if dist_dir.exists():
            print("\nBuild artifacts:")
            for item in dist_dir.iterdir():
                size = ""
                if item.is_file():
                    size_bytes = item.stat().st_size
                    size = f" ({size_bytes / (1024*1024):.1f} MB)"
                print(f"  {item.name}{size}")
        else:
            print("ERROR: dist directory not created")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout[-1000:] if e.stdout else "No stdout")
        print("STDERR:", e.stderr[-1000:] if e.stderr else "No stderr")
        return e.returncode
    except Exception as e:
        print(f"Build failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
