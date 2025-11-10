import streamlit as st
import pandas as pd
import re
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

    text = re.sub(r'#* ?', '', md_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'[`*_>]', '', text)

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

@st.cache_data
def load_template():
    with open("prompt_template.txt", "r", encoding="ISO-8859-1") as f:
        return f.read()

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

for i, l in enumerate(lessons):
    label = f"✅ {i+1}. {l['Title']}" if l['No'] in completed_list else f"{i+1}. {l['Title']}"
    if st.sidebar.button(label, key=f"jump_{i}"):
        st.session_state.current_index = i
        st.session_state["final_test_mode"] = False
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
if st.session_state.get("final_test_mode", False):
    st.title("🏁 Final Test: Comprehensive Assessment")

    # Generate questions if not already generated
    if "final_test_questions" not in st.session_state:
        all_content = "\n\n".join([f"Lesson {l['No']}: {l['Content']}" for l in lessons])
        with st.spinner("Generating 50 questions... This may take a minute."):
            st.session_state["final_test_questions"] = generate_dynamic_quiz(
                lesson_title="Final Assessment",
                lesson_content=all_content,
                num_questions=50
            )

    quizzes = st.session_state["final_test_questions"]

    # ========== OPTIMIZATION: Final Test Pagination ==========
    FINAL_TEST_PER_PAGE = 10

    # Initialize page state
    if "final_test_page" not in st.session_state:
        st.session_state["final_test_page"] = 0

    current_page = st.session_state["final_test_page"]
    total_pages = (len(quizzes) - 1) // FINAL_TEST_PER_PAGE + 1

    # Calculate indices
    start_idx = current_page * FINAL_TEST_PER_PAGE
    end_idx = min(start_idx + FINAL_TEST_PER_PAGE, len(quizzes))

    # Show page info
    st.info(f"📄 Page {current_page + 1} of {total_pages} | Questions {start_idx + 1}-{end_idx} of {len(quizzes)}")

    # Show progress
    total_answered = sum(1 for i in range(len(quizzes)) if f"final_q{i}" in st.session_state)
    st.caption(f"✍️ Progress: {total_answered}/{len(quizzes)} questions answered")

    # Display questions for current page
    for i in range(start_idx, end_idx):
        item = quizzes[i]
        st.markdown(f"**{i+1}. {item['question']}**")
        choice = st.radio("Select:", item["options"], key=f"final_q{i}")

    # Pagination controls
    st.markdown("---")
    page_col1, page_col2, page_col3, page_col4 = st.columns([1, 2, 2, 1])

    with page_col1:
        if st.button("⬅️ Prev", disabled=(current_page == 0), key="final_prev"):
            st.session_state["final_test_page"] = current_page - 1
            st.rerun()

    with page_col2:
        st.markdown(f"<center>Page {current_page + 1} / {total_pages}</center>", unsafe_allow_html=True)

    with page_col3:
        # Check unanswered on current page
        unanswered_current = sum(1 for i in range(start_idx, end_idx) if f"final_q{i}" not in st.session_state or not st.session_state[f"final_q{i}"])
        if unanswered_current > 0:
            st.warning(f"⚠️ {unanswered_current} unanswered on this page")

    with page_col4:
        if st.button("Next ➡️", disabled=(current_page >= total_pages - 1), key="final_next"):
            st.session_state["final_test_page"] = current_page + 1
            st.rerun()

    st.markdown("---")

    # Submit button logic
    show_submit = (current_page == total_pages - 1) or (total_answered == len(quizzes))

    if show_submit:
        if total_answered < len(quizzes):
            st.warning(f"⚠️ {len(quizzes) - total_answered} questions not answered yet. Unanswered questions will be marked as incorrect.")

        submitted = st.button("✅ Submit Final Test", type="primary", use_container_width=True)
    else:
        st.info("💡 Navigate to the last page or answer all questions to submit the test.")
        submitted = False

    # Process submission
    if submitted:
        score = 0
        results = []

        for i, item in enumerate(quizzes):
            if f"final_q{i}" in st.session_state:
                choice = st.session_state[f"final_q{i}"]
                user_letter = choice[0] if choice else None
            else:
                user_letter = None

            correct_letter = item["answer"]
            is_correct = user_letter == correct_letter

            if is_correct:
                score += 1

            results.append({
                "question": item["question"],
                "user_answer": user_letter,
                "correct_answer": correct_letter,
                "is_correct": is_correct,
                "explanation": item["explanation"]
            })

        # Show results
        st.success(f"🎉 Final Test Completed!")
        st.markdown(f"### 🧾 Final Score: **{score} / {len(quizzes)}** ({score/len(quizzes)*100:.1f}%)")

        if score >= 40:
            st.success("🎉 Excellent! You passed the course!")
        else:
            st.warning("📘 Please review the lessons and try again.")

        # Detailed results
        with st.expander("📋 View Detailed Results"):
            for i, res in enumerate(results):
                if res['is_correct']:
                    st.success(f"**Q{i+1}**: ✅ Correct")
                else:
                    st.error(f"**Q{i+1}**: ❌ Wrong - Your answer: {res['user_answer']}, Correct: {res['correct_answer']}")
                    st.caption(f"💡 {res['explanation']}")

    # Back button
    if st.button("🔙 Back to Lessons"):
        st.session_state["final_test_mode"] = False
        if "final_test_questions" in st.session_state:
            del st.session_state["final_test_questions"]
        if "final_test_page" in st.session_state:
            del st.session_state["final_test_page"]
        st.rerun()

    st.stop()

# ---------- Current Lesson ----------
idx = st.session_state.current_index
lesson = lessons[idx]

# ========== OPTIMIZATION 1: Quick Navigation Bar + Progress Bar ==========
st.markdown("---")

# Progress bar at the top
progress_percent = (idx + 1) / len(lessons)
st.progress(progress_percent)
st.caption(f"📚 Overall Progress: {idx + 1}/{len(lessons)} lessons ({progress_percent*100:.1f}% complete)")

# Quick navigation row
nav_col1, nav_col2, nav_col3 = st.columns([1, 8, 1])

with nav_col1:
    if st.button("⬅️ Previous", disabled=(idx == 0), use_container_width=True):
        st.session_state.current_index = idx - 1
        st.session_state["final_test_mode"] = False
        st.rerun()

with nav_col2:
    # Dropdown selector for quick jump
    selected_idx = st.selectbox(
        "📖 Jump to Lesson:",
        options=range(len(lessons)),
        format_func=lambda x: f"{'✅ ' if lessons[x]['No'] in completed_list else ''}Lesson {lessons[x]['No']}: {lessons[x]['Title'][:40]}{'...' if len(lessons[x]['Title']) > 40 else ''}",
        index=idx,
        key="lesson_quick_selector"
    )
    if selected_idx != idx:
        st.session_state.current_index = selected_idx
        st.session_state["final_test_mode"] = False
        st.rerun()

with nav_col3:
    if st.button("Next ➡️", disabled=(idx >= len(lessons) - 1), use_container_width=True):
        st.session_state.current_index = idx + 1
        st.session_state["final_test_mode"] = False
        st.rerun()

st.markdown("---")

# Lesson title
st.title(f"Lesson {lesson['No']}: {lesson['Title']}")
completed = lesson["No"] in completed_list

# ========== OPTIMIZATION 2: Real-time Save Notification ==========
def show_save_notification(message, icon="✅"):
    """Show temporary notification message"""
    notification_placeholder = st.empty()
    notification_placeholder.success(f"{icon} {message}")
    return notification_placeholder

col1, col2 = st.columns(2)
if completed:
    if col1.button("✅ Completed (Click to Unmark)"):
        db.update_user_progress(USER_ID, lesson["No"], is_completed=False)
        st.session_state['show_notification'] = ("unmarked", lesson['Title'])
        st.rerun()
else:
    if col1.button("📘 Mark as Completed"):
        db.update_user_progress(USER_ID, lesson["No"], is_completed=True)
        st.session_state['show_notification'] = ("completed", lesson['Title'])
        st.rerun()

# Show notification if exists
if 'show_notification' in st.session_state:
    notif_type, lesson_title = st.session_state['show_notification']
    if notif_type == "completed":
        st.success(f"✅ Lesson '{lesson_title}' marked as completed and saved!")
    elif notif_type == "unmarked":
        st.info(f"ℹ️ Lesson '{lesson_title}' unmarked and saved!")
    del st.session_state['show_notification']

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

# ========== OPTIMIZATION 3: Quiz Pagination ==========
QUESTIONS_PER_PAGE = 10

# Initialize quiz page state
if f"quiz_page_{idx}" not in st.session_state:
    st.session_state[f"quiz_page_{idx}"] = 0

current_page = st.session_state[f"quiz_page_{idx}"]
total_pages = (len(quizzes) - 1) // QUESTIONS_PER_PAGE + 1

# Calculate start and end indices for current page
start_idx = current_page * QUESTIONS_PER_PAGE
end_idx = min(start_idx + QUESTIONS_PER_PAGE, len(quizzes))

# Show page info and navigation at top
if len(quizzes) > QUESTIONS_PER_PAGE:
    st.info(f"📄 Page {current_page + 1} of {total_pages} | Questions {start_idx + 1}-{end_idx} of {len(quizzes)}")

score = 0
user_answers = {}
start_time = time.time() if f"quiz_start_time_{idx}" not in st.session_state else st.session_state[f"quiz_start_time_{idx}"]
if f"quiz_start_time_{idx}" not in st.session_state:
    st.session_state[f"quiz_start_time_{idx}"] = start_time

# Show answered progress
total_answered = sum(1 for i in range(len(quizzes)) if f"quiz_{idx}_{i}" in st.session_state)
st.caption(f"✍️ Progress: {total_answered}/{len(quizzes)} questions answered")

# Display questions for current page only
for i in range(start_idx, end_idx):
    item = quizzes[i]
    st.markdown(f"**{i+1}. {item['question']}**")
    user_choice = st.radio(
        label="Please select an answer:",
        options=item["options"],
        key=f"quiz_{idx}_{i}"
    )
    user_letter = user_choice[0] if user_choice else None
    correct_letter = item["answer"]

    # Store user answer
    user_answers[i] = {
        "question": item["question"],
        "user_answer": user_letter,
        "correct_answer": correct_letter,
        "is_correct": user_letter == correct_letter
    }

# Pagination controls
if len(quizzes) > QUESTIONS_PER_PAGE:
    st.markdown("---")
    page_col1, page_col2, page_col3, page_col4 = st.columns([1, 2, 2, 1])

    with page_col1:
        if st.button("⬅️ Prev Page", disabled=(current_page == 0), key=f"quiz_prev_{idx}"):
            st.session_state[f"quiz_page_{idx}"] = current_page - 1
            st.rerun()

    with page_col2:
        st.markdown(f"<center>Page {current_page + 1} / {total_pages}</center>", unsafe_allow_html=True)

    with page_col3:
        # Check if there are unanswered questions on current page
        unanswered_current = sum(1 for i in range(start_idx, end_idx) if f"quiz_{idx}_{i}" not in st.session_state or not st.session_state[f"quiz_{idx}_{i}"])
        if unanswered_current > 0:
            st.warning(f"⚠️ {unanswered_current} unanswered on this page")

    with page_col4:
        if st.button("Next Page ➡️", disabled=(current_page >= total_pages - 1), key=f"quiz_next_{idx}"):
            st.session_state[f"quiz_page_{idx}"] = current_page + 1
            st.rerun()

    st.markdown("---")

# Submit button - only show on last page or if all questions answered
show_submit = (current_page == total_pages - 1) or (total_answered == len(quizzes))

if show_submit:
    # Warning if not all questions answered
    if total_answered < len(quizzes):
        st.warning(f"⚠️ {len(quizzes) - total_answered} questions not answered yet. You can still submit, but unanswered questions will be marked as incorrect.")

    submitted = st.button("✅ Submit Quiz", type="primary", use_container_width=True)
else:
    st.info("💡 Navigate to the last page to submit the quiz, or answer all questions to submit from any page.")
    submitted = False

# Process submission
if submitted:
    # Collect all answers
    for i in range(len(quizzes)):
        item = quizzes[i]
        user_choice_key = f"quiz_{idx}_{i}"

        if user_choice_key in st.session_state:
            user_choice = st.session_state[user_choice_key]
            user_letter = user_choice[0] if user_choice else None
        else:
            user_letter = None

        correct_letter = item["answer"]

        user_answers[i] = {
            "question": item["question"],
            "user_answer": user_letter,
            "correct_answer": correct_letter,
            "is_correct": user_letter == correct_letter
        }

        if user_letter == correct_letter:
            score += 1

    # Save to database
    time_taken = int(time.time() - start_time)
    db.save_quiz_attempt(USER_ID, lesson["No"], score, len(quizzes), time_taken, user_answers)

    # Show results
    st.success(f"🎉 Quiz Submitted!")
    st.info(f"📊 Your Score: **{score}/{len(quizzes)}** ({score/len(quizzes)*100:.1f}%)")

    # Show detailed results
    with st.expander("📋 View Detailed Results"):
        for i in range(len(quizzes)):
            item = quizzes[i]
            ans = user_answers[i]

            if ans['is_correct']:
                st.success(f"**Q{i+1}**: ✅ Correct")
            else:
                st.error(f"**Q{i+1}**: ❌ Wrong - Your answer: {ans['user_answer']}, Correct: {ans['correct_answer']}")
                st.caption(f"💡 {item['explanation']}")
else:
    # Show answers for current page if not submitted
    pass

# ---------- Next Lesson ----------
if st.button("▶ Next Lesson"):
    if idx + 1 < len(lessons):
        st.session_state.current_index += 1
        st.session_state["final_test_mode"] = False

        # Save progress to database
        next_lesson = lessons[st.session_state.current_index]
        db.update_user_progress(USER_ID, next_lesson["No"], current_index=st.session_state.current_index)

        st.rerun()
    else:
        st.success("🎉 Congratulations! All lessons completed!")
