# 🆘 Exam Night Rescue — AI Study Companion

> **"Exam tomorrow? Don't panic. We've got you."**

[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/ExamNightRescueBot)
[![Hackathon](https://img.shields.io/badge/BharatCode-Hackathon%202026-orange)](https://bharatcode.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)

**Exam Night Rescue** is an AI-powered Telegram bot built specifically for college students facing the universal night-before-exam panic. 

Instead of getting overwhelmed by an endless syllabus at 11 PM, a student simply **sends a photo or document of their syllabus (or pastes notes)**. In under 60 seconds, the bot generates a **time-boxed, prioritized 1-night revision schedule**, predicts **likely exam questions**, offers **rapid-fire MCQ quizzes with instant scoring**, and provides **3-minute cheat sheets**.

---

## 🎯 The Problem

Every semester, millions of university students face the exact same crisis:
* ⏰ **Time is running out:** Exam is tomorrow morning (6–8 hours left).
* 🤯 **Cognitive overload:** Syllabi are 40+ pages long; students don't know where to start or what to skip.
* 💸 **Existing tools fail:** Traditional apps (Anki, Quizlet) require hours of manual setup, and paid study platforms cost thousands of rupees.
* 📱 **High friction:** Students won't install heavy desktop software during an emergency.

**Exam Night Rescue solves this with zero friction:** Right inside Telegram on any mobile phone, multimodal AI plans their night in seconds.

---

## ✨ Core Features

| Feature | Description | Trigger |
|---|---|---|
| 📸 **Multimodal Vision Intake** | Snap a photo of a textbook, syllabus handout, handwritten notes, or WebP/PDF file. Vision AI parses all topics instantly. | Send Photo / Document |
| ✍️ **Direct Text Intake** | Paste messy notes or a copy-pasted syllabus directly into chat. AI extracts topics automatically. | Paste text in chat |
| 📅 **1-Night Rescue Plan** | Generates a realistic, time-boxed study schedule categorized by High, Medium, and Low exam weightage. | `/plan` or auto on input |
| ❓ **Likely Exam Questions** | Predicts 2-mark, 5-mark, and 10-mark questions based on university examination patterns. | `/questions [topic]` |
| 🎯 **Interactive MCQ Quiz** | Rapid-fire 5-question test with customized keyboard options (A, B, C, D) and instant feedback. | `/quiz [topic]` |
| 📌 **3-Minute Cheat Sheets** | Dense, high-yield summary cards with definitions, formulas, common pitfalls, and memory tricks. | `/summary [topic]` |
| 🚨 **Emergency Panic Mode** | When there's only 1–2 hours left: ultra-compressed high-yield points and survival tips only. | `/panic` |
| 📊 **Visual Progress Tracker** | Mark topics completed and watch an animated progress bar track your journey to 100%. | `/done [topic]` & `/progress` |
| 📜 **PYQ Exam Simulator** | Generates questions matching the style and marking schemes of past university papers. | `/pyq [topic]` |

---

## 📱 Bot Commands Reference

```text
/start               - Launch bot & view welcome guide
/plan                - View or regenerate your tonight revision plan
/questions [topic]   - Get predicted 2, 5 & 10 mark exam questions
/quiz [topic]        - Launch 5-question interactive MCQ quiz
/endquiz             - Finish quiz early & view performance score
/summary [topic]     - Generate dense 3-minute cheat sheet card
/panic               - Emergency mode for last 1-2 hours
/settopics [t1, t2]  - Manually define your study topics
/done [topic]        - Mark a topic as completed
/progress            - Display visual progress bar & remaining topics
/pyq [topic]         - Generate university-style previous year questions
/reset               - Clear session & start fresh with a new subject
/help                - Show all available commands
```

---

## 🏗️ Technical Architecture

```text
               ┌─────────────────────────────────────┐
               │         Telegram Mobile / Web       │
               │   (Photos, WebP, Notes, Commands)   │
               └──────────────────┬──────────────────┘
                                  │
                                  ▼
               ┌─────────────────────────────────────┐
               │    python-telegram-bot (v21.6)      │
               │   • Photo/Document Handler (Pillow) │
               │   • State Machine Session Manager   │
               │   • Command & Text Router           │
               └──────────────────┬──────────────────┘
                                  │
                                  ▼
               ┌─────────────────────────────────────┐
               │         AI Model Integration        │
               │   • BharatCode / Gemini Vision API  │
               │   • Multimodal prompt engineering   │
               │   • Automatic retry on 503 errors   │
               └──────────────────┬──────────────────┘
                                  │
                                  ▼
               ┌─────────────────────────────────────┐
               │        24/7 Cloud Deployment        │
               │   • Render Free Web Service Tier    │
               │   • Integrated HTTP Health Server   │
               │   • Python 3.11 Asyncio Event Loop  │
               └─────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

* **Language:** Python 3.11+
* **Framework:** `python-telegram-bot` v21.6 (Asyncio)
* **Image Processing:** `Pillow` (WebP, PNG, JPEG normalization)
* **Networking & Resilience:** `httpx` with exponential backoff
* **Model Backend:** BharatCode API specification / Gemini Multimodal Flash
* **Cloud Hosting:** Render Web Service (Free Tier with continuous health check)

---

## 🚀 Quick Setup & Local Development

### 1. Clone the repository
```bash
git clone https://github.com/TGunaSree/exam-night-rescue.git
cd exam-night-rescue
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure `.env`
Create a `.env` file in the root directory:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-flash-latest
```

### 4. Run the bot
```bash
python bot.py
```

---

## 📄 Hackathon Compliance

* `BharatCode.txt` is present in the repository root.
* Uses official OpenAI-compatible endpoints and multimodal vision capabilities.
* Public GitHub repository licensed under MIT.

---

## 🤝 Authors

Created by **[TGunaSree](https://github.com/TGunaSree)** for the **BharatCode Hackathon 2026**.
