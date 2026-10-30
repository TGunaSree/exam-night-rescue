"""
Plan handler — generates a prioritized, time-boxed revision plan.
"""
from telegram import Update
from telegram.ext import ContextTypes
from utils import bharatcode, session

SYSTEM_PROMPT = """You are an expert academic coach specializing in last-minute exam preparation.
Create a realistic, time-boxed revision plan for a student studying tonight.
Format with clean bullet points and emojis. Be encouraging and direct.

Structure:
📅 YOUR RESCUE PLAN — [Subject] ([X] hours)

🔴 HIGH PRIORITY (Do these first!)
  ⏱ [Time] → [Topic] ([duration])
  ⏱ [Time] → [Topic] ([duration])

🟡 MEDIUM PRIORITY
  ⏱ [Time] → [Topic] ([duration])

🟢 IF TIME PERMITS
  ⏱ [Time] → [Topic] ([duration])

💡 QUICK TIPS:
  • [Tip 1]
  • [Tip 2]
  • [Tip 3]

💤 [Encouraging closing line about sleep and passing]

Rules:
- High priority = topics most likely tested / core fundamentals
- Realistic time distribution
- Keep it motivating and practical"""


async def generate_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    msg = update.message
    if not msg:
        return

    topics = session.get_key(chat_id, "topics", [])
    subject = session.get_key(chat_id, "subject", "General Subject")
    hours = session.get_key(chat_id, "hours", 5)

    if not topics:
        await msg.reply_text(
            "📸 Please send a photo or document of your syllabus first, or paste your syllabus text here in chat!"
        )
        return

    status_msg = await msg.reply_text("⚡ Building your 1-night rescue plan... please wait!")

    topic_list = "\n".join(f"{i+1}. {t}" for i, t in enumerate(topics))
    user_prompt = (
        f"Subject: {subject}\n"
        f"Available study time: {hours} hours\n"
        f"Topics to cover:\n{topic_list}\n\n"
        f"Create a practical revision schedule for tonight."
    )

    try:
        plan = await bharatcode.chat(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        await status_msg.edit_text(f"❌ Error generating plan: {e}")
        return

    session.set_key(chat_id, "state", "idle")

    full_response = (
        f"{plan}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Commands you can use right now:\n"
        f"• /questions [topic] — Get likely exam questions\n"
        f"• /quiz [topic] — Start a quick MCQ quiz\n"
        f"• /summary [topic] — Cheat sheet summary\n"
        f"• /panic — Ultra-compressed emergency mode 🚨\n"
        f"• /done [topic] — Mark topic as finished ✅\n"
        f"• /progress — Check completion bar 📊"
    )

    try:
        await status_msg.edit_text(full_response)
    except Exception:
        await msg.reply_text(full_response)
