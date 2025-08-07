import json
import random
from typing import List, Optional
from dotenv import load_dotenv
from game_agents.base_agent import BaseAgent
from game_agents.agent_registry import AGENT_REGISTRY
from game_context.game_context import GameContext, NIGHT_PHASE_ORDER
from game_context.roles import Role
from setup import load_game_config, setup_game_context

# Load environment variables
load_dotenv()

# Game constants
NUM_PLAYERS = 5
QUORUM_FOR_VOTING = (NUM_PLAYERS >> 1) + 1
MAX_ROUNDS_PRIOR_TO_VOTING = 10


class NightPhaseManager:
    """Manages the sequential execution of nighttime actions"""
    
    def __init__(self, game_context: GameContext):
        self.game_context = game_context
    
    def execute_night_phase(self) -> None:
        """Execute all nighttime actions in the proper order"""
        print("🌙 Night falls... The supernatural beings begin their work.")
        print("=" * 60)
        
        for role in NIGHT_PHASE_ORDER:
            if self.game_context.is_night_action_completed(role):
                continue
                
            # Find all players with this role
            players_with_role = []
            for player_id, player in self.game_context.players.items():
                if player.current_role.lower() == role:
                    players_with_role.append((player_id, player))
            
            if not players_with_role:
                # No players have this role, mark as completed
                self.game_context.mark_night_action_completed(role)
                continue
            
            print(f"\n🔮 {role.capitalize()} phase begins...")
            
            # Execute night action for each player with this role
            for player_id, player in players_with_role:
                self._execute_player_night_action(player, role)
            
            # Mark this role's night actions as completed
            self.game_context.mark_night_action_completed(role)
            print(f"✅ {role.capitalize()} phase completed.")
        
        print("\n🌅 The night phase is complete. Dawn breaks...")
        print("=" * 60)
    
    def _execute_player_night_action(self, player: BaseAgent, role: str) -> None:
        """Execute a single player's night action"""
        print(f"  → {player.player_name} ({role}) is taking their night action...")
        
        try:
            # Check if this role needs to use a tool interactively
            forced_tool = player.get_forced_nighttime_tool()
            
            if forced_tool:
                # Tool-based night action (Seer, Robber, Troublemaker, Drunk)
                self._execute_interactive_night_action(player, forced_tool, role)
            else:
                # Automatic night action (Werewolf, Minion, Mason, Insomniac, etc.)
                result = player.execute_night_action(self.game_context)
                if result and not result.startswith("As a"):  # Filter out role descriptions
                    print(f"    {result}")
        
        except Exception as e:
            print(f"    ❌ Error during {player.player_name}'s night action: {str(e)}")
    
    def _execute_interactive_night_action(self, player: BaseAgent, tool_name: str, role: str) -> None:
        """Execute an interactive night action using the player's AI to make decisions"""
        print(f"    🤖 {player.player_name} is deciding what to do...")
        
        try:
            # Get the nighttime-specific system prompt
            if hasattr(player, '_get_nighttime_prompt'):
                nighttime_prompt = player._get_nighttime_prompt(self.game_context)
            else:
                nighttime_prompt = f"You are the {role}. Use your {tool_name} tool to take your night action."
            
            # Have the AI agent decide what action to take
            response = player.act(
                prompt=nighttime_prompt,
                prompt_is_another_player_question=False,
                questioning_player_name="",
                game_state=self.game_context
            )
            
            if response.tool_calls_made:
                print(f"    ✨ {player.player_name} completed their night action")
                # The tool calls have already been processed and knowledge updated
            else:
                print(f"    ⚠️  {player.player_name} did not use any tools during their night phase")
                
        except Exception as e:
            print(f"    ❌ Error during {player.player_name}'s interactive night action: {str(e)}")


def run_game():
    """Main game execution function"""
    print("🐺 Welcome to One Night Werewolf AI! 🐺")
    print("=" * 60)
    
    # Load configuration and setup game
    print("📋 Loading game configuration...")
    game_config = load_game_config()
    print(f"   Available roles: {', '.join(game_config['available_roles'])}")
    
    print("🎲 Setting up game context...")
    game_context = setup_game_context(game_config)
    
    print("👥 Players in the game:")
    for player_id, player in game_context.players.items():
        print(f"   {player.player_name} - {player.current_role.capitalize()}")
    
    print("🃏 Center cards:")
    for i, card in enumerate(game_context.center_cards):
        print(f"   Position {i}: {card.value.capitalize()}")
    
    print("\n" + "=" * 60)
    
    # Execute night phase
    night_manager = NightPhaseManager(game_context)
    night_manager.execute_night_phase()
    
    # Transition to day phase
    game_context.set_nighttime(False)
    print("☀️  Day phase begins! Time for discussion and voting.")
    print("=" * 60)
    
    # Day phase simulation (basic structure for now)
    current_round = 0
    players_ready_to_vote = 0
    
    print("💬 Discussion phase begins...")
    print("   (In a full implementation, this would be the discussion and voting loop)")
    print(f"   Players will discuss for up to {MAX_ROUNDS_PRIOR_TO_VOTING} rounds")
    print(f"   Voting begins when {QUORUM_FOR_VOTING} players are ready")
    
    # For now, we'll just show the final game state
    print("\n📊 Final game state after night phase:")
    print("   Player roles (may have changed during night):")
    for player_id, player in game_context.players.items():
        initial_role = player.initial_role.capitalize()
        current_role = player.current_role.capitalize()
        role_change = "" if initial_role == current_role else f" (was {initial_role})"
        print(f"     {player.player_name}: {current_role}{role_change}")
    
    print("   Center cards (may have changed during night):")
    for i, card in enumerate(game_context.center_cards):
        print(f"     Position {i}: {card.value.capitalize()}")
    
    print("\n   Player knowledge gained during night:")
    for player_id, player in game_context.players.items():
        if player.personal_knowledge:
            print(f"     {player.player_name}:")
            for knowledge in player.personal_knowledge:
                print(f"       - {knowledge}")
        else:
            print(f"     {player.player_name}: No special knowledge gained")
    
    print("\n🎉 Night phase execution complete!")
    print("   The game is now ready for the discussion and voting phases.")


if __name__ == "__main__":
    run_game()