import os
import asyncio
import subprocess
from pathlib import Path

import decky


class Plugin:
    def __init__(self):
        self.loop = None
        self.rumble_task = None
        self.settings = {
            "enabled": True,
            "gain_percent": 60,
            "interval_sec": 2,
        }
        self.device_path = None
        self.binary_path = None
        self.running = False

    async def _main(self):
        """Called when plugin is loaded"""
        self.loop = asyncio.get_event_loop()
        decky.logger.info("ROG Ally Rumble Fixer loaded")
        
        # Load settings
        await self._load_settings()
        
        # Find the binary path
        self.binary_path = self._find_binary()
        if not self.binary_path:
            decky.logger.error("Could not find rumble-fixer binary")
            return
        
        # Start rumble fixer if enabled
        if self.settings["enabled"]:
            await self.start_rumble_fixer()

    async def _unload(self):
        """Called when plugin is unloaded"""
        decky.logger.info("ROG Ally Rumble Fixer unloading")
        await self.stop_rumble_fixer()

    async def _uninstall(self):
        """Called when plugin is uninstalled"""
        decky.logger.info("ROG Ally Rumble Fixer uninstalling")
        await self.stop_rumble_fixer()

    def _get_settings_path(self) -> Path:
        """Get settings file path - use Decky's plugin settings directory"""
        return Path(decky.DECKY_PLUGIN_SETTINGS_DIR) / "settings.json"

    async def _load_settings(self):
        """Load settings from disk"""
        try:
            settings_path = self._get_settings_path()
            decky.logger.info(f"Loading settings from: {settings_path}")
            if settings_path.exists():
                import json
                with open(settings_path, "r") as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
                    decky.logger.info(f"Settings loaded: {self.settings}")
            else:
                decky.logger.info("No settings file found, using defaults")
        except Exception as e:
            decky.logger.error(f"Failed to load settings: {e}")

    async def _save_settings(self):
        """Save settings to disk"""
        try:
            settings_path = self._get_settings_path()
            decky.logger.info(f"Saving settings to: {settings_path}")
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            import json
            with open(settings_path, "w") as f:
                json.dump(self.settings, f, indent=2)
            decky.logger.info(f"Settings saved: {self.settings}")
        except Exception as e:
            decky.logger.error(f"Failed to save settings: {e}")

    def _find_binary(self) -> str:
        """Find the rumble-fixer binary"""
        # Check in plugin directory
        plugin_dir = Path(decky.DECKY_PLUGIN_DIR)
        binary = plugin_dir / "bin" / "rumble-fixer"
        if binary.exists():
            # Ensure it's executable
            import stat
            current_mode = binary.stat().st_mode
            if not (current_mode & stat.S_IXUSR):
                binary.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            return str(binary)
        
        # Check backend out directory (development)
        backend_binary = plugin_dir / "backend" / "out" / "rumble-fixer"
        if backend_binary.exists():
            return str(backend_binary)
        
        return None

    async def _detect_device(self) -> bool:
        """Auto-detect the joystick device"""
        try:
            # Look for devices with event-joystick in /dev/input/by-id/
            by_id_path = Path("/dev/input/by-id")
            if by_id_path.exists():
                for device in by_id_path.iterdir():
                    if "event-joystick" in device.name:
                        self.device_path = str(device.absolute())
                        return True
            
            decky.logger.error("No joystick event device found")
        except Exception:
            decky.logger.error("Failed to find joystick event device: {e}")
        return False

    async def _rumble_loop(self):
        """Background task that continuously sets rumble gain"""
        while self.running:
            try:
                if self.device_path and Path(self.device_path).exists():
                    subprocess.run(
                        [
                            str(self.binary_path),
                            str(self.device_path),
                            str(self.settings["gain_percent"])
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
            except Exception as e:
                # Log errors but continue - we'll try again next interval
                decky.logger.warning(f"Rumble loop error: {e}")
            
            # Wait for configured interval
            await asyncio.sleep(self.settings["interval_sec"])

    async def start_rumble_fixer(self):
        """Start the rumble fixer background task"""
        if self.rumble_task and not self.rumble_task.done():
            return
        
        if not await self._detect_device():
            decky.logger.error("Cannot start rumble fixer: no device detected")
            return
        
        self.running = True
        self.rumble_task = self.loop.create_task(self._rumble_loop())
        decky.logger.info("Rumble fixer started")

    async def stop_rumble_fixer(self):
        """Stop the rumble fixer background task"""
        self.running = False
        if self.rumble_task and not self.rumble_task.done():
            self.rumble_task.cancel()
            try:
                await self.rumble_task
            except asyncio.CancelledError:
                pass
        self.rumble_task = None
        decky.logger.info("Rumble fixer stopped")

    # Methods callable from frontend
    async def get_settings(self):
        """Get current settings"""
        return {
            **self.settings,
            "device_path": self.device_path,
            "running": self.running
        }

    async def set_enabled(self, enabled: bool):
        """Enable/disable rumble fixer"""
        self.settings["enabled"] = enabled
        await self._save_settings()
        
        if enabled:
            await self.start_rumble_fixer()
        else:
            await self.stop_rumble_fixer()
        
        return self.settings["enabled"]

    async def set_gain(self, gain_percent: int):
        """Set rumble gain percentage"""
        gain_percent = max(0, min(100, gain_percent))
        self.settings["gain_percent"] = gain_percent
        await self._save_settings()
        return self.settings["gain_percent"]

    async def set_interval(self, interval_sec: int):
        """Set update interval in seconds"""
        interval_sec = max(1, min(10, interval_sec))
        self.settings["interval_sec"] = interval_sec
        await self._save_settings()
        return self.settings["interval_sec"]

    async def get_device_status(self):
        """Get device detection status"""
        return {
            "device_path": self.device_path,
            "device_exists": Path(self.device_path).exists() if self.device_path else False,
            "binary_path": self.binary_path,
            "binary_exists": Path(self.binary_path).exists() if self.binary_path else False
        }

    async def _migration(self):
        """Handle migrations"""
        decky.logger.info("Running migration")
