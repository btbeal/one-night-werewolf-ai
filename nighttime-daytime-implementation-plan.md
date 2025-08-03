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
- ⏳ Ready for Phase 2: Nighttime Tool System