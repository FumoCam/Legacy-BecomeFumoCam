from actions import *
from selenium import webdriver
from imutils import rotate_bound
import numpy as np
import json
import cv2 as cv


async def force_get_best_server():
    found_best_server = False
    attempts = 0
    log("Attempting to find best server to join...")
    while not found_best_server:
        found_best_server = await get_best_server()
        if found_best_server:
            break
        attempts += 1
        log(f"Attempt #{attempts} to find best server failed, retrying...")
        await async_sleep(5)
    return found_best_server["id"]


async def check_if_should_change_servers(current_server_id="N/A"):
    original_current_server_id = current_server_id
    log("Querying Roblox API for server list")
    url = f"https://games.roblox.com/v1/games/{CFG.game_id}/servers/Public?sortOrder=Asc&limit=10"
    try:
        response = requests.get(url, timeout=10)
    except Exception:
        return False, f"[WARN] Could not poll Roblox servers. Is Roblox down?"
    if response.status_code == 200:
        log("Finding best server and comparing to current...")

        response_result = response.json()
        servers = response_result["data"]
        highest_player_server = {"id": "", "maxPlayers": 100, "playing": 0, "fps": 59, "ping": 100}
        if current_server_id == "N/A":
            current_server = {"id": "", "maxPlayers": 100, "playing": 0, "fps": 59, "ping": 100}
        else:
            current_server = {"id": current_server_id, "maxPlayers": 100, "playing": 0, "fps": 59, "ping": 100}
        for server in servers:
            if current_server["id"] == server["id"]:
                current_server = server
            elif "playing" in server and server["playing"] > highest_player_server["playing"]:
                highest_player_server = server
        log("")
        if current_server["id"] == "" or current_server["id"] == "undefined":
            if highest_player_server["playing"] == 0:
                return False, f"[WARN] Could not poll Roblox servers. Is Roblox down?"
            print(servers)
            return_message = f"[WARN] Could not find FumoCam. Are we in a server?\n" \
                             f"Original Server ID: {original_current_server_id}\n" \
                             f"Detected Server ID: {current_server['id']}"
            return True, return_message
        elif current_server["playing"] + 5 < highest_player_server["playing"]:
            difference = highest_player_server["playing"] - current_server["playing"]
            return True, f"[WARN] There is a server with {difference} more players online."
        else:
            return False, ""
    return False, f"[WARN] Could not poll Roblox servers. Is Roblox down?"


async def check_if_in_nil_world():
    current_server_id = "N/A"
    url = f"https://games.roblox.com/v1/games/{CFG.game_id_nil}/servers/Public?sortOrder=Asc&limit=10"
    try:
        response = requests.get(url, timeout=10)
    except Exception:
        print(format_exc())
        return "ERROR"
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        for server in servers:
            if CFG.player_token in server["playerTokens"]:
                current_server_id = server["id"]
                break
        if current_server_id != "ERROR":
            print(current_server_id)
        return current_server_id
    return "ERROR"


async def check_if_in_hinamizawa_world():
    current_server_id = "N/A"
    url = f"https://games.roblox.com/v1/games/{CFG.game_id_hinamizawa}/servers/Public?sortOrder=Asc&limit=10"
    try:
        response = requests.get(url, timeout=10)
    except Exception:
        print(format_exc())
        return "ERROR"
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        for server in servers:
            if CFG.player_token in server["playerTokens"]:
                current_server_id = server["id"]
                break
        if current_server_id != "ERROR":
            print(current_server_id)
        return current_server_id
    return "ERROR"


async def get_current_server_id():
    current_server_id = "N/A"
    url = f"https://games.roblox.com/v1/games/{CFG.game_id}/servers/Public?sortOrder=Asc&limit=10"
    try:
        response = requests.get(url, timeout=10)
    except Exception:
        print(format_exc())
        return "ERROR"
    if response.status_code == 200:
        response_result = response.json()
        print(response_result)
        servers = response_result["data"]
        if len(servers) == 0:
            return "ERROR"
        for server in servers:
            if CFG.player_token in server["playerTokens"]:
                current_server_id = server["id"]
                break
        if current_server_id != "ERROR":
            print(current_server_id)
        return current_server_id
    return "ERROR"


async def check_for_better_server():
    last_check_time = time()
    output_log("last_check_for_better_server", last_check_time)
    previous_status_text = read_output_log("change_server_status_text")
    output_log("change_server_status_text", "")

    log_process("Checking for better server")
    current_server_id = await get_current_server_id()
    if current_server_id == "ERROR":
        for i in range(CFG.max_attempts_better_server):
            log_process(f"Attempt {i+1}/{CFG.max_attempts_better_server} failed! Retrying better server check...")
            await async_sleep(5)
            current_server_id = await get_current_server_id()
            if current_server_id != "ERROR":
                break
    if current_server_id == "ERROR":        
        log_process(f"Failed to connect to Roblox API {CFG.max_attempts_better_server} times! Skipping...")
        await async_sleep(5)
        log_process("")
        return True
    if current_server_id == "N/A":
        nil_world_id = await check_if_in_nil_world()
        hinamizawa_world_id = await check_if_in_hinamizawa_world()
        if nil_world_id == "N/A" and hinamizawa_world_id == "N/A":
            log_process("Could not find FumoCam in any servers")
            await CFG.add_action_queue("handle_crash")
            return False
        else:  # other world easter egg
            log("Successfully failed! Could not find FumoCam in the realms of the living.")
            Beep(60, 2000)
            log("S#c%e!s%u^l& f!i@e%! &o#l* ^o$ f!n& @u$o%a& *n !h# $e^l!s #f ^$e #i!i$g.")
            Beep(50, 2000)
            log("!#@%&!@%%^^& $!#@&%! &@#!* ^*$ @!$& @^$@%a& *$ !@# $#^%!@ #@ ^$% #@!%$#.")
            Beep(40, 2000)
            log_process("")
            log("")
            return True
    should_change_servers, change_server_status_text = await check_if_should_change_servers(current_server_id)
    log(change_server_status_text)
    output_log("change_server_status_text", change_server_status_text)
    if not should_change_servers:
        log("PASS! Current server has sufficient players")
        log("")
        log_process("")
        return True
    elif previous_status_text != change_server_status_text:
        if "Could not find FumoCam" in change_server_status_text:
            for i in range(2):
                log(f"Rechecking (attempt {i + 1}/3")
                current_server_id = await get_current_server_id()
                while current_server_id == "":
                    log_process("Retrying get current server check")
                    await async_sleep(5)
                    current_server_id = await get_current_server_id()
                should_change_servers, change_server_status_text = await check_if_should_change_servers(current_server_id)
                if "Could not find FumoCam" not in change_server_status_text:
                    break
            if should_change_servers:
                notify_admin(change_server_status_text)
                await CFG.add_action_queue("handle_join_new_server")
        else:
            await CFG.add_action_queue("handle_join_new_server")
    log("")
    log_process("")


async def open_roblox_with_selenium_browser(js_code):
    log("Opening Roblox via Browser...")
    Beep(40, 25)
    try:
        with open(CFG.browser_cookies_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
    except FileNotFoundError:
        print("COOKIES PATH NOT FOUND, INITIALIZE WITH TEST FIRST")
        log("")
        return False
    
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={CFG.browser_profile_path}")
    driver = webdriver.Chrome(options=options, executable_path=CFG.browser_driver_path)
    driver.get(CFG.game_instances_url)
    
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    driver.execute_script(js_code);
    
    sleep_time = 0.25
    success = False
    log("Verifying Roblox has opened...")
    for i in range(int(CFG.max_seconds_browser_launch/sleep_time)):
        crashed = await do_crash_check(do_notify=False)
        active = is_process_running(CFG.game_executable_name)
        if not crashed and active:
            success = True
            break
        await async_sleep(sleep_time)
    try:
        driver.quit()       
        kill_process(CFG.browser_driver_executable_name)
        kill_process(CFG.browser_executable_name)
    except:
        print(format_exc())
        
    if not success:
        log("Failed to launch game. Notifying Dev...")
        notify_admin("Failed to launch game")
        await async_sleep(5)
        log("")
        return False
    log("")
    return True


async def join_target_server(instance_id):
    join_js_code = f"Roblox.GameLauncher.joinGameInstance({CFG.game_id}, \"{instance_id}\")"
    success = await open_roblox_with_selenium_browser(join_js_code)
    return success


async def get_best_server():
    server_obj = {"id": "", "maxPlayers": 100, "playing": 0, "fps": 59, "ping": 100}
    highest_player_count_server = server_obj
    url = f"https://games.roblox.com/v1/games/{CFG.game_id}/servers/Public?sortOrder=Asc&limit=10"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        for server in servers:
            print(server)
            if "playing" in server and server["playing"] > highest_player_count_server["playing"]:
                highest_player_count_server = server
    if highest_player_count_server == server_obj:
        return False
    return highest_player_count_server


async def click_character_select_button(check_open_state=None):
    await async_sleep(0.5)
    #Beep(150, 100)
    button_x, button_y = await get_character_select_button_pos()
    ACFG.moveMouseAbsolute(x=int(button_x), y=int(button_y))
    ACFG.left_click()
    
    if check_open_state is not None:
        log(f"Checking that character select is {'open' if check_open_state else 'closed'}")
        await async_sleep(2)
        last_button_x, last_button_y = button_x, button_y
        success = False
        for i in range(CFG.character_select_max_close_attempts):
            new_button_x, new_button_y = await get_character_select_button_pos()
            if check_open_state is True and (new_button_y > last_button_y):
                success = True
                break  # If we want it open and the new pos is further down the screen than before
            elif check_open_state is False and (new_button_y < last_button_y):
                success = True
                break  # If we want it closed and the new pos is further up the screen than before
            else:
                ACFG.moveMouseAbsolute(x=int(new_button_x), y=int(new_button_y))
                ACFG.left_click()
                await async_sleep(2)
                last_button_x, last_button_y = new_button_x, new_button_y 
        if not success:
            log("Unable to toggle character menu!")
            sleep(2)
        log("")
    else:
        await async_sleep(0.5)    
    #Beep(100, 50)
    
async def ocr_for_character(character=None):
    desired_character = CFG.character_select_desired.lower()
    if character is not None:
        desired_character = character.lower()
    button_x, button_y = await get_character_select_button_pos()
    
    await async_sleep(0.5)
    #Beep(150, 100)
    monitor = mss().monitors[-1]
    screen_width = monitor["width"]
    screen_height = monitor["height"]
    print(screen_width)
    monitor["width"] = int(CFG.character_select_width * screen_width)
    monitor["left"] = int(button_x - (CFG.character_select_width/2) * screen_width)
    monitor["height"] = int(button_y - (CFG.character_select_button_height * screen_height))
    ocr_data = None
    last_ocr_text = None
    times_no_movement = 0
    found_character = False
    scroll_amount = 0
    for attempts in range(CFG.character_select_max_scroll_attempts):
        log(f"Scanning list for '{desired_character.capitalize()}' {attempts}/{CFG.character_select_max_scroll_attempts}")
        for i in range(CFG.character_select_scan_attempts):  # Attempt multiple OCRs
            screenshot = None
            with mss() as sct:
                screenshot = sct.grab(monitor)
            screenshot = np.array(screenshot)

            #rgb = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)  # PyTesseract
            gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)  # PyTesseract
            #_, screenshot = cv.threshold(screenshot, 132, 255, 3)
            gray, img_bin = cv.threshold(gray,100,255,cv.THRESH_BINARY | cv.THRESH_OTSU)
            gray = cv.bitwise_not(img_bin)            
            kernel = np.ones((2, 1), np.uint8)
            img = cv.erode(gray, kernel, iterations=1)
            img = cv.dilate(img, kernel, iterations=1)

            #scale_percent = 60 # percent of original size
            #width = int(img.shape[1] * scale_percent / 100)
            #height = int(img.shape[0] * scale_percent / 100)
            #dim = (width, height)
            #resized = cv.resize(img, dim, interpolation = cv.INTER_AREA)
            # cv.imshow("OCR", resized)
            # cv.waitKey(500)
            ocr_data = pytesseract.image_to_data(img, config='--oem 1', output_type=pytesseract.Output.DICT)
            ocr_data["text"] = [word.lower() for word in ocr_data["text"]]
            print(ocr_data["text"])
            if desired_character in ocr_data["text"]:
                found_character = True
                break
            sleep(0.1)
        
        if found_character:
            break
        
        if last_ocr_text == ocr_data["text"]:
            times_no_movement += 1
        else:
            times_no_movement = 0
            last_ocr_text = ocr_data["text"]
        
        if times_no_movement > 3:
            break  # We reached the bottom of the list, OCR isnt changing
        
        ACFG.scrollMouse(1, down=True)
        scroll_amount += 1
        sleep(0.4)
        Beep(60, 100)
    
    if not found_character:
        log(f"Failed to find '{desired_character.capitalize()}'.\n Notifying Dev...")
        notify_admin(f"Failed to find `{desired_character}`")
        sleep(5)
        #click_character_select_button(check_open_state=False)  # Close character select
        return False
    
    # We found the character, lets click it
    ocr_index = ocr_data["text"].index(desired_character)
    desired_character_height = int(ocr_data["top"][ocr_index] + (ocr_data["height"][ocr_index]/2))
    with open(OBS.output_folder / "character_select.json", "w") as f:
        json.dump({
            "scroll_amount": scroll_amount, 
            "desired_character_height": desired_character_height,
        }, f)
    CFG.character_select_screen_height_to_click = desired_character_height / SCREEN_RES["height"]
    CFG.character_select_scroll_down_amount = scroll_amount
    ACFG.moveMouseAbsolute(x=int(button_x), y=int(desired_character_height))
    sleep(0.5)
    ACFG.left_click()
    sleep(0.5)
    return True


async def scroll_to_character_in_menu():
    await async_sleep(0.5)
    log(f"Scrolling down {CFG.character_select_scroll_down_amount} times")
    ACFG.scrollMouse(CFG.character_select_scroll_down_amount, down=True)
    log("")


async def click_character_in_menu(click_mouse=True, click_random=False):
    character_name = CFG.character_select_desired if not click_random else "a random character"
    log(f"Clicking {character_name}")
    button_x, button_y = round(pyautogui.size()[0] * 0.5), round(
        SCREEN_RES["height"] * CFG.character_select_screen_height_to_click)  # Toggle Collisions button
    if click_random:
        button_y += int(SCREEN_RES["height"]*CFG.respawn_character_select_offset)
    ACFG.moveMouseAbsolute(x=button_x, y=button_y)
    ACFG.left_click()
    await async_sleep(0.5)


async def get_character_select_button_pos():
    character_select_button = None
    for i in range(CFG.max_attempts_character_selection):
        await check_active()
        Beep(40, 50)
        try:
            print("TryingToFind")
            character_select_button = pyautogui.locateOnScreen(CFG.character_select_image_path,
                                                               grayscale=True,
                                                               confidence=0.9)  # , #region=character_select_range)
        except pyautogui.ImageNotFoundException:
            character_select_button = None
        if character_select_button is not None:
            character_select_button = pyautogui.center(character_select_button)
            break
        await async_sleep(1)
    return character_select_button


async def change_characters(respawn=False):
    await check_active()
    await async_sleep(1)
    log("Opening character select")
    
    need_zoom_adjust = False
    if CFG.zoom_level < CFG.zoom_ui_min_cv:
        ACFG.zoom("o", CFG.zoom_out_ui_cv)
        need_zoom_adjust = True
    
    await click_character_select_button(check_open_state=True)
    sleep(1)
    if respawn:
        await click_character_in_menu(click_random=True)
        respawn_delay = 12
        log(f"Waiting for {respawn_delay} seconds (or else clicking our character won't work)")
        await async_sleep(respawn_delay)
        await click_character_in_menu()
    else:
        await ocr_for_character()
    sleep(1)
    await async_sleep(1) # I have no idea what causes less errors
    log("Closing character select")
    await async_sleep(0.5)
    sleep(0.5)
    await click_character_select_button(check_open_state=False)
    sleep(1)
    await async_sleep(0.5)
    ACFG.resetMouse()
    if need_zoom_adjust:
        ACFG.zoom("i", CFG.zoom_out_ui_cv)


async def server_spawn():
    await async_sleep(5)
    log("Loading into game")
    if await get_character_select_button_pos() is None:
        log("Failed to load into game.")
        await async_sleep(5)
        notify_admin("Failed to load into game")
        await CFG.add_action_queue("handle_crash")
        return False
    await async_sleep(5)
    if CFG.disable_collisions_on_spawn:
        CFG.collisions_disabled = False
        await toggle_collisions()
    await async_sleep(3)
    await change_characters()
    ACFG.resetMouse()
    await auto_nav("shrimp", do_checks=False)
    return True


async def handle_join_new_server(crash=False):
    CFG.crashed = True  # Just in case
    process_name = "Automatic Relocation System"
    action = "Detected more optimal server. Relocating."
    if crash:
        process_name = "Automatic Crash Recovery"
        action = "Detected Roblox Crash. Recovering."
    log_process(process_name)
    log(action)
    kill_process(force=True)
    server_id = await force_get_best_server()
    await async_sleep(1)

    log_process(f"{process_name} - Joining Server")
    success = await join_target_server(server_id)
    if not success:
        return False
    output_log("change_server_status_text", "")

    log_process(f"{process_name} - Handling Spawn")
    if not await server_spawn():
        return False

    #log_process(f"{process_name} - Detecting Location")
    #cv_detect_spawn()

    log_process("")
    log("Complete. Please use '!dev Error' if we're not in-game.")
    await async_sleep(5)
    CFG.crashed = False
    log_process("")
    log("")


async def auto_nav(location, do_checks=True, slow_spawn_detect=True):
    #await check_active()
    log_process("AutoNav")
    if do_checks:
        await check_active(force_fullscreen=False)
        await async_sleep(0.5)
        await send_chat(f"[AutoNavigating to {CFG.nav_locations[location]['name']}!]")
        if not CFG.collisions_disabled:
            log("Disabling collisions")
            await toggle_collisions()
            await async_sleep(0.5)
        log("Jumping to clear any respawn locks")
        ACFG.jump()
        await async_sleep(1)
        log("Respawning")
        #await change_characters(respawn=True)
        await respawn_character(chat=False)
        await async_sleep(7)
    log("Zooming out to full scale")
    ACFG.zoom(zoom_direction_key="o", amount=105)
    
    spawn = spawn_detection_main(slow=slow_spawn_detect)["location"]
    #log("Zooming in to precision movement scale")
    #ACFG.zoom(zoom_direction_key="i", amount=90)
    if spawn == "comedy_machine":
        comedy_to_main()
    elif spawn == "tree_house":
        treehouse_to_main()
    await async_sleep(1)
    if location == "shrimp":
        main_to_shrimp_tree()
    elif location == "ratcade":
        main_to_ratcade()
    elif location == "train":
        main_to_train()
    elif location == "classic":
        main_to_classic()
    elif location == "treehouse":
        main_to_treehouse()
    log("Zooming in to normal scale")
    default_zoom_in_amount = (CFG.zoom_max - CFG.zoom_default)
    zoom_in_amount = CFG.nav_post_zoom_in.get(location, default_zoom_in_amount)
    ACFG.zoom(zoom_direction_key="i", amount=zoom_in_amount)
    log(f"Complete! This is experimental, so please re-run \n'!nav {location}' if it didn't work.")
    await async_sleep(3)


async def get_settings_button_pos():
    monitor = mss().monitors[-1]
    screen_width = monitor["width"]
    screen_height = monitor["height"]
    monitor["width"] = int(CFG.character_select_width * screen_width)
    monitor["left"] = int((screen_width/2) - (CFG.character_select_width/2) * screen_width)
    
    button_img = cv.imread(CFG.settings_menu_image_path, cv.IMREAD_UNCHANGED)
    button_img = cv.cvtColor(button_img, cv.COLOR_BGR2GRAY)
    _, button_img = cv.threshold(button_img,211,255,3)
    
    success = False
    for i in range(CFG.settings_menu_max_find_attempts):
        screenshot = None
        with mss() as sct:
            screenshot = sct.grab(monitor)
        screenshot = np.array(screenshot)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
        _, screenshot = cv.threshold(screenshot,211,255,3)
        
        best_match = {"max_val": 0, "top_left": (0,0), "bottom_right": (0,0), "angle": 0}
        for rotation_degrees in range(360):  
            rotated_button = rotate_bound(button_img, rotation_degrees)
            result = cv.matchTemplate(screenshot, rotated_button, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)        
            if best_match["max_val"] < max_val:
                button_w = button_img.shape[1]
                button_h = button_img.shape[0]
                top_left = max_loc
                bottom_right = (top_left[0] + button_w, top_left[1] + button_h)
                best_match = {
                    "max_val": max_val,
                    "top_left": top_left,
                    "bottom_right": bottom_right,
                    "angle": rotation_degrees
                }
                # No break; getting highest confidence rotation reduces false positives
        
        #screenshot = cv.cvtColor(screenshot, cv.COLOR_GRAY2RGB)
        #cv.rectangle(screenshot, best_match["top_left"], best_match["bottom_right"], color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
        #img = screenshot
        #scale_percent = 60 # percent of original size
        #width = int(img.shape[1] * scale_percent / 100)
        #height = int(img.shape[0] * scale_percent / 100)
        #dim = (width, height)
        #resized = cv.resize(img, dim, interpolation = cv.INTER_AREA)
        #cv.imshow("OCR", resized)
        #cv.waitKey(1)
        if best_match["max_val"] >= CFG.settings_menu_find_threshold: 
            success = True
            break
        await async_sleep(1)
    try:
        right = best_match["bottom_right"][0]
        left = best_match["top_left"][0]
        width =  max(right,left) - min(right, left)
        center_x = int(monitor["left"]) + int(left + (width/2))
        
        bottom = best_match["bottom_right"][1]
        top = best_match["top_left"][1]
        height = max(top,bottom) - min(top,bottom)
        center_y = int(top + (height/2))
        
        if best_match["max_val"] >= CFG.settings_menu_find_threshold:    
            print(f"Found button. ({round(best_match['max_val']*100,2)}%)")
            log("")
            return center_x, center_y
        else:
            log(f"Could not find settings button!\n(Best match {round(best_match['max_val']*100,2)}% confidence)\n({center_x}, {center_y}")
            await async_sleep(5)            
            log("")
            return None, None
    except:
        error_log(format_exc())
        log(f"Could not find settings button!")
        return None, None


async def click_settings_button(check_open_state=None):
    await async_sleep(0.5)
    button_x, button_y = await get_settings_button_pos()
    if button_x is None:
        return False
    
    # with mss() as sct:
        # screenshot = sct.grab(mss().monitors[-1])
    # screenshot = np.array(screenshot)
    # screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
    
    # button_half = 15
    # print(button_x, button_y)
    # cv.rectangle(screenshot, (button_x-button_half, button_y-button_half), (button_x+button_half, button_y+button_half), color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)
    # img = screenshot
    # scale_percent = 60 # percent of original size
    # width = int(img.shape[1] * scale_percent / 100)
    # height = int(img.shape[0] * scale_percent / 100)
    # dim = (width, height)
    # resized = cv.resize(img, dim, interpolation = cv.INTER_AREA)
    # cv.imshow("OCR", resized)
    # cv.waitKey(10000)
    
    
    ACFG.moveMouseAbsolute(x=int(button_x), y=int(button_y))
    ACFG.left_click()
    
    if check_open_state is not None:
        log(f"Checking that settings menu is {'open' if check_open_state else 'closed'}")
        await async_sleep(2)
        last_button_x, last_button_y = button_x, button_y
        success = False
        for i in range(CFG.character_select_max_click_attempts):
            new_button_x, new_button_y = await get_settings_button_pos()
            if new_button_x is None:
                for i in range(CFG.settings_menu_max_find_attempts):
                    new_button_x, new_button_y = await get_settings_button_pos()
                    if new_button_x is not None:
                        break
                    await async_sleep(2)
                
            if check_open_state is True and (int(new_button_y/2) < int(last_button_y/2)):
                success = True
                break  # If we want it open and the new pos is further up the screen than before
            elif check_open_state is False and (int(new_button_y/2) > int(last_button_y/2)):
                success = True
                break  # If we want it closed and the new pos is further down the screen than before
            else:
                ACFG.moveMouseAbsolute(x=int(new_button_x), y=int(new_button_y))
                ACFG.left_click()
                await async_sleep(2)
                last_button_x, last_button_y = new_button_x, new_button_y 
        if not success:
            log("Unable to toggle settings menu!")
            await async_sleep(2)
        log("")
    else:
        await async_sleep(0.5)
    return True


async def ocr_for_settings(option=None):
    desired_option = CFG.settings_menu_grief_text.lower()
    if option is not None:
        desired_option = option.lower()
    button_x, button_y = await get_settings_button_pos()
    if button_x is None:
        return False
    monitor = mss().monitors[-1]
    screen_width = monitor["width"]
    screen_height = monitor["height"]
    print(screen_width)
    monitor["width"] = int(CFG.settings_menu_width * screen_width)
    monitor["left"] = int(button_x - (CFG.settings_menu_width/2) * screen_width)
    height_offset = int(button_y + (CFG.settings_menu_button_height * screen_height))
    monitor["top"] = height_offset
    monitor["height"] = monitor["height"] - height_offset
    
    ocr_data = None
    last_ocr_text = None
    times_no_movement = 0
    found_option = False
    for attempts in range(CFG.settings_menu_ocr_max_attempts):  # Attempt multiple OCRs
        log(f"Finding '{desired_option.capitalize()}' (Attempt #{attempts}/{CFG.settings_menu_ocr_max_attempts})")
        with mss() as sct:
            screenshot = sct.grab(monitor)
        screenshot = np.array(screenshot)

        gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)  # PyTesseract
        gray, img_bin = cv.threshold(gray,100,255,cv.THRESH_BINARY | cv.THRESH_OTSU)
        gray = cv.bitwise_not(img_bin)            
        kernel = np.ones((2, 1), np.uint8)
        img = cv.erode(gray, kernel, iterations=1)
        img = cv.dilate(img, kernel, iterations=1)

        # scale_percent = 60 # percent of original size
        # width = int(img.shape[1] * scale_percent / 100)
        # height = int(img.shape[0] * scale_percent / 100)
        # dim = (width, height)
        # resized = cv.resize(img, dim, interpolation = cv.INTER_AREA)
        # cv.imshow("ocr", resized)
        # cv.waitKey(5000)
        
        ocr_data = pytesseract.image_to_data(img, config='--oem 1', output_type=pytesseract.Output.DICT)
        ocr_data["text"] = [word.lower() for word in ocr_data["text"]]
        print(ocr_data["text"])
        if desired_option in ocr_data["text"]:
            log("Found option, clicking")
            found_option = True
            break
        await async_sleep(0.25)
    
    if not found_option:
        log(f"Failed to find '{desired_option.capitalize()}'.\n Notifying Dev...")
        notify_admin(f"Failed to find `{desired_option}`")
        await async_sleep(5)
        return False
    
    # We found the option, lets click it
    ocr_index = ocr_data["text"].index(desired_option)
    
    option_top = ocr_data["top"][ocr_index]
    option_half = ocr_data["height"][ocr_index]/2
    desired_option_height = int(option_top + option_half + height_offset)
    ACFG.moveMouseAbsolute(x=int(button_x), y=int(desired_option_height))
    await async_sleep(0.5)
    ACFG.left_click()
    await async_sleep(0.5)
    return True


async def toggle_collisions():
    log_process(f"{'Enabling' if CFG.collisions_disabled else 'Disabling'} Grief Collisions")
    log("Opening Settings")
    await check_active(force_fullscreen=False)
    await async_sleep(1)
    
    need_zoom_adjust = False
    if CFG.zoom_level < CFG.zoom_ui_min_cv:
        ACFG.zoom("o", CFG.zoom_out_ui_cv)
        need_zoom_adjust = True
    
    if not await click_settings_button(check_open_state=True):
        notify_admin("Failed to open settings")
        log("")
        log_process("")
        if need_zoom_adjust:
            ACFG.zoom("i", CFG.zoom_out_ui_cv)
        return False
    
    log(f"Finding {CFG.settings_menu_grief_text} option")
    await async_sleep(1)
    if not await ocr_for_settings():
        notify_admin("Failed to click settings option")
        log("")
        log_process("")
        if need_zoom_adjust:
            ACFG.zoom("i", CFG.zoom_out_ui_cv)
        return False
    
    CFG.collisions_disabled = not(CFG.collisions_disabled)
    collisions_msg = "" if CFG.collisions_disabled else "[WARN] Griefing/Collisions enabled!"
    output_log("collisions", collisions_msg)
    
    log("Closing Settings")
    await async_sleep(0.25)
    if not await click_settings_button(check_open_state=False):
        notify_admin("Failed to close settings")
        log("")
        log_process("")
        if need_zoom_adjust:
            ACFG.zoom("i", CFG.zoom_out_ui_cv)
        return False    
    log("")
    log_process("")
    ACFG.resetMouse()
    if need_zoom_adjust:
        ACFG.zoom("i", CFG.zoom_out_ui_cv)
    return True

if __name__ == "__main__":
    async def test():
        await check_active(force_fullscreen=False)
        sleep(0.5)
        await auto_nav("treehouse", do_checks=False, slow_spawn_detect=False)
        
        #ACFG.zoom("o", 105)
        #ACFG.zoom("i", 50)
           
        
    asyncio.get_event_loop().run_until_complete(test())
    