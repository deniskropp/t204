from typing import List, Optional, Any, Union, Dict, TYPE_CHECKING
from dataclasses import dataclass, field
import uuid
import time

if TYPE_CHECKING:
    from .client import KlipperClient

@dataclass
class HistoryItem:
    """Represents a single item in the clipboard history."""
    content: Union[str, bytes]
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    mime_type: str = "text/plain"
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ClipboardController:
    """
    High-level interface for clipboard operations.
    Aligned with Klipper SDK Architecture v1.0.
    """
    def __init__(self, client: "KlipperClient"):
        self.client = client

    async def get_content(self, mime_type: str = "text/plain") -> Union[str, bytes, None]:
        """Retrieves current clipboard content."""
        # TODO: Implement MIME type handling when supported by D-Bus
        try:
            content = await self.client.get_clipboard_contents()
            return content
        except Exception:
            return None

    async def set_content(self, data: Union[str, bytes], mime_type: str = "text/plain"):
        """Sets current clipboard content."""
        # TODO: Implement MIME type handling
        if isinstance(data, bytes):
            data = data.decode('utf-8') # Basic fallback
        await self.client.set_clipboard_contents(data)

    async def clear(self):
        """Clears the clipboard."""
        await self.client.set_clipboard_contents("")

class HistoryManager:
    """
    High-level interface for history operations.
    Aligned with Klipper SDK Architecture v1.0.
    """
    def __init__(self, client: "KlipperClient"):
        self.client = client

    async def get_items(self, limit: int = 10, offset: int = 0) -> List[HistoryItem]:
        """Retrieves history items with pagination."""
        raw_history = await self.client.get_history()
        
        # Convert raw strings to HistoryItems
        # In the future, this parsing will be more sophisticated
        items = []
        for text in raw_history:
            items.append(HistoryItem(content=text))
            
        # Handle pagination
        start = offset
        end = offset + limit
        return items[start:end]

    async def add_item(self, data: Any, mime_type: str = "text/plain"):
        """Manually adds an item to history."""
        # Currently Klipper D-Bus just has setClipboardContents which adds to history implicitly
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        await self.client.set_clipboard_contents(data)

    async def remove_item(self, uuid: str):
        """Removes an item by UUID."""
        # TODO: Implement when Klipper supports granular removal by ID
        pass

    async def search(self, query: str) -> List[HistoryItem]:
        """Searches history content."""
        all_items = await self.get_items(limit=100) # Arbitrary limit for now
        return [item for item in all_items if query.lower() in str(item.content).lower()]

    async def clear_all(self):
        """Clears the entire history."""
        await self.client.clear_history()
