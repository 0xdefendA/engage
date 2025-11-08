import os
import sys
import argparse
from .utils import get_config, logger, get_agent, run_agent

# turn off telemetry everywhere
os.environ["AGNO_TELEMETRY"] = "false"


def main(arguments):
    # what environment/configuration are we using
    config = get_config(arguments.environment)
    # what are we asked to do
    playbook = arguments.playbook
    # see if the playbook file exists
    if not os.path.exists(playbook):
        logger.error(f"Playbook {playbook} not found")
        sys.exit(1)

    # create the agent
    agent = get_agent(config, arguments)

    # run the agent
    response = run_agent(agent=agent, playbook=playbook)

    # Print the response content to stdout
    print(f"{response.content}")
