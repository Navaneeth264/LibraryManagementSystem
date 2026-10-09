
import os
import sqlite3
from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, session, abort, url_for
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Set these environment variables on Render before deployment.
app.secret_key = os.environ.get("SECRET_KEY", "change-this-local-secret-key")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin").strip()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT DEFAULT 'Available'
        )
    """)

    # Support existing books tables.
    cursor.execute("PRAGMA table_info(books)")
    book_columns = [row["name"] for row in cursor.fetchall()]

    if "status" not in book_columns:
        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN status TEXT DEFAULT 'Available'
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Add roles to an existing users table without deleting accounts.
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [row["name"] for row in cursor.fetchall()]

    if "role" not in user_columns:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN role TEXT NOT NULL DEFAULT 'user'
        """)

    # Ensure the configured admin account exists.
    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (ADMIN_USERNAME,)
    )
    admin = cursor.fetchone()

    if admin is None:
        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, 'admin')
        """, (
            ADMIN_USERNAME,
            generate_password_hash(ADMIN_PASSWORD)
        ))
    else:
        # Promote only the explicitly configured admin account.
        cursor.execute(
            "UPDATE users SET role = 'admin' WHERE username = ?",
            (ADMIN_USERNAME,)
        )

    conn.commit()
    conn.close()


init_db()


# ---------------- ACCESS CONTROL ----------------

def login_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)
    return wrapper


def admin_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))

        if session.get("role") != "admin":
            abort(403)

        return view_function(*args, **kwargs)
    return wrapper


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user:
            stored_password = user["password"]

            # Support older accounts with plain-text passwords,
            # then migrate their password to a secure hash.
            password_ok = False

            if stored_password.startswith(("scrypt:", "pbkdf2:")):
                try:
                    password_ok = check_password_hash(
                        stored_password, password
                    )
                except (ValueError, TypeError):
                    password_ok = False
            else:
                password_ok = (stored_password == password)

                if password_ok:
                    conn.execute(
                        "UPDATE users SET password = ? WHERE id = ?",
                        (generate_password_hash(password), user["id"])
                    )
                    conn.commit()

            if password_ok:
                session.clear()
                session["user_id"] = user["id"]
                session["user"] = user["username"]
                session["role"] = user["role"]
                conn.close()
                return redirect(url_for("index"))

        conn.close()
        error = "Invalid username or password."

    return render_template("login.html", error=error)


# ---------------- REGISTRATION ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password or not confirm_password:
            error = "Please fill in all fields."
        elif len(username) < 3:
            error = "Username must contain at least 3 characters."
        elif len(password) < 8:
            error = "Password must contain at least 8 characters."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif username == ADMIN_USERNAME:
            error = "This username is reserved."
        else:
            conn = get_db()
            try:
                conn.execute("""
                    INSERT INTO users (username, password, role)
                    VALUES (?, ?, 'user')
                """, (
                    username,
                    generate_password_hash(password)
                ))
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                conn.close()
                error = "Username already exists."

    return render_template("register.html", error=error)


# ---------------- LOGOUT ----------------

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- HOME PAGE ----------------

@app.route("/")
@login_required
def index():
    conn = get_db()
    books = conn.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
    conn.close()

    return render_template(
        "index.html",
        books=books,
        role=session.get("role"),
        username=session.get("user")
    )


# ---------------- ADD BOOK ----------------

@app.route("/add", methods=["GET", "POST"])
@admin_required
def add_book():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()

        if title and author:
            conn = get_db()
            conn.execute("""
                INSERT INTO books (title, author, status)
                VALUES (?, ?, 'Available')
            """, (title, author))
            conn.commit()
            conn.close()
            return redirect(url_for("index"))

    return render_template("add_book.html")


# ---------------- DELETE BOOK ----------------

@app.route("/delete/<int:id>", methods=["POST"])
@admin_required
def delete_book(id):
    conn = get_db()
    conn.execute("DELETE FROM books WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


# ---------------- UPDATE BOOK ----------------

@app.route("/update/<int:id>", methods=["GET", "POST"])
@admin_required
def update_book(id):
    conn = get_db()
    book = conn.execute(
        "SELECT * FROM books WHERE id = ?", (id,)
    ).fetchone()

    if book is None:
        conn.close()
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()

        if title and author:
            conn.execute("""
                UPDATE books
                SET title = ?, author = ?
                WHERE id = ?
            """, (title, author, id))
            conn.commit()
            conn.close()
            return redirect(url_for("index"))

    conn.close()
    return render_template("update_book.html", book=book)


# ---------------- SEARCH BOOK ----------------

@app.route("/search", methods=["GET", "POST"])
@login_required
def search_book():
    books = []
    keyword = request.form.get(
        "keyword", request.args.get("keyword", "")
    ).strip()

    if keyword:
        conn = get_db()
        books = conn.execute("""
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ?
            ORDER BY title
        """, (f"%{keyword}%", f"%{keyword}%")).fetchall()
        conn.close()

    return render_template(
        "search_book.html",
        books=books,
        keyword=keyword,
        role=session.get("role")
    )


# ---------------- ISSUE BOOK ----------------

@app.route("/issue/<int:id>", methods=["POST"])
@admin_required
def issue_book(id):
    conn = get_db()
    conn.execute("""
        UPDATE books SET status = 'Issued'
        WHERE id = ? AND status = 'Available'
    """, (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


# ---------------- RETURN BOOK ----------------

@app.route("/return/<int:id>", methods=["POST"])
@admin_required
def return_book(id):
    conn = get_db()
    conn.execute("""
        UPDATE books SET status = 'Available'
        WHERE id = ? AND status = 'Issued'
    """, (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


# ---------------- ERROR PAGE ----------------

@app.errorhandler(403)
def forbidden(error):
    return (
        "<h1>403 - Access Denied</h1>"
        "<p>Only the administrator can perform this action.</p>"
        '<p><a href="/">Back to Library</a></p>',
        403
    )


if __name__ == "__main__":
    app.run(debug=True)