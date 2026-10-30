# 🆘 Exam Night Rescue

> **Exam tomorrow? Don't panic. We've got you.**

A Telegram bot that rescues college students the night before their exam. Send a photo of your syllabus → get a personalized revision plan, key questions, MCQ quizzes, and cheat sheets — all in under 60 seconds.

**Built for BharatCode Hackathon | Powered by BharatCode API (qwen-3.8-27b)**

---

## ✨ Features

| Feature | Command |
|---|---|
| 📸 Photo → Syllabus extraction (vision AI) | Send a photo |
| 📅 Prioritized time-boxed revision plan | `/plan` |
| ❓ Likely exam questions (2/5/10 marks) | `/questions [topic]` |
| 🎯 Interactive MCQ quiz with scoring | `/quiz [topic]` |
| 📌 Cheat sheet / topic summary | `/summary [topic]` |
| 🚨 Ultra-compressed panic mode | `/panic` |
| ✅ Topic progress tracker | `/done [topic]` & `/progress` |
| 📜 Previous year question style | `/pyq [topic]` |
| 🔄 Reset and start fresh | `/reset` |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/TGunaSree/exam-night-rescue
cd exam-night-rescue
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your keys
```

Your `.env` file:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
BHARATCODE_API_KEY=your_bharatcode_api_key
BHARATCODE_BASE_URL=https://bharatcode.ai/api/model/v1
BHARATCODE_MODEL=qwen-3.8-27b
```

### 4. Run the bot
```bash
python bot.py
```

---

## 📱 How to Use

1. Open Telegram → search your bot name
2. Send `/start`
3. Take a photo of your syllabus/notes and send it
4. Tell the bot your subject and available hours
5. Get your rescue plan instantly!

### Example Flow
```
You:  [sends photo of Data Structures syllabus]
Bot:  ✅ Found 8 topics! What subject is this?
You:  Data Structures
Bot:  ⏰ How many hours do you have?
You:  5
Bot:  📅 YOUR RESCUE PLAN — Data Structures (5 hours)
      🔴 HIGH PRIORITY...
      [Full time-boxed plan]

You:  /quiz Binary Trees
Bot:  🎯 Question 1/5 — What is a complete binary tree?...
```

---

## 🏗️ Architecture

```
Telegram User
     ↓
python-telegram-bot (handlers)
     ↓
BharatCode API (qwen-3.8-27b vision + text)
     ↓
Formatted Telegram response
```

### Project Structure
```
exam-night-rescue/
├── bot.py                    # Main entry point
├── handlers/
│   ├── photo_handler.py      # Vision AI syllabus extraction
│   ├── plan_handler.py       # Revision plan generator
│   ├── questions_handler.py  # Key questions generator
│   ├── quiz_handler.py       # Interactive MCQ quiz
│   ├── summary_handler.py    # Cheat sheet generator
│   └── panic_handler.py      # Panic mode
├── utils/
│   ├── bharatcode.py         # BharatCode API wrapper
│   ├── session.py            # User session management
│   └── formatter.py          # Message formatting
├── BharatCode.txt            # Hackathon requirement ✅
├── requirements.txt
└── .env.example
```

---

## 🛠️ Tech Stack

- **Language:** Python 3.11+
- **Bot Framework:** python-telegram-bot v21
- **AI Model:** BharatCode API — qwen-3.8-27b (vision + text)
- **Session State:** In-memory (per chat_id)

---

## 🏆 Hackathon

Built for the **BharatCode Hackathon**.

**Why this wins:**
- 🎓 Every college student has panicked the night before an exam
- ⚡ Instant utility — photo to plan in 60 seconds
- 📱 Telegram = zero friction, already on every phone
- 🇮🇳 Built for Indian students, Indian exam patterns
- 🆓 Completely free, open source

---

## 📄 License

MIT License — free to use, modify and share.
