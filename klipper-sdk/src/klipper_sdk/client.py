import asyncio
import threading
import logging
from typing import Optional, Union, Any, Dict, List

try:
    import dbus
    import dbus.mainloop.glib
except ImportError:
    dbus = None

try:
    from gi.repository import GLib
except ImportError:
    GLib = None

from .bridge import PrismProtocol, NeuronalCluster
from .controllers import ClipboardController, HistoryManager

# Logger
logger = logging.getLogger(__name__)

class KlipperClient:
    """
    Main entry point for the Klipper SDK.
    Manages D-Bus connection and event loop bridging.
    Integrates OCS Bridge Layer (Prism, Neuronal Clusters).
    """
    
    BUS_NAME = "org.kde.klipper"
    OBJECT_PATH = "/klipper"
    INTERFACE = "org.kde.klipper.klipper"

    def __init__(self, app_id: str = "klipper-sdk"):
        self.app_id = app_id
        self._loop = asyncio.get_event_loop()
        self._glib_loop = GLib.MainLoop() if GLib else None
        self._glib_thread: Optional[threading.Thread] = None
        self._session_bus: Optional[dbus.SessionBus] = None
        self._proxy: Optional[dbus.Interface] = None
        self._connected = False
        
        # OCS Bridge Layer
        self.prism = PrismProtocol()
        self.cluster = NeuronalCluster(node_id=app_id)
        
        # Controllers
        self._clipboard = ClipboardController(self)
        self._history = HistoryManager(self)

    @property
    def clipboard(self) -> ClipboardController:
        """Access to current clipboard operations."""
        return self._clipboard

    @property
    def history(self) -> HistoryManager:
        """Access to history operations."""
        return self._history

    async def connect(self):
        """Initializes the D-Bus connection."""
        if self._connected:
            return

        if not dbus or not GLib:
             logger.warning("D-Bus or GLib not available. Running in offline/mock mode.")
             return

        # Setup GLib MainLoop integration for dbus-python
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        
        try:
            self._session_bus = dbus.SessionBus()
            obj = self._session_bus.get_object(self.BUS_NAME, self.OBJECT_PATH)
            self._proxy = dbus.Interface(obj, self.INTERFACE)
            
            # Subscribe to Signals
            self._proxy.connect_to_signal("clipboardContentChanged", self._on_clipboard_changed_signal)
            
            self._connected = True
            logger.info("Connected to Klipper D-Bus interface.")
            
            # Start GLib loop in background thread for signals
            self._start_background_loop()
            
        except dbus.DBusException as e:
            # Prism: Treat connection failure as high entropy
            self.prism.ingest(e)
            logger.error(f"Failed to connect to Klipper: {e}")
            raise ConnectionError(f"Could not connect to Klipper D-Bus service: {e}")

    def _start_background_loop(self):
        """Starts the GLib MainLoop in a separate thread."""
        if not self._glib_loop:
            return

        def run_loop():
            logger.debug("Starting GLib MainLoop...")
            self._glib_loop.run()
            logger.debug("GLib MainLoop stopped.")

        self._glib_thread = threading.Thread(target=run_loop, daemon=True, name="KlipperSDK-GLib")
        self._glib_thread.start()

    def _on_clipboard_changed_signal(self, content: str):
        """
        Callback for D-Bus signal 'clipboardContentChanged'.
        Runs in the GLib thread. Emits a Pulse to the Neuronal Cluster.
        """
        # We bridge this back to the main loop to ensure thread safety for the cluster if needed,
        # or emit directly if Cluster is thread-safe. Our Cluster V1 is simple list iteration.
        try:
            # Emit Pulse: "I sensed a change"
            self.cluster.emit(
                payload=content, 
                vector="clipboard_change", 
                intensity=0.8
            )
            logger.debug("Bridge: Cluster Pulse emitted for clipboard change.")
        except Exception as e:
            logger.error(f"Bridge Signal Error: {e}")

    async def get_clipboard_contents(self) -> str:
        """Retrieves the current clipboard content."""
        if not self._connected:
            await self.connect()
        
        if not self._proxy:
            return ""

        return await self._call_dbus_method("getClipboardContents")

    async def set_clipboard_contents(self, content: str):
        """Sets the current clipboard content."""
        if not self._connected:
            await self.connect()
            
        if not self._proxy:
            return

        await self._call_dbus_method("setClipboardContents", content)

    async def get_history(self) -> List[str]:
        """
        Retrieves clipboard history.
        """
        if not self._connected:
            await self.connect()

        try:
           # Hypothetical fallback or real call
           current = await self.get_clipboard_contents()
           return [current] if current else []
        except Exception as e:
            self.prism.ingest(e)
            return []

    async def clear_history(self):
        """Clears the clipboard history."""
        if not self._connected:
            await self.connect()
        
        if not self._proxy:
            return

        await self._call_dbus_method("clearClipboardHistory")

    async def _call_dbus_method(self, method_name: str, *args):
        """Executes a D-Bus method call in an executor. Wraps result in Prism."""
        if not self._proxy:
            raise ConnectionError("Not connected to Klipper")
            
        method = getattr(self._proxy, method_name)
        
        try:
            # Run synchronous D-Bus call in default executor
            result = await self._loop.run_in_executor(None, method, *args)
            
            # Prism Ingest: Coherent Code
            prism_result = self.prism.ingest(result)
            self.prism.integrate(prism_result)
            return prism_result.core_truth
            
        except Exception as e:
            # Prism Ingest: Entropy/Shadow
            prism_result = self.prism.ingest(e)
            self.prism.integrate(prism_result)
            logger.warning(f"Prism Refraction: {prism_result.entropy_wrapper}")
            raise e

    async def shutdown(self):
        """Stops the background loop and cleans up."""
        if self._glib_loop and self._glib_loop.is_running():
            self._glib_loop.quit()
        self._connected = False
