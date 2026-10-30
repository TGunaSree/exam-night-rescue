"""
Panic handler — ultra-compressed last-minute rescue mode.
"""
from telegram import Update
from telegram.ext import ContextTypes
from utils import bharatcode, session

SYSTEM_PROMPT = """A student has VERY LITTLE TIME before their exam (1-2 hours). 
Give them ONLY the most critical information — no fluff, pure signal.

Format:
🚨 PANIC MODE — [Subject]

For each of the top 3 topics, give:

🔥 [TOPIC NAME]
  • [Key point 1 — one line]
  • [Key point 2 — one line]  
  • [Key point 3 — one line]
  ❓ Must-know Q: [Single most important expected question]
  🧠 Remember: [One memory trick]

━━━
💊 EXAM SURVIVAL TIPS:
  • [Tip 1]
  • [Tip 2]
  • [Tip 3]

You've got this! 💪

Keep everything ULTRA SHORT. Student has no time to read long answers."""


async def handle_panic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    topics = session.get_key(chat_id, "topics", [])
    subject = session.get_key(chat_id, "subject", "your subject")

    await update.message.reply_text(
        "🚨 *PANIC MODE ACTIVATED!*\n\nGenerating your emergency rescue in 10 seconds...",
        parse_mode="Markdown",
    )

    topic_list = ", ".join(topics[:8]) if topics else "all topics"
    user_prompt = (
        f"Subject: {subject}\n"
        f"Topics: {topic_list}\n"
        f"Student has 1-2 hours. Give ultra-compressed rescue."
    )

    try:
        rescue = await bharatcode.chat(SYSTEM_PROMPT, user_prompt, temperature=0.3)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
        return

    await update.message.reply_text(rescue)
