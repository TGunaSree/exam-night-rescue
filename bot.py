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

from handlers.photo_handler import handle_photo
from handlers.plan_handler import generate_plan
from handlers.questions_handler import handle_questions
from handlers.quiz_handler import start_quiz, handle_quiz_answer, end_quiz
from handlers.summary_handler import handle_summary
from handlers.panic_handler import handle_panic
from utils import session

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Welcome / Start ──────────────────────────────────────────────────────────

WELCOME = """
🆘 *Exam Night Rescue* — Your Last-Minute Study Companion!

*Exam tomorrow? Don't panic. I've got you.* 💪

*How to start:*
📸 Send me a *photo* of your syllabus or notes
→ I'll extract topics, build a plan, and quiz you!

*Or use commands directly:*
/plan — Generate revision plan
/questions \\[topic\\] — Get likely exam questions  
/quiz \\[topic\\] — Start a quick MCQ quiz
/summary \\[topic\\] — Get a cheat sheet
/panic — Ultra\\-compressed last\\-minute mode 🚨
/done \\[topic\\] — Mark topic as completed ✅
/progress — See your progress tonight
/pyq \\[topic\\] — Previous year question style
/reset — Start fresh
/help — Show all commands

*Just send your syllabus photo to begin!* 📸
"""

PYQ_SYSTEM = """You are an expert at predicting university exam questions based on previous year patterns.
Generate 5 Previous Year Question (PYQ) style questions for the given topic.
Format them as realistic long-answer university exam questions with marks indicated.
Label each: [YEAR PATTERN - X Marks]"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session.reset(update.effective_chat.id)
    await update.message.reply_text(WELCOME, parse_mode="MarkdownV2")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME, parse_mode="MarkdownV2")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session.reset(update.effective_chat.id)
    await update.message.reply_text(
        "🔄 Reset! Send me a new syllabus photo or use /plan to start over."
    )


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /done [topic name]\nExample: /done Arrays")
        return
    topic = " ".join(args)
    done = session.get_key(chat_id, "done_topics", set())
    done.add(topic.lower())
    session.set_key(chat_id, "done_topics", done)
    topics = session.get_key(chat_id, "topics", [])
    remaining = [t for t in topics if t.lower() not in done]
    await update.message.reply_text(
        f"✅ *{topic}* marked as done!\n\n"
        f"📊 Progress: {len(done)}/{len(topics)} topics completed\n"
        f"📋 Remaining: {len(remaining)} topics left\n\n"
        f"Keep going! 💪",
        parse_mode="Markdown",
    )


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    topics = session.get_key(chat_id, "topics", [])
    done = session.get_key(chat_id, "done_topics", set())

    if not topics:
        await update.message.reply_text(
            "No topics loaded yet. Send a photo of your syllabus first! 📸"
        )
        return

    done_list = [t for t in topics if t.lower() in done]
    pending_list = [t for t in topics if t.lower() not in done]

    pct = int(len(done_list) / len(topics) * 100) if topics else 0

    # Progress bar
    filled = int(pct / 10)
    bar = "█" * filled + "░" * (10 - filled)

    msg = (
        f"📊 *Tonight's Progress*\n\n"
        f"`[{bar}]` {pct}%\n\n"
    )
    if done_list:
        msg += "✅ *Completed:*\n" + "\n".join(f"  • {t}" for t in done_list) + "\n\n"
    if pending_list:
        msg += "⏳ *Remaining:*\n" + "\n".join(f"  • {t}" for t in pending_list)

    if pct == 100:
        msg += "\n\n🎉 All topics covered! Go get some sleep. You're ready! 🎓"
    elif pct >= 50:
        msg += "\n\n💪 Halfway there! Keep pushing!"
    else:
        msg += "\n\n⚡ Stay focused — you can do this!"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def pyq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args
    subject = session.get_key(chat_id, "subject", "")

    if not args:
        await update.message.reply_text("Usage: /pyq [topic]\nExample: /pyq Sorting Algorithms")
        return

    topic = " ".join(args)
    await update.message.reply_text(f"📜 Generating PYQ-style questions for *{topic}*...", parse_mode="Markdown")

    from utils import bharatcode
    try:
        result = await bharatcode.chat(
            PYQ_SYSTEM,
            f"Subject: {subject or 'General'}\nTopic: {topic}\nGenerate PYQ-style questions."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
        return

    await update.message.reply_text(f"📜 *PYQ Questions — {topic}*\n\n{result}", parse_mode="Markdown")


# ── Text message router ───────────────────────────────────────────────────────

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
            f"📚 Got it — *{text}*!\n\n⏰ How many hours do you have to study tonight?\n"
            f"\\(Reply with a number, e\\.g\\. *6* or *3\\.5*\\)",
            parse_mode="MarkdownV2",
        )
        return

    # Awaiting hours
    if state == "awaiting_hours":
        try:
            hours = float(text.replace(" hours", "").replace("h", "").strip())
            session.set_key(chat_id, "hours", hours)
        except ValueError:
            await update.message.reply_text("Please enter a number like 6 or 3.5")
            return
        # Auto-generate plan
        await generate_plan(update, context)
        return

    # Default: guide user
    await update.message.reply_text(
        "📸 Send me a photo of your syllabus to get started!\n"
        "Or type /help to see all commands."
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

    app = Application.builder().token(token).build()

    # Command handlers
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

    # Photo handler
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Text (quiz answers + state machine)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("🆘 Exam Night Rescue Bot is running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
