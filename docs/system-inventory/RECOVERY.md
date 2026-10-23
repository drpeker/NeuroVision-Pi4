# NeuroVision Pi 4 — Recovery Guide

## Verified reference
- Stable release: v1.1-stable-vision (commit 6e6be88)
- OS: Debian 13 Trixie, ARM64
- Python: 3.12.15, managed with uv
- Reference project path: /home/drpeker/projects/neurovision
- Private XiaoZhi configuration: ~/.local/share/py-xiaozhi/config/

## Recovery procedure
1. Install Debian 13 ARM64, Git, uv and required system libraries.
2. Clone https://github.com/drpeker/NeuroVision-Pi4.git
3. Check out the stable tag or the documented backup branch.
4. Create the Python environment with uv venv --python 3.12.15 .venv
5. Install recorded packages with uv pip install --python .venv/bin/python -r docs/system-inventory/python-packages.txt
6. Restore any model files not included in Git from a separate backup.
7. Restore private XiaoZhi configuration securely; never commit credentials.
8. Review scripts/neuro-vision and adjust its hard-coded project path if needed.
9. Start the launcher only when no existing camera or XiaoZhi process is running.

## Verification
- Check processes: pgrep -af "neurovision_live.py|main.py --mode cli"
- Check live objects: curl -fsS http://127.0.0.1:8080/scene
- Check JPEG: curl -fsS -o /tmp/neurovision-check.jpg http://127.0.0.1:8080/snapshot
- Verify voice interaction and detailed image analysis separately.

## Limitations
This is a documented reference environment, not a tested automated installer.
The inventories do not contain private credentials, all model binaries, or an OS image.
Package inventories should be reviewed rather than blindly installed in full.
