import asyncio
import json
import traceback
from asyncio import create_task
from asyncio import sleep as async_sleep
from datetime import datetime
from enum import Enum
from os import getenv, system
from typing import Optional, Union

import aiohttp
from requests import get, post
from requests.exceptions import HTTPError
from twitchio import Chatter as TwitchChatter
from twitchio import Message as TwitchMessage
from twitchio.ext import commands, routines

import chat_whitelist
from chat_ocr import can_activate_ocr, do_chat_ocr
from config import ActionQueueItem, Twitch
from health import CFG, do_crash_check, get_hw_stats
from hw_stats import hw_update_loop, ws_init
from utilities import (
    discord_log,
    error_log,
    log,
    log_process,
    notify_admin,
    username_whitelist_request,
    whitelist_request,
)


class NameWhitelistRequest(Enum):
    NOT_ON_RECORD = 1
    NEEDS_MORE_MESSAGES = 2
    READY_TO_REQUEST = 3
    WHITELIST_REQUEST_SENT = 4


class TwitchBot(commands.Bot):
    def __init__(self, token: str, channel_name: str):
        self.aiohttp_client_session = aiohttp.ClientSession()
        super().__init__(token=token, prefix="!", initial_channels=[channel_name])

    async def event_ready(self):
        print(f'[Twitch] Logged in as "{self.nick}"')
        await CFG.async_main()
        await self.run_subroutines()
        await asyncio.gather(ws_init(), hw_update_loop())

    async def event_message(self, message: TwitchMessage):
        if message.echo:
            return

        # Log message
        log_task = create_task(self.do_discord_log(message))
        try:
            await log_task
        except Exception:
            print(traceback.format_exc())
            notify_admin(f"```{traceback.format_exc()}```")

        # Send a greeting + help message if new user
        if await self.is_new_user(message.author.name):
            new_user_msg = CFG.new_user_msg.format(user_mention=message.author.mention)
            await message.channel.send(new_user_msg)
            await message.channel.send(CFG.help_msg)

            if message.content.lower().startswith("!help"):
                # Do not process the command: Help is sent if they're first-time chatters
                return

        # Execute task
        commands_task = create_task(self.handle_commands(message))
        try:
            await commands_task
        except commands.errors.CommandNotFound:
            pass
        except Exception:
            print(traceback.format_exc())
            notify_admin(f"```{traceback.format_exc()}```")

    async def event_command_error(self, ctx: commands.Context, error: Exception):
        if type(error) == commands.errors.CommandNotFound:
            await ctx.send("[Not a valid command!]")
            return
        print(f'"{type(error)}"')
        print(f'"{commands.errors.CommandNotFound}"')
        traceback.print_exception(type(error), error, error.__traceback__)
        error_log(f"({type(error)})\n{error}\n{error.__traceback__}")

    async def is_new_user(self, username):
        username = username.lower()
        if username in CFG.twitch_chatters:
            return False
        CFG.twitch_chatters.add(username)
        with open(CFG.twitch_chatters_path, "w") as f:
            json.dump(list(CFG.twitch_chatters), f)
        return True

    async def username_whitelist_requested(self, username):
        username = username.lower()
        min_to_req_whitelist = 2
        if username in CFG.twitch_username_whitelist_requested:
            return NameWhitelistRequest.WHITELIST_REQUEST_SENT
        elif username not in CFG.twitch_username_whitelist_requested_pre:
            # Only trigger a whitelist req if they send more than one message in a session
            # (But say a whitelist req was made on the first message)
            CFG.twitch_username_whitelist_requested_pre[username] = 1
            return NameWhitelistRequest.NOT_ON_RECORD
        elif (
            CFG.twitch_username_whitelist_requested_pre[username] + 1
            < min_to_req_whitelist
        ):
            # Havent reached the desired amount to send a whitelist req
            # Currently this code is redundant until the number is raised
            amount = CFG.twitch_username_whitelist_requested_pre[username] + 1
            CFG.twitch_username_whitelist_requested_pre[username] = amount
            return NameWhitelistRequest.NEEDS_MORE_MESSAGES

        CFG.twitch_username_whitelist_requested.add(username)
        with open(CFG.twitch_username_whitelist_requested_path, "w") as f:
            json.dump(list(CFG.twitch_username_whitelist_requested), f)
        return NameWhitelistRequest.READY_TO_REQUEST

    async def do_discord_log(self, message: TwitchMessage, is_chat=False):
        author = message.author.display_name
        author_url = f"https://twitch.tv/popout/{getenv('TWITCH_CHAT_CHANNEL')}/viewercard/{author.lower()}"
        author_avatar = "https://brand.twitch.tv/assets/images/black.png"
        message = message.content
        if is_chat:
            message = message.replace("!m ", "", 1)
        await discord_log(message, author, author_avatar, author_url, is_chat)

    async def get_args(self, ctx: commands.Context):
        msg = ctx.message.content
        prefix = ctx.prefix
        command_name = ctx.command.name
        return msg.replace(f"{prefix}{command_name}", "", 1).strip().split()

    async def is_dev(self, author: TwitchChatter):
        return author.name.lower() in Twitch.admins

    async def run_subroutines(self):
        print("[Twitch] Initializing Subroutines")
        subroutines = [
            routine_anti_afk,
            routine_check_better_server,
            routine_crash_check,
            routine_reboot,
            routine_ocr,
            routine_monitor_game_updates,
        ]
        for subroutine in subroutines:
            print(
                f"[Routine] Starting subroutine: {subroutine._coro.__name__.replace('routine_','')}"
            )
            subroutine.start()

    # Basic Commands

    @commands.command()
    async def help(self, ctx: commands.Context):
        await ctx.send(CFG.help_msg)

    @commands.command()
    async def backpack(self, ctx: commands.Context):
        await ctx.send(
            f"[{'Closing' if CFG.backpack_open else 'Opening'} backpack,"
            " please make sure it's closed when you're done!]"
        )
        await CFG.add_action_queue(ActionQueueItem("backpack_toggle"))

    @commands.command()
    async def click(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("mouse_click"))

    @commands.command()
    async def grief(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("grief"))

    @commands.command()
    async def hidemouse(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("mouse_hide"))

    @commands.command()
    async def item(self, ctx: commands.Context):
        args = await self.get_args(ctx)
        if len(args) < 1:
            await ctx.send("[Please specify an item number! (Must be 1-8)")
            return
        try:
            item_number = int(args[0])
            if item_number not in CFG.backpack_item_positions:
                raise
        except Exception:
            await ctx.send("[Error! Invalid number specified. (Must be 1-8)]")
            return
        if not CFG.backpack_open:
            await ctx.send(
                "[Doesn't seem like the backpack is open! Clicking anyway, just in case."
                "(Use !backpack to open, if needed)]"
            )
        action = ActionQueueItem("backpack_item", {"item_number": item_number})
        await CFG.add_action_queue(action)

    @commands.command()
    async def jump(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("jump"))

    @commands.command()
    async def mute(self, ctx: commands.Context):
        action = ActionQueueItem("mute", {"set_muted": None})
        await CFG.add_action_queue(action)

    @commands.command()
    async def mouse(self, ctx: commands.Context):
        args = await self.get_args(ctx)
        if len(args) < 2:
            await ctx.send(
                "[Please specify the two numbers (x and y) that you want the mouse to"
                " move away from center of the screen!]"
            )
            return
        try:
            x = int(args[0])
            y = int(args[1])
        except Exception:
            await ctx.send("[Error! Invalid number(s) specified.]")
            return
        action = ActionQueueItem("mouse_move", {"x": x, "y": y, "twitch_ctx": ctx})
        await CFG.add_action_queue(action)

    @commands.command()
    async def unmute(self, ctx: commands.Context):
        action = ActionQueueItem("mute", {"set_muted": False})
        await CFG.add_action_queue(action)

    @commands.command()
    async def respawnforce(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("respawn_force"))

    @commands.command()
    async def respawn(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("respawn"))

    @commands.command()
    async def sit(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("sit"))

    async def _stoptaunt(self, ctx: commands.Context):
        await ctx.send(
            "If this opened a menu, please run the command again to close it!"
        )
        await CFG.add_action_queue(ActionQueueItem("stoptaunt"))

    @commands.command()
    async def stoptaunt(self, ctx: commands.Context):
        await self._stoptaunt(ctx)

    @commands.command()
    async def tauntstop(self, ctx: commands.Context):
        await self._stoptaunt(ctx)

    @commands.command()
    async def canceltaunt(self, ctx: commands.Context):
        await self._stoptaunt(ctx)

    @commands.command()
    async def tauntcancel(self, ctx: commands.Context):
        await self._stoptaunt(ctx)

    @commands.command()
    async def use(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("use"))

    # Complex commands/Commands with args
    async def camera_pitch_handler(
        self, pitch_camera_direction: str, ctx: commands.Context
    ):
        pitch: float = 45
        max_pitch: float = 180
        args = await self.get_args(ctx)
        if args:
            try:
                pitch = float(args[0])
                if not (max_pitch >= pitch > 0):
                    await ctx.send(
                        f"[{args[0]} is too high/low! Please use an angle between 0 and {max_pitch}.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return

        action = ActionQueueItem(
            "camera_pitch",
            {
                "pitch_direction": pitch_camera_direction,
                "pitch_degrees": pitch,
            },
        )
        await CFG.add_action_queue(action)

    # Complex commands/Commands with args
    async def camera_turn_handler(
        self, turn_camera_direction: str, ctx: commands.Context
    ):
        turn_degrees: float = 45
        max_turn_degrees: float = 360
        args = await self.get_args(ctx)
        if args:
            try:
                turn_degrees = float(args[0])
                if not (max_turn_degrees >= turn_degrees > 0):
                    await ctx.send(
                        f"[{args[0]} is too high/low! Please use an angle between 0 and 360.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return

        action = ActionQueueItem(
            "camera_turn",
            {
                "turn_direction": turn_camera_direction,
                "turn_degrees": turn_degrees,
            },
        )
        await CFG.add_action_queue(action)

    async def precision_camera_turn_handler(
        self, turn_camera_direction: str, ctx: commands.Context
    ):
        turn_degrees: float = 45
        max_turn_degrees: float = 360
        args = await self.get_args(ctx)
        if args:
            try:
                turn_degrees = float(args[0])
                if not (max_turn_degrees >= turn_degrees > 0):
                    await ctx.send(
                        f"[{args[0]} is too high/low! Please use an angle between 0 and 360.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return

        action = ActionQueueItem(
            "precision_camera_turn",
            {
                "turn_direction": turn_camera_direction,
                "turn_degrees": turn_degrees,
            },
        )
        await CFG.add_action_queue(action)

    @commands.command()
    async def left(self, ctx: commands.Context):
        turn_camera_direction = "left"
        await self.camera_turn_handler(turn_camera_direction, ctx)

    @commands.command()
    async def right(self, ctx: commands.Context):
        turn_camera_direction = "right"
        await self.camera_turn_handler(turn_camera_direction, ctx)

    @commands.command()
    async def pleft(self, ctx: commands.Context):
        turn_camera_direction = "left"
        await self.precision_camera_turn_handler(turn_camera_direction, ctx)

    @commands.command()
    async def pright(self, ctx: commands.Context):
        turn_camera_direction = "right"
        await self.precision_camera_turn_handler(turn_camera_direction, ctx)

    @commands.command()
    async def up(self, ctx: commands.Context):
        pitch_camera_direction = "up"
        await self.camera_pitch_handler(pitch_camera_direction, ctx)

    @commands.command()
    async def down(self, ctx: commands.Context):
        pitch_camera_direction = "down"
        await self.camera_pitch_handler(pitch_camera_direction, ctx)

    @commands.command()
    async def dev(self, ctx: commands.Context):
        args = await self.get_args(ctx)
        if not args:
            await ctx.send(
                "[Specify a message, this command is for emergencies! (Please do not misuse it)]"
            )
            return
        msg = " ".join(args)
        notify_admin(f"{ctx.message.author.display_name}: {msg}")
        await ctx.send(
            "[Notified dev! As a reminder, this command is only for emergencies. If you were unaware of this and used"
            " the command by mistake, please write a message explaining that or you may be timed-out/banned.]"
        )

    @commands.command()
    async def leap(self, ctx: commands.Context):
        forward_time = 0.4
        jump_time = 0.3
        max_forward_time = 1
        max_jump_time = 1
        args = await self.get_args(ctx)
        if len(args) > 0:
            try:
                number = float(args[0])
                if max_forward_time >= number > 0:
                    forward_time = number
                else:
                    await ctx.send(
                        f"[{args[0]} is too high/low! Please use a time between 0 and {max_forward_time}.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return
        if len(args) > 1:
            try:
                number = float(args[1])
                if max_jump_time >= number > 0:
                    jump_time = number
                else:
                    await ctx.send(
                        f"[{args[1]} is too high/low! Please use a time between 0 and {max_jump_time}.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return
        action = ActionQueueItem(
            "leap",
            {"forward_time": forward_time, "jump_time": jump_time},
        )
        await CFG.add_action_queue(action)

    async def old_m(self, ctx: commands.Context, msg: str) -> Optional[ActionQueueItem]:
        """
        Old messaging logic when using onboard censor. Retained for emergency usage on launch.
        """

        nickname = CFG.chat_nicknames.val.get(ctx.message.author.display_name)
        # Chat with CamDev Tag
        if ctx.message.author.display_name == getenv("TWITCH_CHAT_CHANNEL"):
            action = ActionQueueItem(
                "chat_with_name", {"name": "[CamDev]:", "msgs": [msg]}
            )
        # Non-trusted chat (whitelist only)
        elif not chat_whitelist.user_is_trusted(CFG, ctx.message.author.display_name):
            original_name = ctx.message.author.display_name
            real_or_temp_name = nickname or original_name
            if (
                not chat_whitelist.username_in_whitelist(CFG, original_name)
                and not nickname
            ):
                real_or_temp_name = chat_whitelist.get_random_name(CFG, original_name)
                whitelist_requested_status = await self.username_whitelist_requested(
                    original_name.lower()
                )
                if whitelist_requested_status == NameWhitelistRequest.NOT_ON_RECORD:
                    await ctx.send(
                        f"[Assigning random username '{real_or_temp_name}'. Your real username "
                        f"'{original_name}' is pending approval.]"
                    )
                elif (
                    whitelist_requested_status == NameWhitelistRequest.READY_TO_REQUEST
                ):
                    # Only send the request after a certain amount of messages, most users do not stick around
                    username_whitelist_request(msg, original_name)

            blacklisted_words = []
            for word in msg.encode("ascii", "ignore").decode("ascii").split(" "):
                if chat_whitelist.word_in_blacklist(CFG, word):
                    blacklisted_words.append(word)

            if blacklisted_words:
                await ctx.send(
                    "[You've attempted to send a message with blacklisted words ("
                    f"{', '.join(blacklisted_words)}). The dev has been notified.]"
                )
                notify_admin(
                    f"[BLACKLIST ALERT]\nUser: `{original_name}`\nMessage: {msg}\n"
                    f"Blacklisted Words: `{', '.join(blacklisted_words)}`\n"
                    f"<https://twitch.tv/popout/{getenv('TWITCH_CHAT_CHANNEL')}/viewercard/{original_name.lower()}>"
                )
                return None

            censored_words, censored_message = chat_whitelist.get_censored_string(
                CFG, msg
            )

            if censored_words:
                await ctx.send(
                    f"[Some words you used are not in the whitelist for new users and have been sent for "
                    f"approval ({', '.join(censored_words)})]"
                )

            if censored_words:
                whitelist_request(censored_words, msg, original_name)

            action = ActionQueueItem(
                "chat_with_name",
                {
                    "name": f"{real_or_temp_name}:",
                    "msgs": [censored_message],
                },
            )

        # Standard ("Trusted") chat
        else:
            action = ActionQueueItem(
                "chat_with_name",
                {
                    "name": f"{nickname or ctx.message.author.display_name}:",
                    "msgs": [msg],
                },
            )

        return action

    async def new_m(self, ctx: commands.Context, msg: str) -> Optional[ActionQueueItem]:
        """
        New message logic that uses Censor Service.
        """

        data = {
            "username": ctx.message.author.display_name,
            "message": msg,
        }
        async with self.aiohttp_client_session.post(
            "http://127.0.0.1:8086/request_censored_message",
            json=data,
            raise_for_status=True,
        ) as resp:
            censor_response = await resp.json()

        # {
        #     "username": "some_username",
        #     "message": "test message with random word (dfgdsfgdsfvds)",
        #     "bot_reply_message": [],
        #     "send_users_message": true,
        # }
        for message in censor_response["bot_reply_message"]:
            await ctx.send(message)

        if not censor_response["send_users_message"]:
            return None

        return ActionQueueItem(
            "chat_with_name",
            {
                "name": f"{censor_response['username']}:",
                "msgs": [censor_response["message"]],
            },
        )

    @commands.command()  # Send message in-game
    async def m(self, ctx: commands.Context):
        args = await self.get_args(ctx)
        if not args:
            await ctx.send('[Please specify a message! (i.e. "!m Hello World!"]')
            return

        msg = " ".join(args)
        if len(msg) > 100:
            await ctx.send(
                "[In-game character limit is 100! Please shorten your message.]"
            )
            return
        is_dev = await self.is_dev(ctx.message.author)

        # Disable whisper functionality
        if msg.startswith("[") or msg.startswith("/w"):
            await ctx.send("[You do not have permission to whisper.]")
            return

        # Make muting dev-only
        elif msg.startswith("/mute") or msg.startswith("/unmute"):
            if is_dev:
                action = ActionQueueItem("chat", {"msgs": [msg]})
            else:
                await ctx.send("[You do not have permission to mute/unmute.]")
                return

        # Allow /e, disable all other commands from twitch
        elif msg.startswith("/"):
            if msg.startswith("/e"):
                action = ActionQueueItem("chat", {"msgs": [msg]})
            else:
                return
        else:
            try:
                potential_action = await self.new_m(ctx, msg)
                if potential_action is None:
                    return
                action = potential_action  # HACK: MyPy can be weird
            except Exception as e:
                error_msg = f"Censor Service Client Failure\n{e}"
                error_log(error_msg, do_print=True)
                await ctx.send(
                    "[Something went wrong, can't send a message. Contacting dev...]"
                )
                notify_admin(error_msg)
                return

        await self.do_discord_log(ctx.message, is_chat=True)
        await CFG.add_action_queue(action)

    @commands.command()  # Send announcement in-game
    async def a(self, ctx: commands.Context):
        is_dev = await self.is_dev(ctx.message.author)
        if not is_dev:
            await ctx.send("[You do not have permission to announce.]")
            return

        args = await self.get_args(ctx)
        if not args:
            await ctx.send('[Please specify a message! (i.e. "!a Hello World!"]')
            return

        msg = " ".join(args)
        msg = msg.capitalize()
        if len(msg) > 100:
            await ctx.send(
                "[In-game character limit is 100! Please shorten your message.]"
            )
            return

        await self.do_discord_log(ctx.message)

        action = ActionQueueItem("chat", {"msgs": [f"[{msg}]"]})
        await CFG.add_action_queue(action)

    @commands.command()
    async def move(self, ctx: commands.Context):
        move_time: float = 1
        max_move_time: float = 10
        valid_movement_keys = ["w", "a", "s", "d"]
        args = await self.get_args(ctx)
        if not args or args[0].lower() not in valid_movement_keys:
            await ctx.send('[Please specify a valid direction! (i.e. "!move w")]')
            return
        move_key = args[0].lower()

        if len(args) > 1:
            try:
                move_time = float(args[1])
                if not (max_move_time >= move_time > 0):
                    await ctx.send(
                        f"[{args[1]} is too high/low! Please use a unit between 0 and {max_move_time}.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return

        action = ActionQueueItem("move", {"move_key": move_key, "move_time": move_time})
        await CFG.add_action_queue(action)

    @commands.command()
    async def nav(self, ctx: commands.Context):
        args = await self.get_args(ctx)
        if not args or args[0].lower() not in CFG.nav_locations:
            await ctx.send("[Please specify a valid location!]")
            await ctx.send(f'[{", ".join(list(CFG.nav_locations.keys()))}]')
            return
        location = args[0].lower()
        if location == "treehouse":
            await ctx.send(
                "Sorry, Treehouse autonav no longer works! The game was updated and the terrain is too user-hostile to "
                "navigate there."
            )
            await ctx.send(
                "If you want to help, reach out to https://twitter.com/@OkuechiRblx and ask him to fix the treehouse "
                "path."
            )
            return

        await ctx.send("[Requested AutoNav! If we fail, re-run the command!]")
        await ctx.send(
            "[If we did not respawn, please run !respawnforce (we're stuck!) and re-run the !nav command.]"
        )
        action = ActionQueueItem("autonav", {"location": location})
        await CFG.add_action_queue(action)

    @commands.command()
    async def rejoin(self, ctx: commands.Context):
        if await self.is_dev(ctx.author):
            await ctx.send(f"[@{ctx.author.name} Added restart to queue]")
            CFG.crashed = True
            await CFG.add_action_queue(ActionQueueItem("rejoin"))
            CFG.crashed = False
        else:
            await ctx.send("[You do not have permission!]")

    @commands.command()
    async def whitelist(self, ctx: commands.Context):
        if not await self.is_dev(ctx.author):
            await ctx.send("[You do not have permission!]")
            return

        args = await self.get_args(ctx)
        if not args:
            await ctx.send("[Specify a word to whitelist!]")
            return
        before = len(CFG.chat_whitelist_datasets["custom"])

        word_to_whitelist = args[0].lower()

        CFG.chat_whitelist_datasets["custom"].add(word_to_whitelist)
        with open(CFG.chat_whitelist_dataset_paths["custom"], "w") as f:
            json.dump(sorted(CFG.chat_whitelist_datasets["custom"]), f, indent=2)

        after = len(CFG.chat_whitelist_datasets["custom"])  # Sanity Check

        await ctx.send(
            f"[Added '{word_to_whitelist}' to whitelist! ({before}->{after})]"
        )

        return False

    @commands.command()
    async def userwhitelist(self, ctx: commands.Context):
        if not await self.is_dev(ctx.author):
            await ctx.send("[You do not have permission!]")
            return

        args = await self.get_args(ctx)
        if not args:
            await ctx.send("[Specify a username to whitelist!]")
            return
        before = len(CFG.chat_whitelist_datasets["usernames"])

        word_to_whitelist = args[0].lower()

        CFG.chat_whitelist_datasets["usernames"].add(word_to_whitelist)
        with open(CFG.chat_whitelist_dataset_paths["usernames"], "w") as f:
            json.dump(
                sorted(CFG.chat_whitelist_datasets["usernames"]),
                f,
                indent=2,
            )

        after = len(CFG.chat_whitelist_datasets["usernames"])  # Sanity Check

        await ctx.send(
            f"[Added '{word_to_whitelist}' to username whitelist! ({before}->{after})]"
        )

        return False

    async def zoom_handler(self, zoom_key, ctx: commands.Context):
        zoom_amount: float = 15
        max_zoom_amount: float = 100
        args = await self.get_args(ctx)
        if args:
            try:
                zoom_amount = float(args[0])
                if not (max_zoom_amount >= zoom_amount > 0):
                    await ctx.send(
                        f"[{args[0]} is too high/low! Please use a percentage between 0 and {max_zoom_amount}.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return
        action = ActionQueueItem(
            "camera_zoom",
            {"zoom_key": zoom_key, "zoom_amount": zoom_amount},
        )
        await CFG.add_action_queue(action)

    @commands.command()
    async def zoomin(self, ctx: commands.Context):
        zoom_key = "i"
        await self.zoom_handler(zoom_key, ctx)

    @commands.command()
    async def zoomout(self, ctx: commands.Context):
        zoom_key = "o"
        await self.zoom_handler(zoom_key, ctx)

    @commands.command()
    async def fixbright(self, ctx: commands.Context):
        await ctx.send("[Trying to navigate to the portal and back out again!]")
        await ctx.send("[If it didnt work, re-run the command or use !dev!]")
        action = ActionQueueItem("autonav", {"location": "fixbright"})
        await CFG.add_action_queue(action)


@routines.routine(minutes=10, wait_first=True)
async def routine_anti_afk():
    print("[Subroutine] AntiAFK")
    try:
        await CFG.add_action_queue(ActionQueueItem("anti_afk"))
        CFG.anti_afk_runs += 1
        if CFG.anti_afk_runs % 3 == 0:
            await CFG.add_action_queue(ActionQueueItem("chat", {"msgs": ["/clear"]}))
            await CFG.add_action_queue(ActionQueueItem("advert"))
            print("[Subroutine] Queued Advert")
            CFG.anti_afk_runs = 0
    except Exception:
        error_log(traceback.format_exc())


@routines.routine(minutes=2)
async def routine_check_better_server():
    print("[Subroutine] Better Server Check")
    try:
        while CFG.crashed:
            print("[Better Server Check] Currently crashed, waiting...")
            await async_sleep(60)
        await CFG.add_action_queue(ActionQueueItem("check_for_better_server"))
    except Exception:
        error_log(traceback.format_exc())


@routines.routine(seconds=1)
async def routine_hw_stats():
    await get_hw_stats()


@routines.routine(seconds=1, wait_first=True)
async def routine_unstuck_queue():
    # This is a bad solution
    await CFG.do_process_queue()


@routines.routine(seconds=3, wait_first=True)
async def routine_ocr():
    if (
        CFG.action_running
        or CFG.crashed
        or (not CFG.chat_cleared_after_response)
        or (not CFG.chat_ocr_ready)
    ):
        return

    if not CFG.chat_ocr_active:
        if not CFG.chat_ocr_activation_queued and await can_activate_ocr():
            await CFG.add_action_queue(ActionQueueItem("activate_ocr"))
    else:
        try:
            # HACK: psuedo-blocking, make non-async
            CFG.chat_ocr_ready = False
            await do_chat_ocr()
        except Exception:
            CFG.chat_ocr_ready = True
            CFG.chat_cleared_after_response = True
            error_log(traceback.format_exc())


@routines.routine(time=datetime(year=1970, month=1, day=1, hour=3, minute=58))
async def routine_reboot():
    action_queue_item = ActionQueueItem(
        "chat", {"msgs": ["[System restart in 2 minutes]"]}
    )
    await CFG.add_action_queue(action_queue_item)
    await async_sleep(60)

    action_queue_item = ActionQueueItem(
        "chat", {"msgs": ["[System restart in 1 minute]"]}
    )
    await CFG.add_action_queue(action_queue_item)
    await async_sleep(60)

    log_process("System Shutdown")
    log("Initiating shutdown sequence")
    action_queue_item = ActionQueueItem("chat", {"msgs": ["[System restarting]"]})
    await CFG.add_action_queue(action_queue_item)
    await async_sleep(10)
    system("shutdown /f /r /t 0")  # nosec


@routines.routine(seconds=5, wait_first=True)
async def routine_crash_check():
    if CFG.crashed:
        return
    try:
        crashed = await do_crash_check()
        if crashed:
            print("[Routine] Crash detected")
            await CFG.add_action_queue(ActionQueueItem("handle_crash"))
            await async_sleep(60)
    except Exception:
        error_log(traceback.format_exc())


def get_gamemode_update_timestamp() -> Union[None, str]:
    """
    Queries the Roblox API for the gamemode, returns latest-update timestamp
    """
    UNIVERSE_ID = 2291704236
    API_URL = "https://games.roblox.com/v1/games"
    try:
        response = get(API_URL, params={"universeIds": [UNIVERSE_ID]}, timeout=10)
    except Exception:
        print("[Could not poll for game updates, servers may be down]")
        error_log(traceback.format_exc())
        return None

    if response.status_code == 200:
        response_result = response.json()
        data = response_result.get("data", [{}])[0]
        if "updated" in data:
            timestamp = data["updated"]
            # HACK: timestamp suffix can vary for no reason
            # https://i.imgur.com/jEPZWKz.png
            truncated_timestamp = timestamp.rsplit(".", 1)[0]
            return truncated_timestamp

    try:
        readable_response = json.dumps(json.loads(response.text), indent=4)
    except Exception:
        readable_response = response.text

    error_log(f"[Error, bad response]\n{readable_response}", do_print=True)
    return None


@routines.routine(seconds=30)
async def routine_monitor_game_updates():
    """
    Monitors updates to the gamemode and notifies if a new update has happened
    """
    print("[Checking for game updates]")
    last_update = get_gamemode_update_timestamp()
    if last_update is None or CFG.game_update_timestamp == last_update:
        # API failed or the game hasn't been updated, so we don't care
        print("[No game updates found]")
        return

    CFG.game_update_timestamp = last_update
    with open(CFG.game_update_file, "w") as f:
        json.dump(CFG.game_update_timestamp, f)

    webhook_url = getenv("DISCORD_WEBHOOK_UPDATES_CHANNEL")
    webhook_data = {"content": f"**__Update detected__**\n{last_update}"}
    result = post(webhook_url, json=webhook_data)
    try:
        result.raise_for_status()
    except HTTPError as err:
        print(err)
    else:
        print("[Update notification sent]")


def twitch_main():
    token = getenv("TWITCH_BOT_TOKEN")
    channel = Twitch.channel_name
    bot = TwitchBot(token, channel)
    bot.run()


if __name__ == "__main__":  # Not supposed to run directly, but can be
    twitch_main()
