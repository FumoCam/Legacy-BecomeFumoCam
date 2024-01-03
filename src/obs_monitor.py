import asyncio
import base64
import hashlib
import json
import os
import uuid
from time import strftime
from traceback import format_exc
from typing import Any, Dict

import requests
import websockets.client
from dotenv import load_dotenv

from utilities import error_log

# https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md


# Dotenv
load_dotenv()
DISCORD_WEBHOOK_DEV_CHANNEL = os.getenv("DISCORD_WEBHOOK_DEV_CHANNEL")
if DISCORD_WEBHOOK_DEV_CHANNEL is None:
    raise Exception("DISCORD_WEBHOOK_DEV_CHANNEL not defined in .env")
OBS_WS_URL = os.getenv("OBS_WS_URL")
if OBS_WS_URL is None:
    raise Exception("OBS_WS_URL not defined in .env")
OBS_WS_PASSWORD = os.getenv("OBS_WS_PASSWORD")
if OBS_WS_PASSWORD is None:
    raise Exception("OBS_WS_PASSWORD not defined in .env")
DISCORD_OWNER_ID = os.getenv("DISCORD_OWNER_ID")
if DISCORD_OWNER_ID is None:
    raise Exception("DISCORD_OWNER_ID not defined in .env")

# Constants
INIT_ATTEMPTS = 10
START_STREAMING_POST_CHECK_DELAY_SECONDS = 10
INIT_ATTEMPT_DELAY_SECONDS = 5
MONITOR_CHECK_DELAY_SECONDS = 10
OBS_RPC_VERSION = 1

# Globals
started_streaming = False


def do_log(message: Any):
    timestamp = strftime("%Y-%m-%d %I:%M:%S%p EST")
    print(f"[{timestamp}]\n{message}\n\n")


async def obs_notify_admin(message):
    do_log(f"Attempting to notify admin on Discord with message:\n{message}\n\n")
    data = {"content": message}
    try:
        result = requests.post(DISCORD_WEBHOOK_DEV_CHANNEL, json=data, timeout=5)
        result.raise_for_status()
    except Exception:
        error_log(f"Error posting to Discord:\n{format_exc()}")
    else:
        print(f"[Dev Notified] {message}")


async def send_request(
    ws: websockets.client.WebSocketClientProtocol, request_type: str, **kwargs
) -> Dict:
    request = {
        "op": 6,  # Request Opcode
        "d": {
            "requestType": request_type,
            "requestId": f"obs_live_monitor_{uuid.uuid4()}",
            "requestData": kwargs,
        },
    }
    do_log(f"send_request\n{request}")
    await ws.send(json.dumps(request))
    return json.loads(await ws.recv())


async def check_streaming_status(ws: websockets.client.WebSocketClientProtocol) -> bool:
    response = await send_request(ws, "GetStreamStatus")
    do_log(f"GetStreamStatus\n{response}")
    data: Dict = response.get("d", {}).get("responseData", {})
    return data.get("outputActive", False)


async def start_streaming(ws: websockets.client.WebSocketClientProtocol):
    response = await send_request(ws, "StartStream")
    do_log(f"StartStream\n{response}")
    do_log("Waiting...")
    await asyncio.sleep(START_STREAMING_POST_CHECK_DELAY_SECONDS)
    is_streaming = await check_streaming_status(ws)
    return is_streaming


async def check_and_start_streaming(
    ws: websockets.client.WebSocketClientProtocol,
) -> bool:
    global started_streaming

    is_streaming = await check_streaming_status(ws)

    if is_streaming:
        do_log("Already livestreaming.")
        started_streaming = True
        return True
    else:
        if started_streaming:
            await obs_notify_admin(
                "OBS has stopped livestreaming. Attempting to go live..."
            )
        go_live_success = await start_streaming(ws)
        if go_live_success:
            if started_streaming:
                await obs_notify_admin("OBS has recovered and gone live again.")
            else:
                await obs_notify_admin(
                    "OBS was not live, but was able to force go-live."
                )
            started_streaming = True
            return True
        else:
            await obs_notify_admin("Failed to start stream.")

    return False


def compute_auth_response(password: str, salt: str, challenge: str) -> str:
    secret = base64.b64encode(
        hashlib.sha256((password + salt).encode("utf-8")).digest()
    )
    authentication_string = base64.b64encode(
        hashlib.sha256(secret + (challenge.encode("utf-8"))).digest()
    ).decode("utf-8")
    return authentication_string


async def authenticate(ws: websockets.client.WebSocketClientProtocol):
    hello_response: Dict = json.loads(await ws.recv())
    do_log(hello_response)

    auth_response: Dict = hello_response.get("d", {}).get("authentication", {})
    salt: str = str(auth_response.get("salt", ""))
    challenge: str = str(auth_response.get("challenge", ""))

    # Send Identify request with auth response
    assert isinstance(OBS_WS_PASSWORD, str)  # mypy is annoying
    auth_str = compute_auth_response(OBS_WS_PASSWORD, salt, challenge)
    identify_message = {
        "op": 1,
        "d": {
            "rpcVersion": OBS_RPC_VERSION,
            "authentication": auth_str,
            # No events, we only care about request/response
            "eventSubscriptions": 0,
        },
    }

    do_log(json.dumps(identify_message))
    await ws.send(json.dumps(identify_message))
    identify_response = json.loads(await ws.recv())
    do_log(identify_response)
    return identify_response["op"] == 2  # "Identified" opcode


async def main():
    do_log("Connecting to websocket...")
    global started_streaming
    async with websockets.client.connect(OBS_WS_URL) as ws:
        do_log("Connected.")
        # Authenticate
        do_log("Authenticating...")
        if not await authenticate(ws):
            raise Exception("Authentication failed")
        do_log("Authenticated.")

        # Initialize livestream
        do_log("Initializing livestream...")
        for attempt in range(INIT_ATTEMPTS):
            do_log(f"Initializing livestream attempt #{attempt+1}")
            await check_and_start_streaming(ws)
            if started_streaming:
                do_log("Initialized livestream.")
                break
            await asyncio.sleep(INIT_ATTEMPT_DELAY_SECONDS)
        else:
            await obs_notify_admin("Failed to start stream after 10 attempts.")

        # Monitor livestream
        do_log("Monitoring livestream.")
        checks = 0
        while True:
            await asyncio.sleep(MONITOR_CHECK_DELAY_SECONDS)
            await check_and_start_streaming(ws)
            checks += 1
            do_log(f"Check #{checks} complete.")


if __name__ == "__main__":
    try:
        do_log("Initializing OBS monitor...")
        asyncio.run(main())
    except Exception:
        error_msg = f"Unexpected error with OBS monitor:\n```\n{format_exc()}\n```"
        error_log(error_msg)
        asyncio.run(obs_notify_admin(error_msg))
