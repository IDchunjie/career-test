@echo off
chcp 65001 >nul
title GitHub 访问修复

net session >nul 2>&1
if not "%errorlevel%"=="0" (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix_github_scan.ps1"
echo.
pause
