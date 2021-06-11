from sqlite3.dbapi2 import connect
from flask import Flask, render_template, request, make_response, flash, redirect, session
from passlib.hash import sha256_crypt as sha256
from dotenv import load_dotenv
import json
import sqlite3
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.context_processor
def inject_user():
    if 'username' in session:
        logged_in = True
        username = session['username']
    else:
        logged_in = False
        username = None
    return dict(logged_in=logged_in, username=username)

@app.context_processor
def inject_debug():
    return dict(debug=app.debug)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/api/user", methods=["GET", "POST"])
def user():
    if request.method == 'GET':
        if 'username' in session:
            with sqlite3.connect("database.db") as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT state, color FROM users WHERE username=?', (session['username'],))
                user = cursor.fetchone()
                if user:
                    return {"state": json.loads(user[0]), "color": user[1]}
                else:
                    return "401"
        return "401"

    if request.method == 'POST':
        if 'username' in session:
            if request.form.get('change') == 'state':
                pieces = request.form.get('id').split('-')
                buttonRow = int(pieces[1])
                buttonCol = int(pieces[2])
                with sqlite3.connect("database.db") as connection:
                    cursor = connection.cursor()
                    cursor.execute('SELECT state FROM users WHERE username=?', (session['username'],))
                    user = cursor.fetchone()
                    if user:
                        state = json.loads(user[0])
                        state[buttonRow][buttonCol] = not state[buttonRow][buttonCol]
                        cursor.execute('UPDATE users SET state=? WHERE username=?', (json.dumps(state), session['username']))
                        return json.dumps(state)
                    else:
                        return "401"
            if request.form.get('change') == 'color':
                with sqlite3.connect("database.db") as connection:
                    cursor = connection.cursor()
                    print(request.form.get('color'))
                    cursor.execute('UPDATE users SET color=? WHERE username=?', (request.form.get('color'), session['username']))
                    return "200"
        return "401"
        

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

            session['username'] = username
            res = make_response(redirect("/"))
            return res

@app.route("/logout", methods=["GET"])
def logout():
    session.pop('username', None)
    res = make_response(redirect("/"))
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
        
        color = request.form.get("color")
        if not color:
            flash("Somehow, your browser was not able to detect your preferred color scheme with JavaScript. For being such a tricky little user, you get blood red as your default.")
            color = "#ff0000"
        
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
            cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (username, hashed_password, str(json.dumps([[False]*10]*10)), color))
        
            session['username'] = username
            res = make_response(redirect("/"))
            return res

@app.route('/account', methods=['GET'])
def account():
    if request.method == 'GET':
        return render_template('account.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.getenv("PORT", default=8000), debug=bool(os.getenv("DEBUG", default=False)))