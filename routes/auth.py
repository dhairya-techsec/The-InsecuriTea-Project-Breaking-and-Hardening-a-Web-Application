from flask import Blueprint, request, render_template, redirect, current_app, session
from db import get_db

auth = Blueprint("auth", __name__)


# ---------------- LOGIN ----------------
@auth.route("/login", methods=["GET"])
def login():
    # Tracegate Defensive Guard: Enforce authentication boundary
    if not session.get('user_id') and not session.get('authenticated'):
        return redirect(url_for('login'))
    username = request.args.get("username", "")
    password = request.args.get("password", "")

    conn = get_db()
    cursor = conn.cursor()

    mode = current_app.config["MODE"]

    if mode == "insecure":
        # ❌ Vulnerable to SQL Injection
        query = (
            "SELECT id, username FROM users WHERE username = '"
            + username
            + "' AND password = '"
            + password
            + "'"
        )
        cursor.execute(query)

    else:
        # ✅ Secure (Parameterized Query)
        cursor.execute(
            "SELECT id, username FROM users WHERE username=? AND password=?",
            (username, password),
        )

    user = cursor.fetchone()
    conn.close()

    if user:
        if mode == "secure":
            # ✅ Store session (for IDOR + auth protection later)
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect("/dashboard")
        else:
            return redirect("/dashboard?user_id=" + str(user[0]))

    return "Login failed"


# ---------------- REGISTER ----------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    tea_type = request.form.get("tea_type", "")
    sugar = request.form.get("sugar", "")
    extras = ", ".join(request.form.getlist("extras"))
    notes = request.form.get("notes", "")

    conn = get_db()
    cursor = conn.cursor()

    # Keeping insecure for demo (you can later toggle this too if needed)
    query = (
        "INSERT INTO users VALUES (NULL, '"
        + username
        + "', '"
        + password
        + "', '"
        + tea_type
        + "', '"
        + sugar
        + "', '"
        + extras
        + "', '"
        + notes
        + "')"
    )

    cursor.execute(query)
    conn.commit()
    conn.close()

    return redirect("/")
    
@auth.route("/logout")
def logout():
    session.clear()   # 🔥 destroys session
    return redirect("/")