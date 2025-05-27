import os
import sys
import argparse
from .utils import get_config, logger, get_agent
from agno.agent import RunResponse

# turn off telemetry
os.environ["AGNO_TELEMETRY"] = "false"

def main(arguments):
    config=get_config(arguments.environment)
    # what are we asked to do
    playbook = arguments.playbook
    # see if the playbook file exists
    if not os.path.exists(playbook):
        logger.error(f"Playbook {playbook} not found")
        sys.exit(1)

    # create the agent
    agent = get_agent(config)
    # load the playbook
    with open(playbook, "r") as f:
        playbook_content = f.read()
    agent.instructions = playbook_content
    response=agent.run("hi")
    logger.info(f"Response: {response.content}")



