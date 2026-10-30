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

For each of the top 3-4 topics, give:

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
    subject = session.get_key(chat_id, "subject", "Your Subject")

    status_msg = await update.message.reply_text("🚨 PANIC MODE ACTIVATED!\nGenerating your emergency rescue in seconds...")

    topic_list = ", ".join(topics[:8]) if topics else "all core exam topics"
    user_prompt = (
        f"Subject: {subject}\n"
        f"Topics: {topic_list}\n"
        f"Student has 1-2 hours. Give ultra-compressed survival rescue."
    )

    try:
        rescue = await bharatcode.chat(SYSTEM_PROMPT, user_prompt, temperature=0.3)
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {e}")
        return

    await status_msg.edit_text(rescue)
