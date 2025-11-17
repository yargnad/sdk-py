# Contributing to Anima Locus Python SDK

See the main [Contributing Guide](../CONTRIBUTING.md) for general guidelines.

---

## Python SDK-Specific Requirements

**License:** AGPLv3

### Code Style

- **Python:** 3.11+
- **Type Hints:** All public APIs (mypy strict mode)
- **Formatter:** Black (line length 100)
- **Import Order:** isort
- **Docstrings:** Google style

```bash
# Format
black anima_locus/
isort anima_locus/

# Type check
mypy anima_locus/ --strict

# Lint
ruff check anima_locus/
```

### Naming Conventions

- **Classes:** `PascalCase` (`AnimaClient`, `PresetManager`)
- **Functions:** `snake_case` (`set_param`, `load_preset`)
- **Private methods:** `_leading_underscore` (`_parse_message`)
- **Constants:** `UPPER_SNAKE_CASE` (`DEFAULT_TIMEOUT`)

### Type Annotations

```python
# Good: Fully typed
from typing import Optional, List, Dict

async def get_presets(
    self,
    *,
    tag: Optional[str] = None,
    limit: int = 100
) -> List[Preset]:
    """
    Retrieve presets from API.
    
    Args:
        tag: Filter by tag (optional)
        limit: Maximum number of presets to return
        
    Returns:
        List of Preset objects
        
    Raises:
        APIError: If request fails
    """
    ...
```

### Async-First Design

```python
# Prefer asyncio
import asyncio

async def main():
    async with AnimaClient("ws://anima.local:8080") as client:
        await client.set_param("granular", "grain_size", 0.25)

asyncio.run(main())

# Also provide sync wrappers for CLI tools
def main_sync():
    client = AnimaClient("http://anima.local:8080")
    client.set_param_sync("granular", "grain_size", 0.25)
```

### Error Handling

```python
from anima_locus.exceptions import (
    AnimaError,
    ConnectionError,
    APIError,
    ValidationError
)

# Raise specific exceptions
if not self._connected:
    raise ConnectionError("Client not connected")

# Document exceptions in docstring
def set_param(self, engine: str, param: str, value: float) -> None:
    """
    Set audio engine parameter.
    
    Raises:
        ConnectionError: If WebSocket not connected
        ValidationError: If parameter name invalid
        APIError: If server rejects parameter value
    """
```

### Testing

**Unit Tests:**
```bash
pytest tests/ -v --cov=anima_locus --cov-report=html
```

**Type Checking:**
```bash
mypy anima_locus/ --strict
```

**Integration Tests:**
```bash
# Requires live API server
pytest tests/integration/ --api-url http://localhost:8080
```

### Documentation

**Docstrings (Google Style):**
```python
def telemetry_stream(
    self,
    rate_hz: int = 30
) -> AsyncIterator[TelemetryMessage]:
    """
    Stream telemetry messages from device.
    
    Args:
        rate_hz: Telemetry rate in Hz (default: 30)
        
    Yields:
        TelemetryMessage objects with sensor and audio data
        
    Raises:
        ConnectionError: If WebSocket disconnects
        
    Example:
        >>> async for msg in client.telemetry_stream():
        ...     print(f"Temp: {msg.sensors.temperature}°C")
    """
```

### Pull Request Checklist

- [ ] Code formatted (black, isort)
- [ ] Type hints on all public APIs
- [ ] Docstrings (Google style)
- [ ] Tests pass (pytest)
- [ ] Type check passes (mypy --strict)
- [ ] Coverage > 80%
- [ ] `CHANGELOG.md` updated
- [ ] DCO sign-off

### Commit Message Format

```
[sdk-py] Add preset validation

Adds client-side validation for preset creation:
- Check required fields (name, engines)
- Validate parameter ranges
- Verify mapping paths

Prevents invalid presets from reaching API.

Fixes #28

Signed-off-by: Your Name <your.email@example.com>
```

### Versioning

- **SemVer:** `MAJOR.MINOR.PATCH`
- **Breaking changes:** Increment MAJOR
- **New features:** Increment MINOR
- **Bug fixes:** Increment PATCH

Update `pyproject.toml` and `CHANGELOG.md` for each release.

### Publishing

```bash
# Build package
python -m build

# Upload to PyPI (maintainers only)
python -m twine upload dist/*
```

---

## DCO Sign-Off

All commits must include:

```
Signed-off-by: Your Name <your.email@example.com>
```

Use `git commit -s` to add automatically.

---

## Questions?

Open a GitHub Discussion or see [main Contributing Guide](../CONTRIBUTING.md).

---

*Licensed under AGPLv3. See [LICENSE](./LICENSE).*
