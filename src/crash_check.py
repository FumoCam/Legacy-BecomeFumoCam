import json
from time import sleep, strftime
from typing import Dict, List, Optional, cast

import cv2 as cv
import numpy as np
import pydirectinput
from cv2.typing import MatLike
from mss import mss
from mss import tools as mss_tools
from mss.models import Monitor
from mss.screenshot import ScreenShot
from pygetwindow import Win32Window, getActiveWindow, getAllWindows

from arduino_integration import ACFG
from config import CFG

# Lot of redefined functions from utilities.py, this needs to be crosscompatible with the rust equivalent

def log_crashcheck(msg: str):

    entry_timestamp = strftime("%Y-%m-%d %I:%M:%S%p EST")
    entry = f"[{entry_timestamp}]\n{msg}"
    print(entry)
    with open("log_crashcheck.txt", "a", encoding="utf-8") as f:
        f.write(f"{entry}\n\n\n\n")

def focus_window(window: Win32Window):
    try:
        window.minimize()
        log_crashcheck(f"[focus_window] Minimized {window.title}")
    except Exception:
        log_crashcheck(f"[focus_window] ERROR IN MINIMIZING {window.title}")
    try:
        window.activate()
        log_crashcheck(f"[focus_window] Activated {window.title}")
    except Exception:
        log_crashcheck(f"[focus_window] ERROR IN ACTIVATING {window.title}")
    try:
        window.maximize()
        log_crashcheck(f"[focus_window] Maximized {window.title}")
    except Exception:
        log_crashcheck(f"[focus_window] ERROR IN MAXIMIZING {window.title}")
    log_crashcheck("[focus_window] Focused - Waiting")
    sleep(0.75)
    log_crashcheck("[focus_window] Focused - Done Waiting")

def check_if_active_window_edgecases_present(windows_map: Dict[str, Win32Window]) -> bool:
    """Checks known edgecases that interfere with active-window operations. Returns False if all clear"""
    if "Error" in windows_map:
        windows_map["Error"].close()
        log_crashcheck("[check_active_edgecases] SensApi.dll or other error detected. Closing.")
        return True
    if "Microsoft .NET Framework" in windows_map:
        try:
            windows_map["Microsoft .NET Framework"].close()
        except Exception:
            log_crashcheck("[check_active_edgecases] NET Framework Error, failed to resolve")
            from os import system

            system("shutdown /f /r /t 30")  # nosec
            exit()
        log_crashcheck("[check_active_edgecases] LibreHardwareMonitor or other error detected. Closing.")

        return True
    return False

def make_roblox_active_window() -> bool:
    """Checks if Roblox is the active window. If not, makes it active. Returns success status."""

    title = "Roblox"
    log_crashcheck(f"[check_active] {title}")
    windows_list: List[Win32Window] = getAllWindows()
    windows_map: Dict[str, Win32Window] = {window.title: window for window in windows_list}

    # Rare edgecases. Fail
    issues_detected = check_if_active_window_edgecases_present(windows_map)
    if issues_detected:
        log_crashcheck(f"[check_active] Edgecase detected. Returning false")
        return False

    # Window not found. Fail
    if title not in windows_map:
        log_crashcheck(f"[check_active] {title} window does not exist. Returning false")
        return False

    # Window already active. Pass
    if getActiveWindow() == title:
        log_crashcheck(f"[check_active] {title} already active. Returning true")
        return True

    # Window exists, just not active. Activate, then Pass
    focus_window(windows_map[title])
    log_crashcheck(f"[check_active] Made window active. Returning true")
    return True

def save_screenshot(screenshot: ScreenShot, filename: str) -> MatLike:
    rgba_np_array = np.array(screenshot)
    rgb_np_array = cv.cvtColor(rgba_np_array, cv.COLOR_RGBA2RGB)
    cv.imwrite(f"{filename}.jpg", rgb_np_array)
    return rgb_np_array


def take_screenshot_binary(monitor: Monitor) -> ScreenShot:
    with mss() as sct:
        screenshot = sct.grab(monitor)
    return screenshot

def take_and_save_screenshot(monitor: Monitor, filename: str) -> MatLike:
    screenshot_obj = take_screenshot_binary(monitor)
    matlike_screenshot = save_screenshot(screenshot_obj, filename)
    return matlike_screenshot

def apply_edge_filter(original_image: MatLike, filename: str) -> MatLike:
    edge_filter = {
        "kernelSize": 5,
        "erodeIter": 1,
        "dilateIter": 1,
        "canny1": 0,
        "canny2": 60,
    }

    kernel = np.ones((edge_filter["kernelSize"], edge_filter["kernelSize"]), np.uint8)
    eroded_image = cv.erode(original_image, kernel, iterations=edge_filter["erodeIter"])
    dilated_image = cv.dilate(
        eroded_image, kernel, iterations=edge_filter["dilateIter"]
    )

    # canny edge detection
    result = cv.Canny(dilated_image, edge_filter["canny1"], edge_filter["canny2"])
    # convert single channel image back to BGR
    img = cv.cvtColor(result, cv.COLOR_GRAY2BGR)

    cv.imwrite(f"{filename}.jpg", img)

    return img


def shake_cursor():
    """Sometimes the mouse moves to a spot but isn't actually 'updated'. Jiggling it like this helps (quicker than alt tab)"""
    pydirectinput.move(1, 1)
    pydirectinput.move(-2, -2)
    pydirectinput.move(1, 1)

def hide_mouse():
    """Move the cursor off-screen"""
    monitor = mss().monitors[-1]
    target_x = monitor["width"]-1
    target_y = monitor["height"]-1
    pydirectinput.moveTo(x=target_x, y=target_y)
    shake_cursor()

def move_camera(reverse:bool = False):
    pydirectinput.moveTo(600, 100)
    shake_cursor()
    # Need click AND mouseDown
    pydirectinput.click(button="right")
    pydirectinput.mouseDown(button="right")

    amount = 100
    if reverse:
        amount *= -1

    pydirectinput.move(amount, 0, relative=True)
    pydirectinput.mouseUp(button="right")
    shake_cursor()


def check_if_still_online() -> bool:
    """
    Returns True if likely online.
    Checks to see if Roblox is still active.
    If so, moves the camera and visually compares before/after.
    The visual section is centered around where a roblox error would be, so a crash would be 100% similar visually
    """

    log_crashcheck(f"===CRASH CHECK START===\n================\n============")
    if CFG.chat_ocr_active:
        CFG.chat_ocr_ready = False

    roblox_window_active = make_roblox_active_window()
    if not roblox_window_active:
        log_crashcheck("[main] Failed to make roblox window active")
        return False

    monitor = mss().monitors[-1]
    # Specifically the place where an error message would pop up
    monitor["height"] = 230
    monitor["width"] = 390
    monitor["left"] = 450
    monitor["top"] = 250

    # Take current screenshot
    before = take_and_save_screenshot(monitor, "crashcheck_before")
    before_edge = apply_edge_filter(before, "crashcheck_before_edge")
    # Move the camera away
    move_camera()

    # Take moved away screenshot
    after = take_and_save_screenshot(monitor, "crashcheck_after")
    after_edge = apply_edge_filter(after, "crashcheck_after_edge")

    # Move the camera back
    move_camera(reverse=True)
    hide_mouse()

    if CFG.chat_ocr_active:
        CFG.chat_ocr_ready = True
        ACFG.keyPress("/")

    # Do a binary edge comparison; Camera cannot move if disconnected so they should be similar if so
    needle_mask = cv.bitwise_not(after_edge) / 255
    difference = (before_edge * needle_mask).clip(0, 255).astype(np.uint8)

    original_sum = np.sum(before_edge.astype(np.uint8) > 0)
    difference_sum = np.sum(difference > 0)

    percentage = round(
        ((original_sum - difference_sum) / original_sum) * 100, 2
    )
    log_crashcheck(f"[main] Similarity ratio: {percentage}")

    # Final results
    CUTOFF = 98
    likely_online = percentage <= CUTOFF
    log_crashcheck(f"[main] Result: {'Likely online' if likely_online else 'Likely crashed'}")
    return likely_online

if __name__ == "__main__":
    result = check_if_still_online()
    print(json.dumps(result)) # For rust to read console output
