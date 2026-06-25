@echo off
rem ===========================================================================
rem  DEMO MODE — same as serve.bat, but prints a LIVE LOG of every page users
rem  open. Double-click this when presenting: as people navigate the tutorial
rem  (on this PC or via the Wi-Fi link), each request prints in the window:
rem
rem      time   client-IP        method  path  -> status
rem
rem  Great for showing "HTTP is a request, then a response" in real time.
rem  Close the window to stop the server.
rem
rem  If Windows blocks admin/UAC: double-click index.html instead (pre-built in git).
rem ===========================================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve.ps1" -Log
