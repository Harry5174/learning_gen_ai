import streamlit as st
import requests

# Set the FastAPI backend URL
BACKEND_URL = "http://localhost:8000"

st.title('Chat with OpenAI')

# Start a new conversation
if st.button('Start New Conversation'):
    response = requests.get(f"{BACKEND_URL}/start")
    if response.status_code == 200:
        thread_id = response.json().get('thread_id')
        st.session_state['thread_id'] = thread_id
        st.success(f"Conversation started with thread ID: {thread_id}")
    else:
        st.error("Failed to start a new conversation")

# Input for user message
user_message = st.text_input("Your Message:")

# Send message
if st.button('Send'):
    if 'thread_id' in st.session_state:
        thread_id = st.session_state['thread_id']
        response = requests.post(f"{BACKEND_URL}/chat", json={"thread_id": thread_id, "message": user_message})
        if response.status_code == 200:
            chat_response = response.json()
            st.write(chat_response)
        else:
            st.error("Failed to send message")
    else:
        st.error("No conversation thread. Please start a new conversation.")