from typing import List, Optional, Any
from .client import KlipperClient

class ClipboardController:
    """
    High-level interface for clipboard operations.
    """
    def __init__(self, client: KlipperClient):
        self.client = client

    async def get_text(self) -> str:
        """Returns the current clipboard text."""
        try:
            content = await self.client.get_clipboard_contents()
            return content
        except Exception as e:
            # Handle specific D-Bus errors or empty states
            return ""

    async def set_text(self, text: str):
        """Sets the clipboard text."""
        await self.client.set_clipboard_contents(text)

    async def clear(self):
        """Clears the clipboard (and potentially history depending on Klipper config)."""
        await self.client.set_clipboard_contents("")


class HistoryManager:
    """
    High-level interface for history operations.
    """
    def __init__(self, client: KlipperClient):
        self.client = client

    async def get_recent_items(self, limit: int = 10) -> List[str]:
        """Returns the most recent N items from history."""
        # Current implementation wraps basic retrieval. 
        # Future: Implement actual pagination if Klipper API supports it or if we maintain a cache.
        history = await self.client.get_history()
        return history[:limit]

    async def clear_all(self):
        """Clears the entire history."""
        await self.client.clear_history()
