from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

# Required for login session
app.secret_key = "library_management_secret_key"


# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # Books table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT DEFAULT 'Available'
        )
    """)

    # If you already created the old books table,
    # this checks whether "status" exists.
    cursor.execute("PRAGMA table_info(books)")
    columns = [column[1] for column in cursor.fetchall()]

    if "status" not in columns:
        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN status TEXT DEFAULT 'Available'
        """)

    # Users table for login
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Create default admin account
    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        ("admin",)
    )

    user = cursor.fetchone()

    if user is None:
        cursor.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            ("admin", "admin123")
        )

    conn.commit()
    conn.close()


init_db()


# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/')

        else:
            error = "Invalid username or password"

    return render_template(
        "login.html",
        error=error
    )


# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')


# ---------------- HOME PAGE ----------------

@app.route('/')
def index():

    # User must login first
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books")

    books = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        books=books
    )


# ---------------- ADD BOOK ----------------

@app.route('/add', methods=['GET', 'POST'])
def add_book():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        title = request.form['title']
        author = request.form['author']

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO books(title, author, status)
            VALUES (?, ?, ?)
            """,
            (title, author, "Available")
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("add_book.html")


# ---------------- DELETE BOOK ----------------

@app.route('/delete/<int:id>')
def delete_book(id):

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM books WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


# ---------------- UPDATE BOOK ----------------

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_book(id):

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    if request.method == 'POST':

        title = request.form['title']
        author = request.form['author']

        cursor.execute(
            """
            UPDATE books
            SET title=?, author=?
            WHERE id=?
            """,
            (title, author, id)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    cursor.execute(
        "SELECT * FROM books WHERE id=?",
        (id,)
    )

    book = cursor.fetchone()

    conn.close()

    return render_template(
        "update_book.html",
        book=book
    )


# ---------------- SEARCH BOOK ----------------

@app.route('/search', methods=['GET', 'POST'])
def search_book():

    if 'user' not in session:
        return redirect('/login')

    books = []
    keyword = ""

    if request.method == 'POST':

        keyword = request.form['keyword']

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM books
            WHERE title LIKE ?
            OR author LIKE ?
            """,
            (
                '%' + keyword + '%',
                '%' + keyword + '%'
            )
        )

        books = cursor.fetchall()

        conn.close()

    return render_template(
        "search_book.html",
        books=books,
        keyword=keyword
    )


# ---------------- ISSUE BOOK ----------------

@app.route('/issue/<int:id>')
def issue_book(id):

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE books
        SET status='Issued'
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


# ---------------- RETURN BOOK ----------------

@app.route('/return/<int:id>')
def return_book(id):

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE books
        SET status='Available'
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


# ---------------- RUN APPLICATION ----------------

if __name__ == '__main__':
    app.run(debug=True)