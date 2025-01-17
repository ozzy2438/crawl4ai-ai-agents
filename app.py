# Import required libraries
import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from crawler import Crawler
from embeddings import EmbeddingHandler
from llm_chain import LLMChain
import openai
import logging

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Crawl4AI Web Crawler & Chat",
    page_icon="🕷️",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_KEY", "")

if not supabase_url or not supabase_key:
    st.error("Supabase credentials are missing. Please check your .env file.")
    logging.error("Supabase credentials are missing")
    st.stop()

logging.info(f"Initializing Supabase client with URL: {supabase_url}")
supabase: Client = create_client(supabase_url, supabase_key)

# Test Supabase connection
try:
    test_response = supabase.table("crawled_data").select("count").execute()
    logging.info("Supabase connection test successful")
except Exception as e:
    st.error("Failed to connect to Supabase")
    logging.error(f"Supabase connection error: {str(e)}")
    st.stop()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY", "")

# Initialize embedding handler with Supabase client
embedding_handler = EmbeddingHandler(supabase_client=supabase)

def load_crawled_websites():
    """Load crawled websites from Supabase."""
    try:
        logging.info("Attempting to load crawled websites from Supabase")
        response = supabase.table("crawled_data").select("url").execute()
        if response.data:
            # Get unique URLs
            urls = list(set(item['url'] for item in response.data))
            logging.info(f"Found {len(urls)} unique URLs in database")
            return urls
        logging.warning("No URLs found in database")
        return []
    except Exception as e:
        logging.error(f"Error loading websites from Supabase: {str(e)}")
        st.error(f"Error loading websites: {str(e)}")
        return []

def save_website_to_session(url: str):
    """Save website to session state and initialize its message history."""
    if 'crawled_urls' not in st.session_state:
        st.session_state.crawled_urls = []
    if url not in st.session_state.crawled_urls:
        st.session_state.crawled_urls.append(url)
        st.session_state.messages[url] = []  # Initialize empty message history for new URL
    st.session_state.selected_url = url  # Auto-select newly crawled website
    st.rerun()  # Force refresh to show new website in sidebar

def update_session_state(key, value):
    """Update session state without triggering rerun."""
    if key not in st.session_state or st.session_state[key] != value:
        st.session_state[key] = value

# Add custom CSS
st.markdown("""
<style>
/* Force white text color everywhere */
div[data-testid*="stMarkdown"] p, 
div[data-testid*="stMarkdown"] span,
div[data-testid*="stMarkdown"] h1,
div[data-testid*="stMarkdown"] h2,
div[data-testid*="stMarkdown"] h3,
div[data-testid*="stMarkdown"] li,
.stTextInput input,
.stTextInput label,
.stNumberInput input,
.stNumberInput label,
.stSelectbox label,
.stSelectbox > div,
button,
.stAlert p,
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] span {
    color: #ffffff !important;
}

/* Dark backgrounds */
[data-testid="stAppViewContainer"] {
    background-color: #121212;
}

[data-testid="stSidebar"] {
    background-color: #1e1e1e;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: #1e1e1e !important;
    border: 1px solid #4e4376;
    margin: 0.5rem 0;
}

/* User message */
[data-testid="user-message"] {
    background-color: #2b5876 !important;
}

/* Assistant message */
[data-testid="assistant-message"] {
    background-color: #1e1e1e !important;
}

/* Links */
a {
    color: #64b5f6 !important;
}

/* Buttons */
.stButton button {
    background-color: #2b5876 !important;
    color: #ffffff !important;
    border: 1px solid #4e4376 !important;
}

/* Input fields */
.stTextInput input,
.stNumberInput input {
    background-color: #1e1e1e !important;
    border: 1px solid #4e4376 !important;
}

/* Selectbox */
.stSelectbox > div {
    background-color: #1e1e1e !important;
    border: 1px solid #4e4376 !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize session states at the beginning
if 'crawled_urls' not in st.session_state:
    st.session_state.crawled_urls = load_crawled_websites()

if 'messages' not in st.session_state:
    st.session_state.messages = {}  # Change to dictionary to store messages per URL

if 'selected_url' not in st.session_state:
    st.session_state.selected_url = None

# Title with professional design
st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h1 style='font-size: 2rem; font-weight: 500;'>Crawl4AI</h1>
        <p style='color: #808080; font-size: 1rem;'>Professional Web Crawler & AI Chat Interface</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar with professional design
with st.sidebar:
    st.markdown("### Settings")
    max_pages = st.number_input("Max Pages", min_value=1, value=100)
    os.environ["MAX_PAGES"] = str(max_pages)
    
    st.markdown("### Crawled Websites")
    
    if st.session_state.crawled_urls:
        for url in st.session_state.crawled_urls:
            cols = st.columns([6, 1])
            with cols[0]:
                if st.button(f"🔍 {url}", key=f"btn_{url}"):
                    st.session_state.selected_url = url
                    if url not in st.session_state.messages:
                        st.session_state.messages[url] = []
                    st.rerun()
            with cols[1]:
                if st.button("×", key=f"del_{url}"):
                    st.session_state.crawled_urls.remove(url)
                    if url in st.session_state.messages:
                        del st.session_state.messages[url]
                    supabase.table("crawled_data").delete().eq("url", url).execute()
                    if st.session_state.selected_url == url:
                        st.session_state.selected_url = None
                    st.rerun()
    else:
        st.info("No websites crawled")

# Main content with professional tabs
tab1, tab2 = st.tabs(["Crawler", "Chat"])

# Crawler Tab
with tab1:
    st.markdown("### Web Crawler")
    url = st.text_input("URL", placeholder="https://example.com")
    
    if st.button("Start Crawling", use_container_width=True):
        if url:
            try:
                with st.status("Crawling website...") as status:
                    # Initialize crawler
                    crawler = Crawler(max_pages=max_pages)
                    crawler.browser_config.javascript_enabled = True
                    
                    # Start crawling
                    crawled_data = crawler.crawl(url)
                    
                    if not crawled_data:
                        st.error("No content was found on this website. Please check the URL and try again.")
                        st.stop()
                    
                    status.update(label="Processing and storing data...")
                    
                    # Initialize embedding handler with Supabase client
                    embedding_handler = EmbeddingHandler(supabase_client=supabase)
                    
                    # Process and store embeddings
                    success = embedding_handler.process_and_store(crawled_data)
                    
                    if not success:
                        st.error("Failed to process and store the crawled data.")
                        st.stop()
                    
                    # Save to session state
                    save_website_to_session(url)
                    
                    st.success(f"Successfully crawled and processed {len(crawled_data)} pages from {url}")
                    
            except Exception as e:
                st.error(f"An error occurred during crawling: {str(e)}")
                logging.error(f"Crawling error: {str(e)}")
                logging.error(f"Full error details: {repr(e)}")
        else:
            st.warning("Please enter a URL to crawl")

# Chat Tab
with tab2:
    st.markdown("### AI Chat Interface")
    
    # Website selection
    if st.session_state.crawled_urls:
        cols = st.columns([4, 1])
        with cols[0]:
            selected_url = st.selectbox(
                "Select Website",
                st.session_state.crawled_urls,
                index=st.session_state.crawled_urls.index(st.session_state.selected_url) if st.session_state.selected_url in st.session_state.crawled_urls else 0
            )
            # Update selected_url in session state
            if selected_url != st.session_state.selected_url:
                st.session_state.selected_url = selected_url
                st.rerun()
        
        with cols[1]:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Clear"):
                if selected_url in st.session_state.messages:
                    st.session_state.messages[selected_url] = []
                st.rerun()
        
        # Initialize message history for selected URL if not exists
        if selected_url not in st.session_state.messages:
            st.session_state.messages[selected_url] = []
        
        # Display chat messages for selected website
        for message in st.session_state.messages[selected_url]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask a question..."):
            st.session_state.messages[selected_url].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    with st.spinner("Thinking..."):
                        chain = LLMChain()
                        result = chain.query(prompt, url_filter=selected_url)
                        
                        if result['answer']:
                            response = f"{result['answer']}\n\n"
                            if result.get('sources'):
                                response += "---\n\n"
                                response += "**Sources:**\n"
                                for source in result['sources']:
                                    response += f"- [{source}]({source})\n"
                        else:
                            response = f"I couldn't find any relevant information about that in {selected_url}. Try asking a different question or selecting another website."
                        
                        st.markdown(response)
                        st.session_state.messages[selected_url].append({"role": "assistant", "content": response})
                        
                except Exception as e:
                    error_msg = f"An error occurred while processing your request: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages[selected_url].append({"role": "assistant", "content": error_msg})
    else:
        st.info("Please crawl a website first") 