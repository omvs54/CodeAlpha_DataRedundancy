from flask import Flask, request, render_template, redirect, send_file
import sqlite3
import csv
import hashlib

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serial_number INTEGER,
            data TEXT NOT NULL,
            hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
    data = request.form['data']
    hash = hashlib.sha256(data.encode()).hexdigest()

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM entries WHERE hash=?', (hash,))
    if cursor.fetchone()[0] == 0:
        cursor.execute('SELECT MAX(serial_number) FROM entries')
        max_serial = cursor.fetchone()[0] or 0
        new_serial = max_serial + 1
        cursor.execute('INSERT INTO entries (serial_number, data, hash) VALUES (?, ?, ?)', (new_serial, data, hash))
        conn.commit()
        message = "✅ Data added successfully!"
    else:
        message = "⚠️ Duplicate data detected!"
    conn.close()
    return render_template('index.html', message=message)

@app.route('/view')
def view():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, serial_number, data FROM entries ORDER BY serial_number')
    rows = cursor.fetchall()
    conn.close()
    return render_template('view.html', rows=rows)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM entries WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/view')

@app.route('/export')
def export():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT serial_number, data FROM entries ORDER BY serial_number')
    rows = cursor.fetchall()
    conn.close()
    with open('export.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Serial Number', 'Data'])
        writer.writerows(rows)
    return send_file('export.csv', as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)