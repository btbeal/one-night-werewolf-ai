from openai import OpenAI
import os
import json
import textwrap

def inquire_about_another_player(player_name: str, question: str):
    # Need to implement logic that can grab the player agent and ask them a question
    # This will come from the game controller
    return f"Question sent to {player_name}: {question}"

common_tools = [
    {
        "type": "function",
        "name": "inquire_about_another_player",
        "description": "Sometimes a player may find information about another player slightly suspicious, or they may want to know more about another player. This tool allows you to ask a question of another player.",
        "parameters": {
            "type": "object",
            "properties": {
                "player_name": {"type": "string", "description": "The name of the player you want to inquire about (this information is available via the conversation history you have)"},
                "question": {"type": "string", "description": "The question you want to ask the player"},
            },
            "required": ["player_name", "question"]
        }
    }
]

class BaseAgent:
    def __init__(self, player_id: int, player_name: str, initial_role: str, is_ai: bool, model: str = "gpt-4o-mini", tools: list[dict] = []):
        self.model = model
        self.player_id = player_id
        self.player_name = player_name
        self.initial_role = initial_role
        self.personal_knowledge = []
        self.is_ai = is_ai
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tools = common_tools + tools
    
    def get_system_prompt(self):
        raise NotImplementedError("Subclasses must implement this method")

    def get_prompt(self, conversation_history: list, prompt: str, prompt_is_another_player_question: bool = False, questioning_player_name: str = ""):
        if prompt_is_another_player_question:
            return textwrap.dedent(
                f"""{questioning_player_name} has a question for you!

                The question is: {prompt}
            
                Keep in mind that you have the following personal knowledge that you may want to keep to yourself or disclose:
                {self.personal_knowledge}

                Here is the conversation history you've been participating in:
                {self._format_conversation_history(conversation_history)}    

                Please respond to {questioning_player_name}'s question. You can choose to be truthful, 
                misleading, or evasive depending on what benefits your role."""
            )
        else:
            return textwrap.dedent(
                f"""It's your turn to act!
            
                Keep in mind that you have the following personal knowledge that you may want to keep to yourself or disclose:
                {self.personal_knowledge}

                Here is the conversation history you've been participating in:
                {self._format_conversation_history(conversation_history)}

                Current situation: {prompt}

                What would you like to say to the group or do? You can share information, ask questions, make accusations, 
                or use any available tools."""
            )

    def _format_conversation_history(self, conversation_history: list):
        if not conversation_history:
            return "No conversation history yet."
        
        # Handle different input formats
        if isinstance(conversation_history[0], dict):
            # Format: [{"player": "AI Player 1", "message": "Hello everyone!"}]
            formatted = []
            for entry in conversation_history:
                player = entry.get("player", "Unknown Player")
                message = entry.get("message", "")
                formatted.append(f"{player}: {message}")
            return "\n".join(formatted)
        else:
            # Format: ["AI Player 1: Hello everyone!", "Human Player 2: Hi there!"]
            return "\n".join(conversation_history)
        
    def invoke_model(self, conversation_history: list, prompt: str, prompt_is_another_player_question: bool = False, questioning_player_name: str = ""):
        system_prompt = self.get_system_prompt()
        user_prompt = self.get_prompt(conversation_history, prompt, prompt_is_another_player_question, questioning_player_name)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools if self.tools else None
        )

        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                result = self.call_tool(name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        
        return response.choices[0].message.content

    def call_tool(self, name: str, args: dict):
        if name == "inquire_about_another_player":
            return f"Question sent to {args['player_name']}: {args['question']}"
        else:
            return f"Unknown tool: {name}"

    def get_player_id(self):
        return self.player_id
    
    def get_player_name(self):
        return self.player_name
    
    def get_initial_role(self):
        return self.initial_role