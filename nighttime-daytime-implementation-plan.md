# Nighttime/Daytime Implementation Plan

## Overview
Implement game phase tracking and conditional tool availability for the One Night Werewolf game, allowing agents to perform role-specific nighttime actions during the night phase and transitioning to discussion/voting during the day phase.

## Current State Analysis

### Existing Components
- **GameContext**: Manages players, conversation, center cards, role assignments
- **BaseAgent**: Base class with common tools (inquire_about_another_player)
- **Role-specific Agents**: Werewolf, Seer, Robber, Troublemaker, etc.
- **Setup System**: Game initialization and agent creation

### Missing Components
- ❌ Game phase tracking (Night/Day)
- ❌ Phase-specific tool availability
- ❌ Nighttime action orchestration
- ❌ Phase transition logic

## Implementation Plan

### Phase 1: Core Game Phase System

#### 1.1 Add Game Phase Tracking to GameContext ✅
- [x] Add `_is_nighttime` boolean field to GameContext (defaults to True)
- [x] Add `night_phase_order` to track which roles act in what order
- [x] Add `night_actions_completed` dict to track completed actions
- [x] Add methods:
  - `set_nighttime(is_night: bool)`
  - `is_nighttime() -> bool` (returns the boolean field)
  - `is_daytime() -> bool` (returns `not self._is_nighttime`)
  - `mark_night_action_completed(role: str)`
  - `is_night_action_completed(role: str) -> bool`
  - `get_next_night_role() -> Optional[str]`

#### 1.2 Define Night Phase Order ✅
```python
NIGHT_PHASE_ORDER = [
    "werewolf",      # Werewolves see each other
    "minion",        # Minion sees werewolves  
    "mason",         # Masons see each other
    "seer",          # Seer looks at player or center cards
    "robber",        # Robber swaps with player
    "troublemaker",  # Troublemaker swaps two other players
    "drunk",         # Drunk swaps with center card
    "insomniac"      # Insomniac checks their final role
]
```
*(Already implemented in 1.1)*

### Phase 2: Nighttime Tool System

#### 2.1 Create Nighttime-Specific Tools
For each role that has nighttime actions, create specific tools:

- **Werewolf**: `identify_other_werewolves()` - See other werewolves
- **Minion**: `identify_werewolves()` - See werewolves (but not other minions)
- **Mason**: `identify_other_masons()` - See other masons
- **Seer**: `look_at_player_card(player_name)`, `look_at_center_cards(positions)`
- **Robber**: `rob_player(player_name)` - Swap roles and learn new role
- **Troublemaker**: `swap_two_players(player1, player2)` - Swap two other players' roles
- **Drunk**: `swap_with_center_card(position)` - Swap with center card (don't see new role)
- **Insomniac**: `check_final_role()` - See current role after all swaps

#### 2.2 Tool Availability Logic
- [ ] Add `is_tool_available()` method to BaseAgent
- [ ] Check game phase before allowing tool use
- [ ] Add role-specific nighttime tools to each agent class
- [ ] Disable nighttime tools during daytime

### Phase 3: Night Phase Orchestration

#### 3.1 Night Phase Manager
- [ ] Create `NightPhaseManager` class
- [ ] Implement sequential nighttime actions by role order
- [ ] Handle role-specific logic (e.g., multiple werewolves, no masons present)
- [ ] Track completed nighttime actions

#### 3.2 Integration with Setup
- [ ] Modify setup.py to initialize game in nighttime phase
- [ ] Add night phase execution after game setup
- [ ] Transition to day phase after all night actions complete

### Phase 4: Enhanced Agent Base Class

#### 4.1 Phase-Aware Tool System
- [ ] Modify `BaseAgent.call_tool()` to check phase restrictions
- [ ] Add `get_available_tools()` method that returns tools based on current phase
- [ ] Add tool validation before execution

#### 4.2 Personal Knowledge Updates
- [ ] Update `personal_knowledge` when nighttime actions are performed
- [ ] Ensure agents remember what they learned during the night
- [ ] Handle role swaps and identity changes

### Phase 5: Game Flow Updates

#### 5.1 Main Game Loop
- [ ] Update main game execution to handle phases
- [ ] Night phase (`is_nighttime=True`): Execute nighttime actions in order
- [ ] Day phase (`is_nighttime=False`): Allow discussion and voting
- [ ] Add phase transition messaging

#### 5.2 Conversation History
- [ ] Track phase-specific events in conversation history
- [ ] Separate nighttime actions (private) from daytime discussion (public)
- [ ] Add phase markers in conversation flow

## Technical Details

### GameContext Extensions
```python
class GameContext(BaseModel):
    # ... existing fields ...
    is_nighttime: bool = True
    night_actions_completed: Dict[str, bool] = Field(default_factory=dict)
    role_swaps_this_night: List[Dict] = Field(default_factory=list)
```

### Tool Availability Check
```python
def is_tool_available(self, tool_name: str) -> bool:
    if tool_name in self.nighttime_tools:
        return self.game_context.is_nighttime()
    return True  # Daytime tools always available
```

### Night Action Example
```python
def look_at_player_card(self, player_name: str, game_context: GameContext):
    if not game_context.is_nighttime():
        return "This action can only be performed during nighttime."
    
    target_player = game_context.get_player_by_name(player_name)
    if target_player:
        role = target_player.current_role
        self.personal_knowledge.append(f"I saw that {player_name} has the {role} card.")
        return f"You see that {player_name} has the {role} card."
```

## Testing Strategy

### Unit Tests
- [ ] Test phase transitions
- [ ] Test tool availability logic
- [ ] Test nighttime action execution
- [ ] Test role swap mechanics

### Integration Tests
- [ ] Test complete night phase execution
- [ ] Test phase-aware tool restrictions
- [ ] Test multi-agent nighttime interactions

### Game Flow Tests
- [ ] Test full game from night to day
- [ ] Test various role combinations
- [ ] Test edge cases (no werewolves, etc.)

## Implementation Notes

### Order of Implementation
1. Start with GameContext phase tracking
2. Add tool availability checks
3. Implement simple nighttime tools (Seer, Insomniac)
4. Add complex tools with swapping (Robber, Troublemaker, Drunk)
5. Handle multi-agent interactions (Werewolves, Masons)
6. Complete integration and testing

### Edge Cases to Handle
- No werewolves in game (Minion gets nothing)
- Only one mason (Mason gets nothing)
- Player trying to rob themselves
- Invalid center card positions
- Tool calls during wrong phase

## Success Criteria
- [ ] Game correctly tracks night/day phases using boolean flag
- [ ] Agents can only use nighttime tools when `is_nighttime=True`
- [ ] All role-specific nighttime actions work correctly
- [ ] Role swaps are tracked and reflected in game state
- [ ] Personal knowledge is updated based on nighttime actions
- [ ] Smooth transition from night phase (`is_nighttime=True`) to day phase (`is_nighttime=False`)
- [ ] Comprehensive test coverage for all scenarios

## Next Steps
1. Implement GameContext phase tracking
2. Create basic tool availability system
3. Add simple nighttime tools for testing
4. Gradually expand to more complex interactions

---

## Implementation Log
*Track progress and notes as we work through the plan*

### 2024-12-19
- ✅ Created implementation plan
- ✅ Refined Phase 1 approach: simplified to use single boolean `is_nighttime` instead of string-based phases
- ✅ **Completed Phase 1.1**: Added game phase tracking to GameContext
  - Added `_is_nighttime` boolean field (defaults to True)
  - Added `NIGHT_PHASE_ORDER` constant with role order
  - Added `night_phase_order` and `night_actions_completed` fields
  - Added phase management methods: `set_nighttime()`, `is_nighttime()`, `is_daytime()`
  - Added night action tracking methods: `mark_night_action_completed()`, `is_night_action_completed()`, `get_next_night_role()`
- ✅ **Completed Phase 1.2**: Night phase order already implemented in 1.1
- 🎯 **Phase 1 Complete!** Game context now has full phase tracking capability
- ✅ **Completed Werewolf Proof of Concept (Phase 2.1)**: 
  - Automatic night actions (no tools needed)
  - House rule: lone werewolf gets second center card if first is werewolf
  - Night knowledge integrated into system prompt
  - Proper action completion tracking
- ✅ **Completed Minion Night Action (Phase 2.2)**:
  - Automatic identification of all werewolves
  - Handles no-werewolf scenario appropriately
  - Night knowledge integrated into system prompt
  - Follows same pattern as werewolf implementation
- ✅ **Completed Mason Night Action (Phase 2.3)**:
  - Automatic identification of other masons
  - Handles single mason scenario appropriately
  - Night knowledge integrated into system prompt  
  - Clean, concise messaging consistent with other roles
- ✅ **Completed Seer Investigation Tool (Phase 2.4)**:
  - Interactive nighttime tool (not automatic)
  - Two investigation options: player or center cards
  - Proper OpenAI function calling implementation
  - Strategic choice left to the agent
  - Personal knowledge integration
  - **Clean Abstraction**: `get_forced_nighttime_tool()` method returns `self.nighttime_tool` (singular)
  - **Phase-Aware System Prompts**: Different instructions for night vs day
  - **Forced Tool Choice**: `tool_choice` parameter during nighttime for agents that need it
           - ✅ **Completed Robber Swap Tool (Phase 2.5)**:
             - Interactive nighttime tool for strategic card swapping
             - Player name-based interface (realistic agent interaction)
             - Duplicate name handling via `resolve_player_name_to_id`
             - Personal knowledge integration
             - **Clean Separate Prompts**: Distinct `_get_nighttime_prompt()` and `_get_daytime_prompt()` methods
             - **Code Quality**: Refactored player list logic into `GameContext.get_other_player_names_in_text()`
           - ✅ **Completed Insomniac Automatic Role Check (Phase 2.6)**:
             - Automatic night action (no tools needed)
             - Checks final role after all other night actions complete
             - Detects if role changed during the night
             - Personal knowledge integration
             - **Simplified Design**: Single system prompt (no nighttime prompt needed)
             - Follows same pattern as Mason and Werewolf
           - ✅ **Completed Troublemaker Swap Tool (Phase 2.7)**:
             - Interactive nighttime tool for strategic player swapping
             - Player name-based interface (two players: player1_name, player2_name)
             - Duplicate name handling via `resolve_player_name_to_id` 
             - Personal knowledge integration
             - Clean separate nighttime/daytime prompts
             - Comprehensive error handling (self-swap, same player, non-existent players)
             - Follows same pattern as Seer and Robber tools
           - ✅ **Code Quality Improvement - Centralized Knowledge Management**:
             - **Elegant Solution**: All tool functions now focus purely on logic
             - **BaseAgent.call_tool**: Automatically appends successful results to `personal_knowledge`
             - **DRY Principle**: Eliminated duplicate knowledge management code across tools
             - **Consistent Behavior**: All tools get the same knowledge handling
             - **Error Filtering**: Automatically skips error messages and empty results
           - ✅ **Completed All Remaining Roles (Phase 2.8)**:
             
             **Drunk Agent (Tool-Based)**:
             - Interactive nighttime tool for strategic center card swapping
             - Center position selection (0, 1, or 2)
             - No knowledge of new role (realistic drunk behavior)
             - Phase-aware system prompts
             - Centralized knowledge management
             - Added `swap_player_with_center()` method to GameContext
             
             **Villager Agent (No Night Action)**:
             - Clean system prompt with player list integration
             - Standard execute_night_action (no-op)
             - Follows simplified pattern like Insomniac
             
             **Hunter Agent (No Night Action)**:
             - Special elimination revenge ability documentation
             - Clean system prompt with strategic guidance
             - Standard execute_night_action (no-op)
             
             **Tanner Agent (No Night Action)**:
             - Unique win condition (must be eliminated to win)
             - Strategic suspicious behavior guidance
             - Standard execute_night_action (no-op)
           
           - ✅ **Final Architecture Improvement - Tool Registry Pattern**:
             - **Problem**: Long chain of if/elif statements in `BaseAgent.call_tool` (60+ lines)
             - **Solution**: Dynamic tool registry with configuration-driven function calls
             - **Benefits**: 
               * Easy to add new tools (just add registry entry)
               * Clean separation of configuration vs execution
               * Dynamic imports only when needed
               * Centralized argument mapping
               * Better error handling and debugging
               * Much more maintainable and extensible
             - **Pattern**: `{"module": "...", "function": "...", "args": lambda: {...}}`
           
           - 🎉 **Phase 2 Complete - All Roles Implemented with Clean Architecture!**