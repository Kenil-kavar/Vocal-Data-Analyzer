import autogen
import os

# Configuration for the LLM using Groq API - separate configs for each agent to avoid rate limits
config_list_coordinator = [
    {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "api_key": os.getenv("GROQ_API_KEY1"),
        "base_url": "https://api.groq.com/openai/v1",
        "price": [0.00011, 0.00034]
    }
]

config_list_inspector = [
    {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "api_key": os.getenv("GROQ_API_KEY2"),
        "base_url": "https://api.groq.com/openai/v1",
        "price": [0.00011, 0.00034]
    }
]

config_list_visualizer = [
    {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "api_key": os.getenv("GROQ_API_KEY3"),
        "base_url": "https://api.groq.com/openai/v1",
        "price": [0.00011, 0.00034]
    }
]

config_list_reporter = [
    {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "api_key": os.getenv("GROQ_API_KEY4"),
        "base_url": "https://api.groq.com/openai/v1",
        "price": [0.00011, 0.00034]
    }
]

# Separate llm_configs for each agent - optimized for token efficiency
llm_config_coordinator = {
    "config_list": config_list_coordinator,
    "seed": 42,
    "temperature": 0.1,  # Lower temperature for more deterministic output
    "max_tokens": 1000,  # Limit token output
}

llm_config_inspector = {
    "config_list": config_list_inspector,
    "seed": 42,
    "temperature": 0.1,
    "max_tokens": 1500,  # Slightly higher for data inspection
}

llm_config_visualizer = {
    "config_list": config_list_visualizer,
    "seed": 42,
    "temperature": 0.1,
    "max_tokens": 1200,  # Moderate for code generation
}

llm_config_reporter = {
    "config_list": config_list_reporter,
    "seed": 42,
    "temperature": 0.1,
    "max_tokens": 800,  # Lower for summary reports
}

# Common code execution config for agents
code_execution_config = {
    "work_dir": "coding",
    "use_docker": False
}

# Termination function to detect when workflow is complete
def is_termination_msg(msg):
    """
    Checks if a message indicates the workflow should terminate.
    """
    if not msg:
        return False
    
    content = msg.get("content", "")
    if not isinstance(content, str):
        content = str(content)
    
    content_lower = content.lower().strip()
    
    # Check for empty messages
    if not content_lower:
        return True
    
    # Check for termination keyword
    if "terminate" in content_lower:
        return True
    
    # Check for completion signals
    completion_phrases = [
        "workflow is complete",
        "no further actions are required",
        "no further tasks",
        "analysis is complete"
    ]
    
    for phrase in completion_phrases:
        if phrase in content_lower:
            return True
    
    return False

# 1. Coordinator Agent
coordinator = autogen.UserProxyAgent(
    name="CoordinatorAgent",
    system_message="""You are the coordinator managing the workflow.

Manage DataInspectorAgent, VisualizationAgent, ReportAgent, and CodeExecutor.
Ensure all requested tasks are completed properly.
Let agents finish their work before moving to next task.""",
    code_execution_config=False,
    human_input_mode="NEVER",
)

# 2. Data Inspector Agent
inspector = autogen.AssistantAgent(
    name="DataInspectorAgent",
    llm_config=llm_config_inspector,
    system_message="""You are a data inspector and data cleaner. Only generate code, do not write comments.

Your tasks:
1. Use the provided data preview to list column names and data types.
2. Write minimal Python code to check the full file for missing values and data types.
3. If asked to clean data, generate code to clean it and SAVE the cleaned data in the SAME FORMAT as the original file:
   - If input is CSV, save cleaned data as cleaned_data.csv  
   - If input is Excel, save cleaned data as cleaned_data.xlsx
   - If input is JSON, save cleaned data as cleaned_data.json
4. Use pandas to read and save files. Always save cleaned files with clear names.

When done: Simply respond Data cleaning complete and let the coordinator handle next steps.

Do NOT send empty messages or repeat yourself.""",
    code_execution_config=code_execution_config,
)

# 3. Visualization Agent
visualizer = autogen.AssistantAgent(
    name="VisualizationAgent",
    llm_config=llm_config_visualizer,
    system_message="""You are a data visualization specialist. Only generate code for plots and graphs, do not write comments.

Your tasks:
1. CRITICALLY IMPORTANT: Only create visualizations that are EXPLICITLY mentioned in the user's prompt.
2. If the user does not mention any specific chart type, DO NOT generate any visualizations.
3. COUNT how many of each chart type the user requests:
   - If user says "bar chart", create exactly ONE bar chart
   - If user says "line graph and pie chart", create exactly ONE line graph and ONE pie chart
   - If user says "two bar charts", create exactly TWO bar charts
4. NEVER generate more charts than explicitly requested.
5. Use matplotlib or seaborn to create the exact graph type requested.
6. ALWAYS save every plot as a PNG file with descriptive names:
   - Use names like age_distribution.png, gender_chart.png, correlation_heatmap.png
   - Use plt.savefig with bbox_inches tight and dpi 300
   - DO NOT create multiple versions with different capitalization
7. ALSO save the Python code used to generate each chart:
   - Save code as {chart_name}_code.py (e.g., age_distribution_code.py)
   - Include complete working code with all imports
   - Make code reproducible and self-contained
8. Generate separate PNG files for different visualizations, do not combine them.
9. If no chart is requested, simply respond "No visualizations requested" and let the coordinator handle next steps.

When done: Simply respond Visualizations complete and let the coordinator handle next steps.

Do NOT send empty messages or repeat yourself.""",
    code_execution_config=code_execution_config,
)

# 4. Report Agent
reporter = autogen.AssistantAgent(
    name="ReportAgent",
    llm_config=llm_config_reporter,
    system_message="""You are a reporting agent. Only generate code and a short report, do not write comments.

Your tasks:
1. Create a summary report with essential findings.
2. Save the report as summary_report.xlsx using pandas Excel writer.
3. Include key statistics, insights, and any issues found in the Excel file.

When done: Simply respond Report complete and let the coordinator handle next steps.

Do NOT send empty messages or repeat yourself.""",
    code_execution_config=code_execution_config,
)
