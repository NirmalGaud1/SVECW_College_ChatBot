import streamlit as st
import pandas as pd
import google.generativeai as genai

# Load CSV from GitHub (replace with your actual URL)
csv_url = "colege_details.csv"

try:
    df = pd.read_csv(csv_url, encoding='ISO-8859-1')
except Exception as e:
    st.error(f"Failed to load the CSV file. Error: {e}")
    st.stop()

# Configure Gemini API (replace with your actual API key)
API_KEY = "AIzaSyBsq5Kd5nJgx2fejR77NT8v5Lk3PK4gbH8" #DO NOT EMBED KEYS DIRECTLY! Use st.secrets or env vars!
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to search the CSV file
def search_csv(query, column=None):
    query = query.lower()
    if column:
        results = df[df[column].str.lower().str.contains(query)]
    else:
        results = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)]
    if not results.empty:
        return results.to_string(index=False)
    else:
        return None

# Streamlit app
st.title("🤖 College Chatbot")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the college..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower()

    if "faculty" in prompt_lower and "cse" in prompt_lower:
        csv_response = search_csv("cse", "Department")
        if csv_response:
            gemini_prompt = f"From the following data: {csv_response}, please provide the names of the CSE faculty."
        else:
            gemini_prompt = "Tell me about the cse department faculties"

    elif "faculty" in prompt_lower:
        csv_response = search_csv("faculty", "Faculty Name")
        if csv_response:
            gemini_prompt = f"From the following data: {csv_response}, please provide the faculty names."
        else:
            gemini_prompt = "Tell me about the college faculties"

    elif "department" in prompt_lower:
        csv_response = search_csv(prompt)
        gemini_prompt = f"From the following data: {csv_response}, answer the question {prompt}"

    elif "course" in prompt_lower:
        csv_response = search_csv(prompt)
        gemini_prompt = f"From the following data: {csv_response}, answer the question {prompt}"

    else:
        csv_response = search_csv(prompt)
        gemini_prompt = f"From the following data: {csv_response}, answer the question {prompt}"

    if csv_response:
        try:
            response = st.session_state.chat.send_message(gemini_prompt)
            response_text = response.text
        except Exception as e:
            response_text = f"An error occurred: {e}"
    else:
        try:
            response = st.session_state.chat.send_message(gemini_prompt)
            response_text = response.text
        except Exception as e:
            response_text = f"An error occurred: {e}"

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
