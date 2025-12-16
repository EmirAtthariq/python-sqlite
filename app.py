from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import session, abort
import sqlite3
import secrets
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_urlsafe(16)
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db.session.execute(
            text("SELECT id FROM user WHERE username=:u AND password=:p"),
            {'u': username, 'p': password}
        ).fetchone()

        if user:
            session['user_id'] = user.id
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return "Login gagal", 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/add', methods=['POST'])
def add_student():
    if 'user_id' not in session:
        abort(401)
    name = request.form['name']
    if not re.match(r'^[a-zA-Z0-9\s]+$', name):
        abort(400)
    age = request.form['age']
    if not re.match(r'^[a-zA-Z0-9\s]+$', age):
        abort(400)
    grade = request.form['grade']
    if not re.match(r'^[a-zA-Z0-9\s]+$', grade):
        abort(400)
    

    connection = sqlite3.connect('instance/students.db')
    cursor = connection.cursor()

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()
    query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    cursor.execute(query)
    connection.commit()
    connection.close()
    return redirect(url_for('index'))


@app.route('/delete/<string:id>') 
def delete_student(id):
    if 'user_id' not in session:
        abort(401)
    # RAW Query
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if 'user_id' not in session:
        abort(401)
    if request.method == 'POST':
        name = request.form['name']
        if not re.match(r'^[a-zA-Z0-9\s]+$', name):
            abort(400)
        age = request.form['age']
        if not re.match(r'^[a-zA-Z0-9\s]+$', age):
            abort(400)
        grade = request.form['grade']
        if not re.match(r'^[a-zA-Z0-9\s]+$', grade):
            abort(400)    
            
        # RAW Query
        db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

