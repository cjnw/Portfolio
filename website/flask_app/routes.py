# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import send_from_directory
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
from flask_app.utils.database.database import get_resume_data


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
     ## This function is used to get the user from the session
	return session['email'] if 'email' in session else 'Unknown'

def getDecryptedUser():
    if 'email' in session:
        try:
            return db.reversibleEncrypt('decrypt', session['email'])
        except Exception:
            return session['email']
    return 'Unknown'

# @app.route('/login')
# def login():
#     # Reset login failure count on each new attempt
#     session.pop('failure_count', None)

#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     # Clear the session data
# 	session.pop('email', default=None)
# 	return redirect('/')

@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
    # Check if the request is a POST request
    email = request.form.get('email')
    password = request.form.get('password')
    status = db.authenticate(email, password)
    if status.get('success'):
        session['email'] = db.reversibleEncrypt('encrypt', email)
        session.pop('failure_count', None)
    else:
        # Increment failure count and return it with error status
        failure = session.get('failure_count', 0) + 1
        session['failure_count'] = failure
        status['fail_count'] = failure
    return json.dumps(status)


#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@socketio.on('joined', namespace='/chat')
def joined(message):
    # Join the room
    join_room('main')
    user = getDecryptedUser() if 'email' in session else 'Guest'
    msg = f"{user} has entered the room."
    if user.lower() == 'guest@email.com':
        style = "width:100%; color:black; text-align:left;"
    elif "owner" in user.lower():
        style = "width:100%; color:blue; text-align:right;"
    else:
        style = "width:100%; color:grey; text-align:left;"
    emit('status', {'msg': msg, 'style': style}, room='main')



#######################################################################################
# OTHER
#######################################################################################
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
	resume_data = get_resume_data()
	pprint(resume_data)
	return render_template('experience.html', resume_data = resume_data)

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

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

@app.context_processor
def inject_user():
    # This function is used to inject the user into the template context
    if 'email' in session:
        try:
            decrypted_email = db.reversibleEncrypt('decrypt', session['email'])
            return dict(user=decrypted_email)
        except Exception:
            return dict(user=None)
    else:
         return dict(user=None)
    

@socketio.on('send_message', namespace='/chat')
def handle_message(data):
    # Determine style based on sender
    user = getDecryptedUser() if 'email' in session else 'Guest'
    if "owner" in user.lower():
        style = "color:blue; text-align:right;"
    else:
        style = "color:grey; text-align:left;"
    msg = f"{user}: {data['msg']}"
    emit('message', {'msg': msg, 'style': style}, broadcast=True, namespace='/chat')

@socketio.on('left', namespace='/chat')
def left(message):
    # Leave the room
    user = getDecryptedUser() if 'email' in session else 'Guest'
    msg = f"{user} has left the room."
    if "owner" in user.lower():
        style = "width:100%; color:blue; text-align:right;"
    else:
        style = "width:100%; color:grey; text-align:left;"
    emit('status', {'msg': msg, 'style': style}, broadcast=True, namespace='/chat')