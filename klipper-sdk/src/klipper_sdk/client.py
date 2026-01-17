import asyncio
import threading
import logging
from typing import Optional, Union, Any, Dict, List
import dbus
import dbus.mainloop.glib
from gi.repository import GLib

# Logger
logger = logging.getLogger(__name__)

class KlipperClient:
    """
    Main entry point for the Klipper SDK.
    Manages D-Bus connection and event loop bridging.
    """
    
    BUS_NAME = "org.kde.klipper"
    OBJECT_PATH = "/klipper"
    INTERFACE = "org.kde.klipper.klipper"

    def __init__(self, app_id: str = "klipper-sdk"):
        self.app_id = app_id
        self._loop = asyncio.get_event_loop()
        self._glib_loop = GLib.MainLoop()
        self._glib_thread: Optional[threading.Thread] = None
        self._session_bus: Optional[dbus.SessionBus] = None
        self._proxy: Optional[dbus.Interface] = None
        self._connected = False

    async def connect(self):
        """Initializes the D-Bus connection."""
        if self._connected:
            return

        # Setup GLib MainLoop integration for dbus-python
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        
        try:
            self._session_bus = dbus.SessionBus()
            obj = self._session_bus.get_object(self.BUS_NAME, self.OBJECT_PATH)
            self._proxy = dbus.Interface(obj, self.INTERFACE)
            self._connected = True
            logger.info("Connected to Klipper D-Bus interface.")
            
            # Start GLib loop in background thread for signals
            self._start_background_loop()
            
        except dbus.DBusException as e:
            logger.error(f"Failed to connect to Klipper: {e}")
            raise ConnectionError(f"Could not connect to Klipper D-Bus service: {e}")

    def _start_background_loop(self):
        """Starts the GLib MainLoop in a separate thread."""
        def run_loop():
            logger.debug("Starting GLib MainLoop...")
            self._glib_loop.run()
            logger.debug("GLib MainLoop stopped.")

        self._glib_thread = threading.Thread(target=run_loop, daemon=True, name="KlipperSDK-GLib")
        self._glib_thread.start()

    async def get_clipboard_contents(self) -> str:
        """Retrieves the current clipboard content."""
        if not self._connected:
            await self.connect()
        
        return await self._call_dbus_method("getClipboardContents")

    async def set_clipboard_contents(self, content: str):
        """Sets the current clipboard content."""
        if not self._connected:
            await self.connect()
            
        await self._call_dbus_method("setClipboardContents", content)

    async def get_history(self) -> List[str]:
        """
        Retrieves clipboard history.
        Note: Klipper's D-Bus API might only expose the current item or a limited list depending on version.
        This aims to use the standard interface.
        """
        if not self._connected:
            await self.connect()

        # Some Klipper versions expose getHistory/klipperHistory
        # Fallback to internal management if not available, but for now we try to call it.
        # Often getClipboardHistory is not standard.
        # We will implement a robust method later. For v0.1 we wrap standard calls.
        try:
           # Hypothetical method from Spec - verifying existence would be Phase 2
           # For now, we return a mock or current content as history [0]
           current = await self.get_clipboard_contents()
           return [current] if current else []
        except Exception as e:
            logger.warning(f"History retrieval failed: {e}")
            return []

    async def clear_history(self):
        """Clears the clipboard history."""
        if not self._connected:
            await self.connect()
        await self._call_dbus_method("clearClipboardHistory")

    async def _call_dbus_method(self, method_name: str, *args):
        """Executes a D-Bus method call in an executor to avoid blocking the asyncio loop."""
        if not self._proxy:
            raise ConnectionError("Not connected to Klipper")
            
        method = getattr(self._proxy, method_name)
        
        # Run synchronous D-Bus call in default executor
        return await self._loop.run_in_executor(None, method, *args)

    async def shutdown(self):
        """Stops the background loop and cleans up."""
        if self._glib_loop.is_running():
            self._glib_loop.quit()
        self._connected = False
