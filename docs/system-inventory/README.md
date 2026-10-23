# NeuroVision Pi 4 — System Inventory

This directory documents the verified runtime environment of NeuroVision Pi 4.

## Reference System

- Platform: Raspberry Pi 4, ARM64 (aarch64)
- Operating system: Debian GNU/Linux 13.7 (Trixie)
- Python runtime: 3.12.15
- Python environment: project-local .venv managed with uv
- Stable source revision: 6e6be88
- Stable release tag: v1.1-stable-vision

## Inventory Files

- os-release.txt: operating system details
- kernel.txt: Linux kernel information
- python-version.txt: Python runtime version
- python-packages.txt: 75 installed Python packages
- apt-packages.txt: installed Debian packages and versions
- services.txt: systemd service unit inventory
- usb-devices.txt: detected USB devices
- audio-inputs.txt: ALSA recording devices
- audio-outputs.txt: ALSA playback devices
- model-and-vision-files.txt: model and vision file inventory
- launch-scripts.txt: project launch scripts

## Security

Do not commit API keys, passwords, authentication tokens, private configuration files, or personal credentials.

## Recovery Notes

The stable source code is preserved by the v1.1-stable-vision Git tag.
Python packages are documented in python-packages.txt.
System packages and detected hardware are documented in this directory.
Runtime credentials and private XiaoZhi configuration must be restored separately.
This inventory is not a full operating-system image or a complete automated installer.
