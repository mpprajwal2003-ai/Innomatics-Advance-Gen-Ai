from langchain.prompts import PromptTemplate

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
