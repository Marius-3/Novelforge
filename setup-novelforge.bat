@echo off
cd /d "%~dp0"
echo Starting NovelForge setup with PowerShell...
powershell.exe -NoProfile -ExecutionPolicy Bypass -NoExit -File "%~dp0setup-novelforge.ps1"
