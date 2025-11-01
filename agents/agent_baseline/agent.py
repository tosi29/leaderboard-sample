"""AI Agent Baseline - Simple baseline agent for comparison"""

import os
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors import BuiltInCodeExecutor

# Ensure GOOGLE_API_KEY is set
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Define a baseline agent with code execution
root_agent = Agent(
    model='gemini-2.0-flash',  # Use gemini-2.0-flash for code execution support
    name='agent_baseline',
    description="A baseline file search agent with code execution",
    instruction="""Find the requested file using Python code and return its path.

    Important:
    - First check your current directory with os.getcwd()
    - Use absolute paths: os.path.join(os.getcwd(), 'relative/path')
    - Check if paths exist with os.path.exists() before accessing
    - Use os.walk() to search directories recursively

    Format your final response as:
    FOUND: <path_to_file>

    If you cannot find the file, return: FOUND: None
    """,
    code_executor=BuiltInCodeExecutor(),
)
