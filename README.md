# 🔒 Nirixa — AI-Powered Exam Proctoring System

<div align="center">

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Hugging_Face-yellow?style=for-the-badge)](https://arujain-nirixa.hf.space) [![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)](https://python.org) [![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com) [![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-orange?style=for-the-badge)](https://groq.com) [![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=for-the-badge&logo=opencv)](https://opencv.org)

**AI that watches you while you learn** 👁️

</div>

---

## ✨ What is Nirixa?

Nirixa is an intelligent, browser-based exam proctoring system that combines **real-time AI surveillance** with **AI-generated quizzes** — all without expensive software or human monitors. Students take exams. Nirixa watches. Cheaters get caught.

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| 🤖 **AI Quiz Generation** | Generate unique exams on any topic instantly using Groq LLaMA 3.1 |
| 📷 **Live Proctoring** | Real-time webcam monitoring with face detection |
| 📱 **Mobile Detection** | YOLOv8-powered phone detection during exams |
| 👁️ **Head Pose Tracking** | MediaPipe-based head pose and gaze analysis |
| ⚠️ **Violation System** | 3-strike auto-submission system |
| 💬 **AI Study Assistant** | Built-in Nirixa AI chatbot for pre-exam help |
| 🎤 **Voice Input** | Ask the chatbot using your microphone |
| ⏱️ **Smart Timer** | Auto-calculated exam duration based on difficulty |
| 📊 **Detailed Results** | Full score breakdown with per-question analysis |
| 🔒 **Secure Sessions** | Flask session management with terms acceptance |

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | Python, Flask |
| AI / ML | Groq API (LLaMA 3.1), MediaPipe, YOLOv8, OpenCV |
| Database | MySQL |
| Deployment | Hugging Face Spaces (Docker) |

---

## 🔍 How It Works

1. Student signs up and logs in
2. Generates a custom AI quiz — topic, difficulty, number of questions
3. Accepts terms and conditions
4. Exam starts — webcam activates, AI chatbot disappears
5. Nirixa monitors in real time — face not visible, phone detected, or tab switched each count as a violation — 3 violations triggers auto-submit
6. Student submits — camera stops — full results shown instantly

---

## ⚡ Proctoring Detection

| Detection Type | Method | Trigger |
|---|---|---|
| Face Missing | Haar Cascade + MediaPipe | No face in frame |
| Mobile Phone | YOLOv8 Object Detection | Phone visible in frame |
| Tab Switch | Browser Visibility API | Tab changed or minimized |
| Window Blur | Browser Focus API | Window loses focus |

---

## 🤖 AI Quiz Generation

Nirixa uses Groq LLaMA 3.1 to generate unique multiple-choice exams on any topic. Smart timer auto-calculates based on difficulty — 3 mins per question for easy, 4 mins for medium, 6 mins for hard. Supports up to 20 questions per exam.

---

## 🚀 Getting Started

**1. Clone the repo and install dependencies**

```bash
git clone https://github.com/aru-jain/nirixa.git
cd nirixa
pip install -r requirements.txt
```

**2. Create a `.env` file with your credentials**

```bash
GROQ_API_KEY=your_groq_api_key
DB_HOST=your_database_host
DB_PORT=3306
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
```

**3. Set up the database and run**

```bash
python create_tables.py
python app.py
```

Visit `http://localhost:7860`

---

## 📁 Project Structure

```bash
nirixa/
├── app.py
├── Dockerfile
├── requirements.txt
├── haarcascade_frontalface_default.xml
├── detection_modules/
│   ├── head_pose.py
│   ├── eye_movement.py
│   └── mobile_detection.py
├── static/
│   └── images/
└── templates/
    ├── exam.html
    ├── login.html
    ├── signup.html
    └── index.html
```

---

## 🧠 What We Learned

Building Nirixa taught us that AI APIs deprecate fast and without warning — always abstract model names and endpoints into config variables. Browser security treats localhost and network IPs completely differently, which broke our microphone feature until we understood why. And balancing exam security with student fairness is genuinely hard design work — the 3-violation system with real-time warnings was the sweet spot between too strict and too lenient.

---

## 📄 License

MIT License — free to use, modify, and deploy.

---

<div align="center">

**⭐ Star this repo if you found it useful!**

[![Try Nirixa Live](https://img.shields.io/badge/Try_Nirixa_Live-→-purple?style=for-the-badge)](https://arujain-nirixa.hf.space)

</div>
