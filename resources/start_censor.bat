:: For manually starting after updates or something
@echo off
set BECOMEFUMOCAM_DIR=%USERPROFILE%\Desktop\BecomeFumoCam
cd /d %BECOMEFUMOCAM_DIR%\censor\
start poetry run python main.py