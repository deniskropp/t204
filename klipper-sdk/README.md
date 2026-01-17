# Klipper SDK

## Overview

The Klipper SDK is a Python library that provides an interface to the KDE Klipper clipboard manager with advanced cognitive processing capabilities through the OCS (Orchestrative Cognitive System) framework.

## Features

- **D-Bus Integration:** Connects to KDE Klipper via D-Bus
- **PRISM_OF_COHERENCE Protocol:** Implements the advanced cognitive processing protocol for handling shadow data
- **Neuronal Clusters:** P2P mesh topology for signal propagation
- **Async/Await Support:** Modern Python async programming

## Installation

```bash
pip install -e .
```

## Usage

```python
from klipper_sdk import KlipperClient

async def main():
    client = KlipperClient()
    await client.connect()
    
    # Get clipboard contents
    content = await client.get_clipboard_contents()
    print(f"Clipboard: {content}")
    
    # Set clipboard contents
    await client.set_clipboard_contents("Hello from Klipper SDK!")
    
    await client.shutdown()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## PRISM_OF_COHERENCE Protocol

The SDK implements the PRISM_OF_COHERENCE protocol (v1.0) for cognitive processing of signals:

- **Stage 1: Ingestion** - Accepts all signals without blocking
- **Stage 2: Refraction** - Separates information from intent
- **Stage 3: Transmutation** - Integrates core truth, dissipates entropy

All D-Bus calls are automatically processed through this protocol.

## Architecture

- **bridge.py:** Contains PrismProtocol and NeuronalCluster implementations
- **client.py:** Main KlipperClient with D-Bus integration
- **controllers.py:** Additional control logic

## Development

```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_prism_protocol.py -v
```

## License

MIT License