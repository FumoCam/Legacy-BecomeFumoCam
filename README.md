# A note about code quality

This version of the bot was built from patches upon hacky solutions upon more patches.

Architecture, good coding practices, and maintainability was the lowest priority during development.

A redesign is in progress.

# About

A 24/7, interactive, in-game Twitch bot that has run for over a year, amassing 5,000+ followers by itself.

Due to targeted report spam, and Twitch not reviewing appeals, it now streams to a second channel, to avoid the first being permanantly deleted (along with historical clips).

Original Channel: https://twitch.tv/becomefumocam

# Writeup

A semi-technical "intro" exists, but there has been too many drastic additions and removals of functionality since it was created to have an accurate, formal writeup.

**_So, want to know why I made a bot for a game I dont play about a fandom I don't follow?_**

[https://fumocam.xyz/day-0-fumocam-beginnings](https://fumocam.xyz/day-0-fumocam-beginnings)

# Installation

1. You will see README.md files in some of the resource folders with "Items not in version control".
   - You can find these in the private [Legacy-BecomeFumoCam-Other-Resources](https://github.com/FumoCam/Legacy-BecomeFumoCam-Other-Resources) repository.
   - If you do not have access, you can request it from me.
   - Alternatively, you can supply your own versions of the missing files, there is nothing remarkably unique.
2. You will see some OCR functions referring to an "`ai`" module.
   - This is a private, unshared repository located at [Legacy-BecomeFumoCam-AI](https://github.com/FumoCam/Legacy-BecomeFumoCam-AI).
   - This will not be shared. The code that utilizes it is stubabble, so write your own replacement or comment it out.
3. You will see a reference to "Censor Service" in message functions. You can rewrite the code to not use a censor, but otherwise you must install and configure:
   - [Whitelist-Censor-Client](https://github.com/FumoCam/Whitelist-Censor-Client), on the same machine
   - [Whitelist-Censor-Server](https://github.com/FumoCam/Whitelist-Censor-Server), ideally on a remote server
4. A setup guide can be found in [INSTRUCTIONS.md](INSTRUCTIONS.md)
   - Its a very verbose guide, and is only updated on system wipes.
   - It may not be easy to follow or be up to date.

# Other Notes

## Deprecated Software-Driven Input

This has always been a project that aims to replicate a human as mechanically and programmatically as possible. Due to how the Windows scheduler works, there is no software that can be written, in any language, that adequately supports consistent input (for example, `!move w 1` always moving the exact same amount, no error margin).

Linux could see negligible error margins, but still believed to have _some_ error margin.

Due to this, all precision keyboard and mouse input has been offloaded to an Arduino Leonardo that can receive a payload, emulate HID Keyboard + Mouse natively (no hacky workarounds), and have consistent timing due to the nature of how close-to-metal the code is running (in addition, is not tethered to any OS scheduler but directly to CPU clock).

Obviously, this requires external hardware (Arduino Leonardo) that not everyone can get. You can view the old code that used software-driven input emulation on the [pre-arduino tag](https://github.com/FumoCam/Legacy-BecomeFumoCam/releases/tag/no-arduino-movement).

## Deprecated Exploit Functionality

Older commands like teleportation required the use of a third party Lua injector is required (alongside some code).

This led to system instability, was challenging to develop around, and was ultimately a crutch to the final goal, so it was deprecated.

You can view the old code that still supported injector commands on the [injector support tag](https://github.com/FumoCam/Legacy-BecomeFumoCam/releases/tag/injector-support).

In addition, it needs the injector module (No longer functional) to be extracted into the project at the "resources/injector" path. You can find the injector here:

[https://github.com/FumoCam/Legacy-BecomeFumoCam-Injector](https://github.com/FumoCam/Legacy-BecomeFumoCam-Injector)
