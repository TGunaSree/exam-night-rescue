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

SYSTEM_PROMPT = """You are an expert at reading academic syllabus documents, handwritten notes, 
and study materials. Extract all topics/chapters/units mentioned in the image.
Return ONLY a clean numbered list of topics, nothing else.
Example:
1. Arrays and Strings
2. Linked Lists
3. Trees and Graphs
Keep topic names short (3-7 words max). Extract every distinct topic you can see."""


async def handle_photo_or_doc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg:
        return
    chat_id = update.effective_chat.id

    status_msg = await msg.reply_text("📸 Got your syllabus file! Analyzing topics... please wait ⏳")

    image_bytes = None

    try:
        if msg.photo:
            photo = msg.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            raw_bytes = await file.download_as_bytearray()
            # Convert to standard JPEG via Pillow
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            image_bytes = buf.getvalue()

        elif msg.document:
            doc = msg.document
            file = await context.bot.get_file(doc.file_id)
            raw_bytes = await file.download_as_bytearray()
            # Check if it's an image or convert via Pillow
            try:
                img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                image_bytes = buf.getvalue()
            except Exception as e:
                logger.error(f"Cannot parse document as image: {e}")
                await status_msg.edit_text(
                    "❌ That document couldn't be opened as an image. Please send a photo, WebP, PNG, or JPG."
                )
                return
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        await status_msg.edit_text(f"❌ Failed to download file: {e}")
        return

    if not image_bytes:
        await status_msg.edit_text("❌ No image data received.")
        return

    try:
        result = await bharatcode.vision_chat(
            system=SYSTEM_PROMPT,
            user_text="Extract all topics, chapters, or syllabus points from this image.",
            image_bytes=image_bytes,
        )
    except Exception as e:
        logger.error(f"Vision API error: {e}")
        await status_msg.edit_text(f"❌ Could not analyze the image. Please try again.\nError: {e}")
        return

    # Parse topics from output
    topics = []
    for line in result.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        cleaned = line.lstrip("0123456789.-)•* ").strip()
        if cleaned:
            topics.append(cleaned)

    if not topics:
        await status_msg.edit_text(
            "😕 I couldn't identify distinct topics in that image.\n"
            "Try sending a clearer photo or just paste your topics as text in the chat!"
        )
        return

    session.set_key(chat_id, "topics", topics)
    session.set_key(chat_id, "state", "awaiting_subject")

    topic_lines = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(topics))
    reply_text = (
        f"✅ Found {len(topics)} topics:\n\n"
        f"{topic_lines}\n\n"
        f"📚 What subject is this? (e.g. Astrobiology, Data Structures, Physics)"
    )

    try:
        await status_msg.edit_text(reply_text)
    except Exception:
        await msg.reply_text(reply_text)
