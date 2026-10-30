"""
Photo handler — extracts syllabus topics from an image using BharatCode vision.
"""
from telegram import Update
from telegram.ext import ContextTypes

from utils import bharatcode, session

SYSTEM_PROMPT = """You are an expert at reading academic syllabus documents, handwritten notes, 
and study materials. Extract all topics/chapters/units mentioned in the image.
Return ONLY a clean numbered list of topics, nothing else.
Example:
1. Arrays and Strings
2. Linked Lists
3. Trees and Graphs
Keep topic names short (3-6 words max). Extract every distinct topic you can see."""


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    msg = update.message

    await msg.reply_text(
        "📸 Got your image! Analyzing syllabus... please wait ⏳"
    )

    # Download the highest resolution photo
    photo = msg.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()

    try:
        result = await bharatcode.vision_chat(
            system=SYSTEM_PROMPT,
            user_text="Extract all topics/chapters from this syllabus or notes image.",
            image_bytes=bytes(image_bytes),
        )
    except Exception as e:
        await msg.reply_text(f"❌ Could not read the image. Please try again.\nError: {e}")
        return

    # Parse topics from numbered list
    topics = []
    for line in result.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Remove leading numbers/dots/dashes
        cleaned = line.lstrip("0123456789.-) ").strip()
        if cleaned:
            topics.append(cleaned)

    if not topics:
        await msg.reply_text(
            "😕 I couldn't find any topics in that image.\n"
            "Please send a clearer photo of your syllabus or notes."
        )
        return

    # Save to session
    session.set_key(chat_id, "topics", topics)
    session.set_key(chat_id, "state", "awaiting_subject")

    topic_list = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(topics))
    await msg.reply_text(
        f"✅ Found *{len(topics)} topics*:\n\n{topic_list}\n\n"
        f"📚 What subject is this? \\(e\\.g\\. Data Structures, Organic Chemistry\\)",
        parse_mode="MarkdownV2",
    )
