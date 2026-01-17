# PiFan - Raspberry Pi 5 Fan Controller

**PiFan** is a modern GUI application designed specifically for the Raspberry Pi 5. It allows you to take full control of your active cooler's fan speed using hardware PWM (GPIO 45).

## Features

- **Dual Modes**:
    - **Automatic**: Reads the system's kernel fan speed and displays it.
    - **Manual**: Take full control with a precision slider.
- **Presets**: Quick-access buttons for **Silent** (30%), **Balanced** (60%), and **Max** (100%) profiles.
- **Visual Feedback**: Temperature bar changes color (Green/Yellow/Red) based on thermal status.
- 
## Installation

### Pre-built Package
If you have the `.deb` file:

```bash
sudo dpkg -i pifan_3.3_arm64.deb
```

Once installed, find **PiFan** in your system menu (under System Tools or Settings).

## Compilation (Building from Source)

To build the Debian package yourself from the source code:

1.  **Clone or Download** this repository.
2.  Ensure you have `dpkg-deb` installed (standard on Raspberry Pi OS).
3.  Run the build script:

```bash
./build_deb.sh
```

This will generate a new `.deb` file (e.g., `pifan_3.3_arm64.deb`) in the project directory.

## Requirements

- Raspberry Pi 5 (Active Cooler on GPIO 45)
- Raspberry Pi OS (Bookworm or newer recommended)
- Python 3.11+

The package manager automatically installs necessary Python dependencies:
- `customtkinter`
- `packaging`
- `Pillow`
- `rpi-lgpio`

## License

MIT License.
