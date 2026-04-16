@echo off
cd /d D:\first_squad_project
del /f /q ".squad\decisions\inbox\ripley-copilot-instructions-refine.md" 2>nul
del /f /q ".squad\decisions\inbox\ripley-copilot-instructions.md" 2>nul
git --no-pager add .squad/
git commit -F .squad/commit-msg.txt
pause
