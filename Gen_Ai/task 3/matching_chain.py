from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

match_prompt = PromptTemplate(
    input_variables=["resume_data", "job"],
    template="""
Compare resume with job.

Resume:
{resume_data}

Job:
{job}

Return matched and missing skills.
"""
)

def match_data(resume_data, job):
    chain = match_prompt | llm
    return chain.invoke({"resume_data": resume_data, "job": job})
