from health import *  # Optimized import, contains all other src files down the line of dependency
from twitch_integration import *

async def queue_movement(action):  # todo: Simplify
    CFG.action_running = True
    log_process("Manual Movement")
    valid_keys = {"w": "Forward", "a": "Left", "s": "Backwards", "d": "Right"}
    key = action["move_key"].lower()
    if key not in valid_keys.keys():
        log(f"Not a valid movement! ({','.join(valid_keys)})")
        await async_sleep(5)
        log("")
        log_process("")
        CFG.action_running = False
        return False
    time_to_press = action["move_time"]
    log(f"Moving {valid_keys[key]} for {time_to_press}s")
    await check_active()
    #await async_sleep(0.75)
    pydirectinput.keyDown(key)
    await async_sleep(time_to_press)
    pydirectinput.keyUp(key)
    log("")
    log_process("")
    CFG.action_running = False


async def queue_leap(action):  # todo: Simplify
    CFG.action_running = True
    log_process("Leap Forward")
    time_forward = action["forward_time"]
    time_jump = action["jump_time"]
    log(f"Moving forward for {time_forward}s and jumping for {time_jump}s")
    await check_active()
    #await async_sleep(0.75)
    pydirectinput.keyDown("w")
    pydirectinput.keyDown("space")
    if time_forward > time_jump:
        await async_sleep(time_jump)
        pydirectinput.keyUp("space")
        await async_sleep(time_forward - time_jump)
        pydirectinput.keyUp("w")
    else:
        await async_sleep(time_forward)
        pydirectinput.keyUp("w")
        await async_sleep(time_jump - time_forward)
        pydirectinput.keyUp("space")
    log("")
    log_process("")
    CFG.action_running = False


async def do_process_queue():  # todo: Investigate benefits of multithreading over single-threaded/async
    if len(CFG.action_queue) == 0 or CFG.action_running:
        return
    print(CFG.action_queue)
    CFG.action_running = True
    while len(CFG.action_queue) > 0:
        action = CFG.action_queue[0]
        if action == "anti-afk":
            await do_anti_afk()
        elif action == "advert":
            await do_advert()
        elif "turn_camera_direction" in action:
            turn_direction = action['turn_camera_direction']
            turn_time = action['turn_camera_time']
            log_process(f"{turn_direction.upper()} for {turn_time}s")
            await turn_camera(action)
            log_process("")
        elif "zoom_camera_direction" in action:
            zoom_direction = "in" if action['zoom_camera_direction'] == "i" else "out"
            zoom_time = action['zoom_camera_time']
            log_process(f"Zooming {zoom_direction} for {zoom_time}s")
            await zoom_camera(action)
            log_process("")
        elif action == "check_for_better_server":
            crashed = await do_crash_check()
            if not crashed:
                await check_for_better_server()
                await check_active()
            else:
                CFG.action_queue.insert(0, "handle_crash")
        elif "chat_with_name" in action:
            name = action["chat_with_name"][0]
            await send_chat(name)
            await async_sleep(len(name) * CFG.chat_name_sleep_factor)
            msgs = action["chat_with_name"][1:]
            for msg in msgs:
                await send_chat(msg)
        elif "chat" in action:
            for message in action["chat"]:
                await send_chat(message)
        elif action == "handle_crash":
            await handle_join_new_server(crash=True)
        elif action == "handle_join_new_server":
            await handle_join_new_server()
        elif action == "click":
            await alt_tab_click()
        elif action == "sit":
            await click_sit_button()
        elif action == "use":
            log_process("Pressing Use (e)")
            await check_active()
            pydirectinput.keyDown("e")
            await async_sleep(1)
            pydirectinput.keyUp("e")
            log_process("")
            log("")
        elif action == "grief":
            await toggle_collisions()
            pydirectinput.moveTo(1, 1)
            await alt_tab_click(click_mouse=False)
            log_process("")
            log("")
        elif action == "respawn":
            await respawn_character()
            log_process("")
            log("")
        elif action == "jump":
            await jump()
        elif "movement" in action:
            await queue_movement(action)
        elif "leap" in action:
            await queue_leap(action)
        else:
            print("queue failed")
        CFG.action_queue.pop(0)
    await async_sleep(0.1)
    CFG.action_running = False
async def add_action_queue(item):
    CFG.action_queue.append(item)
    await do_process_queue()


async def async_main():
    print("[Async_Main] Start")
    crashed = await do_crash_check()
    if crashed or "Roblox" not in pyautogui.getAllTitles():
       CFG.action_queue.append("handle_crash")
       await do_process_queue()
    else:
       await check_active()
    

def main():
    CFG.anti_afk = 0
    log_process("")
    log("")
    output_log("change_server_status_text", "")
    CFG.anti_afk_runs = 0
    CFG.add_action_queue = add_action_queue
    CFG.async_main = async_main
    twitch_main()


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    main()