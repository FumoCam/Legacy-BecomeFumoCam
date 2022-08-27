## Note

These are rough, self-reference instructions based on a recent machine migration.

They are not intended for someone to pickup, understand, and execute flawlessly, but they're better than nothing.

## Fresh Windows 10 Install

1. Ensure Windows auto-logon is enabled (or your account has no password)
2. Create a power plan that does not allow sleep or monitor turn-off
3. Set up remote desktop access such as RealVNC
4. Set resolution to 1280x720, and change scaling to 100% if available
5. Set time/time zone
6. Disable Windows sounds
7. Download all windows updates
8. Download drivers
9. In Task Manager, go to the Startup tab and disable all irrelevant items
10. Under Settings->Accounts->Sign-In Options, ensure Restart Apps is disabled
11. [Recommended] Enable "Show hidden files, folders and drives" and disable "Hide extensions for known file types"
12. [Optional] Download Notepad++
13. Download Google Chrome
14. [Optional] Sign into a google account for bookmark/passwords sync
15. [Recommended] Make Chrome default
16. [Recommended] Disable Google Chrome updates to prevent selenium driver malfunction
    - In msconfig->Services, disable Google Update Service (gupdate) and Google 18. Update Service (gupdatem), then apply
17. Install git
18. Clone this repo (FumoCam)
19. In the src folder, clone the FumoCam AI repo if you have access (https://github.com/<HISTORICALLY_REDACTED>). If not, you will have to make dummy functions.
    - Also, rename the folder to just "ai".
20. [Recommended] Run `windows_block_updates.bat` as admin in the resources folder, to prevent unexpected behavior
21. Install VLC or reconfigure VLC code to use media player of choice
22. Install OBS
    - Use Stream Key (Recommended, or use Connect Account if you really want)
    - [Recommended] Change server to closest physical location
    - Generally, 4000 target bitrate (CBR) at Keyframe Interval of 2 is good.
    - [Recommended] For AMD iGPU:
      - Encoder: H264/AVC Encoder (AMD Advanced Media Framework)
      - Preset: None
      - Quality Preset: Quality
      - Rate Control Method: CBR
      - Pre-Pass Mode: Disabled
      - Target Bitrate: 4000
      - Filler Data: Enabled (IMPORTANT)
      - Keyframe Interval: 2
    - Output:
      - Base (Canvas): 1280x720
      - Output (Scaled): 1280x720
      - Downscale Filter: Bicubic (Sharpened scaling, 16 samples)
      - FPS: 30
    - Under Scene Collection,
      - Import -> resources/OBS_Fumocam_Default.json
      - Take note of all missing files (except muted_icon.png) and create them.
      - Most .txt files should be created in output. If output folder does not exist (beside resources and src), create it.
    - Under Scene Collection, click Untitled, then Remove
23. Ensure path to OBS exe matches whats written in `windows_fumocam_startup.bat`
24. Extract fonts.rar (password protected), or find them on the internet/find alternative fonts and replace in main.css
25. Hide and unhide the HUD source in OBS to refresh it, and ensure the font has changed from Times New Roman
26. Download Python 3.10.6
    - Check off "Add Python 3.10 to PATH"
    - [Recommended] Customize installation, Check `Install for all users`, `Add Python to environment variables`, and `Precompile standard library`
    - Click `Disable path length limit` if given the option
27. Download Poetry for Python, ensure using the new `official installer` (install.python-poetry.org)
    - [Recommended] The windows powershell install instructions are often fully sufficient.
    - If requested, add the poetry directory to your PATH
    - Close any open terminals so Poetry is a valid command going forward
28. At the root directory of the project, run `poetry install`
29. Create a file called `.env` in the src folder, using `.env.default` as a template. Fill it out with appropriate data.
30. Install Tesseract OCR v5 (https://tesseract-ocr.github.io/tessdoc/Home.html)
31. Download `tessdata_best` (https://github.com/tesseract-ocr/tessdata_best), delete the contents of the `tessdata` folder in C:\Program Files\Tesseract-OCR, and replace it with the contents of `tessdata_best`
32. Download "Open Hardware Monitor" and extract it somewhere permission-neutral (Like desktop)
    - File->Hardware and uncheck everything except CPU
    - Options->Start Minimized = Enabled
    - Options->Minimize On Close = Enabled
    - Options->Run On Windows Startup = Enabled
    - Options->Remote Web Server->Run
    - Restart the computer and ensure Open Hardware Monitor starts automatically
33. Download the correct "Chrome Driver" (Selenium) for your version of Google Chrome, and put it in resources/selenium.
34. Run the `test_get_cookies_for_browser()` function to get cookies for the auto-rejoin system
35. Run the `test_loading_cookies_for_browser()` function a few times to verify it will work.
    - The first time, you will be prompted to download roblox. When downloaded and installed, join an instance and check off "Always allow..." and click Open Roblox.
    - Ensure the second and third time, Roblox opens automatically. It will load into an experience 'you no longer have access' to, thats fine.
36. Load into a roblox game and
    - Lower camera sensitivity to minimum
    - Change Fullscreen to On
    - Change Graphics Mode to Manual
    - Change Graphics Quality to the highest setting that DOESNT blur objects in the distance. (Should be 7 bars)
    - Ensure the audio graph in OBS is lighting up, if not change audio device
    - IF not already done, mess around with test_get_player_token() until you get your player token by process of elimination, and put it in the .env
37. You can copy `main.bat` and `pull latest.bat` from the resources folder to desktop, for ease of use
38. Install Arduino software to allow serial device auto-detection
39. Set volume of VLC to 61%
40. Create a shortcut file for `resources/windows_fumocam_startup.bat` and move it to the windows startup folder (`shell:startup`)
