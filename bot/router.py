"""
LLM-powered intent router for natural language queries.
"""

import json
import sys
import requests

from services.lms_client import LMSClient
from tools import TOOLS
from config import Config


class IntentRouter:
    """Routes user messages using LLM with tools."""
    
    def __init__(self):
        self.client = LMSClient()
        self.api_base = Config.LLM_API_BASE_URL
        self.api_key = Config.LLM_API_KEY
        self.model = Config.LLM_API_MODEL
        self.system_prompt = """You are an assistant for a Learning Management System (LMS).
You have access to various tools to query data about labs, students, and analytics.

When a user asks a question:
1. Determine which tool(s) you need to call
2. Call them with appropriate parameters
3. Use the results to answer the user's question

Rules:
- For multi-step questions, call get_items first, then call get_pass_rates for each lab
- Always use tools to get data — don't guess
- Be concise and helpful
- If you're unsure, ask for clarification"""
    
    def _call_llm(self, messages):
        """Call LLM with messages and tools."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[error] LLM call failed: {e}", file=sys.stderr)
            return None
    
    def _execute_tool(self, tool_call):
        """Execute a tool call and return result as string."""
        tool_name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])
        
        print(f"[tool] LLM called: {tool_name}({args})", file=sys.stderr)
        
        # Map to client method
        if tool_name == "get_items":
            result = self.client.get_items()
        elif tool_name == "get_learners":
            result = self.client.get_learners()
        elif tool_name == "get_scores":
            result = self.client.get_scores(args.get("lab"))
        elif tool_name == "get_pass_rates":
            result = self.client.get_pass_rates(args.get("lab"))
        elif tool_name == "get_timeline":
            result = self.client.get_timeline(args.get("lab"))
        elif tool_name == "get_groups":
            result = self.client.get_groups(args.get("lab"))
        elif tool_name == "get_top_learners":
            result = self.client.get_top_learners(args.get("lab"), args.get("limit", 5))
        elif tool_name == "get_completion_rate":
            result = self.client.get_completion_rate(args.get("lab"))
        elif tool_name == "trigger_sync":
            result = self.client.trigger_sync()
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        result_str = json.dumps(result, ensure_ascii=False)
        print(f"[tool] Result: {result_str[:200]}...", file=sys.stderr)
        return result_str
    
    def route(self, user_message, max_turns=5):
        """Route user message to appropriate tool(s) and return response."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        for turn in range(max_turns):
            print(f"[turn {turn+1}] Calling LLM...", file=sys.stderr)
            
            response = self._call_llm(messages)
            if not response:
                return "Sorry, I'm having trouble connecting. Please try again."
            
            message = response["choices"][0]["message"]
            
            if "tool_calls" in message and message["tool_calls"]:
                print(f"[tool] Received {len(message['tool_calls'])} tool call(s)", file=sys.stderr)
                messages.append(message)
                
                for tool_call in message["tool_calls"]:
                    result = self._execute_tool(tool_call)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result
                    })
            else:
                answer = message.get("content", "")
                print(f"[summary] Final answer: {answer[:100]}...", file=sys.stderr)
                return answer
        
        return "I'm having trouble answering. Please try rephrasing."
