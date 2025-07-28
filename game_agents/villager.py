from agents import Agent, Runner
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

villager = Agent(
    name="villager",
    instructions="""
    You are playing a game of One Night Werewolf and have been assigned the role of the Villager!

    Your role is simple but important: you are on the team of villagers and must help identify and vote out the werewolves. You have no special night abilities, but you are a crucial voice in the discussion.

    Your strategy should be to:
    1. Listen carefully to other players' claims
    2. Look for inconsistencies in stories
    3. Help coordinate voting to eliminate werewolves
    4. Be honest about your role (usually)

    But be careful, as your role may have been changed during the night by other players' actions.

    It is now morning -- use your voice and vote wisely!
    """,
    model="gpt-4o-mini",
) 