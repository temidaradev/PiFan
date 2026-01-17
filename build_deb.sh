#!/bin/bash
VERSION="3.3"
PKG_NAME="pifan"
ARCH="arm64"
BUILD_DIR="build/deb"
DEB_NAME="${PKG_NAME}_${VERSION}_${ARCH}.deb"

echo "Building Debian Package: $DEB_NAME"

# Clean build dir
rm -rf build

# Create directory structure
mkdir -p $BUILD_DIR/DEBIAN
mkdir -p $BUILD_DIR/opt/pifan
mkdir -p $BUILD_DIR/usr/share/applications
mkdir -p $BUILD_DIR/usr/bin

# 1. Create Control File
cat <<EOF > $BUILD_DIR/DEBIAN/control
Package: $PKG_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: Temi <temi@example.com>
Description: Pi 5 Fan Controller
 A premium GUI for controlling the Raspberry Pi 5 Fan.
EOF

# 2. Create Post-Install Script (Setup venv)
cat <<EOF > $BUILD_DIR/DEBIAN/postinst
#!/bin/bash
echo "Setting up pifan environment..."
# Create venv in /opt/pifan/venv
python3 -m venv /opt/pifan/venv
source /opt/pifan/venv/bin/activate
pip install customtkinter packaging Pillow rpi-lgpio
# Fix permissions
chmod -R 755 /opt/pifan
# Update desktop database if available
if command -v update-desktop-database >/dev/null; then
    update-desktop-database /usr/share/applications || true
fi
echo "Done."
EOF
chmod 755 $BUILD_DIR/DEBIAN/postinst

# 3. Copy Source Code
cp -r src/pifan $BUILD_DIR/opt/pifan/

# 4. Copy Assets
cp assets/pifan.desktop $BUILD_DIR/usr/share/applications/

# 5. Create Sudoers File (No Password for pifan)
mkdir -p $BUILD_DIR/etc/sudoers.d
cat <<EOF > $BUILD_DIR/etc/sudoers.d/pifan
%sudo ALL=(ALL) NOPASSWD: /usr/bin/pifan
EOF
chmod 440 $BUILD_DIR/etc/sudoers.d/pifan

# 6. Create Launcher Script
cat <<EOF > $BUILD_DIR/usr/bin/pifan
#!/bin/bash
export PYTHONPATH=\$PYTHONPATH:/opt/pifan
source /opt/pifan/venv/bin/activate
# If not running as root, re-run self with sudo (which will be passwordless now)
if [ "\$EUID" -ne 0 ]; then
    exec sudo \$0 "\$@"
    exit
fi
python3 -m pifan
EOF
chmod 755 $BUILD_DIR/usr/bin/pifan

# Build .deb
dpkg-deb --build $BUILD_DIR $DEB_NAME
echo "Package built: $DEB_NAME"
