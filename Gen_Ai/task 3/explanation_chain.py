from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

explain_prompt = PromptTemplate(
    input_variables=["match", "score"],
    template="""
Explain score.

Match:
{match}

Score:
{score}
"""
)

def explain_data(match, score):
    chain = explain_prompt | llm
    return chain.invoke({"match": match, "score": score})
