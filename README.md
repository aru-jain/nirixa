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
Student signs up and logs in
Generates a custom AI quiz — topic, difficulty, number of questions
Accepts terms and conditions
Exam starts — webcam activates, AI chatbot disappears
Nirixa monitors in real time:
• Face not visible  → Violation ⚠️
• Phone detected    → Violation ⚠️
• Tab switched      → Violation ⚠️
• 3 violations      → Auto-submit 🚨
Student submits → Camera stops → Full results shown instantly

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

Nirixa uses Groq LLaMA 3.1 to generate unique multiple-choice exams on any topic. Smart timer auto-calculates based on difficulty — 3 mins per question (easy), 4 mins (medium), 6 mins (hard). Supports up to 20 questions per exam.

---

## 🚀 Getting Started

**1. Clone the repo**
