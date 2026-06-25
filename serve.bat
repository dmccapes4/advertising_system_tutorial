@echo off
rem ===========================================================================
rem  DOUBLE-CLICK THIS to open the tutorial as a little web server.
rem
rem  - Windows will ask permission ("Do you want to allow...?"). Click YES.
rem    That is just the server asking to share on your network - it's normal.
rem  - Your address will appear in the window, and a browser will open.
rem  - To let someone else read it, give them the "Share on Wi-Fi" link.
rem  - Close the window to stop the server.
rem
rem  If Windows blocks Administrator access (UAC No, SmartScreen, org policy):
rem    WORKAROUND — double-click  index.html  instead.
rem    The pre-built file from git is the full tutorial. No server required.
rem
rem  To retry the server: right-click this file -> Run as administrator -> Yes.
rem ===========================================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve.ps1"
