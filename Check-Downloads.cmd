@echo off
cd /d "%~dp0"
py -3.11 "%~dp0scripts\prepare_models.py" --probe --timeout 10
pause
