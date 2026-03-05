#!/bin/bash

# ROG Ally Rumble Fixer - Install Script
# Downloads and installs the latest release from GitHub

set -e

PLUGIN_NAME="rog-ally-rumble-fixer"
GITHUB_REPO="alicerum/${PLUGIN_NAME}"
RELEASE_URL="https://github.com/${GITHUB_REPO}/releases/latest/download/${PLUGIN_NAME}.zip"

# Detect homebrew directory
if [ -d "/home/deck/homebrew" ]; then
    DECKY_HOME="/home/deck/homebrew"
elif [ -d "$HOME/homebrew" ]; then
    DECKY_HOME="$HOME/homebrew"
else
    echo "Error: Could not find Decky Loader homebrew directory"
    echo "Expected one of:"
    echo "  - /home/deck/homebrew (SteamOS)"
    echo "  - $HOME/homebrew"
    exit 1
fi

PLUGIN_DIR="${DECKY_HOME}/plugins/${PLUGIN_NAME}"
TEMP_DIR=$(mktemp -d)

echo "ROG Ally Rumble Fixer - Installer"
echo "=================================="
echo ""
echo "Detected Decky homebrew: ${DECKY_HOME}"
echo "Plugin will be installed to: ${PLUGIN_DIR}"
echo ""

# Cleanup function
cleanup() {
    rm -rf "${TEMP_DIR}"
}
trap cleanup EXIT

# Download latest release
echo "Downloading latest release..."
if command -v curl &> /dev/null; then
    curl -L -o "${TEMP_DIR}/${PLUGIN_NAME}.zip" "${RELEASE_URL}"
elif command -v wget &> /dev/null; then
    wget -O "${TEMP_DIR}/${PLUGIN_NAME}.zip" "${RELEASE_URL}"
else
    echo "Error: Neither curl nor wget is installed"
    exit 1
fi

if [ ! -f "${TEMP_DIR}/${PLUGIN_NAME}.zip" ]; then
    echo "Error: Failed to download plugin"
    exit 1
fi

echo "Download complete!"
echo ""

# Remove old version if exists
if [ -d "${PLUGIN_DIR}" ]; then
    echo "Removing old version..."
    rm -rf "${PLUGIN_DIR}"
fi

# Extract plugin
echo "Installing plugin..."
mkdir -p "${PLUGIN_DIR}"
unzip -q "${TEMP_DIR}/${PLUGIN_NAME}.zip" -d "${TEMP_DIR}/extracted"

# Move files (handle the nested directory)
if [ -d "${TEMP_DIR}/extracted/${PLUGIN_NAME}" ]; then
    mv "${TEMP_DIR}/extracted/${PLUGIN_NAME}"/* "${PLUGIN_DIR}/"
else
    echo "Error: Unexpected archive structure"
    exit 1
fi

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Restart Decky Loader (Settings → Restart Decky)"
echo "  2. Open Quick Access Menu (≡ button)"
echo "  3. Find 'ROG Ally Rumble Fixer'"
echo ""
echo "To uninstall, run: rm -rf ${PLUGIN_DIR}"
