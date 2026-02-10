#!/usr/bin/env bash
set -e

# ----------------------------
# User-local installer/uninstaller for File Sorter
# 
# # # # # Usage:
# # Install
# ./install.sh
# 
# # Uninstall
# ./install.sh --uninstall
# 
# 
# ----------------------------

APP_NAME="file-sorter"
RUN_SCRIPT_SRC="$(realpath "$(dirname "$0")/file-sorter.py")"
RUN_SCRIPT="$HOME/bin/$APP_NAME"
DESKTOP_ENTRY="$HOME/.local/share/applications/$APP_NAME.desktop"
ICON_PATH="/home/knoppix/additions/graphics/icons/cowsGoatsBirds026_icon_144.ico"

# Usage helper
usage() {
    echo "Usage: $0 [--uninstall]"
    echo "   --uninstall   Remove File Sorter"
    exit 1
}

# Parse args
if [ "$1" == "--uninstall" ]; then
    echo "Uninstalling $APP_NAME…"

    # Remove run script
    if [ -f "$RUN_SCRIPT" ]; then
        rm "$RUN_SCRIPT"
        echo "Removed $RUN_SCRIPT"
    fi

    # Remove desktop entry
    if [ -f "$DESKTOP_ENTRY" ]; then
        rm "$DESKTOP_ENTRY"
        echo "Removed $DESKTOP_ENTRY"
    fi

    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$HOME/.local/share/applications" || true
    fi

    echo "✔ Uninstall complete"
    exit 0
elif [ "$#" -ne 0 ]; then
    usage
fi

# ----------------------------
# INSTALL
# ----------------------------
echo "Installing $APP_NAME…"

# 1. Ensure ~/bin exists
mkdir -p "$HOME/bin"

# 2. Create the run script
cat > "$RUN_SCRIPT" <<EOF
#!/usr/bin/env bash
# Auto-generated run script for File Sorter

# Activate venv
source ~/all/docs/txt/programs/python-image-sorter-1/venv/bin/activate

# Run the program
python3 "$RUN_SCRIPT_SRC" "\$@"
EOF

chmod +x "$RUN_SCRIPT"
echo "Created run script at $RUN_SCRIPT"

# 3. Create desktop entry
mkdir -p "$HOME/.local/share/applications"
cat > "$DESKTOP_ENTRY" <<EOF
[Desktop Entry]
Type=Application
Name=Image Sorter
Comment=Image and File viewer and sorter
Exec=$RUN_SCRIPT %f
Icon=$ICON_PATH
Terminal=false
Categories=Graphics;Viewer;
MimeType=image/jpeg;image/png;image/webp;image/bmp;image/tiff;
EOF

echo "Created desktop entry at $DESKTOP_ENTRY"

# 4. Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" || true
fi

echo "✔ Install complete"
echo "You can now run '$APP_NAME' from your applications menu or using ~/bin/$APP_NAME"
