from actions import *
from health import change_characters


async def click_sit_button():
    log_process("Standing up" if CFG.sitting_status else "Sitting down")
    await check_active()
    
    need_zoom_adjust = False
    if CFG.zoom_level < CFG.zoom_ui_min:
        ACFG.zoom("o", CFG.zoom_out_ui)
        need_zoom_adjust = True
    
    try:
        ratio_x, ratio_y = CFG.sit_button_position
        x = round(SCREEN_RES["width"] * ratio_x)
        y = round(SCREEN_RES["height"] * ratio_y)
        ACFG.moveMouseAbsolute(x=x, y=y)
        ACFG.left_click()
        await async_sleep(0.25)
        ACFG.resetMouse()
        CFG.sitting_status = not CFG.sitting_status
    except Exception:
        log("Could not find sit button on screen?")
        await async_sleep(5)
        log("")
    
    if need_zoom_adjust:
        ACFG.zoom("i", CFG.zoom_out_ui_cv)
    log_process("")


async def click_backpack_button():
    log_process(f"{'Closing' if CFG.backpack_open else 'Opening'} backpack")
    await check_active()
    
    need_zoom_adjust = False
    if CFG.zoom_level < CFG.zoom_ui_min:
        ACFG.zoom("o", CFG.zoom_out_ui)
        need_zoom_adjust = True
    
    try:
        ratio_x, ratio_y = CFG.backpack_button_position
        x = round(SCREEN_RES["width"] * ratio_x)
        y = round(SCREEN_RES["height"] * ratio_y)
        ACFG.moveMouseAbsolute(x=x, y=y)
        ACFG.left_click()
        await async_sleep(0.25)
        ACFG.resetMouse()
        CFG.backpack_open = not CFG.backpack_open
    except Exception:
        log("Could not find backpack button on screen?")
        await async_sleep(5)
        log("")
    
    if need_zoom_adjust:
        ACFG.zoom("i", CFG.zoom_out_ui_cv)
    log_process("")


async def click_item(item_number):
    log_process(f"Clicking item #{item_number}")
    await check_active()
    
    item_x = int(SCREEN_RES["width"]*CFG.backpack_item_positions[item_number]["x"])
    item_y = int(SCREEN_RES["height"]*CFG.backpack_item_positions[item_number]["y"])
    ACFG.moveMouseAbsolute(x=item_x, y=item_y)
    ACFG.left_click()
    CFG.backpack_open = False


async def force_respawn_character():
    await check_active()
    await async_sleep(0.5)
    log_process("Force-Respawning")
    await send_chat("[Respawning!]")
    await change_characters(respawn=True)
    log_process("")
