import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(
    page_title="AI Student & Career Assistant",
    page_icon="logo.png",
    layout="wide",
)


# PROFESSIONAL AI ASSISTANT THEME
st.markdown("""
<style>
    :root {
        color-scheme: light;
        --orange: #F58232;
        --ink: #202124;
        --muted: #777B82;
        --line: #E6E6E6;
    }

    .stApp {
        background: #F0F0EE;
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: #FFFFFF;
    }

    .block-container {
        max-width: 1120px;
        padding: 2rem 2rem 3rem;
        background: #FFFFFF;
        min-height: 94vh;
        border-radius: 15px;
        box-shadow: 0 8px 35px rgba(0, 0, 0, 0.07);
    }

    [data-testid="stSidebar"] {
        background: #171717;
        border-right: 1px solid #292929;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: #171717;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #F0F0F0;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #C4C4C4;
    }

    h1, h2, h3 {
        color: #202124;
        letter-spacing: -0.5px;
    }

    h1 {
        font-weight: 750;
    }

    p, li, label {
        color: #414348;
    }

    [data-testid="stCaptionContainer"] {
        color: #777B82;
    }

    [data-testid="stChatMessage"] {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 15px;
        padding: 17px 19px;
        margin-bottom: 14px;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.035);
        animation: appear 0.3s ease-out both;
    }

    [data-testid="stChatMessage"] p {
        color: #303238;
        line-height: 1.7;
    }

    [data-testid="stChatInput"] {
        background: #FFFFFF;
        border: 1px solid #DDDDDD;
        border-radius: 15px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.045);
        transition: border-color 0.2s ease,
                    box-shadow 0.2s ease;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #F58232;
        box-shadow: 0 0 0 3px rgba(245, 130, 50, 0.12);
    }

    [data-testid="stChatInput"] textarea {
        color: #202124;
        caret-color: #F58232;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #929292;
    }

    .stButton > button,
    .stDownloadButton > button {
        background: #F58232;
        color: #FFFFFF;
        border: 1px solid #F58232;
        border-radius: 9px;
        font-weight: 600;
        transition: background 0.2s ease,
                    transform 0.2s ease,
                    box-shadow 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #E96E1D;
        color: #FFFFFF;
        border-color: #E96E1D;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(245, 130, 50, 0.2);
    }

    [data-testid="stSidebar"] .stButton > button {
        background: #F58232;
        color: #FFFFFF;
        border-color: #F58232;
    }

    [data-testid="stSelectbox"] > div > div {
        background: #FFFFFF;
        border: 1px solid #DDDDDD;
        border-radius: 9px;
        color: #202124;
    }

    [data-testid="stAlert"] {
        border-radius: 11px;
    }

    hr {
        border-color: #EAEAEA;
    }

    [data-testid="stChatMessage"] a {
        color: #D9681C;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    @keyframes appear {
        from {
            opacity: 0;
            transform: translateY(6px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @media (prefers-reduced-motion: reduce) {
        [data-testid="stChatMessage"] {
            animation: none;
        }

        .stButton > button,
        .stDownloadButton > button,
        [data-testid="stChatInput"] {
            transition: none;
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1.25rem 0.9rem 2rem;
            min-height: 90vh;
            border-radius: 10px;
        }

        h1 {
            font-size: 1.7rem;
        }

        [data-testid="stChatMessage"] {
            padding: 13px;
        }
    }
</style>
""", unsafe_allow_html=True)

INSTRUCTIONS = """
You are an AI Student Academic and Career Assistant.

Help university students with:
- Academic explanations and study plans
- CV improvement and interview preparation
- Professional emails and writing
- Career guidance and skill development

Guidelines:
- Explain concepts clearly for beginners.
- Use headings and examples when helpful.
- Never invent a student's qualifications or experience.
- Be honest when uncertain and encourage verification.
- Do not promise grades, jobs, or guaranteed outcomes.
"""

TASKS = {
    "General assistance": "Help with the user's question.",
    "Academic learning": "Explain concepts step by step and include examples.",
    "Study planning": "Create a realistic study plan with breaks and priorities.",
    "CV improvement": "Suggest honest, specific improvements to a student's CV.",
    "Interview preparation": "Provide interview practice questions and feedback.",
    "Professional writing": "Help draft clear, polite professional messages.",
}

# Initialize conversation state before displaying sidebar controls.
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🎓 AI Student & Career Assistant")
st.caption("Your companion for learning, study planning, and career preparation.")

def select_welcome_task(task_name, prompt_text):
    st.session_state["task_selector"] = task_name
    st.session_state["pending_prompt"] = prompt_text


with st.sidebar:
    st.image("logo.png", use_container_width=True)
    st.markdown("### AI Student & Career Assistant")
    st.header("Assistant settings")
    task = st.selectbox(
    "Choose a task",
    list(TASKS.keys()),
    key="task_selector",
)

    if not st.session_state.messages:
        st.markdown(
            """
            <div style="text-align:center; padding:45px 10px 20px;">
                <h1 style="font-size:34px;">What can I help you with today?</h1>
                <p style="font-size:16px; color:#777;">
                    Your AI-powered companion for learning and career growth.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.button(
                "📚 Academic Learning",
                use_container_width=True,
                on_click=select_welcome_task,
                args=(
                    "Academic learning",
                    "Act as my academic tutor. Help me start learning immediately. Briefly ask me to specify a subject and topic only if I have not provided one, and offer a few examples relevant to university students. Once I choose a topic, teach it step by step with simple explanations, examples, and a short practice question. Do not give only a generic greeting.",
                ),
            )

            st.button(
                "📄 CV Improvement",
                use_container_width=True,
                on_click=select_welcome_task,
                args=(
                    "CV improvement",
                    "Help me improve my CV and make it more professional.",
                ),
            )

        with col2:
            st.button(
                "📅 Study Planning",
                use_container_width=True,
                on_click=select_welcome_task,
                args=(
                    "Study planning",
                    "Help me create a realistic study plan with breaks and priorities.",
                ),
            )

            st.button(
                "🎤 Interview Preparation",
                use_container_width=True,
                on_click=select_welcome_task,
                args=(
                    "Interview preparation",
                    "Help me prepare for an interview with practice questions and feedback.",
                ),
            )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.session_state.pop("pending_prompt", None) or st.chat_input(
    "Ask your academic or career question..."
)

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        st.error("Groq API key not found. Check your local .env file.")
    else:
        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1",
            )

            history = st.session_state.messages[-12:]
            conversation = [
                {
                    "role": message["role"],
                    "content": message["content"],
                }
                for message in history
            ]

            with st.chat_message("assistant"):
                with st.spinner("Preparing your answer..."):
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    INSTRUCTIONS
                                    + "\nSelected task: "
                                    + task
                                    + "\n"
                                    + TASKS[task]
                                ),
                            },
                            *conversation,
                        ],
                    )

                    answer = response.choices[0].message.content
                    if not answer:
                        answer = "The AI returned an empty response."

                    st.markdown(answer)

                    st.download_button(
                        label="Download answer",
                        data=answer,
                        file_name="student_assistant_answer.txt",
                        mime="text/plain",
                    )

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as exc:
            st.error("The Groq API request failed.")
            st.caption(
                f"Error type: {type(exc).__name__}. "
                "Check your API key, model availability, internet "
                "connection, and Groq usage limits."
            )
