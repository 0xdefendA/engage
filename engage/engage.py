import os
import sys
import argparse
from utils import get_config, logger

# turn off telemetry
os.environ["AGNO_TELEMETRY"] = "false"

def main():
    parser = argparse.ArgumentParser(
        description="Engage - AI-powered SOC operations assistant"
    )
    parser.add_argument(
        "--environment",
        choices=["development", "test", "production"],
        default="development",
        help="Choose the configuration environment",
    )
    parser.add_argument(
        "--playbook",
        help="Which playbook to use",
        required=True,
    )


    arguments = parser.parse_args()
    config=get_config(arguments.environment)
    # what are we asked to do
    playbook = arguments.playbook
    # see if the playbook file exists
    if not os.path.exists(playbook):
        logger.error(f"Playbook {playbook} not found")
        sys.exit(1)



if __name__ == "__main__":
    main()