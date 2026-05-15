from flask import Flask, request, jsonify
import sqlite3
import os
import subprocess

app = Flask(__name__)

# Hardcoded secrets
SECRET_KEY = "super_secret_key_123"
ADMIN_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"

DATABASE = "/tmp/school.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students 
                     (id INTEGER PRIMARY KEY, name TEXT, grade TEXT, password TEXT)''')
    cursor.execute("INSERT OR IGNORE INTO students VALUES (1, 'Alice', 'A', 'alice123')")
    cursor.execute("INSERT OR IGNORE INTO students VALUES (2, 'Bob', 'B', 'bob123')")
    cursor.execute("INSERT OR IGNORE INTO students VALUES (3, 'Charlie', 'C', 'charlie123')")
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return jsonify({
        "app": "School Management System",
        "status": "running",
        "endpoints": [
            "/health",
            "/students",
            "/search?name=Alice",
            "/login?username=Alice&password=alice123",
            "/ping?host=localhost",
            "/run?cmd=ls"
        ]
    })

@app.route('/health')
def health():
    return jsonify({"status": "UP"})

# SQL Injection vulnerability
@app.route('/search')
def search():
    name = request.args.get('name', '')
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        query = f"SELECT * FROM students WHERE name='{name}'"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)})

# SQL Injection + Sensitive Data Exposure
@app.route('/login')
def login():
    username = request.args.get('username', '')
    password = request.args.get('password', '')
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        query = f"SELECT * FROM students WHERE name='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        if user:
            return jsonify({"status": "success", "user": user})
        return jsonify({"status": "failed"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Sensitive Data Exposure
@app.route('/students')
def get_students():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        conn.close()
        return jsonify({"students": students})
    except Exception as e:
        return jsonify({"error": str(e)})

# Command Injection vulnerability
@app.route('/ping')
def ping():
    host = request.args.get('host', 'localhost')
    try:
        result = os.popen(f"ping -c 1 {host}").read()
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})

# Subprocess Injection vulnerability
@app.route('/run')
def run_command():
    cmd = request.args.get('cmd', 'ls')
    try:
        result = subprocess.check_output(cmd, shell=True)
        return jsonify({"output": result.decode()})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
