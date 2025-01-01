from flask import Flask, render_template, request, redirect, url_for, jsonify
import qrcode
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Paths for the database files
USERS_DB = 'database/users.csv'
CLASSES_DB = 'database/classes.csv'
ATTENDANCE_DB = 'database/attendance.csv'

# Ensure the database directory exists
os.makedirs('database', exist_ok=True)

# Initialize CSV files if they don't exist
for file in [USERS_DB, CLASSES_DB, ATTENDANCE_DB]:
    if not os.path.exists(file):
        pd.DataFrame().to_csv(file, index=False)

# Helper functions for reading and writing CSV files
def read_csv(file):
    return pd.read_csv(file) if os.path.getsize(file) > 0 else pd.DataFrame()

def write_csv(df, file):
    df.to_csv(file, index=False)

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# Teacher Registration
@app.route('/teacher/register', methods=['GET', 'POST'])
def teacher_register():
    if request.method == 'POST':
        data = request.form
        teachers = read_csv(USERS_DB)
        import pandas as pd

        # Assuming teachers is a DataFrame
        teachers = pd.DataFrame(columns=['username', 'password'])

        # New teacher data as a dictionary
        new_teacher = {'username': 'new_teacher', 'password': 'password123'}

        # Convert the dictionary into a DataFrame
        new_teacher_df = pd.DataFrame([new_teacher])

        # Now, concatenate the DataFrames
        teachers = pd.concat([teachers, new_teacher_df], ignore_index=True)

        # Print the updated teachers DataFrame
        print(teachers)

        write_csv(teachers, USERS_DB)
        return redirect(url_for('index'))
    return render_template('teacher/register.html')

# Create Class
@app.route('/teacher/create_class', methods=['GET', 'POST'])
def create_class():
    if request.method == 'POST':
        data = request.form
        classes = read_csv(CLASSES_DB)
        new_class = {
            'class_name': data['class_name'],
            'teacher': data['teacher']
        }
        classes = classes.append(new_class, ignore_index=True)
        write_csv(classes, CLASSES_DB)
        return redirect(url_for('teacher_dashboard'))
    return render_template('teacher/create_class.html')

# Teacher Dashboard
@app.route('/teacher/dashboard')
def teacher_dashboard():
    classes = read_csv(CLASSES_DB)
    return render_template('teacher/dashboard.html', classes=classes)

# Home Route
@app.route('/choose-signup')
def signup():
    return render_template('../choose_signup.html')

# Generate QR Code for Attendance
@app.route('/teacher/generate_qr', methods=['GET', 'POST'])
def generate_qr():
    if request.method == 'POST':
        data = request.form
        class_name = data['class_name']
        expiration = datetime.now() + timedelta(minutes=5)
        qr_data = f"{class_name}|{expiration.strftime('%Y-%m-%d %H:%M:%S')}"
        qr_code = qrcode.make(qr_data)
        qr_code_path = f"static/qrcodes/{class_name}.png"
        qr_code.save(qr_code_path)
        return render_template('teacher/generate_qr.html', qr_code=qr_code_path, class_name=class_name, expiration=expiration)
    return render_template('teacher/generate_qr.html')

# Approve Students for Class
@app.route('/teacher/approve_students', methods=['GET', 'POST'])
def approve_students():
    students = read_csv(USERS_DB)
    if request.method == 'POST':
        student_id = request.form['student_id']
        students.loc[students['id'] == student_id, 'approved'] = True
        write_csv(students, USERS_DB)
        return redirect(url_for('approve_students'))
    return render_template('teacher/approve_students.html', students=students)

# Student Registration
@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        data = request.form
        students = read_csv(USERS_DB)
        new_student = {
            'username': data['username'],
            'password': data['password'],
            'role': 'student',
            'approved': False
        }
        students = pd.concat([students, pd.DataFrame([new_student])], ignore_index=True)
        write_csv(students, USERS_DB)
        return redirect(url_for('index'))
    return render_template('student/register.html')

# Scan QR Code
@app.route('/student/scan_qr', methods=['GET', 'POST'])
def scan_qr():
    qr_data = request.form['qr_data']
    class_name, expiration = qr_data.split('|')
    if datetime.now() > datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S'):
        return jsonify({'status': 'failed', 'message': 'QR Code expired'})
    attendance = read_csv(ATTENDANCE_DB)
    new_record = {
        'class_name': class_name,
        'student': request.form['student'],
        'timestamp': datetime.now()
    }
    attendance = attendance.append(new_record, ignore_index=True)
    write_csv(attendance, ATTENDANCE_DB)
    return jsonify({'status': 'success', 'message': 'Attendance marked'})

if __name__ == '__main__':
    app.run(debug=True)
