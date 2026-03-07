# ROG Ally Rumble Fixer

A Decky Loader plugin that fixes rumble intensity on the ROG Ally X running SteamOS/Linux.

## Problem

On the ROG Ally X with SteamOS, InputPlumber (the input handling service) periodically overrides the controller's force feedback gain to its default value. This causes the rumble intensity to reset unexpectedly, leading to inconsistent haptic feedback during gaming.

## Solution

This plugin continuously monitors and sets the force feedback gain on the controller's input device to maintain your preferred rumble intensity. It auto-detects the joystick device and reapplies settings at a configurable interval to prevent InputPlumber from overriding them.

## Features

- **Auto-detection**: Automatically finds the joystick device (looks for `event-joystick` in `/dev/input/by-id/`)
- **Configurable rumble intensity**: Adjustable from 0% to 100% (default: 60%)
- **Update interval**: Configurable check interval from 1-10 seconds (default: 2 seconds)
- **Toggle on/off**: Enable or disable the fixer as needed
- **Persistent settings**: Saves your preferences between sessions

## Installation

### Quick Install (Terminal)

Run this command in a terminal to automatically download and install the latest release:

```bash
curl -fsSL https://raw.githubusercontent.com/alicerum/rog-ally-rumble-fixer/main/install.sh | sudo bash
```

**What the script does:**
- Detects your Decky Loader installation (SteamOS or custom path)
- Downloads the latest release from GitHub
- Extracts it to the correct plugins directory

### Manual Installation

1. Download the latest release ZIP file from the [Releases page](../../releases)
2. Extract it to your Decky plugins directory:
   ```bash
   unzip rog-ally-rumble-fixer.zip -d ~/homebrew/plugins/
   ```
3. Restart Decky Loader (Settings → Restart Decky)
4. Open Quick Access Menu (≡ button) and find "ROG Ally Rumble Fixer"

### Uninstallation

To remove the plugin:

```bash
rm -rf ~/homebrew/plugins/rog-ally-rumble-fixer/
```

Then restart Decky Loader.

## Building from Source

### Prerequisites

- Node.js v16.14+ and pnpm v9
- GCC compiler (for the backend binary)
- Docker (if building backend for CI)

### Build Steps

```bash
# Install dependencies
pnpm install

# Build everything and create distribution zip
make zip

# Or build components individually
make backend    # Build C binary
make frontend   # Build TypeScript/React frontend

# Clean build artifacts
make clean
```

The zip file will be created at `build/rog-ally-rumble-fixer-1.0.0.zip`

## Usage

1. Open the Decky menu (Quick Access Menu) on your ROG Ally X
2. Find the "ROG Ally Rumble Fixer" plugin
3. Toggle "Enable Rumble Fix" to turn it on
4. Adjust the "Rumble Gain" slider to your preferred intensity (0-100%)
5. Set the "Update Interval" to how often the plugin should reapply the settings

### Recommended Settings

- **Rumble Gain**: 40%
- **Update Interval**: 2 seconds (catches most InputPlumber overrides without excessive CPU usage)

## How It Works

The plugin uses a compiled C binary to perform `ioctl` operations on the input device, setting the `FF_GAIN` (force feedback gain) value. The backend runs as a background task that calls this binary at the configured interval.

The gain value is calculated as:
```
gain_value = (gain_percent / 100.0) * 0xFFFF
```

## Troubleshooting

### Device not detected

- Make sure your ROG Ally X controller is connected
- Click "Refresh Device Status" to re-scan for devices
- Check that the device exists in `/dev/input/by-id/`

### Binary not found

- Ensure the plugin was built correctly
- The binary should be at `bin/rumble-fixer` in the plugin directory
- If building manually, run `make` in the `backend/` directory

### Rumble still being overridden

- Try decreasing the update interval (check more frequently)
- Ensure the plugin is enabled and running
- Check Decky Loader logs for error messages

## Compatibility

- **Device**: ASUS ROG Ally X
- **OS**: SteamOS 3.x, other Linux distributions with Decky Loader
- **Controller**: Built-in ROG Ally X gamepad

## Technical Details

### File Structure

```
rog-ally-rumble-fixer/
├── plugin.json              # Plugin metadata
├── package.json             # NPM dependencies
├── main.py                  # Python backend
├── backend/
│   ├── Makefile            # Build script
│   └── src/
│       └── rumble-fixer.c  # C binary source
├── src/
│   └── index.tsx           # Frontend UI
└── dist/                   # Compiled frontend (generated)
```

### Backend Binary

The `rumble-fixer` binary performs the actual ioctl operations. It's compiled from C code that uses the Linux input subsystem to set the force feedback gain on the event device.

## License

This project is licensed under the BSD 2-Clause License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
