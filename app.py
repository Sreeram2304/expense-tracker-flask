from flask import Flask, render_template, request
import sqlite3
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,get_jwt_identity
)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "expense-secret-key"
jwt = JWTManager(app)

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            type TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- WEB ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        t_type = request.form["type"]

        cursor.execute(
            "INSERT INTO transactions (amount, category, type) VALUES (?, ?, ?)",
            (amount, category, t_type)
        )
        conn.commit()

    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()
    conn.close()

    return render_template("index.html", data=data)

# ---------------- JWT LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if data["username"] == "admin" and data["password"] == "admin123":
        token = create_access_token(identity="admin")
        return {"access_token": token}
    return {"msg": "Invalid credentials"}, 401

# ---------------- REST API ----------------
@app.route("/api/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "amount": r[1],
            "category": r[2],
            "type": r[3]
        })

    return {"transactions": result}

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10000)

