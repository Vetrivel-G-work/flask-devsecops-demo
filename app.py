from flask import Flask, request, render_template_string, redirect, jsonify
import sqlite3
import os
import pickle
import subprocess

app = Flask(__name__)

SECRET_KEY = "super_secret_key_123"
DB_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
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

@app.route('/search')
def search():
    query = request.args.get('q', '')
    template = f"<h1>Search Results for: {query}</h1>"
    return render_template_string(template)

@app.route('/ping')
def ping():
    host = request.args.get('host', 'localhost')
    result = os.popen(f"ping -c 1 {host}").read()
    return f"<pre>{result}</pre>"

@app.route('/read_file')
def read_file():
    filename = request.args.get('file', 'default.txt')
    with open(f"/var/app/files/{filename}", 'r') as f:
        content = f.read()
    return content

@app.route('/load_data', methods=['POST'])
def load_data():
    data = request.data
    obj = pickle.loads(data)
    return jsonify({"status": "loaded", "data": str(obj)})

@app.route('/users')
def get_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/run')
def run_command():
    cmd = request.args.get('cmd', 'ls')
    result = subprocess.check_output(cmd, shell=True)
    return result

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
