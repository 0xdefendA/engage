import os
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open
from engage.main import main
import subprocess
import re


def test_main_playbook_not_found():
    mock_args = MagicMock()
    mock_args.playbook = "nonexistent.yml"
    mock_args.environment = "dev"

    with patch("engage.main.get_config") as mock_get_config, patch(
        "engage.main.logger"
    ) as mock_logger, patch("os.path.exists", return_value=False), pytest.raises(
        SystemExit
    ) as exit_info:

        main(mock_args)

        mock_logger.error.assert_called_once_with("Playbook nonexistent.yml not found")
        assert exit_info.value.code == 1


def test_main_playbook_exists():
    mock_args = MagicMock()
    mock_args.playbook = "existing.yml"
    mock_args.environment = "prod"
    mock_config = {"model": {"provider": "google", "model_name": "gemini-1.5-flash"}}
    mock_playbook_content = (
        "# Test Playbook\nThis is a test playbook for security operations."
    )

    with patch(
        "engage.main.get_config", return_value=mock_config
    ) as mock_get_config, patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=mock_playbook_content)
    ):

        # Mock the agent instance and its run method
        mock_agent = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_agent.run.return_value = mock_response

        main(mock_args)

        mock_get_config.assert_called_once_with("prod")


def test_main_with_empty_playbook():
    mock_args = MagicMock()
    mock_args.playbook = ""
    mock_args.environment = "test"

    with patch("engage.main.get_config") as mock_get_config, patch(
        "engage.main.logger"
    ) as mock_logger, patch("os.path.exists", return_value=False), pytest.raises(
        SystemExit
    ) as exit_info:

        main(mock_args)

        mock_logger.error.assert_called_once_with("Playbook  not found")
        assert exit_info.value.code == 1


def test_environment_variable_set():
    """Test that AGNO_TELEMETRY environment variable is set to false"""
    # Import the module to trigger the environment variable setting
    assert os.environ.get("AGNO_TELEMETRY") == "false"


def test_cli_day_of_week(capsys):
    # Run engage.py with the specified playbook and environment
    result = subprocess.run(
        [
            "python",
            "engage.py",
            "--playbook",
            "./engage/playbooks/test_list_tools.md",
            "--environment",
            "test",
        ],
        capture_output=True,
        text=True,
        check=True,  # Raise an exception for non-zero exit codes
    )

    # Assert that the output contains the current day of the week
    day_of_week_pattern = r"the current day of the week is (\w+)"
    assert re.search(day_of_week_pattern, result.stdout, re.IGNORECASE)
