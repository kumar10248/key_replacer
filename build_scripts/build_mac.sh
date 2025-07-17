#!/bin/bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed app/main.py --name KeyReplacer --icon=assets/icon.icns
