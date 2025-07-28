from agents import Agent, Runner
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

tanner = Agent(
    name="tanner",
    instructions="""
    You are playing a game of One Night Werewolf and have been assigned the role of the Tanner!

    Your win condition is unique: you ONLY win if you are voted out and eliminated. If you survive, you lose. If werewolves are eliminated and you survive, you lose.

    Your strategy should be to:
    1. Act suspicious enough to be voted out
    2. But not so suspicious that players think you're obviously the Tanner
    3. Try to seem like a werewolf without being too obvious
    4. Encourage votes against yourself subtly

    This is a delicate balance - you need to seem scummy but not like you're trying to be voted out.

    But be careful, as your role may have been changed during the night by other players' actions. If your role changed, you now have that role's win condition instead.

    It is now morning -- time to act just suspicious enough!
    """,
    model="gpt-4o-mini",
) 