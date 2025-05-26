import logging
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
import yaml

from agno.models.base import Model
from agno.agent import Agent, AgentMemory
from agno.run.response import RunEvent, RunResponse

from agno.memory.classifier import MemoryClassifier
from agno.memory.summarizer import MemorySummarizer
from agno.memory.manager import MemoryManager
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.memory.db.sqlite import SqliteMemoryDb
from agno.tools.file import FileTools
from agno.tools.decorator import tool
from pathlib import Path


agent_storage: str = "tmp/agent_storage.db"
agent_memory: str = "tmp/agent_memory.db"
agent_database: str = "tmp/agent_database.db"



# tools
@tool
def day_of_week() -> str:
    """Get the current day of the week.
    Returns:
        str: The current day of the week.
    """
    now = datetime.datetime.now()
    return now.strftime("%A")


def get_config(environment="development"):
    # load config file, expecting config.environment.yaml
    my_config = {}
    try:
        with open(f"./files/config.{environment}.yaml") as f:
            my_config = yaml.safe_load(f.read())
    except Exception as e:
        logger.error(f"Exception retrieving config: {e}")
    return my_config


# utility to stream agno run responses to shiny
def as_stream(response):
    for chunk in response:
        if isinstance(chunk, RunResponse) and isinstance(chunk.content, str):
            if chunk.event == RunEvent.run_response:
                yield chunk.content


# select the provider and model
def get_model(provider: str, model_name: str) -> Model:
    if provider == "openai":
        try:
            from agno.models.openai import OpenAIChat

            return OpenAIChat(id=model_name)
        except ImportError:
            print("OpenAI support requires additional packages. Install with:")
            print("pip install openai")
            raise SystemExit(1)

    elif provider == "ollama":
        try:
            from agno.models.ollama import Ollama

            return Ollama(id=model_name)
        except ImportError:
            print("Ollama support requires additional packages. Install with:")
            print("pip install ollama")
            raise SystemExit(1)
    else:  # default is google
        try:
            from app.gemini_models import get_gemini_model

            return get_gemini_model()
        except ImportError:
            print("Google/Gemini support requires additional packages. Install with:")
            print("pip install google-genai")
            raise SystemExit(1)


def get_agent(model_choice: Model, state) -> Agent:

    # TODO customize the agent per provider
    # llama has trouble with history including tool messages and appears to need more guidance for using tools
    # gemini needs the tool messages to not have the tool as role
    # gemini via api key has trouble if show tool calls is true, via vertex it does not

    # TODO toggle debug mode from command line switch

    agent = Agent(
        model=model_choice,
        tools=[
            
        ],
        session_id="engate_agent",
        session_name="engate_agent",
        user_id="engate_agent",
        markdown=True,
        show_tool_calls=False,
        telemetry=False,
        monitoring=False,
        debug_mode=False,
        instructions=[
,
        ],
        description="You are an expert in computer security and data analysis.",
        storage=SqliteAgentStorage(
            table_name="engate_agent", db_file=agent_storage
        ),
        # Adds the current date and time to the instructions
        add_datetime_to_instructions=True,
        # Adds the history of the conversation to the messages
        add_history_to_messages=True,
        # Number of history responses to add to the messages
        num_history_responses=50,
        memory=AgentMemory(
            db=SqliteMemoryDb(db_file=agent_memory),
            create_user_memories=True,
            create_session_summary=True,
            update_user_memories_after_run=True,
            update_session_summary_after_run=True,
            classifier=MemoryClassifier(model=model_choice),
            summarizer=MemorySummarizer(model=model_choice),
            manager=MemoryManager(model=model_choice),
        ),
    )

    return agent
