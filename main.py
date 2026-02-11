import streamlit as st
import google.generativeai as genai

from pypdf import PdfReader
import docx
import os
from dotenv import load_dotenv

# Load API Key securely
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    load_dotenv()
    API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Secure ATS Scorer", layout="centered")
st.title("Secure AI Resume Scorer")

def extract_text(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

with st.sidebar:
    st.header(" Resume Source")
    uploaded_file = st.file_uploader("Upload once, test many times", type=["pdf", "docx"])
    if uploaded_file:
        st.success("Resume Loaded!")

st.title(" Multi-Job ATS Optimizer")
st.write("Upload your resume on the left, then paste any Job Description below to analyze.")

jd_input = st.text_area("Paste a Job Description here:", height=300, key="jd_input")

if st.button("Analyze This JD"):
    if not uploaded_file:
        st.error("Please upload a resume in the sidebar first!")
    elif not jd_input:
        st.warning("Please paste a Job Description to compare.")
    else:
        with st.spinner("Comparing resume to this specific JD..."):
            resume_text = extract_text(uploaded_file)
            
            prompt = f"""
            Act as an advanced ATS (Applicant Tracking System). Analyze the following resume against the job description.
            
            JOB DESCRIPTION:
            {jd_input}
            
            RESUME:
            {resume_text}
            
            Provide a response with:
            - **Overall Score**: (Percentage)
            - **Keyword Match**: (Identify missing high-priority skills)
            - **Format Review**: (Mention if any parts were hard to read)
            - **Increasing Your Score**: (3 actionable bullet points to improve the resume)
            """
            
            response = model.generate_content(prompt)
            
            st.markdown("---")
            st.subheader(" Results for this JD")
            st.markdown(response.text)

