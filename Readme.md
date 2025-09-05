# Cognitive Theater

> An interactive multi-agent chat application designed to simulate a Cognitive Behavioral Therapy (CBT) group session. Users can explore their concerns through a guided conversation with a cast of AI agents, each playing a unique role in the therapeutic process.

## 🛠️ Tech Stack

  * **Backend:**
      * **Python 3.10+**
      * **FastAPI:** For building the high-performance API backend.
      * **LangChain:** For structuring and chaining calls to the language models.
      * **Poe API (`fastapi-poe`):** As the client to connect to external language models (e.g., Claude 3 Sonnet).
      * **Uvicorn:** As the ASGI server to run the FastAPI application.
  * **Frontend:**
      * HTML5
      * CSS3
      * Vanilla JavaScript
  * **Data Persistence:**
      * JSON files for storing session histories.

## 🚀 Getting Started

Follow these steps to get the application running on your local machine.

### Prerequisites

  * Python 3.10 or higher
  * `pip` package manager
  * A Poe API Key

### Installation & Setup

1.  **Clone the Repository**

2.  **Install Dependencies**
    Install all the required Python packages from the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables**
    The application requires a Poe API key to function. 

    Open the `.env` file and add your API key:

    ```env
    POE_API_KEY="your_poe_api_key_here"
    ```

45.  **Run the Backend Server**
    Use `uvicorn` to start the FastAPI server. The `--reload` flag will automatically restart the server when you make changes to the code.

    ```bash
    uvicorn main:app --reload
    ```

    The API will be available at `http://127.0.0.1:8000`.

5.  **Launch the Frontend**
    Simply open the `index.html` file in your web browser. You can do this by double-clicking the file or right-clicking and selecting "Open with Browser".

You are now ready to start your first session\!

## 📂 Project Structure

The project is organized into logical modules to separate concerns.

```
MULTI_AGENTS_FINAL/
│
├── app/                  # Core application logic
│   ├── __pycache__/
│   ├── __init__.py
│   ├── agents.py         # Defines and creates all AI agents and tools.
│   ├── config.py         # Handles loading of environment variables (e.g., API keys).
│   ├── prompts.py        # Loads agent and tool prompts from markdown files.
│   └── system.py         # Main controller (CBTTheaterSystem class) that manages session state and conversation flow.
│
├── assets/               # Static assets for the frontend
│   ├── david.png
│   ├── lucian.png
│   ├── sara.png
│   ├── shadow.png
│   └── you.png
│
├── prompts/              # Contains all markdown prompts for the agents and tools
│   ├── behavioral_activation_tool.md
│   ├── cognitive_distortion_identifier_tool.md
│   ├── facilitator_planner_prompt.md
│   └── ... (and other prompt files)
│
├── sessions/             # Directory where session history JSON files are stored
│
├── .env                  # Environment variables file.
├── index.html            # The single-page frontend for the application.
├── main.py               # The FastAPI server entry point, defines all API endpoints.
└── requirements.txt      # Lists all Python dependencies.
```

## ⚙️ How It Works

The conversation flow for a user's turn is orchestrated by the `CBTTheaterSystem` class:

1.  **User Input:** The user sends a message through the web interface.
2.  **Peer Response:** The system first passes the conversation history to the peer agents (`Sara` and `David`), who generate their responses in sequence.
3.  **Facilitator Planning:** The facilitator agent, `Lucian`, then analyzes the entire conversation history (including the new peer responses). Its "planner" component (`facilitator_planner`) decides on the next action, which can be:
      * Use a specific CBT tool.
      * Invite the `Shadow` agent to speak.
      * Respond directly without using a tool.
4.  **Tool Execution (if applicable):** If the planner decides to use a tool (e.g., `CognitiveDistortionIdentifierTool`), that tool is executed, and its output is collected.
5.  **Facilitator Response Generation:** `Lucian`'s "responder" component (`facilitator_responder`) takes the conversation history and any tool output to formulate a final, cohesive message to the user.
6.  **Streaming & Saving:** All AI responses are streamed back to the frontend. Once the turn is complete, the entire updated conversation history is saved to the corresponding session JSON file.
