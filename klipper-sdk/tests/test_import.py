import pytest
from klipper_sdk.client import KlipperClient
from klipper_sdk.controllers import ClipboardController, HistoryManager

def test_imports():
    """Verify that modules can be imported."""
    assert KlipperClient is not None
    assert ClipboardController is not None
    assert HistoryManager is not None

@pytest.mark.asyncio
async def test_instantiation():
    """Verify that classes can be instantiated."""
    client = KlipperClient()
    clipboard = ClipboardController(client)
    history = HistoryManager(client)
    
    assert clipboard.client == client
    assert history.client == client
    
    # We do NOT connect here to avoid D-Bus dependency in unit tests
    # await client.connect() 
