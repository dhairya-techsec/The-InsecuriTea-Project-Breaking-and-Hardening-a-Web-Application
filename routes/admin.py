from flask import Blueprint, request, render_template, redirect, current_app, session
import sqlite3

admin = Blueprint("admin", __name__)

DB_NAME = "users.db"


# ---------------- ADMIN LIST ----------------
@admin.route("/admin")
def admin_panel():
    mode = current_app.config["MODE"]

    if mode == "insecure":
        # ❌ Weak auth (URL based)
        username = request.args.get("username", "")
        if username != "admin":
            return "Access denied"
    else:
        # ✅ Secure auth (session based)
        if session.get("username") != "admin":
            return redirect("/")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()

    conn.close()

    return render_template("admin.html", users=users, mode=mode)


# ---------------- USER DETAIL ----------------
@admin.route("/admin/user")
def admin_user_detail():
    mode = current_app.config["MODE"]

    user_id = request.args.get("id", "")

    if mode == "insecure":
        # ❌ Weak auth
        username = request.args.get("username", "")
        if username != "admin":
            return "Access denied"

        # ❌ SQLi vulnerable
        query = "SELECT id, username, role FROM users WHERE username = :username AND password = :password"
        query = "SELECT username, tea_type, sugar, extras, notes FROM users WHERE id = " + user_id

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query)

    else:
        # ✅ Secure auth
        if session.get("username") != "admin":
            return redirect("/")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # ✅ Parameterized query (no SQLi)
        cursor.execute(
            "SELECT username, tea_type, sugar, extras, notes FROM users WHERE id=?",
            (user_id,),
        )

    user = cursor.fetchone()
    conn.close()

    if not user:
        return "User not found"

    return render_template(
        "admin_user.html",
        user_id=user_id,
        username=user[0],
        tea_type=user[1],
        sugar=user[2],
        extras=user[3],
        notes=user[4],
        mode=mode
    )


# ---------------- DELETE USER ----------------
@admin.route("/delete_user")
def delete_user():
    mode = current_app.config["MODE"]
    user_id = request.args.get("id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if mode == "insecure":
        # ❌ No auth + SQLi
        cursor.execute("DELETE FROM users WHERE id = " + user_id)

    else:
    # ✅ Secure mode
        if session.get("username") != "admin":
            return redirect("/")

        # 🚫 Prevent admin deleting itself
        current_user = session.get("user_id")

        if str(user_id) == str(current_user):
            return "❌ You cannot delete your own admin account!"

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))

    conn.commit()
    conn.close()

    return redirect("/admin" + ("?username=admin" if mode == "insecure" else ""))