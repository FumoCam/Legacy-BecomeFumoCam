import asyncio
from traceback import format_exc

import websockets

from utilities import error_log


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


async def hud_ws_init():
    while True:
        try:
            async with websockets.serve(hud_manager.ws_handler, "127.0.0.1", 8080):
                await asyncio.Future()  # run forever
        except Exception:
            error_log(format_exc())


async def ws_main():
    await asyncio.gather(hud_ws_init(), ws_test())


async def ws_test():
    print("Test")
    await asyncio.sleep(5)
    hud_manager.message_all("Test")


if __name__ == "__main__":  # Not supposed to run directly, but can be
    asyncio.run(ws_main())
