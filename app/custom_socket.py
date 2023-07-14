from fastapi import WebSocket
from typing import List
import asyncio


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_data(self, data: str):
        for connection in self.active_connections:
            await connection.send_text(data)

    async def close(self, websocket: WebSocket):
        if websocket in self.active_connections:
            await websocket.close()
            self.active_connections.remove(websocket)


async def wait_for_timeout(websocket: WebSocket, timeout: int = 20 * 60):
    await asyncio.sleep(timeout)
    await websocket.close()



