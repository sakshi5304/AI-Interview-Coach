import streamlit as st
import docx2txt
import PyPDF2
import requests
import base64

# -------------------- Page Config --------------------
st.set_page_config(page_title="AI Interview Coach", layout="centered")



API_KEY = st.secrets["openai"]["api_key"]


# -------------------- Background --------------------
def set_background(image_path):
    with open(image_path, "rb") as img_file:
        b64_img = base64.b64encode(img_file.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64_img}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: 'Segoe UI', sans-serif;
        }}
        h1 {{
            color: #ffb3ec;
            text-align: center;
            font-size: 3rem;
            text-shadow: 2px 2px 4px #000000;
        }}
        .welcome-text {{
            color: white;
            font-size: 20px;
            text-align: center;
            margin-top: 30px;
            text-shadow: 1px 1px 3px #000;
        }}
        .stFileUploader label {{
            color: white !important;
            font-weight: bold;
            font-size: 18px;
        }}
        .stFileUploader div[role="button"] {{
            background: linear-gradient(to right, #6a11cb, #2575fc);
            color: white;
            font-weight: 600;
            border: 2px solid white;
            border-radius: 12px;
            padding: 10px;
            box-shadow: 0 0 10px #2575fc;
            transition: all 0.3s ease;
        }}
        .stFileUploader div[role="button"]:hover {{
            background: linear-gradient(to right, #ff6ec4, #7873f5);
            box-shadow: 0 0 20px #ff6ec4;
        }}
        .stButton > button {{
            background-color: #ff66b2;
            color: black;
            font-size: 18px;
            font-weight: bold;
            border: none;
            border-radius: 15px;
            padding: 12px 30px;
            box-shadow: 0 0 15px #ff66b2;
            transition: 0.3s;
        }}
        .stButton > button:hover {{
            background-color: #ff3385;
            box-shadow: 0 0 25px #ff3385;
        }}
        .content-box {{
            background-color: rgba(0, 0, 0, 0.6);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
            margin-top: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

set_background("pho.png")

# -------------------- Text Extraction --------------------
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([page.extract_text() for page in reader.pages])

def extract_text_from_docx(file):
    return docx2txt.process(file)

def extract_text_from_txt(file):
    return file.read().decode("utf-8")

# -------------------- AI Question Generator --------------------
def generate_questions(resume_text, jd_text):
    prompt = f"""
You are an AI Interview Coach.

Resume:
{resume_text}

Job Description:
{jd_text}

Generate exactly 10 **short**, single-line, **interview questions** tailored to the job description and the resume.

Instructions:
- DO NOT merge multiple questions into one.
- Each question must be **clear and concise**.
- Only bold **1 to 3 keywords** per question (important skills/tools/technologies).
- Use professional language.
- Output only the questions in numbered list (no explanation).
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {response.status_code} - {response.text}"

# -------------------- Page Navigation --------------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# -------------------- Welcome Page --------------------
if st.session_state.page == "welcome":
    st.title("🎯 IntelliHire – Your AI-Powered Interview Coach")
    st.markdown(
        '<div class="welcome-text">Welcome to <b>IntelliHire!</b> — Your personalized AI companion to <b>master job interviews</b> with confidence.<br><br>🚀How it works:<br>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp I. Upload your resume. 📂 <br>II. Upload job description. 🗒️<br> III. let AI ask you exactly what recruiters would. 🧑‍💻<br><br><b>Get <i>tailored</i>, <b>relevant</b> questions instantly.</b></div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    center = st.columns(3)
    with center[1]:
        if st.button("🚀 Click here to Start"):
            st.session_state.page = "main"
            st.rerun()

# -------------------- Main Page --------------------
elif st.session_state.page == "main":
    st.title("🧠 AI INTERVIEW COACH")

    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    resume_file = st.file_uploader("📄 Upload Your Resume", type=["pdf", "docx"])
    jd_file = st.file_uploader("📝 Upload Job Description", type=["txt"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    if st.button("🎯 Generate Interview Questions"):
          if resume_file and jd_file:
            st.success("✅ Files uploaded.")

            resume_text = ""
            if resume_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(resume_file)
            elif resume_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = extract_text_from_docx(resume_file)

            jd_text = extract_text_from_txt(jd_file)

            with st.spinner("🤖 Thinking like an interviewer..."):
                questions_raw = generate_questions(resume_text, jd_text)

            # Clean and format questions
            question_lines = [q.strip() for q in questions_raw.strip().split('\n') if q.strip()]
            formatted_questions = "<ol style='padding-left: 20px;'>"

            for i, q in enumerate(question_lines, start=1):
                # Remove leading number if exists
                if q[0].isdigit():
                    q = q[q.find('.') + 1:].strip()

                # Bold keywords wrapped in "**" (markdown-style bold)
                q = q.replace("**", "<b>").replace("**", "</b>", 1)  # handles up to 1 bold word
                q = q.replace("**", "<b>").replace("**", "</b>", 1)  # handles 2nd
                q = q.replace("**", "<b>").replace("**", "</b>", 1)  # handles 3rd

                formatted_questions += f"<li>{q}</li>"
            formatted_questions += "</ol>"

            st.markdown(f"""
                <div class="content-box" style="background-color: rgba(0,0,0,0.7); padding: 30px; border-radius: 20px; margin-top: 25px; box-shadow: 0 0 20px #000;">
                  <h3 style="color: #ffffff; margin-bottom: 20px;">💬 Your AI Interview Questions:</h3>
                  <div style="color: #f0f0f0; font-size: 17px; line-height: 1.8;">
                    {formatted_questions}
                  </div>
                </div>
            """, unsafe_allow_html=True)

else:
            st.error("⚠️ Please upload both your resume and job description.")
            st.markdown('</div>', unsafe_allow_html=True)
