from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for session management

# Function to connect to the database
def connect_db():
    conn = sqlite3.connect('student.db')
    return conn

# Function to create the 'Students' table
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        batch TEXT NOT NULL,
        academic_performance INTEGER NOT NULL,
        hackathon_participation INTEGER NOT NULL,
        papers_presented INTEGER NOT NULL,
        overall_score REAL
    )''')
    conn.commit()
    conn.close()

# Create the 'Students' table
create_table()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_student():
    name = request.form['studentName']
    batch = request.form['batch']
    academic = request.form['academicPerformance']
    hackathons = request.form['hackathons']
    papers = request.form['papers']

    # Validate input data
    if not name or not batch or not academic.isdigit() or not hackathons.isdigit() or not papers.isdigit():
        flash('Invalid input data. Please ensure all fields are filled correctly.')
        return redirect(url_for('home'))

    academic = int(academic)
    hackathons = int(hackathons)
    papers = int(papers)

    try:
        # Add data to the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Students (name, batch, academic_performance, hackathon_participation, papers_presented) VALUES (?, ?, ?, ?, ?)', 
                       (name, batch, academic, hackathons, papers))
        conn.commit()

        # Fetch all student data for ML training
        data = pd.read_sql_query('SELECT * FROM Students', conn)

        # Input features (X) and labels (y)
        X = data[['academic_performance', 'hackathon_participation', 'papers_presented']]
        y = data['overall_score'].fillna(0)  # Using existing overall scores or filling with zero

        # Split data for training and testing
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the Linear Regression model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Evaluate the model
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        print(f'Model R^2 Score: {r2:.2f}')

        # Predict the overall score for the current student
        current_student = pd.DataFrame({
            'academic_performance': [academic],
            'hackathon_participation': [hackathons],
            'papers_presented': [papers]
        })

        overall_score = model.predict(current_student)[0]

        # Update the predicted overall score for the student
        cursor.execute('UPDATE Students SET overall_score = ? WHERE name = ? AND batch = ?', (overall_score, name, batch))
        conn.commit()

    except Exception as e:
        flash(f'An error occurred: {e}')
        return redirect(url_for('home'))
    finally:
        conn.close()

    flash(f'Student {name} submitted with predicted overall score: {overall_score:.2f}')
    return redirect(url_for('home'))

@app.route('/top_students')
def top_students():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name, overall_score FROM Students ORDER BY overall_score DESC LIMIT 3')
    top_students = cursor.fetchall()
    conn.close()
    return render_template('top_students.html', top_students=top_students)

if __name__ == '__main__':
    app.run(debug=True)