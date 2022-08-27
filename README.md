# About

A 24/7, interactive, in-game Twitch bot that has run for over a year, amassing 5,000+ followers by itself.

Due to targeted report spam, and Twitch not reviewing appeals, it now streams to a second channel, to avoid the first being permanantly deleted (along with historical clips). 

Original Channel: https://twitch.tv/becomefumocam

# Writeup

A semi-technical "intro" exists, but there has been too many drastic additions and removals of functionality since it was created to have an accurate, formal writeup.

***So, want to know why I made a bot for a game I dont play about a fandom I don't follow?***

< HISTORICALLY_REDACTED >

# Other Notes
## Installation
[A guide can be found in INSTRUCTIONS.md](INSTRUCTIONS.md), but its a rough guide that may change, and may not be easy to follow.


## Deprecated Software-Driven Input

This has always been a project that aims to replicate a human as mechanically and programmatically as possible. Due to how the Windows scheduler works, there is no software that can be written, in any language, that adequately supports consistent input (for example, `!move w 1` always moving the exact same amount, no error margin).

Linux could see negligible error margins, but still believed to have _some_ error margin.

Due to this, all precision keyboard and mouse input has been offloaded to an Arduino Leonardo that can receive a payload, emulate HID Keyboard + Mouse natively (no hacky workarounds), and have consistent timing due to the nature of how close-to-metal the code is running (in addition, is not tethered to any OS scheduler but directly to CPU clock).

Obviously, this requires external hardware (Arduino Leonardo) that not everyone can get. You can view the old code that used software-driven input emulation on the [pre-arduino branch](https://github.com/<HISTORICALLY_REDACTED>).

## Deprecated Exploit Functionality

Older commands like teleportation required the use of a third party Lua injector is required (alongside some code).

This led to system instability, was challenging to develop around, and was ultimately a crutch to the final goal, so it was deprecated.

You can view the old code that still supported injector commands on the [injector support branch](https://github.com/<HISTORICALLY_REDACTED>).

In addition, it needs the injector module (No longer functional) to be extracted into the project at the "resources/injector" path. You can find the injector here: < HISTORICALLY REDACTED >
