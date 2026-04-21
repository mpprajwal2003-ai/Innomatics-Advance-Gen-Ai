from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

score_prompt = PromptTemplate(
    input_variables=["match"],
    template="Give score (0-100): {match}"
)

def score_data(match):
    chain = score_prompt | llm
    return chain.invoke({"match": match})
