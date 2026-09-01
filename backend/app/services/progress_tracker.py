import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
import json
from datetime import datetime
from backend.app.core.logging import logger


class ProgressTracker:
    def __init__(self):
        self._listeners: Dict[str, list] = {}
        self._latest_state: Dict[str, Dict[str, Any]] = {}

    def update_progress(
        self,
        test_id: str,
        percentage: int,
        stage: str,
        current_page: Optional[str] = None,
        error_message: Optional[str] = None,
        status: str = "running"
    ):
        data = {
            "test_id": test_id,
            "status": status,
            "progress_percentage": percentage,
            "current_stage": stage,
            "current_page_url": current_page,
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self._latest_state[test_id] = data
        logger.info(f"Test [{test_id[:8]}] {percentage}%: {stage} (status: {status})")

        # Notify any active SSE/WebSocket listeners
        if test_id in self._listeners:
            for queue in self._listeners[test_id]:
                try:
                    queue.put_nowait(data)
                except Exception:
                    pass

    def get_latest_state(self, test_id: str) -> Optional[Dict[str, Any]]:
        return self._latest_state.get(test_id)

    async def stream_progress(self, test_id: str) -> AsyncGenerator[str, None]:
        queue = asyncio.Queue()
        if test_id not in self._listeners:
            self._listeners[test_id] = []
        self._listeners[test_id].append(queue)

        # Emit initial state if already recorded
        initial = self._latest_state.get(test_id)
        if initial:
            yield f"data: {json.dumps(initial)}\n\n"

        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") in ("completed", "failed", "cancelled"):
                    break
        finally:
            if test_id in self._listeners and queue in self._listeners[test_id]:
                self._listeners[test_id].remove(queue)


progress_tracker = ProgressTracker()
