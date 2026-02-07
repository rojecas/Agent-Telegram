# Unit Test Plan for Security Logger

## Objective
Verify that modifications to `logger.py` (specifically the path of logs) have not broken existing functionality.

## Scope
Test the `FileSecurityLogger` class and its methods:
- `__init__`
- `log_event`
- `log_threat_detected`
- `log_profile_access`
- `log_secret_verification`

## Testing Strategy
- Mock file system operations (`Path`, `open`, `json.load`, `json.dump`) to avoid side effects.
- Use `pytest` with `unittest.mock`.
- Validate that log entries have correct structure.
- Validate that file paths are constructed as expected.

## Test Cases

### 1. Initialization
- Default log directory is `./logs`.
- Custom log directory is respected.
- Directory is created if it doesn't exist.

### 2. `log_event`
- Returns a dict with expected keys (`timestamp`, `event_type`, `threat_level`, `user`, `details`, `action_taken`).
- Appends entry to the appropriate JSON file (mocked).
- Creates new file when none exists.
- Prints to console (optional).

### 3. `log_threat_detected`
- Calls `log_event` with correct parameters.
- Threat level is "medium".
- Event type includes threat type.

### 4. `log_profile_access`
- Calls `log_event` with `PROFILE_ACCESS` event type.
- Threat level is "low".

### 5. `log_secret_verification`
- Success case: event type `SECRET_VERIFICATION_SUCCESS`, threat level "low".
- Failure case: event type `SECRET_VERIFICATION_FAILED`, threat level "high".
- Details include success flag and attempts.

## Mocking Details
- Patch `pathlib.Path.mkdir` to avoid actual directory creation.
- Patch `open` and `json.load`/`json.dump` to simulate file read/write.
- Use `unittest.mock.MagicMock` to capture calls.

## Test File Location
Create a new file `tests/unit/test_logger.py` (or update existing test files). Prefer a dedicated unit test file.

## Example Test Code

```python
"""
Unit tests for security logger.
"""
import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
import json
from datetime import datetime

from src.agent_telegram.security.logger import FileSecurityLogger, SecurityLogger


class TestFileSecurityLogger:
    """Test suite for FileSecurityLogger."""

    def test_init_default(self):
        """Test initialization with default log directory."""
        with patch.object(Path, 'mkdir') as mock_mkdir:
            logger = FileSecurityLogger()
            assert logger.log_dir == Path('./logs')
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_init_custom_dir(self):
        """Test initialization with custom log directory."""
        with patch.object(Path, 'mkdir') as mock_mkdir:
            logger = FileSecurityLogger('/custom/logs')
            assert logger.log_dir == Path('/custom/logs')
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_log_event_new_file(self, tmp_path):
        """Test log_event creates new file when none exists."""
        logger = FileSecurityLogger(log_dir=str(tmp_path))
        mock_details = {'test': 'data'}
        mock_user = 'testuser'

        with patch('builtins.open', mock_open()) as mock_file, \
             patch('json.dump') as mock_dump, \
             patch('json.load', side_effect=FileNotFoundError), \
             patch('src.agent_telegram.security.logger.datetime') as mock_dt:
            mock_dt.now.return_value.isoformat.return_value = '2026-02-06T00:00:00'
            result = logger.log_event('TEST_EVENT', mock_details, user=mock_user)

        # Verify result structure
        assert 'timestamp' in result
        assert result['event_type'] == 'TEST_EVENT'
        assert result['user'] == mock_user
        assert result['details'] == mock_details
        assert result['threat_level'] == 'low'
        assert result['action_taken'] == 'logged'

        # Verify file operations
        # (mock assertions can be added)

    def test_log_event_existing_file(self, tmp_path):
        """Test log_event appends to existing file."""
        logger = FileSecurityLogger(log_dir=str(tmp_path))
        existing_logs = [{'old': 'log'}]

        with patch('builtins.open', mock_open()) as mock_file, \
             patch('json.dump') as mock_dump, \
             patch('json.load', return_value=existing_logs):
            result = logger.log_event('TEST_EVENT', {'new': 'data'})

        # Verify json.dump was called with list containing old and new logs
        call_args = mock_dump.call_args
        dumped_list = call_args[0][0]
        assert len(dumped_list) == 2
        assert dumped_list[0] == existing_logs[0]
        assert dumped_list[1]['event_type'] == 'TEST_EVENT'

    def test_log_threat_detected(self):
        """Test log_threat_detected calls log_event with correct parameters."""
        logger = FileSecurityLogger()
        with patch.object(logger, 'log_event') as mock_log_event:
            logger.log_threat_detected('information_fishing', 'user input', 'response', user='testuser')
            mock_log_event.assert_called_once()
            args, kwargs = mock_log_event.call_args
            assert args[0] == 'THREAT_DETECTED_INFORMATION_FISHING'
            assert kwargs['threat_level'] == 'medium'
            assert kwargs['user'] == 'testuser'
            assert 'user_input' in kwargs['details']

    def test_log_profile_access(self):
        """Test log_profile_access calls log_event with correct parameters."""
        logger = FileSecurityLogger()
        with patch.object(logger, 'log_event') as mock_log_event:
            logger.log_profile_access('target_user', accessed_by='admin', purpose='audit')
            mock_log_event.assert_called_once()
            args, kwargs = mock_log_event.call_args
            assert args[0] == 'PROFILE_ACCESS'
            assert kwargs['threat_level'] == 'low'
            assert kwargs['user'] == 'target_user'
            assert kwargs['details']['profile_accessed'] == 'target_user'

    def test_log_secret_verification_success(self):
        """Test secret verification success."""
        logger = FileSecurityLogger()
        with patch.object(logger, 'log_event') as mock_log_event:
            logger.log_secret_verification('user', success=True, attempts=1)
            mock_log_event.assert_called_once()
            args, kwargs = mock_log_event.call_args
            assert args[0] == 'SECRET_VERIFICATION_SUCCESS'
            assert kwargs['threat_level'] == 'low'
            assert kwargs['details']['success'] is True

    def test_log_secret_verification_failure(self):
        """Test secret verification failure."""
        logger = FileSecurityLogger()
        with patch.object(logger, 'log_event') as mock_log_event:
            logger.log_secret_verification('user', success=False, attempts=3)
            mock_log_event.assert_called_once()
            args, kwargs = mock_log_event.call_args
            assert args[0] == 'SECRET_VERIFICATION_FAILED'
            assert kwargs['threat_level'] == 'high'
            assert kwargs['details']['success'] is False
```

## Next Steps
1. Review this plan with the user.
2. If approved, switch to Code mode to implement the test file.
3. Run the tests to verify nothing broke.
4. Update any failing tests accordingly.

## Notes
- The existing integration tests (`test_security_refactor.py`, `test_security_legacy.py`) should continue to pass.
- Ensure the global `security_logger` instance still works.
- Consider adding a test for the abstract `SecurityLogger` interface (optional).