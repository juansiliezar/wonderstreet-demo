<!-- 1d9face7-6689-458b-9ef0-05c1f8ef351e 175acf06-f4e6-43d5-9fd2-c81dec47a7d0 -->
# Implement Core Logging Module with Loguru

## Overview

Implement `core/logging.py` with a centralized logging configuration function using loguru. This provides consistent, structured logging across the application and replaces print statements with proper logging.

## Implementation Steps

### 1. Add loguru dependency

- Update `pyproject.toml` to include `loguru>=0.7.0` in dependencies
- Loguru provides a modern, structured logging API with better defaults

### 2. Create `core/logging.py` file structure

- Add three-line module docstring describing the logging module's purpose
- Import required modules:
  - `from loguru import logger`
  - `import sys` (for removing default handler)

### 3. Implement `setup_logging()` function

- Function signature: `def setup_logging(level: str = "INFO") -> None:`
- Add Google-style docstring explaining the function's purpose
- Configure loguru logger:
  - Remove default handler: `logger.remove()`
  - Add custom handler with format: `logger.add(sys.stdout, format="[{time}] {level} - {name} - {message}", level=level)`
  - Format matches plan requirement: `[{time}] {level} - {name} - {message}`
  - Use loguru's time formatting (default ISO-like format)
- Loguru automatically handles idempotency through its handler management

### 4. Export module-level logger instance

- Loguru provides a global `logger` object, so we can simply re-export it
- This allows other modules to import: `from core.logging import logger`
- Logger name will be automatically set based on the calling module when using `logger.bind(name=__name__)` or loguru's automatic context

## Code Structure

```python
"""
Core logging module for application-wide logging configuration.

This module provides centralized logging setup using loguru and exports
a module-level logger instance for consistent logging across the application.
"""

import sys
from loguru import logger


def setup_logging(level: str = "INFO") -> None:
    """Configure loguru logging for the application.
    
    Sets up loguru with a standard format and console output.
    This function should be called once at application startup.
    
    Args:
        level: Logging level as string (default: "INFO")
              Valid values: "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"
    """
    # Remove default handler
    logger.remove()
    
    # Add custom handler with specified format
    logger.add(
        sys.stdout,
        format="[{time}] {level} - {name} - {message}",
        level=level,
    )


# Export loguru's logger instance for easy importing
# Other modules can use: from core.logging import logger
```

## Design Decisions

1. **Loguru over standard library**: Modern API, better structured logging, automatic serialization
2. **Remove default handler**: Start with clean slate, add only our custom handler
3. **String level parameter**: Loguru accepts string levels (more intuitive than constants)
4. **Module-level logger export**: Re-export loguru's global logger for consistency
5. **Format compatibility**: Format string matches plan requirement pattern

## Integration Points

- Step 7 (`main.py`): Will call `core.logging.setup_logging()` at startup
- Step 5 (`domains/email/ingestion.py`): Will use `from core.logging import logger`
- Existing code (`integrations/base_client.py`): Uses standard logging - can coexist or be migrated later

## Notes on Existing Code

- `integrations/base_client.py` currently uses `logging.getLogger(__name__)` from standard library
- This code will continue to work (standard logging and loguru can coexist)
- Future refactoring could migrate to loguru for consistency, but not required for this step

## Validation Checklist

- [ ] `loguru>=0.7.0` added to `pyproject.toml` dependencies
- [ ] File `core/logging.py` exists with three-line module docstring
- [ ] `setup_logging()` function implemented with Google-style docstring
- [ ] Function accepts optional `level` parameter (default: `"INFO"` as string)
- [ ] Format string matches pattern: `[{time}] {level} - {name} - {message}`
- [ ] Default handler removed with `logger.remove()`
- [ ] Custom handler added to stdout with specified format
- [ ] Module-level `logger` exported from loguru
- [ ] Type hints included on function signature
- [ ] Function can be safely called multiple times

## Testing Considerations

- `setup_logging()` can be tested by checking logger configuration
- Module-level logger can be imported and used in tests
- Logging level can be overridden in tests: `setup_logging(level="DEBUG")`
- Loguru provides built-in testing utilities for capturing logs