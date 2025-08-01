import json
import random
from typing import List
from game_context import GameContext, Role
from game_agents.agent_registry import AGENT_REGISTRY
from game_agents.base_agent import BaseAgent


def load_game_config() -> dict:
    """Load game configuration from JSON file"""
    with open('game_config.json', 'r') as f:
        return json.load(f)


def create_agents_from_config(game_config: dict) -> List[BaseAgent]:
    # Calculate number of players: all available roles minus 3 (for center cards)
    total_roles = len(game_config["available_roles"])
    num_players = total_roles - 3
    
    if num_players <= 0:
        raise ValueError("Must have at least 4 roles to create 1 player and 3 center cards")
    
    if num_players < 3:
        raise ValueError(f"Must have at least 3 players, but only {num_players} players calculated from {total_roles} total roles")
    
    if num_players > 10:
        raise ValueError(f"Cannot have more than 10 players, but {num_players} players calculated from {total_roles} total roles")
    
    roles = game_config["available_roles"].copy()
    random.shuffle(roles)
    
    player_roles = roles[:num_players]
    
    num_human_players = game_config["number_human_players"]
    if num_human_players > num_players:
        raise ValueError(f"Cannot have {num_human_players} human players when total players is {num_players}")
    
    all_agents = []
    
    for i, role in enumerate(player_roles):
        is_human = i < num_human_players
        role_enum = Role(role.lower())
        agent_cls = role_enum.get_agent_class()
        
        if is_human:
            agent_instance = agent_cls(player_id=i, player_name=f"Human {i + 1}", initial_role=role.lower(), is_ai=False)
        else:
            agent_instance = agent_cls(player_id=i, player_name=f"AI {i - num_human_players + 1}", initial_role=role.lower(), is_ai=True)
        
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
    center_cards = all_roles[num_players:] 
    center_role_enums = [Role(role_str.lower()) for role_str in center_cards]
    
    game_context.initialize_center_cards(center_role_enums)
    
    return game_context
