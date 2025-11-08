import streamlit as st
from rag import RAG
import tempfile
import os
import html
from datetime import datetime

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
    page_title="RAG Document Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- CUSTOM DARK MODE CSS ----------------------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Main Dark Theme */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        background-attachment: fixed;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #6366f1, #8b5cf6);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #8b5cf6, #a78bfa);
    }
    
    /* Main Container */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Header Section */
    .header-section {
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 24px;
        margin-bottom: 40px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 15px;
        letter-spacing: -1px;
        animation: fadeInDown 0.8s ease-out;
    }
    
    .subtitle-text {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: #cbd5e1;
        font-weight: 400;
        margin-top: 10px;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Upload Section */
    .upload-container {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 30px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .upload-container:hover {
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.2);
        transform: translateY(-2px);
    }
    
    /* Chat Container */
    .chat-container {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        display: flex;
        flex-direction: column;
    }
    
    .chat-messages {
        max-height: 400px;
        overflow-y: auto;
        padding: 15px 0;
        margin-bottom: 20px;
        min-height: 100px;
    }
    
    /* Message Bubbles */
    .message-wrapper {
        margin-bottom: 20px;
        animation: slideIn 0.3s ease-out;
    }
    
    .user-message {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 20px 20px 4px 20px;
        margin-left: auto;
        max-width: 75%;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        line-height: 1.6;
        word-wrap: break-word;
    }
    
    .bot-message {
        background: rgba(51, 65, 85, 0.8);
        color: #e2e8f0;
        padding: 16px 24px;
        border-radius: 20px 20px 20px 4px;
        margin-right: auto;
        max-width: 75%;
        border: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        line-height: 1.6;
        word-wrap: break-word;
    }
    
    .bot-message p {
        margin: 0.5em 0;
    }
    
    .bot-message p:first-child {
        margin-top: 0;
    }
    
    .bot-message p:last-child {
        margin-bottom: 0;
    }
    
    .bot-message code {
        background: rgba(0, 0, 0, 0.3);
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9em;
    }
    
    .bot-message pre {
        background: rgba(0, 0, 0, 0.4);
        padding: 12px;
        border-radius: 8px;
        overflow-x: auto;
        border-left: 3px solid #6366f1;
    }
    
    .bot-message ul, .bot-message ol {
        margin: 0.5em 0;
        padding-left: 1.5em;
    }
    
    .bot-message strong {
        color: #a78bfa;
        font-weight: 600;
    }
    
    .message-time {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 6px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .user-message .message-time {
        text-align: right;
    }
    
    .bot-message .message-time {
        text-align: left;
    }
    
    /* Input Section */
    .input-section {
        display: flex;
        gap: 12px;
        margin-top: 10px;
        background: rgba(15, 23, 42, 0.5);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 32px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary Button (Clear/Export) */
    .stButton > button[kind="secondary"] {
        background: rgba(51, 65, 85, 0.8);
        color: #e2e8f0;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(51, 65, 85, 1);
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-2px);
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: rgba(51, 65, 85, 0.8);
        color: #e2e8f0;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .stDownloadButton > button:hover {
        background: rgba(51, 65, 85, 1);
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-2px);
    }
    
    /* Text Input */
    .stTextInput > div > div > input {
        background: rgba(51, 65, 85, 0.6);
        color: #e2e8f0;
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 14px 20px;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        background: rgba(51, 65, 85, 0.8);
    }
    
    /* File Uploader */
    .uploadedFile {
        background: rgba(51, 65, 85, 0.6);
        border: 1px dashed rgba(99, 102, 241, 0.4);
        border-radius: 12px;
        padding: 20px;
        color: #cbd5e1;
    }
    
    /* Status Messages */
    .stSuccess {
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 12px;
        padding: 16px;
        color: #86efac;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 16px;
        color: #93c5fd;
    }
    
    .stSpinner {
        color: #6366f1;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        background: transparent;
    }
    
    /* Sidebar Content */
    .sidebar-content {
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
    }
    
    .sidebar-text {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .sidebar-feature {
        padding: 12px;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 10px;
        margin: 10px 0;
        border-left: 3px solid #6366f1;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 30px 20px;
        color: #94a3b8;
    }
    
    .empty-state-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
        opacity: 0.4;
    }
    
    .empty-state-text {
        font-size: 0.95rem;
        font-family: 'Inter', sans-serif;
        opacity: 0.7;
    }
    
    /* Stats Cards */
    .stats-container {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .stat-card {
        flex: 1;
        background: rgba(30, 41, 59, 0.8);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        color: #cbd5e1;
        font-size: 0.9rem;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- SIDEBAR ----------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content">
        <div class="sidebar-title">🤖 RAG Assistant</div>
        <p class="sidebar-text">Professional Document Q&A System powered by Retrieval-Augmented Generation</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div class="sidebar-content">
        <h4 style="color: #e2e8f0; margin-bottom: 15px;">📋 Features</h4>
        <div class="sidebar-feature">
            <strong style="color: #a78bfa;">📄 Multi-Format Support</strong><br>
            <span class="sidebar-text">PDF, CSV, TXT files</span>
        </div>
        <div class="sidebar-feature">
            <strong style="color: #a78bfa;">🧠 Smart Retrieval</strong><br>
            <span class="sidebar-text">Multi-Query Retriever</span>
        </div>
        <div class="sidebar-feature">
            <strong style="color: #a78bfa;">⚡ Fast Processing</strong><br>
            <span class="sidebar-text">Ollama + Chroma DB</span>
        </div>
        <div class="sidebar-feature">
            <strong style="color: #a78bfa;">🎯 Context-Aware</strong><br>
            <span class="sidebar-text">Answers from your docs only</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------- MAIN PAGE ----------------------
st.markdown("""
<div class="header-section">
    <h1 class="main-title">RAG Document Assistant</h1>
    <p class="subtitle-text">Upload your document and engage in intelligent conversations. Get accurate answers based solely on your document's content.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------- UPLOAD SECTION ----------------------
st.markdown('<div class="upload-container">', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "📂 Upload Document",
    type=["pdf", "csv", "txt"],
    help="Supported formats: PDF, CSV, TXT"
)
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
if "rag_obj" not in st.session_state:
    st.session_state.rag_obj = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False
if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0
if "processing_question" not in st.session_state:
    st.session_state.processing_question = False
if "last_processed_question" not in st.session_state:
    st.session_state.last_processed_question = ""

# Process uploaded file
if uploaded_file is not None:
    # Check if it's a new file
    if st.session_state.get("current_file") != uploaded_file.name:
        st.session_state.current_file = uploaded_file.name
        st.session_state.file_processed = False
        st.session_state.chat_history = []
        st.session_state.rag_obj = None
    
    if not st.session_state.file_processed:
        file_ext = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(uploaded_file.read())
            file_path = tmp.name
        
        with st.spinner("🔄 Processing document... This may take a moment."):
            try:
                rag = RAG(file=file_path)
                rag.load()
                rag.splitting()
                rag.models()
                rag.store()
                rag.prompting()
                
                st.session_state.rag_obj = rag
                st.session_state.file_processed = True
                st.success(f"✅ **{uploaded_file.name}** processed successfully! You can now ask questions.")
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.session_state.file_processed = False
    
    # Show stats if file is processed
    if st.session_state.file_processed:
        # Get file extension from uploaded file name
        file_ext = os.path.splitext(uploaded_file.name)[1]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">{}</div>
                <div class="stat-label">Questions Asked</div>
            </div>
            """.format(len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">{}</div>
                <div class="stat-label">File Type</div>
            </div>
            """.format(file_ext.upper().replace('.', '')), unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">✓</div>
                <div class="stat-label">Ready</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ---------------------- INPUT SECTION (AT TOP) ----------------------
        st.markdown("""
        <div style="margin-top: 20px; margin-bottom: 20px;">
            <h4 style="color: #cbd5e1; font-family: 'Inter', sans-serif; margin-bottom: 15px;">
                💬 Ask Your Question
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        col_input, col_button = st.columns([5, 1])
        
        with col_input:
            # Use a counter to force input refresh when clearing
            if "input_counter" not in st.session_state:
                st.session_state.input_counter = 0
            
            question = st.text_input(
                "Ask a question",
                key=f"question_input_{st.session_state.input_counter}",
                placeholder="Type your question here and press Enter or click Send...",
                label_visibility="collapsed",
                value=""
            )
        
        with col_button:
            st.markdown("<br>", unsafe_allow_html=True)
            ask_button = st.button("Send ➤", type="primary", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle question submission (button click or Enter key)
        question_submitted = ask_button or (question and question.strip() and st.session_state.get("last_processed_question") != question.strip())
        
        if question_submitted and question and question.strip():
            # Prevent duplicate submissions by checking if we're already processing
            if st.session_state.processing_question:
                st.rerun()
            
            # Check if this question was already asked (prevent duplicates)
            last_user_msg = None
            if st.session_state.chat_history:
                for msg in reversed(st.session_state.chat_history):
                    if msg["role"] == "user":
                        last_user_msg = msg["content"]
                        break
            
            # Only process if it's a new question and not currently processing
            if question.strip() != last_user_msg and not st.session_state.processing_question:
                st.session_state.processing_question = True
                
                # Add user message immediately
                user_msg = {
                    "role": "user",
                    "content": question,
                    "timestamp": datetime.now().strftime("%H:%M")
                }
                st.session_state.chat_history.append(user_msg)
                
                # Get answer
                if st.session_state.rag_obj:
                    with st.spinner("🤔 Thinking... Generating response based on your document."):
                        try:
                            answer = st.session_state.rag_obj.chain(question)
                            bot_msg = {
                                "role": "bot",
                                "content": answer,
                                "timestamp": datetime.now().strftime("%H:%M")
                            }
                            st.session_state.chat_history.append(bot_msg)
                        except Exception as e:
                            error_msg = f"Sorry, I encountered an error while processing your question: {str(e)}"
                            st.error(f"❌ Error: {str(e)}")
                            bot_msg = {
                                "role": "bot",
                                "content": error_msg,
                                "timestamp": datetime.now().strftime("%H:%M")
                            }
                            st.session_state.chat_history.append(bot_msg)
                
                # Clear input by incrementing counter and reset processing flag
                st.session_state.input_counter += 1
                st.session_state.processing_question = False
                st.session_state.last_processed_question = question.strip()
                st.rerun()
            elif question.strip() == last_user_msg:
                # If it's a duplicate, just clear the input
                st.session_state.input_counter += 1
                st.rerun()
        
        st.markdown("---")
        
        # ---------------------- CHAT SECTION ----------------------
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        
        if len(st.session_state.chat_history) == 0:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <div class="empty-state-text">No messages yet. Ask your first question below ↓</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for chat in st.session_state.chat_history:
                timestamp = chat.get("timestamp", datetime.now().strftime("%H:%M"))
                if chat["role"] == "user":
                    st.markdown(f"""
                    <div class="message-wrapper">
                        <div class="user-message">
                            {chat['content']}
                            <div class="message-time">{timestamp}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Escape HTML and render bot message
                    escaped_content = html.escape(chat['content']).replace('\n', '<br>')
                    st.markdown(f"""
                    <div class="message-wrapper">
                        <div class="bot-message">
                            {escaped_content}
                            <div class="message-time">{timestamp}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat controls (below chat)
        if len(st.session_state.chat_history) > 0:
            col_clear, col_export, col_spacer = st.columns([1, 1, 4])
            with col_clear:
                if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
                    st.session_state.chat_history = []
                    st.session_state.input_counter += 1
                    st.rerun()
            with col_export:
                chat_text = "\n\n".join([
                    f"{'User' if msg['role'] == 'user' else 'Assistant'} ({msg.get('timestamp', '')}):\n{msg['content']}"
                    for msg in st.session_state.chat_history
                ])
                st.download_button(
                    "📥 Export Chat",
                    chat_text,
                    file_name=f"rag_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    type="secondary"
                )
    
else:
    st.markdown("""
    <div class="upload-container" style="text-align: center; padding: 60px 40px;">
        <div class="empty-state-icon">📄</div>
        <div class="empty-state-text" style="font-size: 1.2rem; margin-top: 20px;">
            Upload a document to get started<br>
            <span style="font-size: 0.9rem; opacity: 0.7;">Supported formats: PDF, CSV, TXT</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

