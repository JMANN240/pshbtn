from sqlite3.dbapi2 import connect
from flask import Flask, render_template, request, make_response, flash, redirect
from passlib.hash import sha256_crypt as sha256
import json
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.context_processor
def add_user():
    sid = request.cookies.get('sessionID')
    logged_in = sid is not None
    if logged_in:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT username FROM users WHERE sessionID=?', (sid,))
            username = cursor.fetchone()[0]
    else:
        username = None
    return dict(logged_in=logged_in, username=username)

@app.route("/")
def index():
    sid = request.cookies.get('sessionID')
    print(f"SID: {sid}")
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT username FROM users WHERE sessionID=?', (sid,))
        username = cursor.fetchone()
        print(f"Logged in as {username}")
        
    return render_template('index.html')

@app.route("/api/checks", methods=["GET", "POST"])
def checks():
    sid = request.cookies.get('sessionID')
    if sid is None:
        return "401"
    
    if request.method == 'GET':
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT state FROM users WHERE sessionID=?', (sid,))
            return {"state": json.loads(cursor.fetchone()[0])}

    if request.method == 'POST':
        pieces = request.form.get('id').split('-')
        buttonRow = int(pieces[1])
        buttonCol = int(pieces[2])
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT state FROM users WHERE sessionID=?', (sid,))
            state = json.loads(cursor.fetchone()[0])
            state[buttonRow][buttonCol] = not state[buttonRow][buttonCol]
            cursor.execute('UPDATE users SET state=? WHERE sessionID=?', (json.dumps(state), sid))
        return json.dumps(state)
    return ""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get("username")
        if not username:
            flash("No username provided")
            return make_response(redirect("/login"))
        
        password = request.form.get("password")
        if not password:
            flash("No password provided")
            return make_response(redirect("/login"))
        
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT username FROM users WHERE username=?', (username,))
            if not cursor.fetchall():
                flash(f"Could not find username '{username}'")
                return make_response(redirect("/login"))
            
            cursor.execute('SELECT password FROM users WHERE username=?', (username,))
            hashed_password = cursor.fetchone()[0]
            if not sha256.verify(password, hashed_password):
                flash("Incorrect username or password")
                return make_response(redirect("/login"))
        
            res = make_response(redirect("/"))
            sessionID = sha256.hash(f"{username}{password}")
            cursor.execute('UPDATE users SET sessionID=? WHERE username=?', (sessionID, username))
            res.set_cookie('sessionID', sessionID)

            return res

@app.route("/logout", methods=["GET"])
def logout():
    sid = request.cookies.get("sessionID")
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE users SET sessionID="" WHERE sessionID=?', (sid,))
        res = make_response(redirect("/"))
        res.set_cookie('sessionID', "", expires=0)
        return res

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    if request.method == 'POST':
        username = request.form.get("username")
        if not username:
            flash("No username provided")
            return make_response(redirect("/signup"))
        
        password = request.form.get("password")
        if not password:
            flash("No password provided")
            return make_response(redirect("/signup"))
        
        confirm_password = request.form.get("confirm-password")
        if not confirm_password:
            flash("No confirmation password provided")
            return make_response(redirect("/signup"))
        
        if password != confirm_password:
            flash("Passwords do not match")
            return make_response(redirect("/signup"))
        
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT username FROM users WHERE username=?', (username,))
            if cursor.fetchall():
                flash(f"Username '{username}' unavailable")
                return make_response(redirect("/signup"))
            
            hashed_password = sha256.hash(password)
            cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (username, hashed_password, str(json.dumps([[False]*10]*10)), ""))
        
            res = make_response(redirect("/"))
            sessionID = sha256.hash(f"{username}{password}")
            cursor.execute('UPDATE users SET sessionID=? WHERE username=?', (sessionID, username))
            res.set_cookie('sessionID', sessionID)

            return res

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)