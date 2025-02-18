from flask import Flask, render_template, request, jsonify
import sqlite3
import time

app = Flask(__name__)

# Initialize database
def init_db():
    with sqlite3.connect("tracker.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                total_time INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                start_time INTEGER,
                end_time INTEGER,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            )
        ''')
        conn.commit()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

# Add a new task
@app.route("/add_task", methods=["POST"])
def add_task():
    data = request.json
    with sqlite3.connect("tracker.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (name) VALUES (?)", (data["name"],))
        conn.commit()
    return jsonify({"message": "Task added successfully"}), 201

# Start a Pomodoro session
@app.route("/start_timer", methods=["POST"])
def start_timer():
    data = request.json
    task_id = data["task_id"]
    start_time = int(time.time())
    
    with sqlite3.connect("tracker.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (task_id, start_time) VALUES (?, ?)", (task_id, start_time))
        conn.commit()
    
    return jsonify({"message": "Timer started", "start_time": start_time})

# Stop a Pomodoro session
@app.route("/stop_timer", methods=["POST"])
def stop_timer():
    data = request.json
    log_id = data["log_id"]
    end_time = int(time.time())
    
    with sqlite3.connect("tracker.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE logs SET end_time = ? WHERE id = ?", (end_time, log_id))
        cursor.execute("UPDATE tasks SET total_time = total_time + (? - start_time) WHERE id = (SELECT task_id FROM logs WHERE id = ?)", (end_time, log_id))
        conn.commit()
    
    return jsonify({"message": "Timer stopped", "end_time": end_time})

# Get all tasks and logs
@app.route("/tasks", methods=["GET"])
def get_tasks():
    with sqlite3.connect("tracker.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
    return jsonify({"tasks": tasks})

if __name__ == "__main__":
    app.run(debug=True)

