import json
import random
from typing import List
from game_context import GameContext, Role
from game_agents.agent_registry import ROLE_TO_AGENT_CLASS
from game_agents.base_agent import BaseAgent


def load_game_config() -> dict:
    """Load game configuration from JSON file"""
    with open('game_config.json', 'r') as f:
        return json.load(f)


def create_agents_from_config(game_config: dict) -> List[BaseAgent]:
    roles = game_config["available_roles"].copy()
    random.shuffle(roles)
    
    num_human_players = game_config["number_human_players"]
    all_agents = []
    
    for i, role in enumerate(roles):
        if i < num_human_players:
            role = Role(role.lower())
            agent_cls = role.get_agent_class()
            agent_instance = agent_cls(role=role, player_id=i, player_name=f"Human {i + 1}", is_ai=False)
        else:
            role = Role(role.lower())
            agent_cls = role.get_agent_class()
            agent_instance = agent_cls(role=role, player_id=i, player_name=f"AI {i - num_human_players + 1}", is_ai=True)
        all_agents.append(agent_instance)
    
    return all_agents


def setup_game_context(game_config: dict) -> GameContext:
    agents = create_agents_from_config(game_config)
    game_context = GameContext()

    for agent in agents:
        game_context.players[agent.player_id] = agent
    
    all_roles = game_config["available_roles"].copy()
    random.shuffle(all_roles)
    
    num_players = len(agents)
    player_roles = all_roles[:num_players]
    center_cards = all_roles[num_players:]
    
    player_role_assignments = {}
    for i, role_str in enumerate(player_roles):
        player_role_assignments[i] = Role(role_str)
    
    center_role_enums = [Role(role_str) for role_str in center_cards]
    
    game_context.initialize_game_roles(player_role_assignments, center_role_enums)
    
    return game_context


if __name__ == "__main__":
    # Set a dummy API key for testing setup without actually calling OpenAI
    import os
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"
    
    # Load config and create complete game context
    config = load_game_config()
    game_context = setup_game_context(config)
    
    print("=== GAME SETUP COMPLETE ===")
    print(f"Total players: {len(game_context.players)}")
    print()
    
    print("Players (Agents):")
    for player_id, agent in game_context.players.items():
        current_role = game_context.get_player_current_role(player_id)
        role_name = current_role.value if current_role else "Unknown"
        print(f"  {agent.player_name} (ID: {agent.player_id}) - Role: {role_name} - AI: {agent.is_ai} - Agent: {type(agent).__name__}")
    
    print()
    print("Center cards:")
    for i in range(3):
        center_role = game_context.get_center_card_role(i)
        role_name = center_role.value if center_role else "Empty"
        print(f"  Center {i + 1}: {role_name}")
    
    print()
    print("Role assignments summary:")
    summary = game_context.get_role_assignments_summary()
    print(f"  Player roles: {summary['player_roles']}")
    print(f"  Center cards: {summary['center_cards']}")
    
    print()
    print("GameContext created successfully!")
    print(f"  Players in context: {len(game_context.players)}")
    print(f"  Conversation history initialized: {game_context.conversation is not None}")
