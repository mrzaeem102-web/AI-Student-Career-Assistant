import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(
    page_title="AI Student & Career Assistant",
    page_icon="🎓",
    layout="centered",
)

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

with st.sidebar:
    st.header("Assistant settings")
    task = st.selectbox("Choose a task", list(TASKS.keys()))
    st.info("Review AI-generated information before relying on it.")

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask your academic or career question...")

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
