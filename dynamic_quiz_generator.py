import json
import random
from config import config
from ai_api import call_deepseek

SYSTEM_PROMPT_TEMPLATE = """
You are a professional exam question generator.
Based on the following lesson content, generate {n} realistic, scenario-based multiple-choice questions (single answer).

Each question should:
- Simulate real-world scenarios
- Have 4 answer choices (A/B/C/D)
- Mark the correct answer (A, B, C, or D)
- Provide a short explanation of the correct answer

Respond in the following JSON format:
{{
  "quizzes": [
    {{
      "question": "...",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "B",
      "explanation": "..."
    }}
  ]
}}
"""

MOCK_QUIZZES = [
    {
        "question": "Can a notary who has been removed from office serve again?",
        "options": ["A. Yes", "B. Must retake the exam", "C. Permanently banned", "D. Automatically reinstated after 1 year"],
        "answer": "C",
        "explanation": "The law prohibits reapplication after removal."
    },
    {
        "question": "Is it legal for a notary to notarize a document without seeing the signer in person?",
        "options": ["A. Legal", "B. Legal if noted", "C. Illegal", "D. Assistant may sign instead"],
        "answer": "C",
        "explanation": "Verifying identity in person is a fundamental requirement."
    }
]

# ✅ Determine question count based on content length
def count_question_num(content: str) -> int:
    length = len(content)
    if length < 300:
        return random.randint(1, 2)
    elif length < 700:
        return random.randint(3, 4)
    elif length < 1200:
        return random.randint(5, 7)
    else:
        return random.randint(8, 10)

# ✅ Dynamic generation with batch control
def generate_dynamic_quiz(lesson_title, lesson_content, num_questions=None):
    if num_questions is None:
        num_questions = count_question_num(lesson_content)

    batch_size = 10
    total_quizzes = []

    for batch_start in range(0, num_questions, batch_size):
        current_batch_size = min(batch_size, num_questions - batch_start)

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(n=current_batch_size)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Lesson Title: {lesson_title}\n\nLesson Content:\n{lesson_content}"}
        ]

        try:
            # Use the new AI API with optimized parameters for quiz generation
            content = call_deepseek(messages, temperature=0.8, max_tokens=800)

            # Clean up the response content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()

            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                print("❌ JSON decode error:", e)
                print("🔍 Raw content:", content)
                return MOCK_QUIZZES

            if isinstance(data, dict) and "quizzes" in data:
                total_quizzes.extend(data["quizzes"])
            elif isinstance(data, list):
                total_quizzes.extend(data)
            else:
                print("⚠️ Unexpected format:", data)
                return MOCK_QUIZZES

        except Exception as e:
            print("❌ Exception occurred:", e)
            return MOCK_QUIZZES

    return total_quizzes


# ✅ Test
if __name__ == "__main__":
    title = "Final Exam"
    content = "This is a very long lesson content. " * 200
    quiz = generate_dynamic_quiz(title, content, num_questions=50)
    for q in quiz:
        print(json.dumps(q, indent=2, ensure_ascii=False))
