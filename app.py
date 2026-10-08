from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route('/')
def index():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    conn.close()

    return render_template("index.html", books=books)


@app.route('/add', methods=['GET', 'POST'])
def add_book():

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO books(title, author) VALUES (?, ?)",
            (title, author)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("add_book.html")


@app.route('/delete/<int:id>')
def delete_book(id):

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM books WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)