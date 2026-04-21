import os
os.environ["OPENAI_API_KEY"] = "sk-proj-PASTE_YOUR_REAL_KEY"

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


# Create LLM
llm = ChatOpenAI()

# Prompt
extract_prompt = PromptTemplate(
    input_variables=["resume"],
    template="""
Extract:
- Skills
- Experience
- Tools

Resume:
{resume}
"""
)

# Function
def extract_data(resume):
    chain = extract_prompt | llm
    return chain.invoke({"resume": resume})

# Load resume
with open("data/strong_resume.txt") as f:
    resume = f.read()

# Run
result = extract_data(resume)

# Output
print("\n===== OUTPUT =====\n")
print(result)
