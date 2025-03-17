import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import io
import base64

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Custom CSS for a techy cyberpunk theme
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
        
        * {
            font-family: 'JetBrains Mono', monospace;
        }
        
        body {
            background-color: #0d0d0d;
            color: #0aff9d;
        }
        
        .stApp {
            background: linear-gradient(135deg, #121212, #1e1e1e);
            color: #0aff9d;
            padding: 20px;
        }
        
        .stButton > button {
            background: #1f1f1f;
            color: #0aff9d;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            transition: 0.3s ease-in-out;
            border: 1px solid #0aff9d;
        }

        .stButton > button:hover {
            background: #0aff9d;
            color: black;
        }
        
        .stTextInput > div > div > input {
            background: #0d0d0d;
            color: #0aff9d;
            border: 1px solid #0aff9d;
            border-radius: 10px;
            padding: 8px;
        }

        .stChatInput > div > div > input {
            background: #0d0d0d;
            color: #0aff9d;
            border: 1px solid #0aff9d;
            border-radius: 10px;
            padding: 8px;
        }

        .stSidebar {
            background: rgba(20, 20, 20, 0.8);
            border-right: 1px solid #0aff9d;
        }

        .stSidebar h1 {
            color: #0aff9d;
            text-align: center;
        }
        
        .message-container {
            border-radius: 10px;
            padding: 10px;
            background-color: rgba(10, 10, 10, 0.9);
            margin: 10px 0;
        }
        
        .assistant-message {
            background: #222;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #0aff9d;
            color: #0aff9d;
        }
        
        .user-message {
            background: #333;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ff0a78;
            color: #ff0a78;
        }

        .blinking-cursor {
            animation: blink 1s infinite;
        }

        @keyframes blink {
            50% { opacity: 0; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit UI
st.title("💻 Code Mentor AI 🤖")

# Available models
available_models = [
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-4.5-preview",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k"
]

# Sidebar with glass effect
st.sidebar.markdown("## ⚙️ Settings")
st.session_state.model = st.sidebar.selectbox("Choose a model:", available_models, index=0)

# System-level prompt
system_prompt = {
    "role": "system",
    "content": (
        "You are a highly skilled AI coding assistant. Your job is to:\n"
        "1. Provide optimized code solutions.\n"
        "2. Break down problems step by step.\n"
        "3. Offer best practices and explanations.\n"
        "4. Analyze uploaded code files.\n"
        "5. Process and analyze images (code snippets, diagrams, handwritten notes).\n"
        "6. Keep responses concise but informative."
    )
}

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [system_prompt]

# File Upload Feature
st.sidebar.markdown("## 📂 Upload a File")
uploaded_file = st.sidebar.file_uploader("Upload `.py`, `.txt`, `.csv`, `.json`", type=["py", "txt", "csv", "json"])

if uploaded_file:
    file_contents = uploaded_file.read().decode("utf-8")
    st.session_state.messages.append({"role": "user", "content": f"File `{uploaded_file.name}` uploaded.\n\n{file_contents}"})

# Image Upload Feature
st.sidebar.markdown("## 📷 Upload or Paste an Image")
uploaded_image = st.sidebar.file_uploader("Upload an image (`.png`, `.jpg`, `.jpeg`)", type=["png", "jpg", "jpeg"])

if uploaded_image:
    image = Image.open(uploaded_image)
    st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)

# Display chat history
for message in st.session_state["messages"][1:]:
    role_class = "assistant-message" if message["role"] == "assistant" else "user-message"
    st.markdown(f'<div class="message-container {role_class}">{message["content"]}</div>', unsafe_allow_html=True)

# User input
if user_prompt := st.chat_input("Ask about coding problems or optimizations..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Generate AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=st.session_state.model,
                messages=st.session_state.messages,
                stream=True,
            )
            for chunk in stream:
                token = chunk.choices[0].delta.content
                if token is not None:
                    full_response += token
                    message_placeholder.markdown(full_response + '<span class="blinking-cursor">▌</span>', unsafe_allow_html=True)

            message_placeholder.markdown(full_response)

            # Store response in session
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"❌ Error: {e}")
