import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "gym_secret_key"

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    conn = sqlite3.connect('gym.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (request.form["username"], request.form["password"])
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user"] = request.form["username"]
            return redirect("/home")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?,?)",
                (request.form["username"], request.form["password"])
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("signup.html", error="Username already exists")
        conn.close()
        return redirect("/")
    return render_template("signup.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- HOME ----------------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("home.html")

# ====================================================
# ===================== MEMBERS ======================
# ====================================================
@app.route("/member/register", methods=["GET", "POST"])
def member_register():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        cursor.execute("""
            INSERT INTO member (member_name, age, gender, phone, email, join_date, expiry_date, trainer_id)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            request.form["name"],
            request.form["age"],
            request.form["gender"],
            request.form["phone"],
            request.form["email"],
            request.form["join_date"],
            request.form["expiry_date"],
            request.form["trainer_id"]
        ))
        conn.commit()
        conn.close()
        return redirect("/member/directory")
    
    cursor.execute("SELECT * FROM trainer")
    trainers = cursor.fetchall()
    conn.close()
    return render_template("member_register.html", trainers=trainers)

@app.route("/member/directory")
def member_directory():
    sort_by = request.args.get("sort", "member_id")
    filter_trainer = request.args.get("trainer_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT m.*, t.trainer_name 
        FROM member m
        LEFT JOIN trainer t ON m.trainer_id = t.trainer_id
    """
    params = []
    
    if filter_trainer:
        query += " WHERE m.trainer_id = ?"
        params.append(filter_trainer)
    
    if sort_by == "trainer":
        query += " ORDER BY t.trainer_name ASC"
    else:
        query += f" ORDER BY m.{sort_by} ASC"
        
    cursor.execute(query, params)
    members = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM trainer")
    trainers = cursor.fetchall()
    
    conn.close()

    today = datetime.today().date().strftime('%Y-%m-%d')

    for m in members:
        if m["expiry_date"] and m["expiry_date"] >= today:
            m["status"] = "Active"
        else:
            m["status"] = "Expired"

    return render_template("member_directory.html", data=members, trainers=trainers, selected_trainer=filter_trainer)

@app.route("/member/modify", methods=["GET", "POST"])
def member_modify():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        cursor.execute("""
            UPDATE member
            SET member_name=?, age=?, gender=?, phone=?, email=?, expiry_date=?, trainer_id=?
            WHERE member_id=?
        """, (
            request.form["name"],
            request.form["age"],
            request.form["gender"],
            request.form["phone"],
            request.form["email"],
            request.form["expiry_date"],
            request.form["trainer_id"],
            request.form["id"]
        ))
        conn.commit()
        conn.close()
        return redirect("/member/directory")

    mid = request.args.get("id")
    cursor.execute("SELECT * FROM member WHERE member_id=?", (mid,))
    member = cursor.fetchone()
    
    cursor.execute("SELECT * FROM trainer")
    trainers = cursor.fetchall()
    
    conn.close()
    return render_template("member_modify.html", m=member, trainers=trainers)

@app.route("/member/remove", methods=["POST"])
def member_remove():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM member WHERE member_id=?", (request.form["id"],))
    conn.commit()
    conn.close()
    return redirect("/member/directory")

# ====================================================
# ===================== TRAINERS =====================
# ====================================================
@app.route("/trainer/onboard", methods=["GET", "POST"])
def trainer_onboard():
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trainer (trainer_name, specialization, phone, email)
            VALUES (?,?,?,?)
        """, (
            request.form["trainer_name"],
            request.form["speciality"],
            request.form["phone"],
            request.form["email"]
        ))
        conn.commit()
        conn.close()
        return redirect("/trainer/directory")
    return render_template("trainer_onboard.html")

@app.route("/trainer/directory")
def trainer_directory():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trainer")
    trainers = cursor.fetchall()
    conn.close()
    return render_template("trainer_directory.html", data=trainers)

@app.route("/trainer/modify", methods=["GET", "POST"])
def trainer_modify():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        cursor.execute("""
            UPDATE trainer
            SET trainer_name=?, specialization=?, phone=?, email=?
            WHERE trainer_id=?
        """, (
            request.form["trainer_name"],
            request.form["specialization"],
            request.form["phone"],
            request.form["email"],
            request.form["id"]
        ))
        conn.commit()
        conn.close()
        return redirect("/trainer/directory")

    tid = request.args.get("id")
    cursor.execute("SELECT * FROM trainer WHERE trainer_id=?", (tid,))
    trainer = cursor.fetchone()
    conn.close()
    return render_template("trainer_modify.html", t=trainer)

@app.route("/trainer/remove", methods=["POST"])
def trainer_remove():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trainer WHERE trainer_id=?", (request.form["id"],))
    conn.commit()
    conn.close()
    return redirect("/trainer/directory")

# ====================================================
# ====================== PLANS =======================
# ====================================================
@app.route("/plan/enroll", methods=["GET", "POST"])
def plan_enroll():
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO plan (plan_name, duration, fee)
            VALUES (?,?,?)
        """, (
            request.form["plan_name"],
            request.form["duration"],
            request.form["fee"]
        ))
        conn.commit()
        conn.close()
        return redirect("/plan/overview")
    return render_template("plan_enroll.html")

@app.route("/plan/overview")
def plan_overview():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plan")
    plans = cursor.fetchall()
    conn.close()
    return render_template("plan_overview.html", data=plans)

@app.route("/plan/modify", methods=["GET", "POST"])
def plan_modify():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        cursor.execute("""
            UPDATE plan
            SET plan_name=?, duration=?, fee=?
            WHERE plan_id=?
        """, (
            request.form["plan_name"],
            request.form["duration"],
            request.form["fee"],
            request.form["id"]
        ))
        conn.commit()
        conn.close()
        return redirect("/plan/overview")

    pid = request.args.get("id")
    cursor.execute("SELECT * FROM plan WHERE plan_id=?", (pid,))
    plan = cursor.fetchone()
    conn.close()
    return render_template("plan_modify.html", p=plan)

@app.route("/plan/remove", methods=["POST"])
def plan_remove():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM plan WHERE plan_id=?", (request.form["id"],))
    conn.commit()
    conn.close()
    return redirect("/plan/overview")

# ====================================================
# ===================== PAYMENTS =====================
# ====================================================
@app.route('/payment/entry', methods=['GET', 'POST'])
def payment_entry():
    conn = get_db_connection()
    if request.method == 'POST':
        member_id = request.form.get("member_id")
        amount = request.form.get("amount")
        payment_date = request.form.get("payment_date")

        if member_id and amount:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO billing (member_id, amount, bill_date)
                VALUES (?, ?, ?)
            """, (member_id, amount, payment_date))
            conn.commit()
            conn.close()
            return redirect("/payment/history")
        else:
            conn.close()
            return "Error: Missing required fields", 400

    cursor = conn.cursor()
    cursor.execute("SELECT member_id, member_name FROM member")
    members = cursor.fetchall()
    conn.close()
    return render_template("payment_entry.html", members=members)

@app.route("/payment/history")
def payment_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.billing_id AS payment_id, m.member_name, b.amount, b.bill_date AS payment_date
        FROM billing b
        JOIN member m ON b.member_id = m.member_id
    """)
    payments = cursor.fetchall()
    conn.close()
    return render_template("payment_history.html", data=payments)

@app.route("/payment/modify", methods=["GET", "POST"])
def payment_modify():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        cursor.execute("""
            UPDATE billing
            SET amount=?, bill_date=?
            WHERE billing_id=?
        """, (
            request.form["amount"],
            request.form["payment_date"],
            request.form["id"]
        ))
        conn.commit()
        conn.close()
        return redirect("/payment/history")

    pid = request.args.get("id")
    cursor.execute("""
        SELECT billing_id AS payment_id, amount, bill_date AS payment_date 
        FROM billing WHERE billing_id=?
    """, (pid,))
    payment = cursor.fetchone()
    conn.close()
    return render_template("payment_modify.html", p=payment)

@app.route("/payment/remove", methods=["POST"])
def payment_remove():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM billing WHERE billing_id=?", (request.form["id"],))
    conn.commit()
    conn.close()
    return redirect("/payment/history")

# ====================================================
# ====================== SEARCH ======================
# ====================================================
@app.route("/member/lookup", methods=["GET", "POST"])
def member_lookup():
    data = None
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, t.trainer_name
            FROM member m
            LEFT JOIN trainer t ON m.trainer_id = t.trainer_id
            WHERE m.member_name LIKE ?
        """, ('%' + request.form["name"] + '%',))
        data = cursor.fetchall()
        conn.close()
    return render_template("member_lookup.html", data=data)

# ====================================================
# ===================== REPORTS ======================
# ====================================================
@app.route("/analytics")
def analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) AS total_payments,
            SUM(amount) AS total_revenue,
            AVG(amount) AS avg_payment,
            MIN(amount) AS min_payment,
            MAX(amount) AS max_payment
        FROM billing
    """)
    agg = dict(cursor.fetchone())
    conn.close()

    return render_template("analytics.html", agg=agg)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)