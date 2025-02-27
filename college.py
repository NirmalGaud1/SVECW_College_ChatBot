import streamlit as st
import pandas as pd
import google.generativeai as genai

# Load CSV from GitHub
csv_url = "colege_details.csv"  # Replace with your CSV's raw URL

try:
    df = pd.read_csv(csv_url, encoding='ISO-8859-1')
except Exception as e:
    st.error(f"Failed to load the CSV file. Error: {e}")
    st.stop()  # Stop the app if the CSV cannot be loaded

# Configure Gemini API
API_KEY = "AIzaSyBsq5Kd5nJgx2fejR77NT8v5Lk3PK4gbH8"  # Replace with your Gemini API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize session state for chat history
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to search the CSV file for the query
def search_csv(query):
    # Convert the query to lowercase for case-insensitive search
    query = query.lower()
    
    # Search in all columns of the CSV
    results = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)]
    
    if not results.empty:
        return results.to_string(index=False)  # Return the matching rows as a string
    else:
        return None

# Function to check if the query is related to the college
def is_college_related(query):
    # List of keywords related to the college
    college_keywords = ["college", "svecw", "faculty", "department", "hostel", "placement", "admission", "course", "library", "club"]
    
    # Check if any keyword is present in the query
    return any(keyword in query.lower() for keyword in college_keywords)

# Streamlit app
st.title("🤖 Chatbot - Your AI Assistant")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Say something..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Step 1: Search the CSV file
    csv_response = search_csv(prompt)
    
    if csv_response:
        # If the query is found in the CSV, return the result
        st.session_state.messages.append({"role": "assistant", "content": csv_response})
        with st.chat_message("assistant"):
            st.markdown(csv_response)
    else:
        # If the query is not found in the CSV, check if it is related to the college
        if is_college_related(prompt):
            # Use Gemini to generate a response for college-related queries
            response = st.session_state.chat.send_message(prompt)
            response_text = response.text
        else:
            # Respond for non-college-related queries
            response_text = "Your query cannot be answered as it is not related to the college."
        
        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)
