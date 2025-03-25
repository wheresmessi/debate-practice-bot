import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Set up the model
model = genai.GenerativeModel('gemini-2.0-flash')

def get_debate_response(topic, history, user_input):
    try:
        # Construct the context from history
        context = f"This is a debate about: {topic}\n\nPrevious discussion:\n"
        for msg in history:
            prefix = "User" if msg["role"] == "user" else "Assistant"
            context += f"{prefix}: {msg['content']}\n"
        
        # Add current input
        context += f"\nUser's latest argument: {user_input}\n"
        
        prompt = f"""{context}
        
        Provide a concise counter-argument in 5-10 lines while:
        1. Being focused and direct
        2. Using clear reasoning and evidence
        3. Addressing the most important points
        4. Maintaining a respectful tone
        
        Keep your response brief - aim for a medium-sized paragraph (5-10 lines maximum)."""
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    st.title("🎤 Debate Practice Assistant")
    
    # Initialize session state for chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'debate_topic' not in st.session_state:
        st.session_state.debate_topic = ""
    
    # Topic input with reset button
    col1, col2 = st.columns([4, 1])
    with col1:
        new_topic = st.text_input("Enter the debate topic:", key="topic_input")
    with col2:
        if st.button("Reset Debate"):
            st.session_state.messages = []
            st.session_state.debate_topic = ""
            st.experimental_rerun()
    
    # Set or update debate topic
    if new_topic and new_topic != st.session_state.debate_topic:
        st.session_state.debate_topic = new_topic
        st.session_state.messages = []
        st.experimental_rerun()
    
    if st.session_state.debate_topic:
        st.write(f"🎯 Current Topic: {st.session_state.debate_topic}")
        
        # Display chat history
        for msg in st.session_state.messages:
            with st.container():
                st.write(f"{msg['role'].capitalize()}: {msg['content']}")
        
        # User input
        user_input = st.text_area("Your argument...")
        
        if st.button("Send") and user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get and display AI response
            response = get_debate_response(
                st.session_state.debate_topic,
                st.session_state.messages[:-1],  # Exclude current message
                user_input
            )
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Display instructions
    with st.sidebar:
        st.markdown("""
        ### How to Use
        1. Enter a debate topic
        2. Start the debate with your argument
        3. Continue the discussion by responding to AI's points
        4. Click 'Reset Debate' to start a new topic
        
        ### Tips
        - Be clear and specific in your arguments
        - Support your points with evidence
        - Stay respectful and focused on the topic
        - Build upon previous exchanges
        
        ### Note
        The AI maintains context of the entire debate history
        to provide more relevant and engaging responses.
        """)

if __name__ == "__main__":
    main()
