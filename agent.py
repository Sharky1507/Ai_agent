import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os
import tempfile
import streamlit as st
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import sys
import traceback
import io

class VisualizationAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = self._get_llm()
    
    def _get_llm(self):
        return GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=self.api_key)
    
    def _create_code_prompt(self, df, question):
        """Create a prompt for code generation based on the dataframe and question."""
        # column types to provide better context
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime', 'datetime64']).columns.tolist()
        
        # Format column information
        col_info = "\nNumeric columns: " + ", ".join(numeric_cols) if numeric_cols else ""
        col_info += "\nCategorical columns: " + ", ".join(categorical_cols) if categorical_cols else ""
        col_info += "\nDatetime columns: " + ", ".join(datetime_cols) if datetime_cols else ""
        
        return f"""
        You are a data analysis expert with advanced Python visualization skills.
        You've been given a pandas DataFrame 'df' with the following characteristics:
        
        DataFrame preview:
        {df.head(5).to_string()}
        
        Column data types:
        {df.dtypes.to_string()}
        {col_info}
        
        Basic statistics:
        {df.describe().to_string()}
        
        User question: "{question}"
        
        Generate Python code to analyze the data and create visualizations to answer this question.
        
        IMPORTANT RULES:
            1. Use pandas for data manipulation, and choose the most appropriate visualization library:
            - Use seaborn for statistical visualizations
            - Use plotly for interactive plots
            - Use matplotlib for custom static plots
            2. Add clear titles, labels, and legends to all visualizations
            3. Don't use plt.show() - instead use st.pyplot() for matplotlib/seaborn or st.plotly_chart() for plotly
            4. Include comments explaining what the code does
            5. Handle potential errors gracefully (missing data, type conversions, etc.)
            6. Focus only on generating executable Python code
            7. Make visualizations attractive and informative with appropriate colors and styling
            8. For time series data, consider using line charts with proper date formatting
            9. Add insights and observations as Streamlit text after the visualization
            10. For multiple visualizations, use st.columns() to arrange them side by side when appropriate
            11. Return ONLY Python code without explanations, markdown, or discussion
            12. VERY IMPORTANT: Do NOT create a new dataframe in your code. An existing dataframe called 'df' is already available in the environment.
            13. Do NOT include any sample or dummy data in your response. Work ONLY with the existing 'df' dataframe.
            14. Do NOT include import statements - these are already handled.
            """
    
    def _generate_analysis_code(self, df, question):
        """Generate Python code for data analysis and visualization."""
        prompt = self._create_code_prompt(df, question)
        
        #chain to generate the code
        code_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["prompt"],
                template="{prompt}"
            )
        )
        
        # Generate the code
        response = code_chain.run(prompt=prompt)
        return self._extract_code(response)
    def _extract_code(self, response):
        """Extract code blocks from the LLM response."""
        # get just the code
        if "```python" in response:
            code_blocks = response.split("```python")
            code = code_blocks[1].split("```")[0].strip()
            return code
        elif "```" in response:
            code_blocks = response.split("```")
            if len(code_blocks) > 1:
                return code_blocks[1].strip()
        
        # If no code blocks found, return the raw response
        return response.strip()
    
    def analyze_data(self, df, question):
        """Main method to analyze data and return visualization code and execution."""
        try:
            # analysis code
            generated_code = self._generate_analysis_code(df, question)
            
            
            return {
                "code": generated_code,
                "result": "Code generated successfully. Execute in Streamlit context.",
                "status": "success"
            }
            
        except Exception as e:
            # treaceback for debugging
            exc_info = sys.exc_info()
            error_details = ''.join(traceback.format_exception(*exc_info))
            
            return {
                "code": f"# Error generating code: {str(e)}\n\n'''\n{error_details}\n'''",
                "result": f"Error: {str(e)}",
                "status": "error"
            }
