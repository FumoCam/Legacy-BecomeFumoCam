# FumoCam

A 24/7, interactive, in-game Twitch bot ran for over a year, amassing 5,000+ followers by itself.

Due to targeted attacks and Twitch staff not reviewing appeals/allowing fake reports, it no longer streams on the original channel.

Original Channel: https://twitch.tv/becomefumocam

# Writeup

There has been too many drastic additions and removals of functionality since it was created to have an accurate, formal writeup.

However, a semi-technical "intro" exists.

Want to know why I made a bot for a game I dont play about a fandom I don't follow?

< HISTORICALLY_REDACTED >

# Tesseract Data

Download the "tessdata_best" for Tesseract and replace your "tessdata" folder where you installed Tesseract (i.e. Program Files).

https://github.com/tesseract-ocr/tessdata_best

# Deprecated Software-Driven Input

This has always been a project that aims to replicate a human as mechanically and programmatically as possible. Due to how the Windows scheduler works, there is no software that can be written, in any language, that adequately supports consistent input (for example, `!move w 1` always moving the exact same amount, no error margin).

Linux could see negligible error margins, but still believed to have _some_ error margin.

Due to this, all precision keyboard and mouse input has been offloaded to an Arduino Leonardo that can receive a payload, emulate HID Keyboard + Mouse natively (no hacky workarounds), and have consistent timing due to the nature of how close-to-metal the code is running (in addition, is not tethered to any OS scheduler but directly to CPU clock).

Obviously, this requires external hardware (Arduino Leonardo) that not everyone can get. You can view the old code that used software-driven input emulation on the [pre-arduino branch](https://github.com/<HISTORICALLY_REDACTED>).

# Deprecated Exploit Functionality

For advanced commands like teleportation, use of a third party Lua injector is required (alongside some code).

This can lead to system instability and is challenging to develop around, so it has been deprecated.

You can view the old code that still supported injector commands on the [injector support branch](https://github.com/<HISTORICALLY_REDACTED>).

In addition, it needs the injector module to be extracted into the project at the "resources/injector" path. You can find the injector here: < HISTORICALLY REDACTED >
