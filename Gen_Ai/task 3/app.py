import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from utils.resume_parser import extract_text
from chains.extraction_chain import get_extraction_chain
from chains.scoring_chain import get_scoring_chain

# Load environment variables (API credentials, LangSmith tracing config)
load_dotenv(override=True)

st.set_page_config(page_title="AI Resume Screening System", page_icon="📝", layout="wide")

st.title("AI Resume Screening System")
st.markdown("An AI-powered system for evaluating candidate resumes against a Job Description.")

st.sidebar.title("Configuration")
model_name = st.sidebar.selectbox("Select Groq Model", ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"])

# Ensure API Key is available
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key or groq_api_key == "your_groq_api_key_here":
    st.sidebar.error("Error: Please set a valid GROQ_API_KEY in your .env file.")
    st.stop()

# Initialize LLM with structured output capabilities
llm = ChatGroq(model=model_name, temperature=0.0, groq_api_key=groq_api_key)

# Build the chains
extraction_chain = get_extraction_chain(llm)
scoring_chain = get_scoring_chain(llm)

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Candidate Resume")
    uploaded_resume = st.file_uploader("Upload a Resume (PDF or TXT)", type=["pdf", "txt"])

with col2:
    st.subheader("2. Job Description")
    job_description = st.text_area("Paste the Job Description here", height=300)

if st.button("Evaluate Candidate", type="primary"):
    if not uploaded_resume:
        st.warning("Please upload a candidate resume.")
    elif not job_description.strip():
        st.warning("Please enter a job description.")
    else:
        st.markdown("---")
        
        try:
            # 1. Parsing
            with st.spinner("Parsing documents..."):
                resume_text = extract_text(uploaded_resume)
            
            # 2. Skill Extraction
            with st.spinner("Analyzing Resume (Extracting Skills, Experience, Tools)..."):
                extraction_result = extraction_chain.invoke({"resume_text": resume_text})
            
            st.subheader("🔍 Extracted Candidate Profile")
            st.write(f"**Skills:** {', '.join(extraction_result.skills) if extraction_result.skills else 'None detected'}")
            st.write(f"**Tools:** {', '.join(extraction_result.tools) if extraction_result.tools else 'None detected'}")
            st.write(f"**Experience Summary:** {extraction_result.experience}")

            st.markdown("---")

            # 3. Matching & Scoring
            with st.spinner("Evaluating applicant fit..."):
                extracted_details_str = f"Skills: {', '.join(extraction_result.skills)}\nExperience: {extraction_result.experience}\nTools: {', '.join(extraction_result.tools)}"
                
                eval_result = scoring_chain.invoke({
                    "extracted_details": extracted_details_str,
                    "job_description": job_description
                })

            # 4. Results Display
            st.subheader("🎯 Evaluation Results")
            
            # Color-code the score display based on value
            score_color = "normal"
            if eval_result.fit_score >= 80:
                score_color = "green"
            elif eval_result.fit_score < 50:
                score_color = "red"
                
            st.metric(label="Fit Score", value=f"{eval_result.fit_score}/100")
            st.progress(eval_result.fit_score / 100)
            
            st.write("**Reasoning & Explanation:**")
            st.info(eval_result.explanation)
            
            st.success("✅ Evaluation Complete! You can view the full process trace in LangSmith.")

        except Exception as e:
            st.error(f"An error occurred during evaluation: {e}")