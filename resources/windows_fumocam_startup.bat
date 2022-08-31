@echo off
cd "%PROGRAMFILES%"\obs-studio\bin\64bit\
start obs64.exe --disable-updater --startstreaming
cd %USERPROFILE%\Desktop\FumoCam\src\
echo [System Reboot Detected]> ..\output\main_process.txt
echo Please wait. Initializing core systems. (0/2)> ..\output\main_status.txt
TIMEOUT /T 15
start /wait initialize_serial.py
echo [System Reboot Detected]> ..\output\main_process.txt
echo Please wait. Initializing core systems. (1/2)> ..\output\main_status.txt
TIMEOUT /T 10
start poetry run python main.py


