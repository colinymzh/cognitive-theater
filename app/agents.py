# app/agents.py
import fastapi_poe as fp
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

def create_poe_llm_runnable(api_key: str, bot_name: str):
    """
    Creates a LangChain Runnable that internally calls the Poe API.
    """
    def poe_api_call(prompt_value):
        # 1. Convert LangChain's Prompt output to Poe's messages format
        langchain_messages = prompt_value.to_messages()
        poe_messages = []
        for msg in langchain_messages:
            if isinstance(msg, HumanMessage):
                poe_messages.append(fp.ProtocolMessage(role="user", content=msg.content))
            elif isinstance(msg, AIMessage):
                poe_messages.append(fp.ProtocolMessage(role="bot", content=msg.content))
            elif isinstance(msg, SystemMessage):
                poe_messages.insert(0, fp.ProtocolMessage(role="system", content=msg.content))

        # 2. Call the Poe API and collect streaming responses
        full_response = ""
        try:
            for partial in fp.get_bot_response_sync(messages=poe_messages, bot_name=bot_name, api_key=api_key):
                full_response += partial.text
            return full_response
        except Exception as e:
            
            print(f"Poe API call error: {e}")
            return f"Poe API call error: {e}"

    return RunnableLambda(poe_api_call)


def create_all_agents(prompts: dict, api_key: str, bot_name: str) -> dict:
    """Create all agents and tools according to prompts and Poe configuration"""
    
    # Create a generic Runnable that connects to a specific Poe Bot
    poe_llm_runnable = create_poe_llm_runnable(api_key=api_key, bot_name=bot_name)

    # Use this common Runnable to build all Agents
    facilitator_planner = ChatPromptTemplate.from_template(prompts["facilitator_planner"]) | poe_llm_runnable
    facilitator_responder = ChatPromptTemplate.from_template(prompts["facilitator_responder"]) | poe_llm_runnable
    inner_projector = ChatPromptTemplate.from_template(prompts["inner_projector"]) | poe_llm_runnable
    
    tools = {
        "CognitiveDistortionIdentifierTool": ChatPromptTemplate.from_template(prompts["cognitive_distortion_identifier_tool"]) | poe_llm_runnable,
        "SocraticQuestioningTool": ChatPromptTemplate.from_template(prompts["socratic_questioning_tool"]) | poe_llm_runnable,
        "BehavioralActivationTool": ChatPromptTemplate.from_template(prompts["behavioral_activation_tool"]) | poe_llm_runnable,
    }
    
    peers = {
        "Sara": ChatPromptTemplate.from_template(prompts["Sara"]) | poe_llm_runnable,
        "David": ChatPromptTemplate.from_template(prompts["David"]) | poe_llm_runnable,
    }
    
    return {
        "facilitator_planner": facilitator_planner,
        "facilitator_responder": facilitator_responder,
        "inner_projector": inner_projector,
        "tools": tools,
        "peers": peers,
    }