import asyncio
import json
from typing import Dict, Set

class SSEManager:
    """
    Manages active SSE connections for real-time webhooks and delivery updates.
    """
    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()

    async def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue):
        self._subscribers.discard(queue)

    async def broadcast(self, event_name: str, payload: dict):
        if not self._subscribers:
            return

        message = {
            "event": event_name,
            "data": payload
        }
        
        # Broadcast to all connected queues
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(message)
            except Exception:
                pass

sse_manager = SSEManager()

