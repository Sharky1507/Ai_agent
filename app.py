import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os
import tempfile
import io
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from agent import VisualizationAgent

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Please set the GOOGLE_API_KEY environment variable")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Set up page configuration
st.set_page_config(
    page_title="Data Visualization Pipeline",
    page_icon="📊",
    layout="wide"
)

# Application title and description
st.title("🧠 AI-Powered Data Visualization Pipeline")
st.markdown("""
Upload your structured data (CSV or Excel) and ask questions about it. 
The AI will analyze your data and create visualizations to answer your questions.
""")

# Initialize session state for storing data
if 'df' not in st.session_state:
    st.session_state.df = None
if 'filename' not in st.session_state:
    st.session_state.filename = None
if 'file_ext' not in st.session_state:
    st.session_state.file_ext = None
if 'visualization_history' not in st.session_state:
    st.session_state.visualization_history = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""

# Function to load and parse data with caching
@st.cache_data
def load_data(uploaded_file):
    filename = uploaded_file.name
    file_ext = os.path.splitext(filename)[1].lower()
    
    try:
        if file_ext == '.csv':
            df = pd.read_csv(uploaded_file)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None, None
        
        return df, filename, file_ext
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None, None, None

# Initialize Visualization Agent
agent = VisualizationAgent(api_key=GOOGLE_API_KEY)

# File uploader section
st.subheader("1️⃣ Load Your Data")

# Add tabs for upload or sample data
data_source = st.radio(
    "Choose your data source:",
    ("Upload your own data", "Use sample data")
)

if data_source == "Upload your own data":
    uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        # Load and display the data
        df, filename, file_ext = load_data(uploaded_file)
        
        # Store in session state if data loaded successfully
        if df is not None:
            st.session_state.df = df
            st.session_state.filename = filename
            st.session_state.file_ext = file_ext
            
            st.success(f"File '{filename}' loaded successfully!")
            
            # Display dataframe info
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Data Preview")
                st.dataframe(df.head())
            
            with col2:
                st.subheader("Data Information")
                buffer = io.StringIO()
                df.info(buf=buffer)
                info_str = buffer.getvalue()
                st.text(info_str)
                
                st.subheader("Data Statistics")
                st.dataframe(df.describe())
else:
    # Load sample data
    try:
        sample_path = os.path.join(os.path.dirname(__file__), "sample_data.csv")
        df = pd.read_csv(sample_path)
        filename = "sample_data.csv"
        file_ext = ".csv"
        st.success("Sample data loaded successfully!")
    except Exception as e:
        st.error(f"Error loading sample data: {e}")
        df, filename, file_ext = None, None, None
    
    if df is not None:
        st.session_state.df = df
        st.session_state.filename = filename
        st.session_state.file_ext = file_ext
        
        st.success(f"File '{filename}' loaded successfully!")
        
        # Display dataframe info
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Data Preview")
            st.dataframe(df.head())
        
        with col2:
            st.subheader("Data Information")
            buffer = io.StringIO()
            df.info(buf=buffer)
            info_str = buffer.getvalue()
            st.text(info_str)
            
            st.subheader("Data Statistics")
            st.dataframe(df.describe())

# User question input
if st.session_state.df is not None:
    st.subheader("2️⃣ Ask Questions About Your Data")
    
    # Example questions
    st.markdown("### Example Questions")
    example_questions = [
        "Show me a histogram of sales",
        "Create a scatter plot of sales vs units",
        "What is the correlation between sales and units?",
        "Show me the sales trend by region",
        "Create a bar chart of total sales by product",
        "Which product has the highest average sales?",
        "Analyze sales by customer type"
    ]
    
    cols = st.columns(3)
    for i, question in enumerate(example_questions):
        if cols[i % 3].button(question, key=f"example_{i}"):
            st.session_state.current_question = question
    
    question = st.text_input(
        "What would you like to know about your data?", 
        value=st.session_state.get("current_question", ""),
        placeholder="E.g., Show me the correlation between variables X and Y, Plot a histogram of column Z"
    )
    if st.button("Generate Visualization") and question:
        with st.spinner("Generating visualization... This may take a moment."):
            try:
                # Generate and execute code using the agent
                result = agent.analyze_data(st.session_state.df, question)
                
                # Add to history
                st.session_state.visualization_history.append({
                    "question": question,
                    "code": result.get("code", ""),
                    "result": result.get("result", ""),
                    "status": result.get("status", "unknown")
                })
                
                # Display success message                
                st.success("Visualization generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating visualization: {e}")
    
    # visualization history
    if st.session_state.visualization_history:
        st.subheader("Visualization History")
        
        for i, entry in enumerate(st.session_state.visualization_history):
            with st.expander(f"Q: {entry['question']}", expanded=(i == len(st.session_state.visualization_history) - 1)):
                st.markdown(f"**Question:** {entry['question']}")
                st.markdown(f"**Status:** {entry['status']}")
                tabs = st.tabs(["Result", "Generated Code"])
                with tabs[0]:
                    # Execute the code directly
                    try:
                        exec(entry['code'])
                        
                        # download button for the current visualization
                        if "plt" in entry['code'] or "px" in entry['code'] or "go" in entry['code']:
                            st.markdown("---")
                            save_options = st.columns(3)
                            
                            # for matplotlib
                            if "plt" in entry['code']:
                                with save_options[0]:
                                    if st.button("Save as PNG", key=f"png_{i}"):
                                        # Add code to save matplotlib figure
                                        plt.savefig(f"visualization_{i}.png", dpi=300, bbox_inches='tight')
                                        st.success(f"Saved as visualization_{i}.png")
                            
                            
                            with save_options[2]:
                                if st.button("Copy Code", key=f"copy_{i}"):
                                    st.code(entry['code'])
                                    st.success("Code copied to clipboard! You can now paste it into your own script.")
                                    
                    except Exception as e:
                        st.error(f"Error executing code: {e}")
                
                with tabs[1]:
                    st.code(entry['code'], language='python')
else:
    st.info("Please upload a file to begin.")

# Footer
st.markdown("---")
st.markdown("Created By Mohammed Kafeel")
st.markdown("This AI-powered visualization pipeline allows you to analyze and visualize data using natural language queries.")
