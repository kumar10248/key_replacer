"""
Core functionality for the Key Replacer application.
"""

import logging
import platform
import threading
import time
from typing import Dict, Optional, Callable, Any
import os
import subprocess
import sys

try:
    import keyboard
except ImportError:
    keyboard = None

try:
    import pyautogui
    # Disable pyautogui's failsafe
    pyautogui.FAILSAFE = False
except ImportError:
    pyautogui = None

logger = logging.getLogger(__name__)


class KeyReplacer:
    """Core text replacement engine."""

    def __init__(self, config=None):
        """Initialize the key replacer with configuration."""
        self.config = config
        self.mappings: Dict[str, str] = {}
        self.is_running = False
        self.is_paused = False
        self.listener_thread: Optional[threading.Thread] = None
        self.typed_buffer = ""
        self.suppress_next = False
        self.system = platform.system()
        
        # Callbacks
        self.on_expansion = None
        self.on_error = None
        self.on_status_change = None
        
        # Platform-specific setup
        self._setup_platform()
        
        logger.info(f"KeyReplacer initialized for {self.system}")

    def _setup_platform(self):
        """Setup platform-specific configurations."""
        if self.system == "Linux":
            # Check if xdotool is available
            try:
                subprocess.run(["which", "xdotool"], check=True, 
                             capture_output=True, text=True)
                self.linux_method = "xdotool"
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    subprocess.run(["which", "wtype"], check=True, 
                                 capture_output=True, text=True)
                    self.linux_method = "wtype"
                except (subprocess.CalledProcessError, FileNotFoundError):
                    self.linux_method = "pyautogui"
                    logger.warning("Neither xdotool nor wtype found, falling back to pyautogui")
        elif self.system == "Darwin":  # macOS
            self.macos_method = "pyautogui"  # Could add AppleScript support later
        elif self.system == "Windows":
            self.windows_method = "pyautogui"

    def set_mappings(self, mappings: Dict[str, str]):
        """Set the text expansion mappings."""
        self.mappings = mappings.copy()
        if not self.config or not self.config.get_setting("settings.case_sensitive", False):
            # Convert all keys to lowercase for case-insensitive matching
            self.mappings = {k.lower(): v for k, v in self.mappings.items()}
        logger.info(f"Updated mappings: {len(self.mappings)} entries")

    def add_mapping(self, key: str, value: str) -> bool:
        """Add a single mapping."""
        if not key or not value:
            return False
        
        if not self.config or not self.config.get_setting("settings.case_sensitive", False):
            key = key.lower()
        
        self.mappings[key] = value
        logger.info(f"Added mapping: {key} -> {value[:50]}...")
        return True

    def remove_mapping(self, key: str) -> bool:
        """Remove a mapping."""
        if not self.config or not self.config.get_setting("settings.case_sensitive", False):
            key = key.lower()
        
        if key in self.mappings:
            del self.mappings[key]
            logger.info(f"Removed mapping: {key}")
            return True
        return False

    def start(self) -> bool:
        """Start the key listener."""
        if self.is_running:
            logger.warning("KeyReplacer is already running")
            return False

        if not keyboard:
            logger.error("keyboard library not available")
            if self.on_error:
                self.on_error("Keyboard library not available. Please install the 'keyboard' package.")
            return False

        try:
            self.is_running = True
            self.is_paused = False
            self.listener_thread = threading.Thread(target=self._listen_keys, daemon=True)
            self.listener_thread.start()
            logger.info("KeyReplacer started")
            if self.on_status_change:
                self.on_status_change("running")
            return True
        except Exception as e:
            logger.error(f"Failed to start KeyReplacer: {e}")
            self.is_running = False
            if self.on_error:
                self.on_error(f"Failed to start: {e}")
            return False

    def stop(self):
        """Stop the key listener."""
        if not self.is_running:
            return

        self.is_running = False
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1.0)
        
        logger.info("KeyReplacer stopped")
        if self.on_status_change:
            self.on_status_change("stopped")

    def pause(self):
        """Pause text expansion without stopping the listener."""
        self.is_paused = True
        logger.info("KeyReplacer paused")
        if self.on_status_change:
            self.on_status_change("paused")

    def resume(self):
        """Resume text expansion."""
        self.is_paused = False
        logger.info("KeyReplacer resumed")
        if self.on_status_change:
            self.on_status_change("running")

    def toggle_pause(self):
        """Toggle between paused and running states."""
        if self.is_paused:
            self.resume()
        else:
            self.pause()

    def _listen_keys(self):
        """Main key listening loop."""
        self.typed_buffer = ""
        
        while self.is_running:
            try:
                if self.is_paused:
                    time.sleep(0.1)
                    continue

                event = keyboard.read_event()
                
                if event.event_type != keyboard.KEY_DOWN:
                    continue

                self._handle_key_event(event)
                
            except Exception as e:
                logger.error(f"Error in key listener: {e}")
                if self.on_error:
                    self.on_error(f"Key listener error: {e}")
                time.sleep(0.1)  # Prevent rapid error loops

    def _handle_key_event(self, event):
        """Handle a single key event."""
        key_name = event.name.lower()
        
        # Handle special keys that trigger expansion
        if key_name in ("space", "enter", "tab"):
            self._check_and_expand(key_name)
        elif key_name == "backspace":
            # Remove last character from buffer
            if self.typed_buffer:
                self.typed_buffer = self.typed_buffer[:-1]
        elif key_name == "escape":
            # Clear buffer on escape
            self.typed_buffer = ""
        elif len(key_name) == 1 and key_name.isprintable():
            # Add printable characters to buffer
            max_buffer_size = 100  # Prevent memory issues
            if len(self.typed_buffer) < max_buffer_size:
                self.typed_buffer += key_name
        else:
            # Clear buffer on other special keys (arrow keys, function keys, etc.)
            self.typed_buffer = ""

    def _check_and_expand(self, trigger_key: str):
        """Check if the current buffer matches any mapping and expand if found."""
        if not self.typed_buffer:
            return

        buffer_to_check = self.typed_buffer
        if not self.config or not self.config.get_setting("settings.case_sensitive", False):
            buffer_to_check = buffer_to_check.lower()

        # Check for exact matches first
        if buffer_to_check in self.mappings:
            self._perform_expansion(buffer_to_check, trigger_key)
            return

        # Check for matches at the end of the buffer (partial matching)
        for key in self.mappings:
            if buffer_to_check.endswith(key):
                self._perform_expansion(key, trigger_key)
                return

    def _perform_expansion(self, matched_key: str, trigger_key: str):
        """Perform the actual text expansion."""
        try:
            replacement_text = self.mappings[matched_key]
            
            # Calculate how many characters to delete
            chars_to_delete = len(matched_key)
            
            # Delete the typed key sequence
            self._delete_characters(chars_to_delete)
            
            # Get timing settings
            if self.config:
                expansion_delay = self.config.get_setting("settings.expansion_delay", 0.1)
                typing_delay = self.config.get_setting("settings.typing_delay", 0.01)
            else:
                expansion_delay = 0.1
                typing_delay = 0.01
            
            # Wait a bit before typing
            time.sleep(expansion_delay)
            
            # Type the replacement text
            self._type_text(replacement_text, typing_delay)
            
            # Add the trigger key if it wasn't space (which might be part of the text)
            if trigger_key != "space":
                if trigger_key == "enter":
                    self._press_key("enter")
                elif trigger_key == "tab":
                    self._press_key("tab")
            
            # Clear the buffer
            self.typed_buffer = ""
            
            # Notify about the expansion
            if self.on_expansion:
                self.on_expansion(matched_key, replacement_text)
                
            logger.debug(f"Expanded '{matched_key}' to '{replacement_text[:50]}...'")
            
        except Exception as e:
            logger.error(f"Error during expansion: {e}")
            if self.on_error:
                self.on_error(f"Expansion error: {e}")

    def _delete_characters(self, count: int):
        """Delete the specified number of characters."""
        if count <= 0:
            return

        try:
            if self.config:
                backspace_delay = self.config.get_setting("settings.backspace_delay", 0.02)
            else:
                backspace_delay = 0.02

            for _ in range(count):
                keyboard.press_and_release("backspace")
                if backspace_delay > 0:
                    time.sleep(backspace_delay)
                    
        except Exception as e:
            logger.error(f"Error deleting characters: {e}")

    def _type_text(self, text: str, delay: float = 0.01):
        """Type text using the appropriate method for the current platform."""
        try:
            if self.system == "Linux":
                self._type_text_linux(text)
            elif self.system == "Darwin":
                self._type_text_macos(text)
            elif self.system == "Windows":
                self._type_text_windows(text)
            else:
                # Fallback to pyautogui
                if pyautogui:
                    pyautogui.write(text, interval=delay)
                else:
                    logger.error("No typing method available")
                    
        except Exception as e:
            logger.error(f"Error typing text: {e}")

    def _type_text_linux(self, text: str):
        """Type text on Linux using xdotool or wtype."""
        try:
            if self.linux_method == "xdotool":
                # Escape special characters for shell
                escaped_text = text.replace("'", "'\"'\"'")
                os.system(f"xdotool type --delay 1 '{escaped_text}'")
            elif self.linux_method == "wtype":
                # wtype for Wayland
                escaped_text = text.replace("'", "'\"'\"'")
                os.system(f"wtype '{escaped_text}'")
            else:
                # Fallback to pyautogui
                if pyautogui:
                    pyautogui.write(text, interval=0.01)
        except Exception as e:
            logger.error(f"Error typing text on Linux: {e}")

    def _type_text_macos(self, text: str):
        """Type text on macOS."""
        try:
            if pyautogui:
                pyautogui.write(text, interval=0.01)
        except Exception as e:
            logger.error(f"Error typing text on macOS: {e}")

    def _type_text_windows(self, text: str):
        """Type text on Windows."""
        try:
            if pyautogui:
                pyautogui.write(text, interval=0.01)
        except Exception as e:
            logger.error(f"Error typing text on Windows: {e}")

    def _press_key(self, key: str):
        """Press a specific key."""
        try:
            keyboard.press_and_release(key)
        except Exception as e:
            logger.error(f"Error pressing key {key}: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status information."""
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "mappings_count": len(self.mappings),
            "system": self.system,
            "buffer": self.typed_buffer,
        }

    def set_callbacks(self, on_expansion: Optional[Callable] = None,
                     on_error: Optional[Callable] = None,
                     on_status_change: Optional[Callable] = None):
        """Set callback functions for various events."""
        self.on_expansion = on_expansion
        self.on_error = on_error
        self.on_status_change = on_status_change
