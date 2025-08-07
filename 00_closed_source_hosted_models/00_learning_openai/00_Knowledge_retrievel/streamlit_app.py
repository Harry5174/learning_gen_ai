import streamlit as st
import requests

# Set the FastAPI backend URL
BACKEND_URL = "http://localhost:8000"

@st.cache
def start_conversation():
    response = requests.get(f"{BACKEND_URL}/start")
    if response.status_code == 200:
        return response.json().get('thread_id')
    else:
        st.error("Failed to start a new conversation")
        return None

@st.cache
def send_message(thread_id, message):
    response = requests.post(f"{BACKEND_URL}/chat", json={"thread_id": thread_id, "message": message})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to send message")
        return None

def main():
    st.title('Chat with OpenAI')

    if st.button('Start New Conversation'):
        thread_id = start_conversation()
        if thread_id:
            st.session_state['thread_id'] = thread_id
            st.success(f"Conversation started with thread ID: {thread_id}")

    user_message = st.text_input("Your Message:")

    if st.button('Send'):
        if 'thread_id' in st.session_state:
            thread_id = st.session_state['thread_id']
            chat_response = send_message(thread_id, user_message)
            if chat_response:
                st.write(chat_response)
        else:
            st.error("No conversation thread. Please start a new conversation.")

if __name__ == "__main__":
    main()
