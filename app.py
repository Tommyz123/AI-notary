import streamlit as st
import pandas as pd
import re
from deepseek_api import call_openai
from progress import load_progress, save_progress
from dynamic_quiz_generator import generate_dynamic_quiz
from completed_tracker import load_completed, mark_completed, unmark_completed
from vector_utils import build_lesson_vectors, search_lessons

# Markdown cleaning function
def clean_markdown(md_text: str) -> str:
    text = re.sub(r'#* ?', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'[`*_>]', '', text)
    return text

# Load lesson data
@st.cache_data
def load_lessons():
    df = pd.read_csv("lessons.csv", encoding="ISO-8859-1")
    return df.to_dict(orient="records")

# Load explanation template
@st.cache_data
def load_template():
    with open("prompt_template.txt", "r", encoding="ISO-8859-1") as f:
        return f.read()

lessons = load_lessons()
lesson_vectors = build_lesson_vectors(lessons)
template = load_template()

if "current_index" not in st.session_state:
    st.session_state.current_index = load_progress()

# Sidebar navigation
st.sidebar.title("📚 Course Outline")
completed_list = load_completed()
for i, l in enumerate(lessons):
    label = f"✅ {i+1}. {l['Title']}" if l['No'] in completed_list else f"{i+1}. {l['Title']}"
    if st.sidebar.button(label, key=f"jump_{i}"):
        st.session_state.current_index = i
        st.session_state["final_test_mode"] = False
        save_progress(i)

# Final Test button
if st.sidebar.button("🏁 Final Test", key="final_test"):
    st.session_state["final_test_mode"] = True

# Final test logic
if st.session_state.get("final_test_mode", False):
    st.title("🏁 Final Test: Comprehensive Assessment")
    all_content = "\n\n".join([f"Lesson {l['No']}: {l['Content']}" for l in lessons])

    with st.spinner("Generating 50 questions..."):
        quizzes = generate_dynamic_quiz(
            lesson_title="Final Assessment",
            lesson_content=all_content,
            num_questions=50
        )

    score = 0
    submitted = st.button("✅ Submit Final Test")

    for i, item in enumerate(quizzes):
        st.markdown(f"**{i+1}. {item['question']}**")
        choice = st.radio("Select:", item["options"], key=f"final_q{i}")
        user_letter = choice[0] if choice else None
        correct_letter = item["answer"]

        if submitted:
            if user_letter == correct_letter:
                st.success("✅ Correct")
                score += 1
            else:
                st.error(f"❌ Incorrect. Correct answer: {correct_letter}")
            st.caption(f"📘 Explanation: {item['explanation']}")

    if submitted:
        st.markdown(f"### 🧾 Final Score: {score} / {len(quizzes)}")
        if score >= 40:
            st.success("🎉 Excellent! You passed the course!")
        else:
            st.warning("📘 Review the lessons and try again.")

    st.stop()

# Current lesson
idx = st.session_state.current_index
lesson = lessons[idx]
st.title(f"Lesson {lesson['No']}: {lesson['Title']}")
completed = lesson["No"] in completed_list

col1, col2 = st.columns(2)
if completed:
    if col1.button("✅ Completed (Click to Unmark)"):
        unmark_completed(lesson["No"])
        st.rerun()
else:
    if col1.button("📘 Mark as Completed"):
        mark_completed(lesson["No"])
        st.rerun()

# GPT Explanation
if f"explanation_{idx}" not in st.session_state:
    prompt = template.format(
        id=lesson["No"],
        title=lesson["Title"],
        content=lesson["Content"]
    )
    messages = [
        {"role": "system", "content": "You are a professional and structured AI teacher."},
        {"role": "user", "content": prompt}
    ]
    with st.spinner("Generating explanation…"):
        output = call_openai(messages)
        st.session_state[f"explanation_{idx}"] = output

st.markdown(st.session_state[f"explanation_{idx}"])

# 🔈 Speech buttons
clean_text = clean_markdown(st.session_state[f"explanation_{idx}"])
escaped_text = clean_text.replace('"', '\\"').replace("\n", " ")
speech_html = f"""
    <script>
    var utterance;
    function speakText() {{
        if (speechSynthesis.speaking) {{
            speechSynthesis.cancel();
        }}
        utterance = new SpeechSynthesisUtterance("{escaped_text}");
        utterance.lang = "en-US";
        speechSynthesis.speak(utterance);
    }}

    function stopSpeech() {{
        if (speechSynthesis.speaking) {{
            speechSynthesis.cancel();
        }}
    }}
    </script>
    <button onclick="speakText()">🔈 Play Explanation</button>
    <button onclick="stopSpeech()">🛑 Stop</button>
"""
st.components.v1.html(speech_html, height=80)

# Question input
st.subheader("💬 Ask a Question (Optional)")
question = st.text_input("Enter your question:", key="qa_input")

if st.button("Submit Question"):
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        related = search_lessons(question, lessons, lesson_vectors)
        context = "\n\n".join(l["Content"] for l in related) or lesson["Content"]
        qa_prompt = f"""Lesson content:
{context}

Please answer the student's question based on the lesson content above:
Question: {question}
"""
        messages = [
            {"role": "system", "content": "You are a helpful AI teaching assistant."},
            {"role": "user", "content": qa_prompt}
        ]
        with st.spinner("Thinking..."):
            answer = call_openai(messages)
            st.markdown(f"📘 Answer:\n\n{answer}")
        if related:
            st.markdown("### 🔍 Related Lessons")
            for l in related:
                st.markdown(f"- {l['No']}: {l['Title']}")

# Quiz generation
if f"quiz_{idx}" not in st.session_state:
    with st.spinner("Generating quiz…"):
        st.session_state[f"quiz_{idx}"] = generate_dynamic_quiz(
            lesson_title=lesson["Title"],
            lesson_content=lesson["Content"]
        )

if st.button("🔄 Regenerate Quiz"):
    with st.spinner("Regenerating quiz…"):
        st.session_state[f"quiz_{idx}"] = generate_dynamic_quiz(
            lesson_title=lesson["Title"],
            lesson_content=lesson["Content"]
        )
        st.rerun()

quizzes = st.session_state[f"quiz_{idx}"]
st.markdown("### 🧪 Quiz for This Lesson")

score = 0
submitted = st.button("✅ Submit All Quiz Questions")

for i, item in enumerate(quizzes):
    st.markdown(f"**{i+1}. {item['question']}**")
    user_choice = st.radio(
        label="Please select an answer:",
        options=item["options"],
        key=f"quiz_{idx}_{i}"
    )
    user_letter = user_choice[0] if user_choice else None
    correct_letter = item["answer"]

    if submitted:
        if user_letter == correct_letter:
            st.success("✅ Correct")
            score += 1
        else:
            st.error(f"❌ Incorrect. Correct answer: {correct_letter}")
        st.caption(f"📘 Explanation: {item['explanation']}")

# Next lesson
if st.button("▶ Next Lesson"):
    if idx + 1 < len(lessons):
        st.session_state.current_index += 1
        st.session_state["final_test_mode"] = False
        save_progress(st.session_state.current_index)
        st.rerun()
    else:
        st.success("🎉 Congratulations! All lessons completed!")
