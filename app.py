from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL

import qrcode
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'database_name'
mysql = MySQL(app)

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# Teacher Registration
@app.route('/teacher/register', methods=['GET', 'POST'])
def teacher_register():
    if request.method == 'POST':
        data = request.form
        print (data)
        #return redirect(url_for('index'))
    return render_template('teacher/register.html')

if __name__ == '__main__':
    app.run(debug=True)
