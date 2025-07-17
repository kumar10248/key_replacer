#!/bin/bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed app/main.py --name keyreplacer --icon=assets/icon.png
