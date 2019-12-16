from flask import render_template

from app import app

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

