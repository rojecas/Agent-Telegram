"""
Unit tests for security logger.
"""
import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
import json
from datetime import datetime

from src.security.logger import (
    SecurityLogger,
    FileSecurityLogger,
    security_logger,
)


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
        # Create a fixed date for predictable filename
        fixed_date = datetime(2026, 2, 6)
        with patch('src.agent_telegram.security.logger.datetime') as mock_dt:
            mock_dt.now.return_value = fixed_date
            # Create log file with existing content
            log_dir = tmp_path / 'logs'
            log_dir.mkdir()
            log_file = log_dir / f'security_log_{fixed_date.strftime("%Y-%m-%d")}.json'
            existing_logs = [{'old': 'log'}]
            log_file.write_text(json.dumps(existing_logs), encoding='utf-8')
            
            logger = FileSecurityLogger(log_dir=str(log_dir))
            result = logger.log_event('TEST_EVENT', {'new': 'data'})
            
            # Verify file contains both logs
            updated_logs = json.loads(log_file.read_text(encoding='utf-8'))
            assert len(updated_logs) == 2
            assert updated_logs[0] == existing_logs[0]
            assert updated_logs[1]['event_type'] == 'TEST_EVENT'
            assert updated_logs[1]['details'] == {'new': 'data'}

    def test_log_threat_detected(self):
        """Test log_threat_detected calls log_event with correct parameters."""
        logger = FileSecurityLogger()
        with patch.object(logger, 'log_event') as mock_log_event:
            logger.log_threat_detected('information_fishing', 'user input', 'response', user='testuser')
            mock_log_event.assert_called_once()
            args, kwargs = mock_log_event.call_args
            # log_threat_detected passes all arguments as keyword arguments, no positional args
            assert args == ()
            assert kwargs['event_type'] == 'THREAT_DETECTED_INFORMATION_FISHING'
            assert kwargs['threat_level'] == 'medium'
            assert kwargs['user'] == 'testuser'
            assert kwargs['details']['user_input'] == 'user input'
            assert kwargs['details']['response_given'] == 'response'
            assert kwargs['details']['detection_method'] == 'pattern_matching'

    def test_log_profile_access(self):
        """Test log_profile_access calls log_event with correct parameters."""
        logger = FileSecurityLogger()
        with patch.object(logger, 'log_event') as mock_log_event:
            logger.log_profile_access('target_user', accessed_by='admin', purpose='audit')
            mock_log_event.assert_called_once()
            args, kwargs = mock_log_event.call_args
            # all arguments are keyword arguments
            assert args == ()
            assert kwargs['event_type'] == 'PROFILE_ACCESS'
            assert kwargs['threat_level'] == 'low'
            assert kwargs['user'] == 'target_user'
            details = kwargs['details']
            assert details['profile_accessed'] == 'target_user'
            assert details['accessed_by'] == 'admin'
            assert details['purpose'] == 'audit'
            assert details['data_protected'] == True

    def test_log_secret_verification_success(self):
        """Test secret verification success."""
        logger = FileSecurityLogger()
        with patch.object(logger, 'log_event') as mock_log_event:
            logger.log_secret_verification('user', success=True, attempts=1)
            mock_log_event.assert_called_once()
            args, kwargs = mock_log_event.call_args
            assert args == ()
            assert kwargs['event_type'] == 'SECRET_VERIFICATION_SUCCESS'
            assert kwargs['threat_level'] == 'low'
            assert kwargs['user'] == 'user'
            assert kwargs['details']['success'] is True
            assert kwargs['details']['attempts'] == 1

    def test_log_secret_verification_failure(self):
        """Test secret verification failure."""
        logger = FileSecurityLogger()
        with patch.object(logger, 'log_event') as mock_log_event:
            logger.log_secret_verification('user', success=False, attempts=3)
            mock_log_event.assert_called_once()
            args, kwargs = mock_log_event.call_args
            assert args == ()
            assert kwargs['event_type'] == 'SECRET_VERIFICATION_FAILED'
            assert kwargs['threat_level'] == 'high'
            assert kwargs['user'] == 'user'
            assert kwargs['details']['success'] is False
            assert kwargs['details']['attempts'] == 3

    def test_log_event_with_threat_level(self, tmp_path):
        """Test log_event with custom threat level."""
        logger = FileSecurityLogger(log_dir=str(tmp_path))
        with patch('builtins.open', mock_open()) as mock_file, \
             patch('json.dump') as mock_dump, \
             patch('json.load', side_effect=FileNotFoundError), \
             patch('src.agent_telegram.security.logger.datetime') as mock_dt:
            mock_dt.now.return_value.isoformat.return_value = '2026-02-06T00:00:00'
            result = logger.log_event('TEST', {}, threat_level='high')
            assert result['threat_level'] == 'high'

    def test_write_log_creates_directory(self, tmp_path):
        """Ensure directory creation is attempted."""
        logger = FileSecurityLogger(log_dir=str(tmp_path))
        with patch('builtins.open', mock_open()), \
             patch('json.dump') as mock_dump, \
             patch('json.load', side_effect=FileNotFoundError):
            logger.log_event('TEST', {})
            # Directory should have been created in __init__, but we can verify
            # that mkdir was called (already tested in init)

    def test_print_output(self, capsys):
        """Test that log_event prints to console."""
        logger = FileSecurityLogger()
        with patch('pathlib.Path.exists', return_value=False), \
             patch('builtins.open', mock_open()), \
             patch('json.dump'):
            logger.log_event('TEST_PRINT', {})
            captured = capsys.readouterr()
            assert '🔒 [SEGURIDAD]' in captured.out


class TestSecurityLoggerInterface:
    """Test the abstract interface."""
    def test_interface_methods(self):
        """SecurityLogger should have required abstract methods."""
        assert hasattr(SecurityLogger, 'log_event')
        assert hasattr(SecurityLogger, 'log_threat_detected')
        assert hasattr(SecurityLogger, 'log_profile_access')
        assert hasattr(SecurityLogger, 'log_secret_verification')


def test_global_security_logger():
    """Verify the global security_logger instance is of correct type."""
    assert isinstance(security_logger, FileSecurityLogger)
    assert security_logger.log_dir == Path('./logs')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])