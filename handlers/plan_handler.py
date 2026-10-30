"""
Plan handler — generates a prioritized, time-boxed revision plan.
"""
from telegram import Update
from telegram.ext import ContextTypes
from utils import bharatcode, session

SYSTEM_PROMPT = """You are an expert academic coach specializing in last-minute exam preparation.
Create a realistic, time-boxed revision plan for a student studying tonight.
Format it exactly like this example — use emojis, be encouraging:

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

💤 [Encouraging closing line about sleep]

Rules:
- Start from current time (approximately 7 PM if not told)
- High priority = topics most likely in exam (fundamentals, frequently tested)
- Be realistic about time — don't overschedule
- Include short 5-10 min breaks every 90 minutes
- Keep it motivating and energetic"""


async def generate_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    topics = session.get_key(chat_id, "topics", [])
    subject = session.get_key(chat_id, "subject", "Unknown Subject")
    hours = session.get_key(chat_id, "hours", 6)

    if not topics:
        await update.message.reply_text(
            "📸 Please send a photo of your syllabus first, or type /settopics [topic1, topic2, ...]"
        )
        return

    await update.message.reply_text("⚡ Building your rescue plan... hang on!")

    topic_list = "\n".join(f"{i+1}. {t}" for i, t in enumerate(topics))
    user_prompt = (
        f"Subject: {subject}\n"
        f"Available study time: {hours} hours\n"
        f"Topics to cover:\n{topic_list}\n\n"
        f"Create a detailed, time-boxed revision plan starting from now."
    )

    try:
        plan = await bharatcode.chat(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating plan: {e}")
        return

    session.set_key(chat_id, "state", "idle")

    await update.message.reply_text(
        f"{plan}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"*Commands you can use now:*\n"
        f"/questions \\[topic\\] — Get exam questions\n"
        f"/quiz \\[topic\\] — Start a quiz\n"
        f"/summary \\[topic\\] — Cheat sheet\n"
        f"/panic — Ultra\\-compressed mode 🚨\n"
        f"/done \\[topic\\] — Mark topic as done ✅",
        parse_mode="MarkdownV2",
    )
