@echo off
set BECOMEFUMOCAM_DIR=%USERPROFILE%\Desktop\BecomeFumoCam

:: Public Repos
:: BecomeFumoCam (This repo, https://github.com/FumoCam/Legacy-BecomeFumoCam)
echo.
echo Updating BecomeFumoCam...
cd /d %BECOMEFUMOCAM_DIR%
git fetch --all
git reset --hard origin/main
poetry install
pause
:: Censor-Client (https://github.com/FumoCam/Whitelist-Censor-Client)
echo.
echo Updating Censor-Client...
cd /d %BECOMEFUMOCAM_DIR%\censor\
git fetch --all
git reset --hard origin/main
poetry install
pause
:: HUD (https://github.com/FumoCam/HUD)
echo.
echo Updating HUD...
cd /d %BECOMEFUMOCAM_DIR%\hud\
git fetch --all
git reset --hard origin/main
pause

:: Private Repos
:: AI (https://github.com/FumoCam/Legacy-BecomeFumoCam-AI)
echo.
echo Updating AI...
cd /d %BECOMEFUMOCAM_DIR%\src\ai\
git fetch --all
git reset --hard origin/main
pause
:: BecomeFumoCam Private Resources (https://github.com/FumoCam/Legacy-BecomeFumoCam-PrivateResources)
echo.
echo Updating Private Resources...
cd /d %BECOMEFUMOCAM_DIR%\resources\private\
git fetch --all
git reset --hard origin/main
pause
:: HUD Private Assets (https://github.com/FumoCam/HUD-PrivateAssets)
echo.
echo Updating HUD Private Assets...
cd /d %BECOMEFUMOCAM_DIR%\hud\private_assets\
git fetch --all
git reset --hard origin/main
pause
