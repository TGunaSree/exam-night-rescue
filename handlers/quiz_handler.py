"""
Quiz handler — interactive MCQ quiz with scoring and instant feedback.
"""
import re
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from utils import bharatcode, session

SYSTEM_PROMPT = """You are a quiz master for university-level exams.
Generate exactly 5 multiple choice questions on the given topic.

Format each question EXACTLY like this (no deviation):
Q1. [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
ANSWER: [A/B/C/D]
EXPLANATION: [One sentence explanation]

---

Q2. [Question text]
...

Make questions test real understanding, not just memorization.
Vary difficulty: 2 easy, 2 medium, 1 hard."""


def parse_questions(raw: str) -> list:
    """Parse raw quiz text into structured question dicts."""
    questions = []
    blocks = re.split(r"\n---\n", raw.strip())
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        q = {}
        # Question text
        qm = re.search(r"Q\d+\.\s*(.+?)(?:\n|$)", block)
        if not qm:
            continue
        q["question"] = qm.group(1).strip()
        # Options
        for opt in ["A", "B", "C", "D"]:
            om = re.search(rf"{opt}\)\s*(.+?)(?:\n|$)", block)
            q[opt] = om.group(1).strip() if om else ""
        # Answer
        am = re.search(r"ANSWER:\s*([ABCD])", block)
        q["answer"] = am.group(1).strip() if am else "A"
        # Explanation
        em = re.search(r"EXPLANATION:\s*(.+?)(?:\n|$)", block)
        q["explanation"] = em.group(1).strip() if em else ""
        questions.append(q)
    return questions


def format_question(q: dict, index: int, total: int) -> str:
    return (
        f"🎯 Question {index}/{total}\n\n"
        f"*{q['question']}*\n\n"
        f"A\\) {q['A']}\n"
        f"B\\) {q['B']}\n"
        f"C\\) {q['C']}\n"
        f"D\\) {q['D']}\n\n"
        f"Reply with A, B, C or D"
    )


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args
    subject = session.get_key(chat_id, "subject", "")

    if not args:
        topics = session.get_key(chat_id, "topics", [])
        topic = topics[0] if topics else None
    else:
        topic = " ".join(args)

    if not topic:
        await update.message.reply_text(
            "Usage: /quiz [topic name]\nExample: /quiz Binary Trees"
        )
        return

    await update.message.reply_text(
        f"🎮 Generating quiz on *{topic}*... Get ready!", parse_mode="Markdown"
    )

    user_prompt = f"Subject: {subject or 'General'}\nTopic: {topic}\nGenerate 5 MCQ questions."

    try:
        raw = await bharatcode.chat(SYSTEM_PROMPT, user_prompt, temperature=0.5)
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating quiz: {e}")
        return

    questions = parse_questions(raw)
    if not questions:
        await update.message.reply_text(
            "😕 Couldn't parse quiz questions. Please try again."
        )
        return

    # Store quiz state
    session.set_key(chat_id, "state", "quiz")
    session.set_key(chat_id, "quiz", {
        "topic": topic,
        "questions": questions,
        "index": 0,
        "score": 0,
    })

    keyboard = ReplyKeyboardMarkup(
        [["A", "B"], ["C", "D"], ["/endquiz"]],
        one_time_keyboard=False,
        resize_keyboard=True,
    )

    q = questions[0]
    await update.message.reply_text(
        format_question(q, 1, len(questions)),
        parse_mode="MarkdownV2",
        reply_markup=keyboard,
    )


async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    quiz = session.get_key(chat_id, "quiz", {})
    answer = update.message.text.strip().upper()

    questions = quiz.get("questions", [])
    index = quiz.get("index", 0)
    score = quiz.get("score", 0)

    if index >= len(questions):
        return

    current_q = questions[index]
    correct = current_q["answer"]
    is_correct = answer == correct

    if is_correct:
        score += 1
        feedback = f"✅ *Correct!*\n_{current_q['explanation']}_"
    else:
        feedback = (
            f"❌ *Wrong!* The answer is *{correct}*\n"
            f"_{current_q['explanation']}_"
        )

    quiz["score"] = score
    quiz["index"] = index + 1
    session.set_key(chat_id, "quiz", quiz)

    await update.message.reply_text(feedback, parse_mode="Markdown")

    # Next question or end
    if quiz["index"] < len(questions):
        next_q = questions[quiz["index"]]
        await update.message.reply_text(
            format_question(next_q, quiz["index"] + 1, len(questions)),
            parse_mode="MarkdownV2",
        )
    else:
        await end_quiz_session(update, context)


async def end_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await end_quiz_session(update, context)


async def end_quiz_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    quiz = session.get_key(chat_id, "quiz", {})
    score = quiz.get("score", 0)
    total = len(quiz.get("questions", []))
    topic = quiz.get("topic", "Unknown")

    session.set_key(chat_id, "state", "idle")

    percentage = (score / total * 100) if total > 0 else 0
    if percentage >= 80:
        emoji = "🏆"
        msg = "Excellent! You know this topic well!"
    elif percentage >= 60:
        emoji = "👍"
        msg = "Good job! Quick revision of weak points and you're ready!"
    elif percentage >= 40:
        emoji = "📖"
        msg = "Needs more revision. Re-read the key concepts!"
    else:
        emoji = "🚨"
        msg = "This topic needs serious attention tonight!"

    await update.message.reply_text(
        f"{emoji} *Quiz Complete — {topic}*\n\n"
        f"Score: *{score}/{total}* \\({int(percentage)}%\\)\n\n"
        f"{msg}\n\n"
        f"Try /quiz \\[another topic\\] or /summary \\[topic\\] for a cheat sheet\\.",
        parse_mode="MarkdownV2",
        reply_markup=ReplyKeyboardRemove(),
    )
