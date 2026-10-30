"""
Exam Night Rescue — Telegram Bot
BharatCode Hackathon 2026

Main entry point — registers all handlers and starts polling.
"""
import os
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from handlers.photo_handler import handle_photo_or_doc
from handlers.plan_handler import generate_plan
from handlers.questions_handler import handle_questions
from handlers.quiz_handler import start_quiz, handle_quiz_answer, end_quiz
from handlers.summary_handler import handle_summary
from handlers.panic_handler import handle_panic
from utils import bharatcode, session

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

WELCOME = """🆘 Exam Night Rescue — Your Last-Minute Study Companion!

Exam tomorrow? Don't panic. I've got you. 💪

📌 How to start:
1. 📸 Send a photo or document (WebP, PNG, JPG) of your syllabus
2. ✍️ OR simply paste your syllabus topics directly in this chat!
3. 📝 OR type: /settopics Topic 1, Topic 2, Topic 3

⚡ Available Commands:
• /plan — Generate time-boxed revision plan
• /questions [topic] — Get likely exam questions (2/5/10 marks)
• /quiz [topic] — Rapid-fire MCQ quiz with scoring
• /summary [topic] — 3-minute cheat sheet card
• /panic — 1-hour emergency compressed revision 🚨
• /done [topic] — Mark topic completed ✅
• /progress — Visual progress bar 📊
• /pyq [topic] — Previous year question pattern 📜
• /reset — Start fresh with a new subject
• /help — Show this help message
"""

TEXT_EXTRACT_PROMPT = """You are an academic coach. Extract all distinct study topics/units/chapters from this student message or syllabus.
Return ONLY a clean numbered list of topics.
Example:
1. Arrays and Strings
2. Linked Lists
3. Trees and Graphs
Keep each topic name concise (3-7 words). Extract every distinct topic."""

PYQ_SYSTEM = """You are an expert at predicting university exam questions based on previous year patterns.
Generate 5 realistic Previous Year Question (PYQ) style exam questions for the given topic.
Label each with marks (e.g. 5 Marks, 10 Marks)."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session.reset(update.effective_chat.id)
    await update.message.reply_text(WELCOME)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session.reset(update.effective_chat.id)
    await update.message.reply_text(
        "🔄 Reset complete! Send a new syllabus photo, paste your notes/topics here, or type /settopics to begin."
    )


async def settopics_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    raw = " ".join(context.args).strip()
    if not raw:
        await update.message.reply_text(
            "Usage: /settopics Topic 1, Topic 2, Topic 3\n"
            "Example: /settopics Arrays, Linked Lists, Trees, Graphs"
        )
        return

    # Split by comma or newline
    topics = [t.strip() for t in raw.replace("\n", ",").split(",") if t.strip()]
    if not topics:
        await update.message.reply_text("Could not find topics. Separate them with commas.")
        return

    session.set_key(chat_id, "topics", topics)
    session.set_key(chat_id, "state", "awaiting_subject")

    topic_lines = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(topics))
    await update.message.reply_text(
        f"✅ Loaded {len(topics)} topics:\n\n{topic_lines}\n\n"
        f"📚 What subject is this? (e.g. Data Structures, Astrobiology)"
    )


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /done [topic name]\nExample: /done Linked Lists")
        return
    topic = " ".join(args).strip()
    done = session.get_key(chat_id, "done_topics", set())
    done.add(topic.lower())
    session.set_key(chat_id, "done_topics", done)
    topics = session.get_key(chat_id, "topics", [])
    remaining = [t for t in topics if t.lower() not in done]

    total_count = len(topics) if topics else len(done)
    await update.message.reply_text(
        f"✅ '{topic}' marked as done!\n\n"
        f"📊 Completed: {len(done)}/{total_count} topics\n"
        f"📋 Remaining: {len(remaining)} topics\n\n"
        f"Use /progress to view your progress bar!"
    )


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    topics = session.get_key(chat_id, "topics", [])
    done = session.get_key(chat_id, "done_topics", set())

    if not topics and not done:
        await update.message.reply_text(
            "No topics loaded yet. Send a photo of your syllabus or paste your topics here! 📸"
        )
        return

    total = len(topics) if topics else len(done)
    done_count = len(done)
    pct = int((done_count / total) * 100) if total > 0 else 0

    filled = int(pct / 10)
    bar = "█" * filled + "░" * (10 - filled)

    done_list = [t for t in topics if t.lower() in done] if topics else list(done)
    pending_list = [t for t in topics if t.lower() not in done] if topics else []

    msg = f"📊 Tonight's Revision Progress\n\n[{bar}] {pct}%\n\n"
    if done_list:
        msg += "✅ Completed:\n" + "\n".join(f"  • {t}" for t in done_list) + "\n\n"
    if pending_list:
        msg += "⏳ Still to study:\n" + "\n".join(f"  • {t}" for t in pending_list)

    if pct == 100:
        msg += "\n\n🎉 Outstanding! All topics covered. Get some rest and ace that exam! 🎓"
    elif pct >= 50:
        msg += "\n\n💪 More than halfway there! Keep the momentum going!"
    else:
        msg += "\n\n⚡ Focus up, one topic at a time. You've got this!"

    await update.message.reply_text(msg)


async def pyq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args
    subject = session.get_key(chat_id, "subject", "")

    if not args:
        topics = session.get_key(chat_id, "topics", [])
        topic = topics[0] if topics else "General"
    else:
        topic = " ".join(args)

    status_msg = await update.message.reply_text(f"📜 Generating PYQ-style questions for {topic}...")

    try:
        result = await bharatcode.chat(
            PYQ_SYSTEM,
            f"Subject: {subject or 'General'}\nTopic: {topic}\nGenerate 5 PYQ exam questions with marks."
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {e}")
        return

    await status_msg.edit_text(f"📜 PYQ Questions — {topic}\n\n{result}")


# ── Text router ───────────────────────────────────────────────────────────────

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    state = session.get_key(chat_id, "state", "idle")
    text = update.message.text.strip()

    # Quiz answer routing
    if state == "quiz" and text.upper() in ["A", "B", "C", "D"]:
        await handle_quiz_answer(update, context)
        return

    # Awaiting subject name
    if state == "awaiting_subject":
        session.set_key(chat_id, "subject", text)
        session.set_key(chat_id, "state", "awaiting_hours")
        await update.message.reply_text(
            f"📚 Subject set to: {text}!\n\n"
            f"⏰ How many hours do you have to study tonight?\n"
            f"(Reply with a number, e.g. 5 or 3.5)"
        )
        return

    # Awaiting hours
    if state == "awaiting_hours":
        try:
            cleaned_num = text.lower().replace("hours", "").replace("hrs", "").replace("h", "").strip()
            hours = float(cleaned_num)
            session.set_key(chat_id, "hours", hours)
        except ValueError:
            await update.message.reply_text("Please enter a valid number of hours, e.g. 4 or 6.5")
            return
        # Generate the rescue plan
        await generate_plan(update, context)
        return

    # User pasted syllabus or notes in idle state!
    if "\n" in text or len(text) > 40 or any(kw in text.lower() for kw in ["week", "unit", "chapter", "module", "topics", "-"]):
        status_msg = await update.message.reply_text("📋 Reading your syllabus text... please wait ⏳")
        try:
            extracted = await bharatcode.chat(TEXT_EXTRACT_PROMPT, text)
            topics = []
            for line in extracted.strip().splitlines():
                cleaned = line.strip().lstrip("0123456789.-)•* ").strip()
                if cleaned:
                    topics.append(cleaned)

            if topics:
                session.set_key(chat_id, "topics", topics)
                session.set_key(chat_id, "state", "awaiting_subject")
                topic_lines = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(topics))
                await status_msg.edit_text(
                    f"✅ Found {len(topics)} topics from your text:\n\n{topic_lines}\n\n"
                    f"📚 What subject is this? (e.g. Astrobiology, Data Structures)"
                )
                return
        except Exception as e:
            logger.error(f"Error parsing text syllabus: {e}")

    # Default guidance
    await update.message.reply_text(
        "💡 To get started:\n"
        "• Send a photo/document of your syllabus 📸\n"
        "• Or paste your topics list directly in this chat\n"
        "• Or type /settopics Topic 1, Topic 2, Topic 3\n\n"
        "Type /help to see all commands."
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

    app = Application.builder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("plan", generate_plan))
    app.add_handler(CommandHandler("questions", handle_questions))
    app.add_handler(CommandHandler("quiz", start_quiz))
    app.add_handler(CommandHandler("endquiz", end_quiz))
    app.add_handler(CommandHandler("summary", handle_summary))
    app.add_handler(CommandHandler("panic", handle_panic))
    app.add_handler(CommandHandler("done", done_command))
    app.add_handler(CommandHandler("progress", progress_command))
    app.add_handler(CommandHandler("pyq", pyq_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("settopics", settopics_command))

    # Photos and Documents (e.g. WebP, PNG, JPG, PDF)
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_photo_or_doc))

    # Text router
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("🆘 Exam Night Rescue Bot is running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
