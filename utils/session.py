"""
In-memory session manager — one session per Telegram chat_id.
"""
from typing import Any, Dict, Optional

_sessions: Dict[int, Dict[str, Any]] = {}


def get(chat_id: int) -> Dict[str, Any]:
    if chat_id not in _sessions:
        _sessions[chat_id] = _default()
    return _sessions[chat_id]


def set_key(chat_id: int, key: str, value: Any) -> None:
    get(chat_id)[key] = value


def get_key(chat_id: int, key: str, default: Any = None) -> Any:
    return get(chat_id).get(key, default)


def reset(chat_id: int) -> None:
    _sessions[chat_id] = _default()


def _default() -> Dict[str, Any]:
    return {
        "subject": None,
        "topics": [],
        "hours": None,
        "done_topics": set(),
        "state": "idle",          # idle | awaiting_subject | awaiting_hours | quiz
        "quiz": {
            "topic": None,
            "questions": [],
            "index": 0,
            "score": 0,
        },
        "lang": "english",
    }
