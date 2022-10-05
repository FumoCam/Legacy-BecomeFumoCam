@echo off
cd "%PROGRAMFILES%"\obs-studio\bin\64bit\
start obs64.exe --disable-updater --startstreaming
cd %USERPROFILE%\Desktop\CensorClient
start poetry run python censor_client\main.py
echo [System Reboot Detected]> %USERPROFILE%\Desktop\FumoCam\output\main_process.txt
echo Please wait. Initializing core systems. (0/3)> %USERPROFILE%\Desktop\FumoCam\output\main_status.txt
TIMEOUT /T 5
cd %USERPROFILE%\Desktop\FumoCam\src\
echo [System Reboot Detected]> %USERPROFILE%\Desktop\FumoCam\output\main_process.txt
echo Please wait. Initializing core systems. (1/3)> %USERPROFILE%\Desktop\FumoCam\output\main_status.txt
TIMEOUT /T 15
start /wait poetry run python initialize_serial.py
echo [System Reboot Detected]> %USERPROFILE%\Desktop\FumoCam\output\main_process.txt
echo Please wait. Initializing core systems. (2/3)> %USERPROFILE%\Desktop\FumoCam\main_status.txt
TIMEOUT /T 10
start poetry run python main.py


