"""
Telegram message formatting helpers.
"""

def bold(text: str) -> str:
    return f"*{escape(text)}*"


def escape(text: str) -> str:
    """Escape MarkdownV2 special characters."""
    specials = r"\_*[]()~`>#+-=|{}.!"
    for ch in specials:
        text = text.replace(ch, f"\\{ch}")
    return text


def section(title: str, body: str) -> str:
    return f"*{title}*\n{body}\n"
