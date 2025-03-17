# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request
from .utils.database.database  import database
from werkzeug.datastructures import ImmutableMultiDict
from pprint import pprint
import json
import random
db = database()

@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
def home():
	# assign random fun fact
	x     = random.choice(['I have never lost fight to a hippo.','I can wiggle my ears','I memorized 10 digts of pi'])
	return render_template('home.html', fun_fact = x)

@app.route('/resume')
def resume():
	resume_data = db.getResumeData()
	pprint(resume_data)
	return render_template('resume.html', resume_data = resume_data)

@app.route('/processfeedback', methods = ['GET','POST'])
def processfeedback():
    if request.method == 'POST':
        # 1) Grab the form data
        name = request.form.get('name')
        email = request.form.get('email')
        comment = request.form.get('comment')

        # 2) Insert the feedback into the database
        db.insertRows(
            table='feedback',
            columns=['name', 'email', 'comment'],
            parameters=[[name, email, comment]]
        )

    # 3) Retrieve all feedback to display (whether GET or POST)
    all_feedback = db.query("SELECT * FROM feedback")

    # 4) Render a template that shows all feedback
    return render_template('processfeedback.html', feedback=all_feedback)

@app.route('/projects')
def projects():
	return render_template('projects.html')

@app.route('/piano')
def  piano():
	return render_template('piano.html')