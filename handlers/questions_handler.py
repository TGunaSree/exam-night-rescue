"""
Questions handler — generates likely exam questions for a topic.
"""
from telegram import Update
from telegram.ext import ContextTypes
from utils import bharatcode, session

SYSTEM_PROMPT = """You are an experienced university professor who knows exactly what questions
appear in exams. Generate realistic exam questions for the given topic.

Format exactly like this:

❓ KEY QUESTIONS — [Topic Name]

📝 SHORT ANSWER (2-3 marks):
  1. [Question]
  2. [Question]
  3. [Question]

📋 MEDIUM ANSWER (5 marks):
  1. [Question]
  2. [Question]

📜 LONG ANSWER (10 marks):
  1. [Question]
  2. [Question]

🎯 MOST LIKELY TO APPEAR IN EXAM:
  → [Single most important question]

Keep questions realistic and based on standard university curriculum."""


async def handle_questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = context.args
    subject = session.get_key(chat_id, "subject", "")

    if not args:
        topics = session.get_key(chat_id, "topics", [])
        if not topics:
            await update.message.reply_text(
                "Usage: /questions [topic name]\nExample: /questions Linked Lists"
            )
            return
        topic = topics[0]
    else:
        topic = " ".join(args)

    await update.message.reply_text(f"🔍 Generating key questions for *{topic}*...", parse_mode="Markdown")

    user_prompt = f"Subject: {subject or 'General'}\nTopic: {topic}\nGenerate exam questions."

    try:
        questions = await bharatcode.chat(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
        return

    await update.message.reply_text(questions)
