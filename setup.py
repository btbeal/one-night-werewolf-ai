import json
import random
from game_context.game_state import PlayerState


with open('game_config.json', 'r') as f:
    game_config = json.load(f)

roles = game_config["available_roles"]
random.shuffle(roles)

num_human_players = game_config["number_human_players"]
players_accounted_for = 0
all_players = []
for i, role in enumerate(roles):
    if i < num_human_players:
        player = PlayerState(player_id=i, player_name=f"Human {i + 1}", initial_role=role)
        all_players.append(player)
    else:
        player = PlayerState(player_id=i, player_name=f"AI {i - num_human_players + 1}", initial_role=role, is_ai=True)
        all_players.append(player)

print(all_players)
