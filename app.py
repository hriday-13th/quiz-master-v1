import uvicorn
import sqlite3, os
from asgiref.wsgi import WsgiToAsgi
from flask import Flask, request, jsonify, redirect, flash, render_template, session, url_for, g

from env import DATABASE_PATH, PORT, HOST
from database.user import User

app = Flask(__name__)
app.secret_key = "password"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, DATABASE_PATH)

# -- database functions --
def get_db():
    if 'db' not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
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


# -- app functions --
@app.route('/')
def home():
    return redirect("/login")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = request.form['dob']

        user_model = User()
        user_model.register(username, password, full_name, qualification, dob)
        user_model.close()

        flash("Signup successful. Please log in.")
        return redirect(url_for('login'))
    
    return render_template("signup_page.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_model = User()
        user, role = user_model.login(username=username, password=password)
        user_model.close()

        if user:
            session['user_id'] = user['UserID']
            if role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash("User not found. Please sign up first.")
            return redirect(url_for('signup'))

    return render_template("login_page.html")

@app.route('/dashboard')
def dashboard():
    # if 'user_id' not in session:
    #     return redirect("/login")
    # return render_template("dashboard.html")
    return "we the user"

@app.route('/admin_dashboard')
def admin_dashboard():
   return "this is the admin burrah!!"

@app.route('/api/data', methods=['GET', 'POST'])
def data():
    if request.method == 'GET':
        return jsonify({"message": "You sent a GET request!"})
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({"message": "You sent a POST request!", "data": data})

asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        with app.app_context():
            init_db()

    event = User()._ensure_admin_exists()
    
    uvicorn.run(
        "app:asgi_app",
        host=HOST,
        port=PORT,
        reload=True
    )
