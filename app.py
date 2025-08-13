import streamlit as st
import pandas as pd
import re
<<<<<<< HEAD
from deepseek_api import call_openai
from progress import load_progress, save_progress
from dynamic_quiz_generator import generate_dynamic_quiz
from completed_tracker import load_completed, mark_completed, unmark_completed
from vector_utils import build_lesson_vectors, search_lessons

# Markdown cleaning function
def clean_markdown(md_text: str) -> str:
=======
import json
import html
import time
from functools import lru_cache
from config import config
from ai_api import call_deepseek, ai_client
from dynamic_quiz_generator import generate_dynamic_quiz
from database import db
from auth import AuthManager, require_auth, get_current_user_id

# ---------- Configuration: Explanation Depth ----------
TARGETS = {
    "Overview (fast)": {"words": 220, "max_tokens": 600},
    "Standard":        {"words": 600, "max_tokens": 1200},
    "In-depth":        {"words": 1200, "max_tokens": 2000},
}

# ---------- Input Validation and Security Functions ----------
def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input to prevent XSS and limit length."""
    if not text:
        return ""
    
    # Limit length
    text = text[:max_length]
    
    # HTML escape
    text = html.escape(text)
    
    # Remove potential script tags and dangerous patterns
    dangerous_patterns = [
        r'<script.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'data:text/html'
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()

def validate_lesson_content(content: str) -> str:
    """Validate and limit lesson content length."""
    if not content:
        return ""
    
    max_length = config.MAX_CONTENT_LENGTH
    if len(content) > max_length:
        st.warning(f"⚠️ Content truncated to {max_length} characters for processing.")
        return content[:max_length]
    
    return content

# ---------- Markdown Cleaning (for speech) ----------
def clean_markdown(md_text: str) -> str:
    if not md_text:
        return ""
    
>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
    text = re.sub(r'#* ?', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'[`*_>]', '', text)
<<<<<<< HEAD
    return text

# Load lesson data
@st.cache_data
def load_lessons():
    df = pd.read_csv("lessons.csv", encoding="ISO-8859-1")
    return df.to_dict(orient="records")

# Load explanation template
=======
    
    # Additional security: remove any remaining HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    return text

# ---------- Load Data from Database ----------
@st.cache_data
def load_lessons():
    """Load lessons from database, fallback to CSV if needed."""
    try:
        with db.get_connection() as conn:
            lessons = conn.execute("""
                SELECT lesson_no as 'No', title as 'Title', content as 'Content'
                FROM lessons ORDER BY CAST(lesson_no AS INTEGER)
            """).fetchall()
            
            if lessons:
                return [dict(lesson) for lesson in lessons]
    except Exception:
        pass
    
    # Fallback to CSV
    try:
        df = pd.read_csv("lessons.csv", encoding="ISO-8859-1")
        return df.to_dict(orient="records")
    except Exception:
        return []

>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
@st.cache_data
def load_template():
    with open("prompt_template.txt", "r", encoding="ISO-8859-1") as f:
        return f.read()

<<<<<<< HEAD
lessons = load_lessons()
lesson_vectors = build_lesson_vectors(lessons)
template = load_template()

if "current_index" not in st.session_state:
    st.session_state.current_index = load_progress()

# Sidebar navigation
st.sidebar.title("📚 Course Outline")
completed_list = load_completed()
=======
def get_user_progress(user_id: int):
    """Get user progress from database."""
    return db.get_user_progress(user_id)

def get_completed_lessons(user_id: int):
    """Get completed lessons for user."""
    return db.get_completed_lessons(user_id)

# ---------- Cached Explanation ----------
@st.cache_data(show_spinner=False)
def explain_cached(lesson_no: str, title: str, content: str, template_text: str, detail_label: str) -> str:
    tgt = TARGETS[detail_label]
    system_msg = (
        f"You are a professional AI teacher. Use ONLY the provided lesson content. "
        f"Write clearly with headings and short paragraphs. Aim for ~{tgt['words']} words. "
        f"If some info is missing in the content, explicitly ask 1–3 clarifying questions."
    )
    prompt = template_text.format(id=lesson_no, title=title, content=content)
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt}
    ]
    return call_deepseek(messages)

# ---------- Point-by-Point Deep Expansion (lazy loading + caching) ----------
@st.cache_data(show_spinner=False)
def expand_point_cached(lesson_no: str, title: str, content: str, point_text: str, detail_label: str) -> str:
    tgt = TARGETS[detail_label]
    target_words = max(400, int(tgt["words"] * 0.6)) if detail_label != "Overview (fast)" else 350
    system_msg = (
        f"You are a professional AI teacher. Use ONLY the provided lesson content. "
        f"Deeply explain the following point with step-by-step reasoning and clear structure. "
        f"Aim for ~{target_words} words. Use headings and bullet lists. Do not invent facts."
    )
    user = f"""Lesson ID: {lesson_no}
Lesson Title: {title}

Lesson Content:
{content}

Focus point to expand:
{point_text}
"""
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user}
    ]
    return call_deepseek(messages)

# ---------- Application Setup ----------
def init_app():
    """Initialize the application."""
    st.set_page_config(
        page_title="Notary Training System",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Initialize app
init_app()

# ---------- Load Data ----------
lessons = load_lessons()
template = load_template()

# Use fixed user ID for single-user mode
USER_ID = 1  # Default user ID

# Initialize session state
if "current_index" not in st.session_state:
    # Try to get from database first
    user_progress = get_user_progress(USER_ID)
    current_index = 0
    
    # Find the highest current_index from user progress
    for lesson_no, progress in user_progress.items():
        if progress.get('current_index', 0) > current_index:
            current_index = progress['current_index']
    
    st.session_state.current_index = current_index

# ---------- Sidebar: Course Outline & Detail Level ----------
st.sidebar.title("📚 Course Outline")

# Get completed lessons from database
completed_list = get_completed_lessons(USER_ID)

>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
for i, l in enumerate(lessons):
    label = f"✅ {i+1}. {l['Title']}" if l['No'] in completed_list else f"{i+1}. {l['Title']}"
    if st.sidebar.button(label, key=f"jump_{i}"):
        st.session_state.current_index = i
        st.session_state["final_test_mode"] = False
<<<<<<< HEAD
        save_progress(i)

# Final Test button
if st.sidebar.button("🏁 Final Test", key="final_test"):
    st.session_state["final_test_mode"] = True

# Final test logic
=======
        # Save progress to database
        db.update_user_progress(USER_ID, l['No'], current_index=i)

# Detail level selection (default: Standard)
detail = st.sidebar.selectbox("Detail level", ["Overview (fast)", "Standard", "In-depth"], index=1)

# Final test entry
if st.sidebar.button("🏁 Final Test", key="final_test"):
    st.session_state["final_test_mode"] = True

# Analytics page entry
if st.sidebar.button("📊 My Analytics", key="analytics"):
    st.session_state["analytics_mode"] = True

# API provider info
st.sidebar.markdown("---")
provider_info = ai_client.get_provider_info()
st.sidebar.markdown("**🤖 AI Provider**")
st.sidebar.markdown(f"Provider: {provider_info['provider'].upper()}")
st.sidebar.markdown(f"Model: {provider_info['model']}")
if provider_info['caching_enabled']:
    st.sidebar.markdown("⚡ Caching: Enabled")

# ---------- Analytics Page Logic ----------
if st.session_state.get("analytics_mode", False):
    from analytics import show_analytics_page
    show_analytics_page()
    
    if st.button("🔙 Back to Lessons"):
        st.session_state["analytics_mode"] = False
        st.rerun()
    
    st.stop()

# ---------- Final Test Logic ----------
>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
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
<<<<<<< HEAD
            st.warning("📘 Review the lessons and try again.")

    st.stop()

# Current lesson
=======
            st.warning("📘 Please review the lessons and try again.")

    st.stop()

# ---------- Current Lesson ----------
>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
idx = st.session_state.current_index
lesson = lessons[idx]
st.title(f"Lesson {lesson['No']}: {lesson['Title']}")
completed = lesson["No"] in completed_list

col1, col2 = st.columns(2)
if completed:
    if col1.button("✅ Completed (Click to Unmark)"):
<<<<<<< HEAD
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
=======
        db.update_user_progress(USER_ID, lesson["No"], is_completed=False)
        st.rerun()
else:
    if col1.button("📘 Mark as Completed"):
        db.update_user_progress(USER_ID, lesson["No"], is_completed=True)
        st.rerun()

content_raw = validate_lesson_content(lesson["Content"])

# ---------- Generate Explanation (adaptive depth + caching) ----------
with st.spinner("Generating explanation…"):
    try:
        output = explain_cached(str(lesson["No"]), lesson["Title"], lesson["Content"], template, detail)
    except Exception as e:
        st.error("❌ Failed to generate explanation")
        st.exception(e)
        output = ""

st.markdown(output if output else "_No content returned._")

# ---------- Point-by-Point Expansion (auto-extract 3-8 points from content) ----------
st.markdown("---")
st.subheader("🔎 Deep dive by point (optional)")
raw_points = [p.strip() for p in re.split(r'[。\.\n;]+', lesson["Content"]) if len(p.strip()) > 30]
points = raw_points[:8] if len(raw_points) > 8 else raw_points

if not points:
    st.caption("No extractable points from content.")
else:
    for i, p in enumerate(points):
        if st.button(f"Explain point {i+1}", key=f"pt_{idx}_{i}"):
            with st.spinner("Expanding…"):
                try:
                    exp = expand_point_cached(str(lesson["No"]), lesson["Title"], lesson["Content"], p, detail)
                except Exception as e:
                    st.error("❌ Failed to expand point")
                    st.exception(e)
                else:
                    st.markdown(exp)

# ---------- Text-to-Speech Controls ----------
clean_text = clean_markdown(output)
>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
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
<<<<<<< HEAD

=======
>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
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

<<<<<<< HEAD
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
=======
# ---------- Student Q&A (adaptive length based on detail level) ----------
st.subheader("💬 Ask a Question (Optional)")
question = st.text_input("Enter your question:", key="qa_input", max_chars=500)

if st.button("Submit Question"):
    sanitized_question = sanitize_input(question)
    if not sanitized_question:
        st.warning("Please enter a valid question.")
    else:
        qa_prompt = f"""Lesson content:
{lesson['Content']}

Please answer the student's question based on the lesson above:
Question: {sanitized_question}
"""
        tgt = TARGETS[detail]
        qa_words = 220 if detail == "Overview (fast)" else (450 if detail == "Standard" else 800)
        qa_system = (
            f"You are a concise teaching assistant. Answer ONLY using the given lesson content. "
            f"Be precise and structured. Aim for ~{qa_words} words."
        )
        messages = [
            {"role": "system", "content": qa_system},
            {"role": "user", "content": qa_prompt}
        ]
        with st.spinner("Thinking..."):
            try:
                answer = call_deepseek(messages)
                st.markdown(f"📘 Answer:\n\n{answer}")
                
                # Save Q&A interaction to database
                db.save_qa_interaction(USER_ID, lesson["No"], sanitized_question, answer, detail)
            except Exception as e:
                st.error("❌ Failed to generate answer")
                st.exception(e)

# ---------- Lesson Quiz ----------
>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
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
<<<<<<< HEAD
=======
user_answers = {}
start_time = time.time() if f"quiz_start_time_{idx}" not in st.session_state else st.session_state[f"quiz_start_time_{idx}"]
if f"quiz_start_time_{idx}" not in st.session_state:
    st.session_state[f"quiz_start_time_{idx}"] = start_time

>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
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
<<<<<<< HEAD
=======
    
    # Store user answer
    user_answers[i] = {
        "question": item["question"],
        "user_answer": user_letter,
        "correct_answer": correct_letter,
        "is_correct": user_letter == correct_letter
    }
>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)

    if submitted:
        if user_letter == correct_letter:
            st.success("✅ Correct")
            score += 1
        else:
            st.error(f"❌ Incorrect. Correct answer: {correct_letter}")
        st.caption(f"📘 Explanation: {item['explanation']}")

<<<<<<< HEAD
# Next lesson
=======
# Save quiz results to database when submitted
if submitted and user_answers:
    time_taken = int(time.time() - start_time)
    db.save_quiz_attempt(USER_ID, lesson["No"], score, len(quizzes), time_taken, user_answers)
    st.info(f"📊 Quiz completed! Score: {score}/{len(quizzes)} ({score/len(quizzes)*100:.1f}%)")

# ---------- Next Lesson ----------
>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
if st.button("▶ Next Lesson"):
    if idx + 1 < len(lessons):
        st.session_state.current_index += 1
        st.session_state["final_test_mode"] = False
<<<<<<< HEAD
        save_progress(st.session_state.current_index)
=======
        
        # Save progress to database
        next_lesson = lessons[st.session_state.current_index]
        db.update_user_progress(USER_ID, next_lesson["No"], current_index=st.session_state.current_index)
        
>>>>>>> c865a80 (更新说明，例如：fix bug / 添加功能)
        st.rerun()
    else:
        st.success("🎉 Congratulations! All lessons completed!")
