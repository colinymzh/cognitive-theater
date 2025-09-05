# app/system.py
import os
import re
import time
import random
import json
from pathlib import Path
from . import config, prompts, agents

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

class CBTTheaterSystem:
    def __init__(self, session_id: str):
        print(f"Initializing system instance for session {session_id}...")
        self.session_id = session_id
        self.session_file_path = SESSIONS_DIR / f"{self.session_id}.json"
        
        api_key = config.POE_API_KEY
        bot_name = "Claude-Sonnet-4"
        
        self.prompts = prompts.load_all_prompts()
        

        agent_components = agents.create_all_agents(
            prompts=self.prompts, 
            api_key=api_key, 
            bot_name=bot_name
        )
        self.facilitator_planner = agent_components["facilitator_planner"]
        self.facilitator_responder = agent_components["facilitator_responder"]
        self.inner_projector = agent_components["inner_projector"]
        self.tools = agent_components["tools"]
        self.peers = agent_components["peers"]
        
        self.peer_turn_order = ["Sara", "David"]
        
        self.load_history()
        print(f"System instance {session_id} initialized.")


    def save_history(self):
        """Save the current conversation history and initial question to a JSON file for this session."""
        history_data = {
            "session_id": self.session_id,
            "initial_problem": self.initial_problem,
            "history": self.conversation_history
        }
        with open(self.session_file_path, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=4)
        print(f" [System Activity]: Session {self.session_id} saved.")

    def load_history(self):
        """Load the conversation history from the JSON file for this session."""
        try:
            with open(self.session_file_path, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                self.conversation_history = history_data.get("history", [])
                self.initial_problem = history_data.get("initial_problem", "")
                print(f" [System Activity]: Successfully loaded session {self.session_id} from file.")
        except FileNotFoundError:
            self.conversation_history = []
            self.initial_problem = ""
            print(f"[System Activity]: History file not found, creating new session for {self.session_id}.")

    def _parse_decision(self, decision_xml: str) -> str:
        match = re.search(r'<decision>(.*?)</decision>', decision_xml)
        return match.group(1).strip() if match else "NoTool"

    async def _run_facilitator_turn_async(self):
        print("\n[System Activity]: Host 'Lucian' is thinking...")
        history_str = "\n".join(self.conversation_history)
        
        decision_xml = await self.facilitator_planner.ainvoke({"conversation_history": history_str})
        tool_name = self._parse_decision(decision_xml)
        print(f"[Lucian-Planning Decision]: {tool_name}")

        if random.random() < 0.15 and tool_name not in ["SocraticQuestioningTool", "BehavioralActivationTool"]:
            print("[System Activity]: Random event triggered! The thought of 'Shadow' suddenly emerged...")
            tool_name = "InviteInnerProjector"
            print(f"[Lucian-Decision Change]: {tool_name}")
        
        tool_output = "None"
        
        if tool_name == "InviteInnerProjector":
            print("[System Activity]: 'Lucian' has decided to invite 'Shadow' to speak again...")
            projector_response = await self.inner_projector.ainvoke({
                "user_problem": self.initial_problem,
                "conversation_history": history_str
            })
            self.conversation_history.append(f"Shadow: {projector_response}")
            yield json.dumps({"speaker": "Shadow", "text": projector_response}) + "\n"
            tool_output = "(Shadow just spoke again)"
            
        elif tool_name != "NoTool" and tool_name in self.tools:
            print(f"[Lucian-Expert Consult]: Calling {tool_name} ...")
            tool_to_run = self.tools[tool_name]
            tool_output = await tool_to_run.ainvoke({"conversation_history": history_str})
        
        final_response = await self.facilitator_responder.ainvoke({
            "conversation_history": "\n".join(self.conversation_history),
            "tool_output": tool_output
        })
        
        self.conversation_history.append(f"Lucian: {final_response}")
        yield json.dumps({"speaker": "Lucian", "text": final_response}) + "\n"

    async def start_session(self, initial_problem: str, session_id: str):
        self.initial_problem = initial_problem
        self.conversation_history.append(f"You (Initial concern): {initial_problem}")

        yield json.dumps({"type": "metadata", "session_id": self.session_id}) + "\n"

        opening_statement = f"Thank you for sharing. To better understand it, let's invite the part of your inner voice that feels most anxious—we'll call it 'Shadow'—to chat with us. What is it specifically worried about?"
        self.conversation_history.append(f"Lucian: {opening_statement}")
        yield json.dumps({"speaker": "Lucian", "text": opening_statement}) + "\n"
        
        projector_response = await self.inner_projector.ainvoke({
            "user_problem": initial_problem,
            "conversation_history": "\n".join(self.conversation_history)
        })
        self.conversation_history.append(f"Shadow: {projector_response}")
        yield json.dumps({"speaker": "Shadow", "text": projector_response}) + "\n"
        
        for peer_name in self.peer_turn_order:
            history_str = "\n".join(self.conversation_history)
            peer_agent = self.peers[peer_name]
            response = await peer_agent.ainvoke({"conversation_history": history_str})
            self.conversation_history.append(f"{peer_name}: {response}")
            yield json.dumps({"speaker": peer_name, "text": response}) + "\n"
        
        async for facilitator_chunk in self._run_facilitator_turn_async():
            yield facilitator_chunk

        self.save_history()

    async def continue_session(self, user_input: str):
        self.conversation_history.append(f"You: {user_input}")
        
        for peer_name in self.peer_turn_order:
            history_str = "\n".join(self.conversation_history)
            peer_agent = self.peers[peer_name]
            response = await peer_agent.ainvoke({"conversation_history": history_str})
            self.conversation_history.append(f"{peer_name}: {response}")
            yield json.dumps({"speaker": peer_name, "text": response}) + "\n"
        
        async for facilitator_chunk in self._run_facilitator_turn_async():
            yield facilitator_chunk
            
        self.save_history()