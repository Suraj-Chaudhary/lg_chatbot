import streamlit as st
from langgraph_db_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid


# ************************************ utility functions ************************************
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def generate_thread_id():
    return uuid.uuid4()

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

# Helper function to extract 'plain text' from content blocks produced by 'streaming' mode of chatbot
def extract_text(content):
    # content can be a plain string OR a list of content block dicts
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""

def load_conversation(thread_id):
    return chatbot.get_state(config = {'configurable': {"thread_id": thread_id}}).values['messages']

# ************************************ Session Setup ************************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

add_thread(st.session_state['thread_id'])

# ************************************ Sidebar UI ************************************
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state['chat_threads'][::-1]:  # Display threads in reverse order (most recent first)
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_message = []

        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            temp_message.append({"role": role, "content": message.content})

        st.session_state['message_history'] = temp_message

# ************************************ Main UI ************************************
CONFIG = {'configurable': {"thread_id": st.session_state['thread_id']}}

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:

    # first add the message to the message history
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            extract_text(message_chunk.content)
            for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )
        
    st.session_state['message_history'].append({"role": "assistant", "content": ai_message})