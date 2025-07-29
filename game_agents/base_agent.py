from openai import OpenAI
import os
import json
import textwrap
from pydantic import BaseModel
from game_context.messages import ConversationHistory

class ONWAgentResponse(BaseModel):
    """Response from the agent"""
    public_response: str  # What the agent says to the group
    private_thoughts: str  # What the agent is thinking privately
    tool_calls: list[dict] = []  # Any tool calls made
    raw_response: str = ""  # The full raw response from the model

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

    def get_prompt(self, conversation_history: ConversationHistory, prompt: str, prompt_is_another_player_question: bool = False, questioning_player_name: str = ""):
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
        
    def invoke_model(self, conversation_history: ConversationHistory, prompt: str, prompt_is_another_player_question: bool = False, questioning_player_name: str = "") -> ONWAgentResponse:
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

        raw_response = response.choices[0].message.content
        tool_calls_made = []

        # Handle tool calls if any
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                result = self.call_tool(name, args)
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
        
        # Parse the structured response
        private_thoughts, public_response = self._parse_structured_response(raw_response)
        
        # Create the agent response
        agent_response = ONWAgentResponse(
            public_response=public_response,
            private_thoughts=private_thoughts,
            tool_calls=tool_calls_made,
            raw_response=raw_response
        )
        
        # Add the full agent response to conversation history
        if public_response.strip() or private_thoughts.strip() or tool_calls_made:  # Add if there's any meaningful content
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
        """Parse the structured response to extract private thoughts and public response"""
        if not raw_response:
            return "", ""
        
        # Default values
        private_thoughts = ""
        public_response = ""
        
        # Split by lines and look for the markers
        lines = raw_response.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('PRIVATE_THOUGHTS:'):
                # Save previous section if any
                if current_section == 'public':
                    public_response = '\n'.join(current_content).strip()
                
                current_section = 'private'
                current_content = [line.replace('PRIVATE_THOUGHTS:', '').strip()]
                
            elif line.startswith('PUBLIC_RESPONSE:'):
                # Save previous section if any
                if current_section == 'private':
                    private_thoughts = '\n'.join(current_content).strip()
                
                current_section = 'public'
                current_content = [line.replace('PUBLIC_RESPONSE:', '').strip()]
                
            elif current_section:
                # Continue adding to current section
                current_content.append(line)
        
        # Don't forget the last section
        if current_section == 'private':
            private_thoughts = '\n'.join(current_content).strip()
        elif current_section == 'public':
            public_response = '\n'.join(current_content).strip()
        
        # Fallback: if no structured format found, treat entire response as public
        if not private_thoughts and not public_response:
            public_response = raw_response.strip()
            private_thoughts = "No private thoughts provided"
        
        return private_thoughts, public_response

    def call_tool(self, name: str, args: dict):
        if name == "inquire_about_another_player":
            return f"Question sent to {args['player_name']}: {args['question']}"
        else:
            return f"Unknown tool: {name}"
    