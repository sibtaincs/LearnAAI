import sys
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 1. Connect to your local Ollama model
# Ensure you have run 'ollama pull llama3.2' (or mistral, llama3, etc.) in your terminal first
llm = ChatOllama(
    model="llama3.2", 
    temperature=0
)

# 2. Define your graph state structure
class State(TypedDict):
    input_text: str
    response_text: str

# 3. Define the LLM execution node
def call_ollama(state: State):
    print("--- Local Ollama Node Executing ---")
    ai_msg = llm.invoke(state["input_text"])
    return {"response_text": ai_msg.content}

# 4. Construct the LangGraph workflow
workflow = StateGraph(State)
workflow.add_node("ollama_agent", call_ollama)

# Define simple sequential execution flow
workflow.add_edge(START, "ollama_agent")
workflow.add_edge("ollama_agent", END)

# Compile the graph workflow
app = workflow.compile()

# 5. Run the graph locally
if __name__ == "__main__":
    query = {"input_text": "Why is the sky blue? Answer in exactly 5 words."}
    result = app.invoke(query)
    print("\nFinal Graph Result:")
    print(result["response_text"])
