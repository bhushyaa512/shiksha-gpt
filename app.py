import streamlit as st

from chapter_data import class6_science, class7_science, class8_science

from groq_api import query_groq

from fpdf import FPDF

# ===== PDF CLASS =====

class LessonPDF(FPDF):

    def header(self):

        self.set_font("Arial", "B", 12)

        self.cell(0, 10, "Zilla Parishad AI Lesson Plan", 0, 1, "C")

    def chapter_title(self, title):

        self.set_font("Arial", "B", 12)

        self.cell(0, 10, f"Lesson Title: {title}", 0, 1, "L")

        self.ln(5)

    def chapter_body(self, body):

        self.set_font("Arial", "", 11)

        self.multi_cell(0, 8, body)

        self.ln()

    def add_lesson(self, title, content):

        self.add_page()

        self.chapter_title(title)

        self.chapter_body(content)

# ===== UI SETUP =====

st.set_page_config(page_title="Teacher's Assistant", layout="wide")

st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>Teacher's Assistant</h1>", unsafe_allow_html=True)

st.markdown("---")

st.sidebar.title("Teacher's Panel")

if "prev_class" not in st.session_state:

    st.session_state.prev_class = "6"

selected_class = st.sidebar.selectbox("Select Class", ["6", "7", "8"])

if selected_class != st.session_state.prev_class:

    st.session_state.clear()

    st.session_state.prev_class = selected_class

    st.rerun()

activity = st.sidebar.radio("Select Activity", ["Explain the Topic", "Plan the Lesson"])

# ===== EXPLAIN MODE =====

if activity == "Explain the Topic":

    st.markdown(f"### Mode: Explain the Topic – Class {selected_class}")

    st.markdown("Ask me anything related to any topic you want explained:")

    if "explain_chat" not in st.session_state:

        st.session_state.explain_chat = []

    user_input = st.chat_input("Type your topic or question here...")

    if user_input:

        topic = st.session_state.get("last_topic", "")

        is_follow_up = len(user_input.split()) <= 4

        if is_follow_up and topic and len(st.session_state.explain_chat) >= 2:

            prev_q, prev_a = st.session_state.explain_chat[-2], st.session_state.explain_chat[-1]

            prompt = f"""

You are a helpful teaching assistant for Class {selected_class} in a rural Indian school.

Continue this conversation:

Teacher previously asked: "{prev_q[1]}"

Your answer was: "{prev_a[1]}"

Now the teacher asks: "{user_input}"

This is a follow-up question based on the earlier topic. Answer in the same context using child-friendly language and relatable Indian examples.

"""

        else:

            topic = user_input

            st.session_state.last_topic = topic

            prompt = f"""

You are a helpful teaching assistant.

Explain '{user_input}' to a Class {selected_class} student using the Feynman technique.

Use child-friendly language, very simple words, and include relevant real-life Indian examples.

Pretend you're explaining to a group of 11-year-old students in a rural classroom.

"""

        response = query_groq(prompt)

        st.session_state.explain_chat.append(("user", user_input))

        st.session_state.explain_chat.append(("ai", response))

    for role, msg in st.session_state.explain_chat:

        st.chat_message(role).write(msg)

    st.markdown(" ")

    if st.button("Generate Flowchart"):

        topic = st.session_state.get("last_topic", "")

        if topic:

            with st.spinner("Generating flowchart..."):

                flowchart_prompt = f"""

Generate a simple chapter-level flowchart for the topic: "{topic}"

Use a text-based tree format like:

Main Topic

   ├── Subtopic 1

   ├── Subtopic 2

   └── ...

Use clear, simple terms that a child can understand.

"""

                flowchart_response = query_groq(flowchart_prompt)

                st.code(flowchart_response)

# ===== PLAN LESSON MODE =====

elif activity == "Plan the Lesson":

    subject = st.sidebar.selectbox("Select Subject", ["Science"])

    if selected_class == "6":

        data = class6_science

    elif selected_class == "7":

        data = class7_science

    else:

        data = class8_science

    selected_chapter = st.sidebar.selectbox("Select Chapter", list(data["Chapters"].keys()))

    selected_period = st.sidebar.selectbox("Select Period", list(data["Chapters"][selected_chapter]["Periods"].keys()))

    subtopics = data["Chapters"][selected_chapter]["Periods"][selected_period]

    st.markdown(f"### Mode: Plan the Lesson – Class {selected_class}")

    st.markdown(f"**Chapter:** {selected_chapter}")

    st.markdown(f"**Period:** {selected_period}")

    st.markdown("**Subtopics:**")

    for s in subtopics:

        st.write(f"- {s}")

    if "lesson_plan" not in st.session_state:

        st.session_state.lesson_plan = ""

    if "lesson_chat" not in st.session_state:

        st.session_state.lesson_chat = []

    if st.button("Generate Lesson Plan"):

        lesson_prompt = f"""

You are an AI assistant helping teachers.

Create a textbook-based lesson plan for Class {selected_class} Science.

Chapter: {selected_chapter}

Period: {selected_period}

Subtopics: {', '.join(subtopics)}

Include:

- Learning Objectives

- Hook (Engaging Introduction)

- Simple Explanation

- Real-life Indian Examples

- Fun Activity

- Recap

- Homework

Use child-friendly tone suitable for a rural classroom.

"""

        st.session_state.lesson_plan = query_groq(lesson_prompt)

        st.session_state.lesson_chat = []

        flowchart_prompt = f"""

Generate a chapter-level flowchart for Class {selected_class} Science chapter "{selected_chapter}".

Use a tree-style text format:

Chapter

   ├── Subtopic 1

   ├── Subtopic 2

   └── ...

Keep it short, child-friendly, and easy to understand.

"""

        st.session_state.flowchart_plan = query_groq(flowchart_prompt)

    if st.session_state.lesson_plan:

        st.success("Lesson Plan Ready!")

        st.write(st.session_state.lesson_plan)

        if st.session_state.get("flowchart_plan"):

            st.markdown("### Chapter Flowchart:")

            st.code(st.session_state.flowchart_plan)

        # ==== PDF Export Button ====

        if st.button("Download as PDF"):

            pdf = LessonPDF()

            lesson_title = f"{selected_chapter} - {selected_period}"

            lesson_content = st.session_state.lesson_plan

            pdf.add_lesson(lesson_title, lesson_content)

            pdf_path = f"{lesson_title.replace(' ', '_').replace('-', '_')}.pdf"

            pdf.output(pdf_path)

            st.success("PDF Generated!")

            st.markdown(f"👉 [Click here to download]({pdf_path})")

    follow_up = st.chat_input("Ask a follow-up question about this lesson")

    if follow_up:

        follow_prompt = f"""

You are helping a teacher with a lesson for Class {selected_class}.

Chapter: {selected_chapter}

Period: {selected_period}

Subtopics: {', '.join(subtopics)}

Teacher's follow-up question: {follow_up}

Answer in a very simple, student-friendly way using Indian examples if possible.

"""

        follow_reply = query_groq(follow_prompt)

        st.session_state.lesson_chat.append(("user", follow_up))

        st.session_state.lesson_chat.append(("ai", follow_reply))

    for role, msg in st.session_state.lesson_chat:

        st.chat_message(role).write(msg) 