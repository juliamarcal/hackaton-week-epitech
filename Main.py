import streamlit as st
import random
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

# pip install streamlit transformers
# Load the Mixtral model
model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)


st.title("Simple chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# # Accept user input
# if prompt := st.chat_input("What is up?"):
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})

user_input = st.text_input("You:", "")
inputs = tokenizer(user_input, return_tensors="pt")

outputs = model.generate(**inputs, max_new_tokens=20)

    
# Display assistant response in chat message container
with st.chat_message("assistant"):
    message_placeholder = st.empty()
    full_response = ""
    assistant_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Simulate stream of response with milliseconds delay
    for chunk in assistant_response.split():
        full_response += chunk + " "
        time.sleep(0.05)
        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
# Add assistant response to chat history
st.session_state.messages.append({"role": "assistant", "content": full_response})