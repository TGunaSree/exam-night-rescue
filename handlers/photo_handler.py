"""
Photo & Document handler — extracts syllabus topics from images (photo, webp, png, etc.)
or document uploads using AI vision.
"""
import io
import logging
from PIL import Image
from telegram import Update
from telegram.ext import ContextTypes

from utils import bharatcode, session

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert at reading academic syllabus documents, course outlines, handwritten notes, 
and study materials. Extract all topics, chapters, units, or modules mentioned in the image.
Return ONLY a numbered list of topics.
Example:
1. Arrays and Strings
2. Linked Lists
3. Trees and Graphs
Keep topic names clear and concise (3-7 words max). Extract every distinct topic you see."""


async def handle_photo_or_doc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg:
        return
    chat_id = update.effective_chat.id

    status_msg = await msg.reply_text("📸 Syllabus image received! Reading topics with AI vision... ⏳")

    image_bytes = None

    try:
        if msg.photo:
            photo = msg.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            raw_bytes = await file.download_as_bytearray()
            # Convert and optimize with Pillow
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            img.thumbnail((1280, 1280))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=80, optimize=True)
            image_bytes = buf.getvalue()

        elif msg.document:
            doc = msg.document
            file = await context.bot.get_file(doc.file_id)
            raw_bytes = await file.download_as_bytearray()
            try:
                img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                img.thumbnail((1280, 1280))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=80, optimize=True)
                image_bytes = buf.getvalue()
            except Exception as e:
                logger.error(f"Cannot parse document as image: {e}")
                await status_msg.edit_text(
                    "❌ That document couldn't be opened as an image. Please send a photo or WebP, PNG, or JPG file."
                )
                return
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        await status_msg.edit_text(f"❌ Failed to download file from Telegram: {e}")
        return

    if not image_bytes:
        await status_msg.edit_text("❌ No image data received.")
        return

    try:
        result = await bharatcode.vision_chat(
            system=SYSTEM_PROMPT,
            user_text="Extract all topics, units, or chapters from this syllabus image.",
            image_bytes=image_bytes,
        )
    except Exception as e:
        logger.error(f"Vision API error: {e}")
        await status_msg.edit_text(f"❌ Could not analyze the image ({e}). Please try again or paste the topics as text!")
        return

    # Parse topics from output
    topics = []
    for line in result.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        cleaned = line.lstrip("0123456789.-)•* ").strip()
        if cleaned and len(cleaned) > 2:
            topics.append(cleaned)

    if not topics:
        await status_msg.edit_text(
            "😕 Couldn't recognize clear syllabus topics in that photo.\n"
            "Try sending a clearer close-up photo, or simply paste your topics as text in this chat!"
        )
        return

    session.set_key(chat_id, "topics", topics)
    session.set_key(chat_id, "state", "awaiting_subject")

    topic_lines = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(topics))
    reply_text = (
        f"✅ Found {len(topics)} topics:\n\n"
        f"{topic_lines}\n\n"
        f"📚 What subject is this? (e.g. Astrobiology, Data Structures, Economics)"
    )

    try:
        await status_msg.edit_text(reply_text)
    except Exception:
        await msg.reply_text(reply_text)
