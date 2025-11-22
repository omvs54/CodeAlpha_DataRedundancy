from flask import Flask, request, render_template, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('data.db')
    conn.execute('CREATE TABLE IF NOT EXISTS entries (data TEXT UNIQUE)')
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
    data = request.form['data']
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM entries WHERE data=?', (data,))
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO entries (data) VALUES (?)', (data,))
        conn.commit()
        message = "Data added successfully!"
    else:
        message = "Duplicate data detected!"
    conn.close()
    return render_template('index.html', message=message)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)