from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "liquor.db")

# -------------------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------
def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS liquors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        image TEXT,
        stock INTEGER,
        category_id INTEGER,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    )
    """)

    # Add new columns if not exist
    try:
        conn.execute("ALTER TABLE liquors ADD COLUMN alcohol_content REAL")
    except:
        pass
    try:
        conn.execute("ALTER TABLE liquors ADD COLUMN volume INTEGER")
    except:
        pass

    # default categories
    default = ["Whiskey", "Wine", "Gin", "Vodka", "Craft Beer"]
    for d in default:
        try:
            conn.execute("INSERT INTO categories (name) VALUES (?)", (d,))
        except:
            pass

    conn.commit()
    conn.close()

init_db()

# -------------------------
@app.route("/")
def index():
    conn = get_db()
    liquors = conn.execute("""
        SELECT liquors.*, categories.name as category_name
        FROM liquors
        LEFT JOIN categories ON liquors.category_id = categories.id
        ORDER BY liquors.id DESC
    """).fetchall()
    conn.close()
    return render_template("cakemenu.html", liquors=liquors)

# -------------------------
@app.route("/append", methods=["GET", "POST"])
def append():
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories").fetchall()

    if request.method == "POST":
        name = request.form["name"]
        image = request.form["image"]

        try:
            price = float(request.form["price"])
            stock = int(request.form["stock"])
            alcohol = float(request.form["alcohol"])
            volume = int(request.form["volume"])
        except:
            return "❌ กรอกข้อมูลตัวเลขผิด"

        category_id = request.form.get("category")

        conn.execute("""
        INSERT INTO liquors
        (name, price, image, stock, category_id, alcohol_content, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, price, image, stock, category_id, alcohol, volume))

        conn.commit()
        conn.close()
        return redirect("/")

    conn.close()
    return render_template("append.html", categories=categories, liquor=None)

# -------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories").fetchall()

    if request.method == "POST":
        try:
            price = float(request.form["price"])
            stock = int(request.form["stock"])
            alcohol = float(request.form["alcohol"])
            volume = int(request.form["volume"])
        except:
            return "❌ กรอกข้อมูลผิด"

        conn.execute("""
        UPDATE liquors SET
        name=?, price=?, image=?, stock=?, category_id=?, alcohol_content=?, volume=?
        WHERE id=?
        """, (
            request.form["name"],
            price,
            request.form["image"],
            stock,
            request.form["category"],
            alcohol,
            volume,
            id
        ))

        conn.commit()
        conn.close()
        return redirect("/")

    liquor = conn.execute("SELECT * FROM liquors WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", liquor=liquor, categories=categories)

# -------------------------
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM liquors WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

# -------------------------
if __name__ == "__main__":
    app.run(debug=True)