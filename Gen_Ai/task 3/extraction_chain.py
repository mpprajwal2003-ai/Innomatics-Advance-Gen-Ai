from langchain_openai import ChatOpenAI
from extract_prompt import extract_prompt


llm = ChatOpenAI()

def extract_data(resume):
    chain = extract_prompt | llm
    return chain.invoke({"resume": resume})