# AI-Powered Data Visualization Pipeline

A Streamlit application that uses Generative AI (Gemini) to analyze and visualize data based on natural language questions.

## Features

- Upload CSV or Excel files or use sample data
- Ask questions about your data in natural language
- AI generates and executes Python code for analysis
- Interactive data visualizations with Plotly and Matplotlib
- Save visualizations to disk
- View the generated code for transparency and learning
- Example questions to help users get started
- Caching for improved performance with large datasets
- Handles errors gracefully with automatic code repair

## Prerequisites

- Python 3.7+
- Google API Key for Gemini
- In the existing code gemini flash 2.0 is used, which can be changed in agent.py.

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Add your Google API key to the `.env` file:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Running the Application

### Using the Script

Windows users can double-click the `run.bat` file:
```
.\run.ps1
```

### Manual Start
```
streamlit run app.py
```

Open your web browser and go to `http://localhost:8501`.

## How to Use

1. Choose to upload your own data or use the sample dataset
2. Review the data preview, information, and statistics
3. Click on one of the example questions or write your own
4. View the generated visualization and insights
5. Save or export the visualization if desired
6. Copy the code to use in your own projects


## Tools Used

- **Streamlit**: Frontend for the web application
- **Gemini Flash**: LLM for generating Python analysis code
- **LangChain**: Framework for creating agents that can execute the generated code
- **Pandas**: Data manipulation and analysis
- **Matplotlib/Seaborn/Plotly**: Data visualization libraries

## Project Structure

- `app.py`: Main Streamlit application
- `agent.py`: Implementation of the VisualizationAgent that handles code generation and execution
- `sample_data.csv`: Sample dataset for testing
- `requirements.txt`: Required Python packages
- `.env`: Environment variables (API keys)
- `run.bat`: Convenience scripts to start the application
