# TODO: Change from functions to variables (like dict or something)
import random
from random import randint
from time import sleep

from arduino_integration import ACFG
from config import SCREEN_RES, SIT_BUTTON_POSITION, ZOOM_FIRST_PERSON
from utilities import log, log_process


def treehouse_spawn_calibration():
    log_process("AutoNav")
    log("Treehouse Spawn -> Calibration Rock")
    ACFG.precision_look("left", 1314, raw=True)
    ACFG.move("s", 1.8, raw=True)
    ACFG.move("d", 3, raw=True)
    ACFG.move("w", 1.5, raw=True)

    standard_calibration()

    log_process("")
    log("")


def comedy_spawn_calibration():
    log_process("AutoNav")
    log("Comedy Machine Spawn -> Calibration Rock")
    ACFG.precision_look("right", 469, raw=True)
    ACFG.move("w", 1.6, raw=True)
    ACFG.move("a", 2.2, raw=True)
    ACFG.move("w", 2.5, raw=True)

    standard_calibration()

    log_process("")
    log("")


def main_spawn_calibration():
    log_process("AutoNav")
    log("Main Spawn -> Calibration Rock")
    ACFG.precision_look("right", 7, raw=True)
    ACFG.move("d", 0.7, raw=True)
    ACFG.move("w", 1.5, raw=True)

    standard_calibration()

    log_process("")
    log("")


def standard_calibration():
    ACFG.move("s", 0.08, raw=True)
    ACFG.move("d", 0.8, raw=True)
    ACFG.move("w", 0.8, raw=True)
    ACFG.move("a", 0.8, raw=True)
    ACFG.move("w", 0.3, raw=True)
    ACFG.move("a", 0.3, raw=True)


def main_to_shrimp_tree():
    log_process("AutoNav")
    log("-> Shrimp Tree")
    ACFG.move("s", 0.5, raw=True)
    ACFG.move("a", 1.9, raw=True)
    ACFG.move("s", 2, raw=True)
    ACFG.leap(forward_time=0.4, jump_time=0.25, direction_key="s", jump_delay=0.1)
    ACFG.leap(forward_time=0.6, jump_time=0.4, direction_key="a", jump_delay=0.1)
    ACFG.leap(
        forward_time=0.7,
        jump_time=0.3,
        direction_key="d",
        jump_delay=0.1,
        diagonal_direction_key="s",
    )
    ACFG.zoom("i", ZOOM_FIRST_PERSON)
    ACFG.zoom("o", ZOOM_FIRST_PERSON)
    ACFG.precision_look("left", 1798, raw=True)
    log_process("")
    log("")


def main_to_ratcade():
    log_process("AutoNav")
    log("-> Ratcade")
    ACFG.move("d", 0.8, raw=True)
    ACFG.move("w", 1.2, raw=True)
    ACFG.move("a", 0.3, raw=True)
    ACFG.move("w", 2.8, raw=True)
    ACFG.move("a", 1.6, raw=True)
    ACFG.move("w", 0.95, raw=True)
    ACFG.move("d", 0.9, raw=True)
    ACFG.precision_look("left", 901, raw=True)
    ACFG.zoom("i", ZOOM_FIRST_PERSON)
    ACFG.zoom("o", ZOOM_FIRST_PERSON)
    ACFG.precision_look("right", 1798, raw=True)
    log_process("")
    log("")


def main_to_train():
    log_process("AutoNav")
    log("-> Train Station")
    ACFG.move("s", 2.4, raw=True)
    ACFG.move("d", 4.2, raw=True)
    ACFG.move("s", 9.8, raw=True)
    ACFG.move("a", 0.7, raw=True)
    ACFG.move("s", 0.9, raw=True)
    ACFG.leap(forward_time=0.25, jump_time=0.25, direction_key="s")
    ACFG.leap(forward_time=0.3, jump_time=0.25, direction_key="a")
    ACFG.move("w", 1.05, raw=True)
    # ACFG.precision_look("right", 901, raw=True)
    # ACFG.zoom("i", ZOOM_FIRST_PERSON)
    # ACFG.zoom("o", ZOOM_FIRST_PERSON)
    # ACFG.precision_look("left", 1798, raw=True)
    log_process("")
    log("")


def _main_to_classic_portal():
    # Calibration Rock
    ACFG.move("s", 2.4, raw=True)
    ACFG.move("d", 4.2, raw=True)
    ACFG.move("s", 11.5, raw=True)
    ACFG.move("a", 1.4, raw=True)
    ACFG.move("w", 1.3, raw=True)
    ACFG.move("d", 0.5, raw=True)

    # Calibration Corner 1
    ACFG.move("s", 0.3, raw=True)
    ACFG.move("a", 1.5, raw=True)
    ACFG.move("s", 0.5, raw=True)
    ACFG.move("a", 0.6, raw=True)
    ACFG.move("w", 0.3, raw=True)
    ACFG.move("a", 0.3, raw=True)

    # Calibration Corner 2
    ACFG.leap(forward_time=0.6, jump_time=0.25, direction_key="a")
    ACFG.leap(
        forward_time=0.3,
        jump_time=0.3,
        direction_key="a",
        diagonal_direction_key="s",
    )
    ACFG.leap(forward_time=0.8, jump_time=0.3, direction_key="s", jump_delay=0.2)
    ACFG.leap(forward_time=1, jump_time=0.5, direction_key="d", jump_delay=0.4)
    ACFG.move("s", 0.2, raw=True)
    ACFG.leap(forward_time=0.9, jump_time=0.5, direction_key="d", jump_delay=0.35)
    ACFG.move("s", 0.2, raw=True)
    ACFG.use()
    sleep(5)


def classic_portal_to_slide():
    ACFG.move("w", 1.8, raw=True)
    ACFG.move("d", 0.125, raw=True)
    ACFG.move("w", 2.270, raw=True)
    ACFG.precision_look("left", 901 + (901 / 2), raw=True)
    ACFG.zoom("i", ZOOM_FIRST_PERSON)
    ACFG.zoom("o", ZOOM_FIRST_PERSON)
    ACFG.precision_look("left", 1798, raw=True)


def main_to_classic():
    log_process("AutoNav")
    log("-> BecomeFumo Classic Portal")
    _main_to_classic_portal()
    classic_portal_to_slide()
    log_process("")
    log("")


def main_to_classic_fix_bright():
    log_process("AutoNav")
    log("-> BecomeFumo Classic Portal\n(And back out)")
    _main_to_classic_portal()
    ACFG.use()
    log_process("")
    log("")


def main_to_treehouse_bench():
    log_process("AutoNav")
    log("-> Treehouse Bench")

    # To calibration corner, bottom of steps
    ACFG.move("d", 0.8, raw=True)
    ACFG.move("w", 1.2, raw=True)
    ACFG.move("a", 0.3, raw=True)
    ACFG.move("w", 2.8, raw=True)
    ACFG.move("a", 4.9, raw=True)
    ACFG.move("s", 1, raw=True)
    ACFG.move("d", 1, raw=True)
    ACFG.move("s", 1, raw=True)
    ACFG.move("d", 0.3, raw=True)
    ACFG.move("s", 0.3, raw=True)

    # TODO: a reasonably replicatable route
    # (Not really possible with the messed up terrain in the new update)


def treehouse_bench_calibration():
    log_process("AutoNav")
    log("Treehouse Spawn-> Treehouse Bench")
    ACFG.precision_look("left", 1314, raw=True)
    ACFG.move("w", 0.65, raw=True)
    ACFG.move("a", 1, raw=True)


def treehouse_bench_to_treehouse():
    log("Treehouse Bench -> Funky Treehouse")

    ACFG.leap(forward_time=0.65, jump_time=0.5)
    ACFG.leap(forward_time=1.5, jump_time=0.2, direction_key="d")
    ACFG.move("w", 0.5)
    ACFG.move("a", 0.8)
    # ACFG.move("s", 1)
    # ACFG.move("d", 1.6)
    # ACFG.leap(forward_time=0.6, jump_time=0.7, direction_key="a")
    # sleep(1)
    # ACFG.leap(forward_time=0.4, jump_time=0.4, direction_key="d", jump_delay=0.1)
    ACFG.move("s", 0.41, raw=True)
    ACFG.move("d", 0.55, raw=True)
    ACFG.leap(forward_time=0.4, jump_time=0.75, direction_key="a")
    ACFG.leap(forward_time=0.2, jump_time=0.3, direction_key="d", jump_delay=0.1)
    ACFG.precision_look("left", 1798, raw=True)
    ACFG.zoom("i", ZOOM_FIRST_PERSON)
    ACFG.zoom("o", ZOOM_FIRST_PERSON)
    ACFG.precision_look("left", 1798, raw=True)

    log_process("")
    log("")


def main_to_beach():
    log_process("AutoNav")
    log("-> Beach")

    main_to_beach_portal()

    log("-> Beach\n(Going through twice to clear portal-lock bug)")
    sleep(5)
    ACFG.use()
    log("-> Beach")
    sleep(5)
    ACFG.use()
    sleep(5)

    if randint(0, 100) > 75:  # nosec
        beach_portal_easter_egg()
    else:
        beach_portal_to_dock()

    log_process("")
    log("")


def main_to_beach_portal():
    ACFG.move("s", 0.3, raw=True)
    ACFG.move("a", 6, raw=True)
    ACFG.move("w", 7.3, raw=True)
    ACFG.move("s", 1.3, raw=True)
    ACFG.leap(forward_time=0.6, jump_time=0.25, direction_key="d", jump_delay=0.1)
    ACFG.use()


def beach_portal_easter_egg():
    ACFG.move("s", 0.5, raw=True)
    ACFG.move("a", 1.8, raw=True)
    ACFG.move("s", 4.4, raw=True)
    ACFG.zoom("i", 50)
    ACFG.use()
    ACFG.send_message("[Fun slide!]")
    sleep(5)
    ACFG.jump()
    ACFG.move("w", 2.5, raw=True)
    ACFG.move("s", 0.2, raw=True)
    ACFG.send_message("[Awoo swim.]")
    sleep(2.5)
    ACFG.zoom("o", 60)
    ACFG.move("d", 0.7, raw=True)
    ACFG.move("w", 0.8, raw=True)
    ACFG.move("d", 0.6, raw=True)
    ACFG.move("s", 1, raw=True)


def beach_portal_to_dock():
    ACFG.move("s", 0.5, raw=True)
    ACFG.move("a", 1.8, raw=True)
    ACFG.move("s", 3.1, raw=True)
    ACFG.move("d", 1.1, raw=True)
    ACFG.move("s", 1, raw=True)


def main_to_miko():
    log_process("AutoNav")
    log("-> Miko Borgar")

    # Get into the building and touch the front table
    ACFG.move("s", 0.3, raw=True)
    ACFG.move("a", 3, raw=True)
    ACFG.move("s", 3.25, raw=True)
    ACFG.move("d", 2.1, raw=True)
    ACFG.move("s", 3.5, raw=True)

    # Get behind the table
    ACFG.move("d", 0.4, raw=True)
    ACFG.move("s", 1, raw=True)

    # 180
    ACFG.zoom("i", ZOOM_FIRST_PERSON)
    ACFG.zoom("o", ZOOM_FIRST_PERSON)
    ACFG.precision_look("left", 1798, raw=True)

    log_process("")
    log("")


def _comedy_machine_arrived():
    # Old phrases from the prototype years ago.
    # It doesn't fit the project, but its worth it for nostalgia.
    comedy_phrases = [
        "Peak comedy incoming!",
        "This is going to be funny!",
        "Wee! c:",
        "That's one small step for fumo, one giant leap for fumbo cam!",
        "Incoming fumo asteroid!",
        "FORE!",
        "Awoo incoming!",
        "To infumoty and beyond!",
        "If I'm using Comedy Machine 3000, does that make me Comedy Machine 4000?",
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        "Orbital fumbo cam!",
        "It's no trebuchet but it'll do.",
    ]

    # Manual Sit
    ratio_x, ratio_y = SIT_BUTTON_POSITION
    x = round(SCREEN_RES["width"] * ratio_x)
    y = round(SCREEN_RES["height"] * ratio_y)
    ACFG.moveMouseAbsolute(x=x, y=y)
    ACFG.left_click()

    # Send message
    ACFG.send_message(f"[{random.choice(comedy_phrases)}]")

    # Manual Unsit
    sleep(5)
    ACFG.jump()
    ACFG.resetMouse()

    # End of navigation
    log_process("")
    log("")


def comedy_spawn_to_comedy_machine():
    log_process("AutoNav")
    log("Comedy Spawn -> Comedy Machine")
    ACFG.precision_look("right", 469, raw=True)
    ACFG.move("w", 0.25, raw=True)
    ACFG.move("d", 0.75, raw=True)
    _comedy_machine_arrived()


def _main_to_comedy_mountain():
    log_process("AutoNav")
    log("Calibration Rock -> Comedy Mountain")

    # Touch Yellow Pillar
    ACFG.move("s", 5.2, raw=True)

    # Use calibration point behind shop
    ACFG.move("d", 2.5, raw=True)
    ACFG.move("w", 1, raw=True)
    ACFG.move("d", 0.5, raw=True)

    # Get behind center of purple pillar
    ACFG.move("a", 2.05, raw=True)
    ACFG.move("s", 0.5, raw=True)

    # Get on top of center of far edge, short jump
    ACFG.leap(forward_time=0.2, jump_time=0.3, direction_key="s", jump_delay=0)

    # Running start to center of right edge, leap to yellow pillar
    ACFG.leap(
        forward_time=0.3,
        jump_time=0.35,
        direction_key="d",
        jump_delay=0.3,
        diagonal_direction_key="s",
    )

    # Leap to blue pillar
    ACFG.move("w", 0.1, raw=True)
    ACFG.leap(
        forward_time=0.05,
        jump_time=0.35,
        direction_key="d",
        jump_delay=0.25,
    )

    # Leap to rooftop
    ACFG.leap(
        forward_time=0.7,
        jump_time=0.5,
        direction_key="w",
        jump_delay=0.25,
    )

    # Leap to Comedy Mountain
    ACFG.move("d", 2, raw=True)
    ACFG.move("a", 0.5, raw=True)
    ACFG.leap(
        forward_time=0.7,
        jump_time=0.4,
        direction_key="d",
        jump_delay=0.25,
    )


def _comedy_mountain_to_comedy_machine():
    log_process("AutoNav")
    log("Comedy Mountain -> Comedy Machine")

    # Psuedo-calibrate
    ACFG.move("w", 0.5, raw=True)
    ACFG.move("d", 0.5, raw=True)
    ACFG.move("w", 0.5, raw=True)

    # Head to X
    ACFG.move("d", 0.5, raw=True)
    ACFG.move("a", 0.2, raw=True)
    ACFG.move("w", 0.5, raw=True)
    ACFG.move("d", 0.325, raw=True)
    _comedy_machine_arrived()


def main_to_comedy_machine():
    _main_to_comedy_mountain()
    _comedy_mountain_to_comedy_machine()


def _comedy_mountain_to_rocket_calib():
    log_process("AutoNav")
    log("Comedy Mountain -> Rocket Calibration Rock")
    # # Psuedo-calibrate
    ACFG.move("w", 0.5, raw=True)
    ACFG.move("d", 0.5, raw=True)
    ACFG.move("s", 0.5, raw=True)

    # Get to comedy mountain calibration rock
    ACFG.leap(forward_time=0.2, jump_time=0.3, direction_key="s", jump_delay=0)
    ACFG.move("a", 0.3, raw=True)
    ACFG.move("s", 1, raw=True)
    ACFG.move("d", 0.5, raw=True)
    ACFG.move("s", 0.5, raw=True)


def _comedy_spawn_to_rocket_calib():
    log_process("AutoNav")
    log("Comedy Spawn -> Rocket Calibration Rock")
    ACFG.precision_look("right", 469, raw=True)
    ACFG.move("s", 1, raw=True)

    # Get to comedy mountain calibration rock
    ACFG.leap(forward_time=0.2, jump_time=0.3, direction_key="s", jump_delay=0)
    ACFG.move("a", 0.2, raw=True)
    ACFG.move("s", 1, raw=True)
    ACFG.move("d", 0.5, raw=True)
    ACFG.move("s", 0.5, raw=True)


def _rocket_calib_to_rocket():
    log_process("AutoNav")
    log("Rocket Calibration Rock -> Rocket Tree")
    # Get to the top rock
    ACFG.leap(forward_time=0.2, jump_time=0.1, direction_key="s", jump_delay=0.05)
    ACFG.move("a", 0.1, raw=True)
    ACFG.move("s", 0.3, raw=True)
    ACFG.leap(forward_time=0.1, jump_time=0.3, direction_key="s", jump_delay=0)

    # Leap to first tree
    ACFG.leap(forward_time=0.4, jump_time=0.5, direction_key="s", jump_delay=0.0)

    # Leap to second tree
    ACFG.leap(forward_time=0.3, jump_time=0.5, direction_key="d", jump_delay=0.3)

    # Pickup the rocket launcher
    # ACFG.move("s", 0.3, raw=True)
    # ACFG.zoom("i", 50)
    # sleep(0.5)
    # ratio_x, ratio_y = (0.56, 0.64)
    # x = round(SCREEN_RES["width"] * ratio_x)
    # y = round(SCREEN_RES["height"] * ratio_y)
    # ACFG.moveMouseAbsolute(x=x, y=y)
    # ACFG.left_click()

    # Open Backpack
    # sleep(0.25)
    # ratio_x, ratio_y = BACKPACK_BUTTON_POSITION
    # x = round(SCREEN_RES["width"] * ratio_x)
    # y = round(SCREEN_RES["height"] * ratio_y)
    # ACFG.moveMouseAbsolute(x=x, y=y)
    # ACFG.left_click()

    # Equip
    # sleep(0.25)
    # item_x = int(SCREEN_RES["width"] * BACKPACK_ITEM_POSITIONS[1]["x"])
    # item_y = int(SCREEN_RES["height"] * BACKPACK_ITEM_POSITIONS[1]["y"])
    # ACFG.moveMouseAbsolute(x=item_x, y=item_y)
    # ACFG.left_click()

    # Reset zoom
    # sleep(0.25)
    # ACFG.zoom("o", ZOOM_FIRST_PERSON)

    # Face towards the camera
    ACFG.precision_look("left", 1798, raw=True)
    ACFG.zoom("i", ZOOM_FIRST_PERSON)
    ACFG.zoom("o", ZOOM_FIRST_PERSON)
    ACFG.precision_look("left", 1798, raw=True)

    # End of navigation
    log_process("")
    log("")


def main_to_rocket():
    _main_to_comedy_mountain()
    _comedy_mountain_to_rocket_calib()
    _rocket_calib_to_rocket()


def comedy_spawn_to_rocket():
    _comedy_spawn_to_rocket_calib()
    _rocket_calib_to_rocket()
