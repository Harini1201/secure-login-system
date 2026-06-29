from flask import Flask, render_template_string, request, redirect, session, url_for
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key_here"


def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()


@app.route("/")
def home():
    if "user" in session:
        return f"""
        <h2>Welcome, {session['user']}!</h2>
        <a href='/logout'>Logout</a>
        """
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if len(username) < 3 or len(password) < 6:
            return "Username must be 3+ chars and password 6+ chars"

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        try:
            conn = sqlite3.connect("users.db")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, hashed)
            )
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return "Username already exists"

    return render_template_string("""
    <h2>Register</h2>
    <form method="post">
        Username: <input name="username"><br><br>
        Password: <input type="password" name="password"><br><br>
        <button type="submit">Register</button>
    </form>
    <a href="/login">Login</a>
    """)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )
        user = cur.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode(), user[0]):
            session["user"] = username
            return redirect("/")

        return "Invalid Username or Password"

    return render_template_string("""
    <h2>Login</h2>
    <form method="post">
        Username: <input name="username"><br><br>
        Password: <input type="password" name="password"><br><br>
        <button type="submit">Login</button>
    </form>
    <a href="/register">Register</a>
    """)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)