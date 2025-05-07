import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask, request, jsonify, redirect, render_template, session, g

import sqlite3, hashlib, os

app = Flask(__name__)
app.secret_key = "password"
DATABASE = "quizmaster.db"


# -- database functions --
def get_db():
    if 'db' not in g:
        g.db = DATABASE
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with app.open_resource('sql/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# -- password hashing --
def hash_password(password):
    return hashlib.sha256(password.encode().hexdigest())


# -- app functions --
@app.route('/')
def home():
    return redirect("/login")

@app.route('/signup')
def signup():
    return render_template("signup_page.html")

@app.route('/login')
def login():
    return render_template("login_page.html")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route('/admin_dashboard')
def admin_dashboard():
    pass

@app.route('/api/data', methods=['GET', 'POST'])
def data():
    if request.method == 'GET':
        return jsonify({"message": "You sent a GET request!"})
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({"message": "You sent a POST request!", "data": data})

asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    # if not os.path.exists(DATABASE):
    #     with app.app_context():
    #         init_db()

    uvicorn.run(
        "app:asgi_app",
        host="0.0.0.0",
        port=9000,
        reload=True
    )
