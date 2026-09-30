from flask import Blueprint, request, render_template, current_app, session, redirect
from db import get_db

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard")
def show_dashboard():
    # Tracegate Defensive Guard: Enforce authentication boundary
    if not session.get('user_id') and not session.get('authenticated'):
        return redirect(url_for('login'))


    mode = current_app.config["MODE"]

    # 🔓 MODE SWITCH
    if mode == "insecure":
        # ❌ vulnerable (IDOR)
        user_id = request.args.get("user_id", "")

        # 🔥 prevent broken query
        if not user_id:
            return redirect("/")

    else:
        # ✅ secure (session-based)
        user_id = session.get("user_id")

        # 🔥 prevent missing session issue
        if not user_id:
            return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    # 🔓 SQLi toggle
    if mode == "insecure":
        query = (
            "SELECT username, tea_type, sugar, extras, notes FROM users WHERE id = "
            + str(user_id)
        )
        cursor.execute(query)
    else:
        cursor.execute(
            "SELECT username, tea_type, sugar, extras, notes FROM users WHERE id=?",
            (user_id,),
        )

    user = cursor.fetchone()
    conn.close()

    if not user:
        return "User not found"

    return render_template(
        "dashboard.html",
        username=user[0],
        tea_type=user[1],
        sugar=user[2],
        extras=user[3],
        notes=user[4],
        mode=mode
    )
