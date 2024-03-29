@echo off
set OBS_DIR="%PROGRAMFILES%"\obs-studio\bin\64bit\
set BECOMEFUMOCAM_DIR=%USERPROFILE%\Desktop\BecomeFumoCam

TIMEOUT /T 5
:: Start OBS
cd %OBS_DIR%
start obs64.exe --disable-updater --startstreaming --disable-shutdown-check
:: Start CensorClient
echo [System Reboot Detected]> %BECOMEFUMOCAM_DIR%\output\main_process.txt
echo Please wait. Initializing core systems. (0/4)> %BECOMEFUMOCAM_DIR%\\output\main_status.txt
cd %BECOMEFUMOCAM_DIR%\censor\
start poetry run python main.py
TIMEOUT /T 5
:: Initialize serial connection
echo [System Reboot Detected]> %BECOMEFUMOCAM_DIR%\output\main_process.txt
echo Please wait. Initializing core systems. (1/4)> %BECOMEFUMOCAM_DIR%\\output\main_status.txt
cd %BECOMEFUMOCAM_DIR%\src\
start /wait poetry run python initialize_serial.py
TIMEOUT /T 15
:: Start OBS Monitor
echo [System Reboot Detected]> %BECOMEFUMOCAM_DIR%\output\main_process.txt
echo Please wait. Initializing core systems. (2/4)> %BECOMEFUMOCAM_DIR%\\output\main_status.txt
start poetry run python obs_monitor.py
TIMEOUT /T 5
:: Start main program
echo [System Reboot Detected]> %BECOMEFUMOCAM_DIR%\output\main_process.txt
echo Please wait. Initializing core systems. (3/4)> %BECOMEFUMOCAM_DIR%\\output\main_status.txt
TIMEOUT /T 5
start poetry run python main.py


