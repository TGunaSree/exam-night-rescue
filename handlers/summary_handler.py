"""
Summary handler — generates compact cheat sheet for a topic.
"""
from telegram import Update
from telegram.ext import ContextTypes
from utils import bharatcode, session

SYSTEM_PROMPT = """You are a master teacher who can explain any topic in a compact, 
exam-ready cheat sheet format. A student has 5 minutes to read this before their exam.

Format exactly like this:

📌 QUICK SUMMARY — [Topic Name]

📖 WHAT IT IS:
[1-2 sentence definition]

⚙️ HOW IT WORKS:
[3-5 bullet points of key mechanism/steps]

📊 KEY FACTS / FORMULAS:
[Important numbers, formulas, or facts]

⚠️ COMMON MISTAKES TO AVOID:
  • [Mistake 1]
  • [Mistake 2]

🧠 MEMORY TRICK:
[A mnemonic, analogy or trick to remember this topic]

🎯 EXAM FOCUS:
[What examiners typically ask about this topic]

Keep it SHORT, DENSE, and EXAM-FOCUSED. No fluff."""


async def handle_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args
    subject = session.get_key(chat_id, "subject", "")

    if not args:
        topics = session.get_key(chat_id, "topics", [])
        if not topics:
            await update.message.reply_text(
                "Usage: /summary [topic name]\nExample: /summary Dijkstra's Algorithm"
            )
            return
        topic = topics[0]
    else:
        topic = " ".join(args)

    await update.message.reply_text(f"📌 Generating cheat sheet for *{topic}*...", parse_mode="Markdown")

    user_prompt = f"Subject: {subject or 'General'}\nTopic: {topic}\nCreate a compact exam cheat sheet."

    try:
        summary = await bharatcode.chat(SYSTEM_PROMPT, user_prompt, temperature=0.4)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
        return

    await update.message.reply_text(
        f"{summary}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Try /quiz {topic} to test yourself! 🎯"
    )
