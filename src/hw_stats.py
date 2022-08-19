import asyncio
import json
from enum import Enum
from typing import Dict, Tuple

import aiohttp
import websockets


class HUDMsgType(Enum):
    SYSTEM_MONITOR_UPDATE = "system_monitor_update"


class HUDManager:
    def __init__(self):
        self.connections = set()

    async def ws_handler(self, websocket):
        self.connections.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.connections.remove(websocket)

    def message_all(self, message):
        print(f"[WS] Sent: {message}")
        websockets.broadcast(self.connections, message)

    def message_all_silent(self, message):
        websockets.broadcast(self.connections, message)


hud_manager = HUDManager()


async def ws_init():
    async with websockets.serve(hud_manager.ws_handler, "127.0.0.1", 8080):
        await asyncio.Future()  # run forever


async def hw_get_server(url: str, session: aiohttp.ClientSession) -> Tuple[bool, Dict]:
    """
    Queries the local OpenHardwareMonitor reporting server.

    Returns a tuple of (success, response_dict)
    """
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return False, {}

            return True, await response.json()
    except Exception:
        return False, {}


async def hw_parse_data(data, valid_sensor_types, valid_sensor_values):
    relevant_data = {}
    parsing_complete = False
    computer = data.get("Children", [{}])[0]
    hardware_list = computer.get("Children", [{}])
    for hardware in hardware_list:
        hardware_sensors = hardware.get("Children", [{}])
        for sensor_type in hardware_sensors:
            sensor_type_label = sensor_type.get("Text")
            if sensor_type_label is None or sensor_type_label not in valid_sensor_types:
                continue

            sensor_list = sensor_type.get("Children", [{}])
            for sensor in sensor_list:
                sensor_label = valid_sensor_values.get(sensor.get("Text"))
                if sensor_label is not None:
                    sensor_value_str = sensor.get("Value")
                    try:
                        sensor_value = round(float(sensor_value_str.split(" ", 1)[0]))
                    except Exception:
                        sensor_value = "ERR"

                    relevant_data[sensor_label] = sensor_value
                    if len(relevant_data) == len(valid_sensor_values):
                        parsing_complete = True
                        break

            if parsing_complete:
                break

        if parsing_complete:
            break

    if len(relevant_data) != len(valid_sensor_values):
        for key in valid_sensor_values.values():
            if key not in relevant_data:
                print(f"[HW Parse] Missing {key}")
                relevant_data[key] = "ERR"

    return relevant_data


async def hw_update_loop():
    URL = "http://localhost:8085/data.json"
    VALID_SENSOR_TYPES = {"Temperatures", "Load"}
    VALID_SENSOR_VALUES = {"CPU Total": "cpu_load", "CPU Package": "cpu_temp"}

    timeout = aiohttp.ClientTimeout(total=3, connect=3, sock_connect=3, sock_read=3)

    last_update = {}
    async with aiohttp.ClientSession(timeout=timeout) as aiohttp_session:
        while True:
            success, response = await hw_get_server(URL, aiohttp_session)
            if not success:
                print("[HW] Couldn't query ")
                relevant_data = dict.fromkeys(list(VALID_SENSOR_VALUES.values()), "ERR")
            else:
                relevant_data = await hw_parse_data(
                    response, VALID_SENSOR_TYPES, VALID_SENSOR_VALUES
                )
            if relevant_data == last_update:
                continue

            hw_stats_packet = {
                "type": HUDMsgType.SYSTEM_MONITOR_UPDATE.value,
                "value": {"data": relevant_data},
            }

            hud_manager.message_all_silent(json.dumps(hw_stats_packet))

            await asyncio.sleep(1)


async def ws_main():
    await asyncio.gather(ws_init(), ws_test(), hw_update_loop())


async def ws_test():
    print("Test")
    await asyncio.sleep(5)
    hud_manager.message_all("Test")


if __name__ == "__main__":  # Not supposed to run directly, but can be
    asyncio.run(ws_main())
