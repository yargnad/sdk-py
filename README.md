# Anima Locus Python SDK

**AGPLv3 Licensed** | Strongly-Typed Python Client for Anima Locus API

Control audio engines, manage presets, and stream sensor telemetry from Python.

---

## Overview

This SDK provides:

- **Typed WebSocket client** (real-time parameter control)
- **REST API client** (presets, scenes, system management)
- **Async-first design** (asyncio-native)
- **CLI tools** (for testing and automation)
- **Type hints** (full mypy compliance)

### Installation

```bash
pip install anima-locus
```

**From source:**
```bash
git clone https://github.com/[org]/sdk-py.git
cd sdk-py
pip install -e .
```

---

## Quick Start

### WebSocket Control

```python
import asyncio
from anima_locus import AnimaClient

async def main():
    async with AnimaClient("ws://anima.local:8080") as client:
        # Set granular engine parameter
        await client.set_param("granular", "grain_size", 0.25)
        
        # Subscribe to telemetry
        async for msg in client.telemetry_stream():
            print(f"Temp: {msg.sensors.temperature}°C")
            if msg.sensors.temperature > 30:
                await client.set_param("effects", "reverb_decay", 6.0)

### Elemental Control API
The SDK exposes a small elemental bus API for high-level expressive controls; each element is a float in [-1.0, 1.0] (or [0.0, 1.0] depending on engine):

```python
# Set element values
await client.set_element('earth', 0.65)
await client.set_element('air', 0.12)

# Or set the entire bus in one frame
await client.set_elemental_bus({'earth': 0.65, 'air': 0.12, 'water': 0.0, 'fire': -0.3})
```

Elemental control frames are recorded into ER Files (if enabled) and appear in telemetry under `msg.elements`.

asyncio.run(main())
```

### REST API

```python
from anima_locus import AnimaClient

client = AnimaClient("http://anima.local:8080")

# List presets
presets = client.presets.list()
for preset in presets:
    print(f"{preset.id}: {preset.name}")

# Load preset
client.presets.load("preset-001")

# Create new preset
new_preset = client.presets.create(
    name="My Preset",
    engines={
        "granular": {
            "enabled": True,
            "grain_size": 0.15,
            "density": 40
        }
    }
)
```

---

## API Reference

### Client Initialization

```python
class AnimaClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        auto_reconnect: bool = True,
        ssl_verify: bool = True
    ):
        """
        Initialize Anima Locus client.
        
        Args:
            base_url: WebSocket (ws://) or HTTP (http://) URL
            timeout: Request timeout in seconds
            auto_reconnect: Reconnect WebSocket on disconnect
            ssl_verify: Verify SSL certificates (wss:// only)
        """
```

### WebSocket API

#### Parameter Control

```python
await client.set_param(
    engine: str,     # "granular", "spectral", "sampler", "effects"
    param: str,      # Parameter name (e.g., "grain_size")
    value: float     # Normalized 0.0-1.0 or absolute value
)
```

#### Telemetry Streaming

```python
async for msg in client.telemetry_stream():
    msg.sensors.temperature   # float (°C)
    msg.sensors.humidity      # float (%)
    msg.sensors.co2           # int (ppm)
    msg.sensors.radar         # RadarData(x, y, z, velocity)
    msg.sensors.efield        # EFieldData(x, y, z)
    msg.audio.cpu             # float (%)
    msg.audio.xruns           # int (count)
```

### REST API

#### Presets

```python
# List all presets
presets: List[Preset] = client.presets.list()

# Get specific preset
preset: Preset = client.presets.get("preset-001")

# Create preset
preset = client.presets.create(
    name="New Preset",
    engines={"granular": {...}},
    mappings={"radar.x": "granular.position"}
)

# Update preset
client.presets.update("preset-001", name="Updated Name")

# Delete preset
client.presets.delete("preset-001")

# Load preset (activate)
client.presets.load("preset-001")
```

#### Scenes

```python
# List scenes
scenes: List[Scene] = client.scenes.list()

# Load scene
client.scenes.load("scene-001")
```

#### System

```python
# Get system status
status: SystemStatus = client.system.status()
status.uptime          # float (seconds)
status.audio.backend   # "JACK" or "PipeWire"
status.mcu.connected   # bool
status.mcu.firmware    # str (version)

# Get audio stats
stats: AudioStats = client.system.audio_stats()
stats.sample_rate      # int (Hz)
stats.buffer_size      # int (samples)
stats.latency          # float (ms)
```

---

## CLI Tools

### anima-ctl

Command-line control interface:

```bash
# Connect to device
anima-ctl --host anima.local

# Set parameter
anima-ctl set granular.grain_size 0.25

# Load preset
anima-ctl load preset-001

# Stream telemetry
anima-ctl monitor --sensors

# List presets
anima-ctl presets list

# System status
anima-ctl status
```

### anima-record

Record telemetry to file:

```bash
# Record 60 seconds of sensor data
anima-record --duration 60 --output recording.json

# Replay recording
anima-replay recording.json --speed 1.0
```

### anima-preset

Preset management:

```bash
# Export preset to file
anima-preset export preset-001 -o my-preset.json

# Import preset from file
anima-preset import my-preset.json

# Validate preset file
anima-preset validate my-preset.json
```

---

## Type Definitions

### Data Models

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class RadarData:
    x: float          # Normalized -1.0 to 1.0
    y: float
    z: float
    velocity: float   # m/s

@dataclass
class EFieldData:
    x: float          # Normalized 0.0 to 1.0
    y: float
    z: float

@dataclass
class EnvironmentalData:
    temperature: float     # °C
    humidity: float        # %
    pressure: float        # hPa
    co2: int               # ppm
    voc: Optional[int]     # IAQ index (if BME688)

@dataclass
class SensorSnapshot:
    timestamp: float             # Unix timestamp
    radar: Optional[RadarData]
    efield: Optional[EFieldData]
    environmental: EnvironmentalData

@dataclass
class AudioStats:
    cpu: float           # CPU usage %
    xruns: int           # Buffer underruns count
    latency: float       # Round-trip latency (ms)

@dataclass
class TelemetryMessage:
    sensors: SensorSnapshot
    audio: AudioStats
```

### Presets

```python
@dataclass
class EngineConfig:
    enabled: bool
    params: Dict[str, float]

@dataclass
class Preset:
    id: str
    name: str
    description: Optional[str]
    engines: Dict[str, EngineConfig]
    mappings: Dict[str, str]  # sensor_path -> param_path
    created_at: datetime
    updated_at: datetime
```

---

## Examples

### Live Performance Script

```python
import asyncio
from anima_locus import AnimaClient

async def performance():
    async with AnimaClient("ws://anima.local:8080") as client:
        # Load intro scene
        await client.scenes.load("intro")
        
        # Wait for temperature to rise (audience present)
        async for msg in client.telemetry_stream():
            if msg.sensors.temperature > 24:
                break
        
        # Transition to main scene
        await client.scenes.load("main")
        
        # React to CO2 levels (audience energy)
        async for msg in client.telemetry_stream():
            co2 = msg.sensors.co2
            if co2 > 800:
                intensity = (co2 - 800) / 400  # 800-1200 ppm range
                await client.set_param("effects", "reverb_mix", intensity)

asyncio.run(performance())
```

### Preset Generator

```python
from anima_locus import AnimaClient

client = AnimaClient("http://anima.local:8080")

# Generate 10 randomized presets
for i in range(10):
    preset = client.presets.create(
        name=f"Random {i:02d}",
        engines={
            "granular": {
                "enabled": True,
                "grain_size": random.uniform(0.01, 0.5),
                "density": random.uniform(5, 80)
            },
            "effects": {
                "reverb": {"decay": random.uniform(1.0, 8.0)}
            }
        }
    )
    print(f"Created: {preset.id}")
```

### Telemetry Logger

```python
import asyncio
import csv
from anima_locus import AnimaClient

async def log_telemetry(duration_sec: int):
    async with AnimaClient("ws://anima.local:8080") as client:
        with open("telemetry.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "temp", "humidity", "co2", "cpu"])
            
            start = asyncio.get_event_loop().time()
            async for msg in client.telemetry_stream():
                elapsed = asyncio.get_event_loop().time() - start
                if elapsed > duration_sec:
                    break
                
                writer.writerow([
                    msg.sensors.timestamp,
                    msg.sensors.environmental.temperature,
                    msg.sensors.environmental.humidity,
                    msg.sensors.environmental.co2,
                    msg.audio.cpu
                ])

asyncio.run(log_telemetry(300))  # 5 minutes
```

---

## Testing

### Run Tests

```bash
pytest tests/ -v
```

### Type Checking

```bash
mypy anima_locus/
```

### Coverage

```bash
pytest --cov=anima_locus --cov-report=html
```

---

## Licensing

Licensed under **GNU Affero General Public License v3.0** (AGPLv3).

See [LICENSE](./LICENSE) for full text.

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for:

- Development setup
- Coding standards
- Testing requirements
- PR process

---

## Related Repositories

- [engine-ui/](../engine-ui/) - Audio engine and API server
- [sdk-ts/](../sdk-ts/) - TypeScript SDK
- [docs-site/](../docs-site/) - Full documentation

---

## Links

- **Documentation:** https://anima-locus.musubiaccord.org/sdk/python
- **PyPI:** https://pypi.org/project/anima-locus/
- **GitHub:** https://github.com/[org]/sdk-py

---

*Part of the [Anima Locus](../) project and [The Authentic Rebellion Framework](https://rebellion.musubiaccord.org) ecosystem.*
