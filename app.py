from flask import Flask, request, render_template_string, redirect, jsonify
import sqlite3
import os
import pickle
import subprocess

app = Flask(__name__)

# Hardcoded secrets (CWE-798)
SECRET_KEY = "super_secret_key_123"
DB_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"

# Hardcoded database path
DATABASE = "/tmp/users.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    cursor.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (2, 'user', 'password', 'user')")
    conn.commit()
    conn.close()

# SQL Injection (CWE-89)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        # Vulnerable query - direct string formatting
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        if user:
            return f"Welcome {username}!"
        return "Invalid credentials"
    return '''
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

# XSS - Cross Site Scripting (CWE-79)
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Directly rendering user input - XSS vulnerable
    template = f"<h1>Search Results for: {query}</h1>"
    return render_template_string(template)

# Command Injection (CWE-78)
@app.route('/ping')
def ping():
    host = request.args.get('host', 'localhost')
    # Directly passing user input to shell command
    result = os.popen(f"ping -c 1 {host}").read()
    return f"<pre>{result}</pre>"

# Path Traversal (CWE-22)
@app.route('/read_file')
def read_file():
    filename = request.args.get('file', 'default.txt')
    # No path sanitization
    with open(f"/var/app/files/{filename}", 'r') as f:
        content = f.read()
    return content

# Insecure Deserialization (CWE-502)
@app.route('/load_data', methods=['POST'])
def load_data():
    data = request.data
    # Using pickle to deserialize user input - dangerous
    obj = pickle.loads(data)
    return jsonify({"status": "loaded", "data": str(obj)})

# Sensitive Data Exposure (CWE-200)
@app.route('/users')
def get_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Returning all user data including passwords
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

# Subprocess Injection (CWE-78)
@app.route('/run')
def run_command():
    cmd = request.args.get('cmd', 'ls')
    # Executing arbitrary user commands
    result = subprocess.check_output(cmd, shell=True)
    return result

# Debug mode enabled in production (CWE-215)
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
