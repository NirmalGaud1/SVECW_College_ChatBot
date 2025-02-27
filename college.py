import streamlit as st
import pandas as pd
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Set page config
st.set_page_config(page_title="College Chatbot 🎓", page_icon="🎓", layout="centered")

# Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Load CSV from GitHub (replace with your actual URL)
csv_url = "college_faq.csv"

try:
    df = pd.read_csv(csv_url)
except Exception as e:
    st.error(f"Failed to load the CSV file. Error: {e}")
    st.stop()

# Preprocess data
df = df.fillna("")
df['Question'] = df['Question'].str.lower()
df['Answer'] = df['Answer'].str.lower()

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer()
question_vectors = vectorizer.fit_transform(df['Question'])

# Configure Gemini API (replace with your actual API key)
API_KEY = "AIzaSyBsq5Kd5nJgx2fejR77NT8v5Lk3PK4gbH8"  # DO NOT EMBED KEYS DIRECTLY! Use st.secrets or env vars!
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to find the closest question using cosine similarity
def find_closest_question(user_query, vectorizer, question_vectors, df):
    query_vector = vectorizer.transform([user_query.lower()])
    similarities = cosine_similarity(query_vector, question_vectors).flatten()
    best_match_index = similarities.argmax()
    best_match_score = similarities[best_match_index]
    if best_match_score > 0.3:  # Threshold for similarity
        return df.iloc[best_match_index]['Answer']
    else:
        return None

# Function to refine the answer using Gemini
def refine_answer_with_gemini(generative_model, user_query, closest_answer):
    try:
        context = """
        You are a college chatbot. Refine the following answer to make it more professional, clear, and actionable.
        Ensure the response is detailed, well-structured, and includes bullet points for clarity.
        """
        prompt = f"{context}\n\nUser Query: {user_query}\nClosest Answer: {closest_answer}\nRefined Answer:"
        response = generative_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error refining the answer: {e}"

# Streamlit app
st.title("College Chatbot 🎓")
st.write("Welcome to the College Chatbot! Ask me anything about the college.")

# Display conversation history
st.markdown("### Conversation History")
for message in st.session_state.conversation:
    if message["role"] == "User":
        st.markdown(f"<div style='background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin: 5px 0;'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin: 5px 0;'><strong>Bot:</strong> {message['content']}</div>", unsafe_allow_html=True)

# Chat input
user_query = st.text_input("User:", placeholder="Type your question here...", key="user_input")

if user_query:
    st.session_state.conversation.append({"role": "User", "content": user_query})
    closest_answer = find_closest_question(user_query, vectorizer, question_vectors, df)

    if closest_answer:
        with st.spinner("Refining the answer..."):
            refined_answer = refine_answer_with_gemini(model, user_query, closest_answer)
            st.session_state.conversation.append({"role": "Bot", "content": refined_answer})
            st.markdown(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin: 5px 0;'><strong>Bot (refined answer):</strong> {refined_answer}</div>", unsafe_allow_html=True)
    else:
        try:
            context = """
            You are a college chatbot. Provide accurate, detailed, and well-structured answers to questions about the college.
            If the question is not related to the college, politely inform the user.
            Use a professional tone and format the response clearly with bullet points.
            """
            prompt = f"{context}\n\nUser: {user_query}\nBot:"
            response = model.generate_content(prompt)
            st.session_state.conversation.append({"role": "Bot", "content": response.text})
            st.markdown(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin: 5px 0;'><strong>Bot (AI-generated):</strong> {response.text}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Sorry, I couldn't generate a response. Error: {e}")
