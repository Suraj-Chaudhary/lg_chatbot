import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {'configurable': {"thread_id": "thread_1"}}

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

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

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

    
    # add the assistant's response to the message history
    # with st.chat_message('assistant'):

    #     ai_message = st.write_stream(
    #         message_chunk.content for message_chunk, metadata in chatbot.stream(
    #             {'messages': [HumanMessage(content = user_input)]},
    #             config = CONFIG,
    #             stream_mode = 'messages'
    #         )
    #     )               Returns list of content blocks instead of plain text


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