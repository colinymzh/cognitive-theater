# app/prompts.py
from pathlib import Path

def _load_prompt_from_file(file_path: str) -> str:
   
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Prompt file not found -> {file_path}")
    return ""

def load_all_prompts(prompt_dir: Path = Path("prompts")) -> dict:
    """Load all .md files in the prompts directory"""
    prompt_files = {
        "facilitator_planner": "facilitator_planner_prompt.md",
        "facilitator_responder": "facilitator_responder_prompt.md",
        "inner_projector": "inner_projector_prompt.md",
        "cognitive_distortion_identifier_tool": "cognitive_distortion_identifier_tool.md",
        "socratic_questioning_tool": "socratic_questioning_tool.md",
        "behavioral_activation_tool": "behavioral_activation_tool.md",
        "Sara": "peer_sara_prompt.md",
        "David": "peer_david_prompt.md",
    }
    
    return {
        key: _load_prompt_from_file(prompt_dir / filename)
        for key, filename in prompt_files.items()
    }