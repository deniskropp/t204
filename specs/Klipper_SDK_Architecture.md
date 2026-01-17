# Klipper SDK: Architectural Design & API Specification

**Version:** 1.0 (Draft)
**Date:** 2026-01-17
**Status:** In Design
**Reference:** `T-20260117-002` | `specs/Klipper_SDK_FRD.md`

---

## 1. Architectural Overview

The Klipper SDK serves as a high-level abstraction layer over the Klipper clipboard service. It employs a **Client-Service** architecture where external applications (Clients) communicate with the Klipper daemon (Service) via Inter-Process Communication (IPC), primarily **D-Bus** on Linux systems.

### 1.1 Components

1.  **Klipper Service (Daemon):** The core clipboard manager maintaining history and configuration. It exposes a D-Bus interface `org.kde.klipper`.
2.  **Klipper SDK (Library):** A wrapper library (available in Python, C++) that handles IPC complexity, serialization, and state management.
3.  **External App / Plugin:** The consumer of the SDK.

### 1.2 Data Flow
```
[Application] <-> [SDK API] <-> [IPC / D-Bus] <-> [Klipper Service] <-> [Clipboard/History]
```

---

## 2. Core API Specification (Python Reference)

The SDK provides a main entry point `KlipperClient`.

### 2.1 Class: `KlipperClient`

```python
class KlipperClient:
    def __init__(self, app_id: str):
        """Initializes connection to Klipper service."""
        pass

    @property
    def clipboard(self) -> 'ClipboardController':
        """Access to current clipboard operations."""
        pass

    @property
    def history(self) -> 'HistoryManager':
        """Access to history operations."""
        pass

    @property
    def settings(self) -> 'SettingsManager':
        """Access to configuration."""
        pass
```

### 2.2 Class: `ClipboardController`

```python
class ClipboardController:
    def get_content(self, mime_type: str = "text/plain") -> Union[str, bytes, None]:
        """Retrieves current clipboard content."""
        pass

    def set_content(self, data: Union[str, bytes], mime_type: str = "text/plain"):
        """Sets current clipboard content."""
        pass

    def clear(self):
        """Clears the clipboard."""
        pass

    # Signals
    on_changed: Signal  # Emits (new_content_preview, mime_type)
```

### 2.3 Class: `HistoryManager`

```python
class HistoryManager:
    def get_items(self, limit: int = 10, offset: int = 0) -> List['HistoryItem']:
        """Retrieves history items with pagination."""
        pass

    def add_item(self, data: Any, mime_type: str):
        """Manually adds an item to history."""
        pass

    def remove_item(self, uuid: str):
        """Removes an item by UUID."""
        pass

    def search(self, query: str) -> List['HistoryItem']:
        """Searches history content."""
        pass

    # Signals
    on_history_updated: Signal # Emits (change_type, item_uuid)
```

### 2.4 Data Model: `HistoryItem`

```python
@dataclass
class HistoryItem:
    uuid: str
    content: Union[str, bytes]
    mime_type: str
    timestamp: int
    metadata: Dict[str, Any]  # Tags, pinned state, app_source
```

### 2.5 Concurrency & Event Loop Strategy

The SDK is designed to be **loop-agnostic** but optimized for **asyncio**.

*   **D-Bus Integration:** The SDK isolates `dbus-python` (which relies on `GLib.MainLoop`) from the user's application loop.
*   **Async Interface:** All I/O-bound methods (e.g., `set_content`, `get_history`) are exposed as `async def`.
*   **Bridge:** A background thread manages the GLib loop for D-Bus signal reception, bridging events to the `asyncio` loop via `loop.call_soon_threadsafe`.
*   **Thread Safety:** Internal state (cache, history) is protected by locks or managed within the single integration thread.

---

## 3. Underlying D-Bus Interface Definition

The SDK communicates with Klipper via `org.kde.klipper`.

**Service:** `org.kde.klipper`
**Path:** `/klipper`
**Interface:** `org.kde.klipper.klipper`

### Methods
*   `getClipboardContents() -> s` (Legacy support)
*   `setClipboardContents(s)`
*   `clearClipboardHistory()`
*   `getHistory(int limit, int offset) -> a{sv}` (Returns array of struct/dict)
*   `addHistoryItem(ay data, s mimeType, a{sv} metadata) -> s` (Returns UUID)
*   `removeHistoryItem(s uuid) -> b`
*   `lockHistory()` / `unlockHistory()` (For sensitive operations)

### Signals
*   `clipboardContentChanged(s preview)`
*   `historyChanged(s changeType, s itemUuid)`

---

## 4. Plugin Architecture

Plugins are isolated scripts or modules that extend Klipper's functionality.

### 4.1 Interface: `KlipperPlugin`

```python
class KlipperPlugin:
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="My Plugin",
            version="1.0",
            permissions=["read_history"]
        )

    def on_load(self, context: 'PluginContext'):
        """Called when plugin is loaded."""
        pass

    def execute(self, action_id: str, data: Any):
        """Called when a custom action is triggered."""
        pass
```

### 4.2 Sandboxing & Security

*   **Isolation:** Plugins run in separate processes.
*   **Permission Model:** Manifest-based permissions (e.g., `klipper.history.read`).
*   **User Consent:**
    *   On plugin installation/first run, the user is prompted to grant requested permissions.
    *   "Sensitive" data access (e.g., password fields) triggers a specific "One-time allow" prompt.

---

## 5. Configuration & Persistence

*   **Format:** JSON or TOML for configuration.
*   **Storage:** `~/.config/klipper-sdk/`
*   **Schema:**
    *   `general`: History size, timeouts.
    *   `plugins`: Enabled/disabled states, permission grants.
    *   `security`: Ignored apps (password managers), encryption settings.

---

## 6. Implementation Roadmap

1.  **Phase 1: Core IPC Wrapper**
    *   Implement `KlipperClient` connecting to existing Klipper D-Bus methods.
2.  **Phase 2: Extended D-Bus Service**
    *   Extend Klipper (C++) to expose `getHistory` (structured), `addHistoryItem` with metadata.
3.  **Phase 3: SDK Logic**
    *   Implement HistoryManager and serialization logic in Python SDK.
4.  **Phase 4: Plugin System**
    *   Develop the plugin runner and permission enforcement logic.

