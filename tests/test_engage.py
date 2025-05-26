import pytest
import os
import sys
from unittest.mock import patch, mock_open, MagicMock
from argparse import Namespace

# Add the engage directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engage.engage import main


class TestEngage:
    
    def test_environment_variable_set(self):
        """Test that AGNO_TELEMETRY environment variable is set to false"""
        # Import the module to trigger the environment variable setting
        import engage.engage
        assert os.environ.get("AGNO_TELEMETRY") == "false"
    
    @patch('engage.engage.argparse.ArgumentParser.parse_args')
    @patch('engage.engage.get_config')
    @patch('engage.engage.logger')
    @patch('os.path.exists')
    def test_main_with_valid_playbook(self, mock_exists, mock_logger, mock_get_config, mock_parse_args):
        """Test main function with valid playbook file"""
        # Setup mocks
        mock_parse_args.return_value = Namespace(
            environment='development',
            playbook='/path/to/valid/playbook.md'
        )
        mock_get_config.return_value = {'some': 'config'}
        mock_exists.return_value = True
        
        # Call main function
        main()
        
        # Assertions
        mock_parse_args.assert_called_once()
        mock_get_config.assert_called_with('development')
        mock_exists.assert_called_with('/path/to/valid/playbook.md')
        mock_logger.error.assert_not_called()
    
    @patch('engage.engage.argparse.ArgumentParser.parse_args')
    @patch('engage.engage.get_config')
    @patch('engage.engage.logger')
    @patch('os.path.exists')
    @patch('sys.exit')
    def test_main_with_invalid_playbook(self, mock_exit, mock_exists, mock_logger, mock_get_config, mock_parse_args):
        """Test main function with invalid playbook file"""
        # Setup mocks
        mock_parse_args.return_value = Namespace(
            environment='production',
            playbook='/path/to/invalid/playbook.md'
        )
        mock_get_config.return_value = {'some': 'config'}
        mock_exists.return_value = False
        
        # Call main function
        main()
        
        # Assertions
        mock_parse_args.assert_called_once()
        mock_get_config.assert_called_with('production')
        mock_exists.assert_called_with('/path/to/invalid/playbook.md')
        mock_logger.error.assert_called_with("Playbook /path/to/invalid/playbook.md not found")
        mock_exit.assert_called_once_with(1)
    
    @patch('engage.engage.argparse.ArgumentParser.parse_args')
    @patch('engage.engage.get_config')
    @patch('engage.engage.logger')
    @patch('os.path.exists')
    def test_main_with_test_environment(self, mock_exists, mock_logger, mock_get_config, mock_parse_args):
        """Test main function with test environment"""
        # Setup mocks
        mock_parse_args.return_value = Namespace(
            environment='test',
            playbook='/path/to/test/playbook.md'
        )
        mock_get_config.return_value = {'test': 'config'}
        mock_exists.return_value = True
        
        # Call main function
        main()
        
        # Assertions
        mock_get_config.assert_called_once_with('test')
        mock_exists.assert_called_with('/path/to/test/playbook.md')
    
    @patch('engage.engage.argparse.ArgumentParser.parse_args')
    def test_argument_parser_configuration(self, mock_parse_args):
        """Test that argument parser is configured correctly"""
        mock_parse_args.return_value = Namespace(
            environment='development',
            playbook='/path/to/playbook.md'
        )
        
        with patch('engage.engage.get_config'), \
             patch('engage.engage.logger'), \
             patch('os.path.exists', return_value=True):
            
            main()
            
        # Verify parse_args was called
        mock_parse_args.assert_called_once()
    
    @patch('engage.engage.main')
    def test_main_entry_point(self, mock_main):
        """Test that main is called when script is run directly"""
        # This tests the if __name__ == "__main__": block
        with patch('engage.engage.__name__', '__main__'):
            exec(open('engage/engage.py').read())