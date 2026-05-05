#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
# Dilder Development Dependencies Installer
#
# Installs everything needed to build firmware, run the DevTool,
# and flash the Pico 2 W. Supports Arch Linux (pacman/yay).
#
# Usage:
#   chmod +x install-deps.sh
#   ./install-deps.sh
# ─────────────────────────────────────────────────────────────────────
set -euo pipefail

B="\033[1m"
G="\033[32m"
Y="\033[33m"
R="\033[31m"
C="\033[36m"
X="\033[0m"

info()  { echo -e "${C}[info]${X} $1"; }
ok()    { echo -e "${G}[ok]${X}   $1"; }
warn()  { echo -e "${Y}[warn]${X} $1"; }
fail()  { echo -e "${R}[fail]${X} $1"; }

# ── Detect package manager ──
if command -v pacman &>/dev/null; then
    PM="pacman"
    INSTALL="sudo pacman -S --needed --noconfirm"
elif command -v apt &>/dev/null; then
    PM="apt"
    INSTALL="sudo apt install -y"
elif command -v dnf &>/dev/null; then
    PM="dnf"
    INSTALL="sudo dnf install -y"
else
    fail "Unsupported package manager. Install dependencies manually."
    exit 1
fi

info "Package manager: $PM"

# ── System packages ──
info "Installing system packages..."

case $PM in
    pacman)
        $INSTALL \
            base-devel cmake ninja git python python-pip \
            arm-none-eabi-gcc arm-none-eabi-newlib \
            docker docker-compose \
            tk python-pyserial python-pillow \
            libusb hidapi \
            libheif
        ;;
    apt)
        $INSTALL \
            build-essential cmake ninja-build git python3 python3-pip \
            gcc-arm-none-eabi libnewlib-arm-none-eabi \
            docker.io docker-compose \
            python3-tk python3-serial python3-pil \
            libusb-1.0-0-dev libhidapi-dev \
            libheif-examples
        ;;
    dnf)
        $INSTALL \
            cmake ninja-build git python3 python3-pip \
            arm-none-eabi-gcc-cs arm-none-eabi-newlib \
            docker docker-compose \
            python3-tkinter python3-pyserial python3-pillow \
            libusb1-devel hidapi-devel \
            libheif-tools
        ;;
esac

ok "System packages installed"

# ── Docker group ──
if ! groups | grep -q docker; then
    info "Adding $USER to docker group..."
    sudo usermod -aG docker "$USER"
    warn "You may need to log out and back in for Docker permissions to take effect"
else
    ok "User already in docker group"
fi

# ── Pico SDK ──
PICO_DIR="$HOME/pico"
SDK_DIR="$PICO_DIR/pico-sdk"

if [ -f "$SDK_DIR/pico_sdk_init.cmake" ]; then
    ok "Pico SDK already installed at $SDK_DIR"
else
    info "Installing Pico SDK..."
    mkdir -p "$PICO_DIR"
    git clone https://github.com/raspberrypi/pico-sdk.git "$SDK_DIR"
    cd "$SDK_DIR"
    git submodule update --init
    cd -
    ok "Pico SDK installed at $SDK_DIR"
fi

# Set env var
if ! grep -q "PICO_SDK_PATH" ~/.bashrc 2>/dev/null && \
   ! grep -q "PICO_SDK_PATH" ~/.zshrc 2>/dev/null; then
    info "Adding PICO_SDK_PATH to shell profile..."
    SHELL_RC="$HOME/.bashrc"
    [ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"
    echo "" >> "$SHELL_RC"
    echo "# Pico SDK" >> "$SHELL_RC"
    echo "export PICO_SDK_PATH=\"$SDK_DIR\"" >> "$SHELL_RC"
    ok "Added PICO_SDK_PATH to $SHELL_RC"
fi
export PICO_SDK_PATH="$SDK_DIR"

# ── Picotool ──
PICOTOOL_DIR="$PICO_DIR/picotool"

if command -v picotool &>/dev/null; then
    ok "picotool already installed: $(which picotool)"
elif [ -f "$PICOTOOL_DIR/build/picotool" ]; then
    ok "picotool already built at $PICOTOOL_DIR/build/picotool"
else
    info "Building picotool from source..."
    if [ ! -d "$PICOTOOL_DIR" ]; then
        git clone https://github.com/raspberrypi/picotool.git "$PICOTOOL_DIR"
    fi
    mkdir -p "$PICOTOOL_DIR/build"
    cmake -G Ninja -DPICO_SDK_PATH="$SDK_DIR" -S "$PICOTOOL_DIR" -B "$PICOTOOL_DIR/build"
    ninja -C "$PICOTOOL_DIR/build"

    if [ -f "$PICOTOOL_DIR/build/picotool" ]; then
        ok "picotool built: $PICOTOOL_DIR/build/picotool"
        info "Adding to PATH..."
        SHELL_RC="$HOME/.bashrc"
        [ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"
        if ! grep -q "picotool" "$SHELL_RC" 2>/dev/null; then
            echo "export PATH=\"$PICOTOOL_DIR/build:\$PATH\"" >> "$SHELL_RC"
            ok "Added picotool to PATH in $SHELL_RC"
        fi
    else
        fail "picotool build failed"
    fi
fi

# ── udev rules for Pico (no sudo for USB) ──
UDEV_RULE="/etc/udev/rules.d/99-pico.rules"
if [ ! -f "$UDEV_RULE" ]; then
    info "Installing udev rules for Pico USB access..."
    sudo tee "$UDEV_RULE" > /dev/null << 'UDEV'
# Raspberry Pi Pico / Pico 2 — BOOTSEL mode
SUBSYSTEM=="usb", ATTR{idVendor}=="2e8a", MODE="0666"
# Raspberry Pi Pico / Pico 2 — serial (CDC)
SUBSYSTEM=="tty", ATTRS{idVendor}=="2e8a", MODE="0666"
UDEV
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    ok "udev rules installed — Pico USB access without sudo"
else
    ok "udev rules already installed"
fi

# ── Summary ──
echo ""
echo -e "${B}${G}════════════════════════════════════════${X}"
echo -e "${B}${G}  Dilder dependencies installed!${X}"
echo -e "${B}${G}════════════════════════════════════════${X}"
echo ""
echo -e "  Pico SDK:   ${C}$SDK_DIR${X}"
echo -e "  picotool:   ${C}${PICOTOOL_DIR}/build/picotool${X}"
echo -e "  DevTool:    ${C}python3 tools/devtool/devtool.py${X}"
echo ""
echo -e "  ${Y}Restart your terminal for PATH changes to take effect.${X}"
echo ""
