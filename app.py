from datetime import datetime
import random
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "vitalbridge.db"

app = Flask(__name__)
app.secret_key = "change-this-demo-secret-before-deployment"


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                heart_rate INTEGER NOT NULL,
                temperature REAL NOT NULL,
                spo2 INTEGER NOT NULL,
                acknowledged INTEGER NOT NULL DEFAULT 0
            )
        """)
        count = db.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
        if count == 0:
            db.execute("""
                INSERT INTO alerts
                (created_at, level, message, heart_rate, temperature, spo2, acknowledged)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (
                datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "INFO",
                "Welcome to the VitalBridge demonstration. These are sample readings.",
                78, 36.8, 98
            ))


def assess_readings(heart_rate, temperature, spo2):
    # Demonstration thresholds only. They are NOT clinical or diagnostic limits.
    if heart_rate >= 125 or heart_rate <= 45 or temperature >= 38.5 or spo2 <= 92:
        return "EMERGENCY", "A simulated reading crossed a demo safety threshold. Please check the individual."
    if heart_rate >= 110 or heart_rate <= 50 or temperature >= 37.8 or spo2 <= 95:
        return "WARNING", "A simulated reading is outside the demo's usual range. Please review the situation."
    return "NORMAL", "Readings are within the demo's configured range."


@app.route("/")
def index():
    return render_template("index.html", role=session.get("role"))


@app.post("/login")
def login():
    role = request.form.get("role", "caregiver")
    if role not in ("caregiver", "individual"):
        role = "caregiver"
    session["role"] = role
    return redirect(url_for("dashboard"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if session.get("role") not in ("caregiver", "individual"):
        return redirect(url_for("index"))
    return render_template("dashboard.html", role=session["role"])


@app.get("/api/state")
def api_state():
    if session.get("role") not in ("caregiver", "individual"):
        return jsonify({"error": "Please choose a demo role first."}), 401
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM alerts ORDER BY id DESC LIMIT 8"
        ).fetchall()
    alerts = [dict(row) for row in rows]
    latest = alerts[0] if alerts else None
    return jsonify({
        "role": session["role"],
        "latest": latest,
        "alerts": alerts,
        "demo_notice": "Simulated data only. Not a medical device or emergency service."
    })


@app.post("/api/simulate")
def api_simulate():
    if session.get("role") not in ("caregiver", "individual"):
        return jsonify({"error": "Please choose a demo role first."}), 401

    # Generate plausible demo values, occasionally including an out-of-range example.
    scenario = request.json.get("scenario", "random") if request.is_json else "random"
    if scenario == "warning":
        heart_rate = random.randint(110, 120)
        temperature = round(random.uniform(37.8, 38.2), 1)
        spo2 = random.randint(93, 95)
    elif scenario == "emergency":
        heart_rate = random.randint(126, 145)
        temperature = round(random.uniform(38.6, 39.2), 1)
        spo2 = random.randint(88, 92)
    else:
        heart_rate = random.randint(65, 100)
        temperature = round(random.uniform(36.3, 37.4), 1)
        spo2 = random.randint(96, 100)

    level, message = assess_readings(heart_rate, temperature, spo2)
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO alerts
            (created_at, level, message, heart_rate, temperature, spo2, acknowledged)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (now, level, message, heart_rate, temperature, spo2))
        alert_id = cursor.lastrowid

    return jsonify({
        "id": alert_id,
        "created_at": now,
        "level": level,
        "message": message,
        "heart_rate": heart_rate,
        "temperature": temperature,
        "spo2": spo2,
        "acknowledged": 0
    })


@app.post("/api/alerts/<int:alert_id>/acknowledge")
def acknowledge_alert(alert_id):
    if session.get("role") != "caregiver":
        return jsonify({"error": "Only the caregiver demo role can acknowledge alerts."}), 403
    with get_db() as db:
        db.execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
    return jsonify({"success": True})


init_db()

if __name__ == "__main__":
    app.run(debug=True)
