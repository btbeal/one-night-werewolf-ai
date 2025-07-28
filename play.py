NUM_PLAYERS = 5
QUORUM_FOR_VOTING = (NUM_PLAYERS >> 1) + 1
MAX_ROUNDS_PRIOR_TO_VOTING = 10

current_round = 0
players_ready_to_vote = 0
while current_round < MAX_ROUNDS_PRIOR_TO_VOTING and players_ready_to_vote < QUORUM_FOR_VOTING:
    pass