from openai import OpenAI
import os
import json
import textwrap
from typing import Optional
from pydantic import BaseModel
from game_context.game_context import GameContext
from game_context.messages import ConversationHistory

class ONWAgentResponse(BaseModel):
    """Response from the agent"""
    public_response: str
    private_thoughts: str
    tool_calls: list[dict] = []
    raw_response: str = ""

def inquire_about_another_player(player_name: str, question: str, game_context: GameContext, questioning_player_name: str):
    """
    Send a question to another player and get their response
    
    Args:
        player_name: Name of the player to question
        question: The question to ask
        game_context: Current game context containing all players
        questioning_player_name: Name of the player asking the question
        
    Returns:
        The response from the questioned player
    """
    target_player = game_context.get_player_by_name(player_name)
    
    if not target_player:
        return f"Player '{player_name}' not found in the game."
    
    try:
        response = target_player.act(
            prompt=question,
            prompt_is_another_player_question=True,
            questioning_player_name=questioning_player_name,
            game_state=game_context
        )
        return f"{player_name} responds: {response.public_response}"
    except Exception as e:
        return f"Error getting response from {player_name}: {str(e)}"

common_tools = [
    {
        "type": "function",
        "function": {
            "name": "inquire_about_another_player",
            "description": "Ask a direct question to another player in the game. Use this when you want to gather information, challenge someone's claims, or investigate suspicious behavior. The target player will respond based on their role and strategy - they may lie, tell the truth, or be evasive. This is a key tool for social deduction and information gathering.",
            "parameters": {
                "type": "object",
                "properties": {
                    "player_name": {
                        "type": "string", 
                        "description": "The exact name of the player you want to question. Make sure to use the exact name as it appears in the conversation history. Case sensitive."
                    },
                    "question": {
                        "type": "string", 
                        "description": "The specific question you want to ask. Be clear and direct. Examples: 'What role did you start with?', 'Did you see my card?', 'Why do you think Alice is suspicious?', 'Who do you plan to vote for?'"
                    },
                },
                "required": ["player_name", "question"],
                "additionalProperties": False
            }
        }
    }
]

class BaseAgent:
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool, model: str = "gpt-4o-mini", tools: list[dict] = []):
        self.model = model
        self.player_id = player_id
        self.player_name = player_name
        self.current_role = initial_role
        self.initial_role = initial_role
        self.personal_knowledge = []
        self.is_ai = is_ai
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tools = common_tools + tools
        self.nighttime_tool = None  # Single nighttime-only tool name
    
    def act(
            self,
            prompt: str,
            prompt_is_another_player_question: bool = False,
            questioning_player_name: str = "",
            game_state: GameContext = None
    ) -> ONWAgentResponse:
        """
        Act on the given prompt.
        """
        conversation_history = game_state.conversation
        return self._invoke_model(conversation_history, prompt, prompt_is_another_player_question, questioning_player_name, game_state)

    def _get_system_prompt(self):
        raise NotImplementedError("Subclasses must implement this method")

    def _get_prompt(self, conversation_history: ConversationHistory, prompt: str, prompt_is_another_player_question: bool = False, questioning_player_name: str = ""):
        if conversation_history.messages:
            conversation_history_text = f"Here is the conversation history you've been participating in:\n\n{conversation_history.get_public_conversation_history()}"
        else:
            conversation_history_text = ""

        if prompt_is_another_player_question:
            return textwrap.dedent(
                f"""{questioning_player_name} has a question for you!

                The question is: {prompt}
             
                Keep in mind that you have the following personal knowledge that you may want to keep to yourself or disclose:
                {self.personal_knowledge}

                {conversation_history_text}    

                Please respond to {questioning_player_name}'s question. You can choose to be truthful, 
                misleading, or evasive depending on what benefits your role.
                
                Format your response exactly like this:
                
                PRIVATE_THOUGHTS: [Your internal reasoning and strategy - what you're actually thinking]
                
                PUBLIC_RESPONSE: [What you want to say out loud to {questioning_player_name} and the group]"""
            )
        else:
            return textwrap.dedent(
                f"""It's your turn to act!
            
                Keep in mind that you have the following personal knowledge that you may want to keep to yourself or disclose:
                {self.personal_knowledge}

                Current situation: {prompt}

                {conversation_history_text}

                What would you like to say to the group or do? You can share information, ask questions, make accusations, 
                or use any available tools.
                
                Format your response exactly like this:
                
                PRIVATE_THOUGHTS: [Your internal reasoning and strategy - what you're actually thinking]
                
                PUBLIC_RESPONSE: [What you want to say out loud to the group]"""
            )
        
    def _invoke_model(self, conversation_history: ConversationHistory, prompt: str, prompt_is_another_player_question: bool = False, questioning_player_name: str = "", game_context: GameContext = None) -> ONWAgentResponse:
        try:
            system_prompt = self._get_system_prompt(game_context)
        except TypeError:
            system_prompt = self._get_system_prompt()
        user_prompt = self._get_prompt(conversation_history, prompt, prompt_is_another_player_question, questioning_player_name)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        api_params = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools if self.tools else None,
            "response_format": ONWAgentResponse
        }
        
        if game_context.is_nighttime:
            forced_tool = self.get_forced_nighttime_tool()
            if forced_tool:
                api_params["tool_choice"] = {"type": "function", "function": {"name": forced_tool}}
        
        response = self.client.chat.completions.parse(**api_params)

        raw_response = response.choices[0].message.content
        tool_calls_made = []

        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                result = self.call_tool(name, args, game_context)
                tool_calls_made.append({
                    "name": name,
                    "args": args,
                    "result": result
                })
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        

        private_thoughts, public_response = self._parse_structured_response(raw_response)
        
        agent_response = ONWAgentResponse(  
            public_response=public_response,
            private_thoughts=private_thoughts,
            tool_calls=tool_calls_made,
            raw_response=raw_response
        )

        conversation_history.add_agent_response(
            player_id=self.player_id,
            player_name=self.player_name,
            public_response=public_response,
            private_thoughts=private_thoughts,
            tool_calls=tool_calls_made,
            raw_response=raw_response
        )
        
        return agent_response

    def _parse_structured_response(self, raw_response: str) -> tuple[str, str]:
        try:
            parsed = json.loads(raw_response)

            private_thoughts = parsed.get("private_thoughts", "No private thoughts provided")
            public_response = parsed.get("public_response", "No public response provided")
            
            return private_thoughts, public_response
            
        except json.JSONDecodeError as e:
            return f"Error parsing JSON response: {str(e)}", raw_response.strip()
        except Exception as e:
            return f"Error parsing response: {str(e)}", raw_response.strip()


    def is_tool_available(self, tool_name: str, game_context: GameContext = None) -> bool:
        """Check if a tool is available based on current game phase"""
        if tool_name == self.nighttime_tool:
            return game_context and game_context.is_nighttime
        return True  # Daytime tools always available
    
    def execute_night_action(self, game_context: GameContext):
        """Execute this agent's automatic nighttime action. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement execute_night_action")
    
    def get_forced_nighttime_tool(self) -> Optional[str]:
        """Return the forced nighttime tool if one is set."""
        return self.nighttime_tool  # None = automatic action, tool name = forced tool
    
    def call_tool(self, name: str, args: dict, game_context: GameContext = None):
        if not self.is_tool_available(name, game_context):
            return f"The tool '{name}' is not available during the current game phase."

        tool_registry = {
            "inquire_about_another_player": {
                "module": "game_agents.common_tools",
                "function": "inquire_about_another_player",
                "args": lambda: {
                    "player_name": args['player_name'],
                    "question": args['question'],
                    "game_context": game_context,
                    "questioning_player_name": self.player_name
                }
            },
            "seer_investigate": {
                "module": "game_agents.seer",
                "function": "seer_investigate",
                "args": lambda: {
                    "game_context": game_context,
                    "seer_player_id": self.player_id,
                    "investigation_type": args.get('investigation_type'),
                    "target_player_name": args.get('target_player_name'),
                    "card_positions": args.get('card_positions')
                }
            },
            "robber_swap": {
                "module": "game_agents.robber",
                "function": "robber_swap",
                "args": lambda: {
                    "game_context": game_context,
                    "robber_player_id": self.player_id,
                    "target_player_name": args.get('target_player_name')
                }
            },
            "troublemaker_swap": {
                "module": "game_agents.troublemaker", 
                "function": "troublemaker_swap",
                "args": lambda: {
                    "game_context": game_context,
                    "troublemaker_player_id": self.player_id,
                    "player1_name": args.get('player1_name'),
                    "player2_name": args.get('player2_name')
                }
            },
            "drunk_swap": {
                "module": "game_agents.drunk",
                "function": "drunk_swap", 
                "args": lambda: {
                    "game_context": game_context,
                    "drunk_player_id": self.player_id,
                    "center_position": args.get('center_position')
                }
            }
        }
        
        if name not in tool_registry:
            return f"Unknown tool: {name}"
                
        try:
            tool_config = tool_registry[name]
            module = __import__(tool_config["module"], fromlist=[tool_config["function"]])
            function = getattr(module, tool_config["function"])
            result = function(**tool_config["args"]())
            
        except Exception as e:
            return f"Error calling tool {name}: {str(e)}"
        
        if result and isinstance(result, str) and not result.startswith("Error:"):
            self.personal_knowledge.append(result)
        
        return result
    