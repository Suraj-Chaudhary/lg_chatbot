from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
# from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3

load_dotenv()
# llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


conn = sqlite3.connect(database = "chatbot.db", check_same_thread = False)
# Checkpointer
checkpointer = SqliteSaver(conn = conn)

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# checkpointer.list(None) # List all saved states

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        print(checkpoint.config)
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)

if __name__ == "__main__":
    # Testing sqlite integration with chatbot
    CONFIG = {'configurable': {"thread_id": "thread_2"}}

    response = chatbot.invoke(
            {'messages': [HumanMessage(content="Add 10 to the result.")]},
            config=CONFIG
    )

    print(response)