from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import cv2
import requests
import random
import html
import numpy as np
import base64
import json
import os
from detection_modules.head_pose import process_head_pose
from detection_modules.eye_movement import process_eye_movement
from detection_modules.mobile_detection import process_mobile_detection

app = Flask(__name__)
app.secret_key = 'nirixa_secret'

# ── Config ────────────────────────────────────────────────────
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE']   = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
GROK_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROK_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROK_MODEL   = "llama-3.1-8b-instant"

# ── DB config ─────────────────────────────────────────────────
DB_CONFIG = {
    'host':            os.environ.get('DB_HOST',     ''),
    'port':            int(os.environ.get('DB_PORT', 3306)),
    'user':            os.environ.get('DB_USER',     ''),
    'password':        os.environ.get('DB_PASSWORD', ''),
    'database':        os.environ.get('DB_NAME',     ''),
    'connect_timeout': 10
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"[DB ERROR] {e}")
        raise

# ── Vision ────────────────────────────────────────────────────
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

YAW_THRESHOLD   = 25
PITCH_THRESHOLD = 20
ROLL_THRESHOLD  = 40

def decode_frame(base64_data):
    if ',' in base64_data:
        base64_data = base64_data.split(',')[1]
    img_bytes = base64.b64decode(base64_data)
    np_arr    = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

def parse_head_direction(result):
    if isinstance(result, str):
        return result
    try:
        pitch, yaw, roll = result
        if yaw < -YAW_THRESHOLD:
            return "Looking Left"
        elif yaw > YAW_THRESHOLD:
            return "Looking Right"
        elif pitch < -PITCH_THRESHOLD:
            return "Looking Down"
        elif pitch > PITCH_THRESHOLD:
            return "Looking Up"
        else:
            return "Looking at Screen"
    except (TypeError, ValueError):
        return "No Face Detected"

def detect_cheating(frame):
    cheating_detected = False
    reasons = []

    _, raw_head        = process_head_pose(frame, None)
    head_direction     = parse_head_direction(raw_head)
    _, gaze_direction  = process_eye_movement(frame)
    _, mobile_detected = process_mobile_detection(frame)

    print(f"[DEBUG] Head: {head_direction} | Gaze: {gaze_direction} | Mobile: {mobile_detected}")

    if head_direction == "No Face Detected":
        cheating_detected = True
        reasons.append("No face detected")

    if mobile_detected:
        cheating_detected = True
        reasons.append("Mobile phone detected")

    return cheating_detected, head_direction, gaze_direction, ', '.join(reasons)

# ── Grok helpers ──────────────────────────────────────────────
def call_grok(messages: list, temperature: float = 0.7) -> str:
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":       GROK_MODEL,
        "messages":    messages,
        "temperature": temperature,
    }
    resp = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def build_quiz_from_grok_response(raw: str) -> list:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])

    data        = json.loads(cleaned)
    questions   = []
    correct_map = {}

    for idx, item in enumerate(data, start=1):
        qid     = str(idx)
        options = item.get("options", [])
        random.shuffle(options)
        correct_map[qid] = item["answer"]
        questions.append({
            "id":       qid,
            "question": item["question"],
            "options":  options,
        })

    session['correct_answers'] = correct_map
    return questions

# ── Routes ────────────────────────────────────────────────────
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return render_template('signup.html', error="Username and password are required.")

        try:
            db     = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            db.commit()
            cursor.close()
            db.close()
            return redirect(url_for('login'))

        except mysql.connector.IntegrityError:
            return render_template('signup.html', error="Username already exists. Try another.")
        except Exception as e:
            print(f"[SIGNUP ERROR] {e}")
            return render_template('signup.html', error=f"Signup failed: {str(e)}")

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        print(f"[LOGIN ATTEMPT] username={username}")

        try:
            db     = get_db()
            cursor = db.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            user = cursor.fetchone()
            cursor.close()
            db.close()

            print(f"[LOGIN] DB result: {user}")

            if user:
                session.clear()
                session['username'] = username
                session.modified = True
                print(f"[LOGIN] Session set: {session.get('username')}")
                return redirect(url_for('exam'))
            else:
                return render_template('login.html', error="Invalid username or password.")

        except Exception as e:
            print(f"[LOGIN ERROR] {e}")
            return render_template('login.html', error=f"Login error: {str(e)}")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/exam')
def exam():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('exam.html', username=session['username'])

@app.route('/test_db')
def test_db():
    try:
        db     = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()
        cursor.close()
        db.close()
        return jsonify({"status": "connected", "user_count": count[0]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ── Chatbot ───────────────────────────────────────────────────
@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    body         = request.get_json()
    user_message = body.get("message", "").strip()
    history      = body.get("history", [])

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    system_prompt = (
        "You are Nirixa AI, an intelligent exam assistant. "
        "You help students by answering questions, explaining concepts, and "
        "generating customized multiple-choice quizzes on any topic they request. "
        "When a user asks you to create a quiz or test, reply ONLY with a JSON array "
        "in this exact format (no extra text):\n"
        "[\n"
        "  {\n"
        '    "question": "Question text here",\n'
        '    "options": ["Option A", "Option B", "Option C", "Option D"],\n'
        '    "answer": "Correct option text"\n'
        "  }\n"
        "]\n"
        "For regular conversation or explanations, reply in plain text."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages += history
    messages.append({"role": "user", "content": user_message})

    try:
        reply    = call_grok(messages)
        stripped = reply.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        is_quiz  = stripped.startswith("[")

        if is_quiz:
            questions = build_quiz_from_grok_response(reply)
            return jsonify({"reply": reply, "quiz": questions, "is_quiz": True})

        return jsonify({"reply": reply, "is_quiz": False})

    except requests.HTTPError as e:
        return jsonify({"error": f"Grok API error: {e.response.status_code}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Test generation ───────────────────────────────────────────
@app.route('/generate_test', methods=['POST'])
def generate_test():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    body          = request.get_json()
    topic         = body.get("topic", "General Knowledge").strip()
    num_questions = min(int(body.get("num_questions", 5)), 20)
    difficulty    = body.get("difficulty", "medium").lower()

    prompt = (
        f"Generate a {difficulty}-difficulty multiple-choice quiz about '{topic}' "
        f"with exactly {num_questions} questions. "
        "Reply ONLY with a JSON array — no preamble, no markdown fences — in this format:\n"
        "[\n"
        "  {\n"
        '    "question": "...",\n'
        '    "options": ["A", "B", "C", "D"],\n'
        '    "answer": "exact text of correct option"\n'
        "  }\n"
        "]\n"
        "Make sure 'answer' is one of the strings in 'options'. "
        "Vary the position of the correct answer across questions."
    )

    try:
        raw       = call_grok([{"role": "user", "content": prompt}], temperature=0.6)
        questions = build_quiz_from_grok_response(raw)
        return jsonify(questions)

    except json.JSONDecodeError:
        return jsonify({"error": "Grok returned malformed JSON. Try again."}), 502
    except requests.HTTPError as e:
        return jsonify({"error": f"Grok API error: {e.response.status_code}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Frame analysis ────────────────────────────────────────────
@app.route('/analyze_frame', methods=['POST'])
def analyze_frame():
    data       = request.get_json()
    frame_data = data.get('frame')

    if not frame_data:
        return jsonify({'error': 'No frame provided'}), 400

    frame = decode_frame(frame_data)
    if frame is None:
        return jsonify({'error': 'Failed to decode frame'}), 400

    cheating, head_direction, gaze_direction, reason = detect_cheating(frame)

    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        color = (0, 0, 255) if cheating else (0, 255, 0)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    cv2.putText(frame, f"Head: {head_direction}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Gaze: {gaze_direction}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    _, buffer      = cv2.imencode('.jpg', frame)
    annotated_b64  = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        'cheating_detected': cheating,
        'head_direction':    head_direction,
        'gaze_direction':    gaze_direction,
        'reason':            reason,
        'annotated_frame':   f'data:image/jpeg;base64,{annotated_b64}'
    })

# ── Quiz submission ───────────────────────────────────────────
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    try:
        body            = request.get_json()
        submitted       = body.get("answers", {})
        correct_answers = session.get('correct_answers', {})
        total           = len(correct_answers)

        answer_details = {}
        score          = 0

        for qid, correct in correct_answers.items():
            user_ans   = submitted.get(qid, None)
            is_correct = user_ans == correct
            if is_correct:
                score += 1
            answer_details[qid] = {
                "question":       f"Question {qid}",
                "user_answer":    user_ans,
                "correct_answer": correct,
                "correct":        is_correct
            }

        return jsonify({"score": score, "total": total, "answers": answer_details})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Misc ──────────────────────────────────────────────────────
@app.route('/log_cheating', methods=['POST'])
def log_cheating():
    data   = request.get_json()
    reason = data.get('reason', 'Unknown reason')
    print(f"[Cheating] User: {session.get('username', 'Unknown')} | Reason: {reason}")
    return jsonify({'status': 'logged'})

@app.route('/mobile_detect')
def mobile_detect():
    return jsonify({'mobile_detected': False, 'info': 'Use /analyze_frame instead'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=False)