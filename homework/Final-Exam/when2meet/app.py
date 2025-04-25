from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from database import Database
import sqlite3

app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['DATABASE_PATH'] = os.path.join(app.instance_path, 'when2meet.db')

# Initialize database
if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)
db = Database(app)

# Only initialize database if it doesn't exist
if not os.path.exists(app.config['DATABASE_PATH']):
    with app.app_context():
        db.init_db()

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

class User(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    user_data = db.execute_query_one('get_user_by_id', (user_id,))
    if user_data:
        return User(user_data['id'], user_data['email'], user_data['password_hash'])
    return None


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Get created events
        created_events = db.execute_query('get_user_created_events', (current_user.id,))
        created_events = [dict(event) for event in created_events]
        for event in created_events:
            event['start_date'] = datetime.strptime(event['start_date'], '%Y-%m-%d').date()
            event['end_date'] = datetime.strptime(event['end_date'], '%Y-%m-%d').date()
            event['start_time'] = datetime.strptime(event['start_time'], '%H:%M').time()
            event['end_time'] = datetime.strptime(event['end_time'], '%H:%M').time()
        
        # Get invited events
        invited_events = db.execute_query('get_user_invited_events', (current_user.id,))
        invited_events = [dict(event) for event in invited_events]
        for event in invited_events:
            event['start_date'] = datetime.strptime(event['start_date'], '%Y-%m-%d').date()
            event['end_date'] = datetime.strptime(event['end_date'], '%Y-%m-%d').date()
            event['start_time'] = datetime.strptime(event['start_time'], '%H:%M').time()
            event['end_time'] = datetime.strptime(event['end_time'], '%H:%M').time()
        
        return render_template('dashboard.html',
                             created_events=created_events,
                             invited_events=invited_events)
                             
    except Exception as e:
        print(f"Error loading dashboard: {str(e)}")
        flash('Error loading dashboard', 'error')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Attempting login for email: {email}")
        user = db.execute_query_one('get_user_by_email', (email,))
        
        if user:
            print(f"User found: {user['email']}")
            print(f"Password hash: {user['password_hash']}")
            if check_password_hash(user['password_hash'], password):
                print("Password check successful")
                user_obj = User(user['id'], user['email'], user['password_hash'])
                login_user(user_obj)
                return redirect(url_for('dashboard'))
            else:
                print("Password check failed")
        else:
            print("No user found with that email")
        
        flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        print(f"Attempting registration for email: {email}")
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        
        try:
            # Create new user
            password_hash = generate_password_hash(password)
            print(f"Generated password hash: {password_hash}")
            
            # Execute the query directly to see any errors
            db_conn = db.get_db()
            cursor = db_conn.cursor()
            try:
                cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash))
                db_conn.commit()
                print("User created successfully")
                
                # Get the new user's ID
                user = db.execute_query_one('get_user_by_email', (email,))
                if user:
                    print(f"Verified user exists: {user['email']}")
                    # Process any pending invites
                    process_pending_invites(user['id'], email)
                else:
                    print("ERROR: User not found after creation")
                
                flash('Registration successful! Please login.')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                print("Email already registered")
                flash('Email already registered. Please use a different email or login.')
                return redirect(url_for('register'))
            except Exception as e:
                print(f"Registration error: {e}")
                raise
            finally:
                db_conn.close()
        except Exception as e:
            print(f"Registration error: {e}")
            flash('Registration failed. Please try again.')
            return redirect(url_for('register'))
    
    return render_template('register.html')

def process_pending_invites(user_id, email):
    """Process any pending invites for a newly registered user."""
    try:
        conn = db.get_db()
        cursor = conn.cursor()
        
        # Get all pending invites for this email
        cursor.execute("""
            SELECT pi.event_id, pi.email
            FROM pending_invites pi
            WHERE pi.email = ?
        """, (email,))
        
        pending_invites = cursor.fetchall()
        
        for invite in pending_invites:
            # Create an actual invite
            cursor.execute("""
                INSERT INTO event_invites (event_id, user_id, email, status)
                VALUES (?, ?, ?, 'pending')
            """, (invite['event_id'], user_id, email))
            
            # Remove from pending invites
            cursor.execute("""
                DELETE FROM pending_invites
                WHERE event_id = ? AND email = ?
            """, (invite['event_id'], email))
        
        conn.commit()
        print(f"Processed {len(pending_invites)} pending invites for user {user_id}")
        
    except Exception as e:
        print(f"Error processing pending invites: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

@app.route('/create_event', methods=['POST'])
@login_required
def create_event():
    try:
        event_name = request.form['event_name']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        
        # Convert time objects to strings for database storage
        start_time_str = start_time.strftime('%H:%M')
        end_time_str = end_time.strftime('%H:%M')
        
        print(f"Creating event: {event_name} for user {current_user.id}")
        print(f"Dates: {start_date} to {end_date}")
        print(f"Times: {start_time_str} to {end_time_str}")
        
        # Get database connection
        conn = db.get_db()
        cursor = conn.cursor()
        
        try:
            # Create the event
            cursor.execute("""
                INSERT INTO events (name, start_date, end_date, start_time, end_time, creator_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (event_name, start_date, end_date, start_time_str, end_time_str, current_user.id))
            
            # Get the event ID
            event_id = cursor.lastrowid
            print(f"Created event with ID: {event_id}")
            
            # Add creator as a participant with 'accepted' status
            cursor.execute("""
                INSERT INTO event_invites (event_id, user_id, email, status)
                VALUES (?, ?, ?, 'accepted')
            """, (event_id, current_user.id, current_user.email))
            print(f"Added creator {current_user.id} as participant for event {event_id}")
            
            # Handle invitees if provided
            invitees = request.form.get('invitees', '').strip()
            if invitees:
                invitee_emails = [email.strip() for email in invitees.split(',')]
                for email in invitee_emails:
                    if email:  # Skip empty strings
                        print(f"Processing invite for email: {email}")
                        # Get user_id for the email
                        user = db.execute_query_one('get_user_by_email', (email,))
                        if user:
                            print(f"Creating invite for registered user {user['id']}")
                            cursor.execute("""
                                INSERT INTO event_invites (event_id, user_id, email, status)
                                VALUES (?, ?, ?, 'pending')
                            """, (event_id, user['id'], email))
                        else:
                            print(f"Creating pending invite for unregistered email: {email}")
                            cursor.execute("""
                                INSERT INTO pending_invites (event_id, email)
                                VALUES (?, ?)
                            """, (event_id, email))
            
            # Commit the transaction
            conn.commit()
            
            flash('Event created successfully!')
            return redirect(url_for('event', event_id=event_id))
            
        except Exception as e:
            conn.rollback()
            raise e
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error creating event: {str(e)}")
        flash(f'Error creating event: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/event/<int:event_id>')
@login_required
def event(event_id):
    try:
        # Get the event
        event = db.execute_query_one('get_event_by_id', (event_id,))
        if not event:
            flash('Event not found', 'error')
            return redirect(url_for('dashboard'))
            
        # Convert to dictionary
        event = dict(event)
        
        # Get creator's email
        creator = db.execute_query_one('get_user_by_id', (event['creator_id'],))
        if creator:
            event['creator_email'] = creator['email']
        else:
            event['creator_email'] = 'Unknown'
        
        # Check if user is invited or is the creator
        if event['creator_id'] != current_user.id:
            invite = db.execute_query_one('get_invite', (event_id, current_user.id))
            if not invite:
                flash('You are not invited to this event', 'error')
                return redirect(url_for('dashboard'))
        
        # Get all invites for this event
        invites = db.execute_query('get_event_invites', (event_id,))
        invites = [dict(invite) for invite in invites]
        
        # Get availability data
        availability = db.execute_query('get_event_availability', (event_id,))
        availability = [dict(avail) for avail in availability]
        
        # Convert date and time strings to proper objects
        event['start_date'] = datetime.strptime(event['start_date'], '%Y-%m-%d').date()
        event['end_date'] = datetime.strptime(event['end_date'], '%Y-%m-%d').date()
        event['start_time'] = datetime.strptime(event['start_time'], '%H:%M').time()
        event['end_time'] = datetime.strptime(event['end_time'], '%H:%M').time()
        
        print(f"Event time range: {event['start_time']} to {event['end_time']}")
        
        # Generate time slots (30-minute intervals)
        time_slots = []
        current_time = event['start_time']
        end_time = event['end_time']
        
        # Handle case where end_time is midnight
        if end_time.hour == 0 and end_time.minute == 0:
            end_time = datetime.strptime('23:59', '%H:%M').time()
            print(f"Adjusted end time to: {end_time}")
        
        # Convert to minutes for easier comparison
        current_minutes = current_time.hour * 60 + current_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        
        while current_minutes <= end_minutes:
            # Convert minutes back to time
            hours = current_minutes // 60
            minutes = current_minutes % 60
            time_slot = datetime.strptime(f"{hours:02d}:{minutes:02d}", "%H:%M").time()
            time_slots.append(time_slot)
            print(f"Added time slot: {time_slot}")
            
            # Add 30 minutes
            current_minutes += 30
        
        print(f"Generated {len(time_slots)} time slots")
        
        # Generate dates
        dates = []
        current_date = event['start_date']
        while current_date <= event['end_date']:
            dates.append(current_date)
            print(f"Added date: {current_date}")
            current_date += timedelta(days=1)
        
        print(f"Generated {len(dates)} dates")
        
        # Convert dates in availability data
        for avail in availability:
            avail['date'] = datetime.strptime(avail['date'], '%Y-%m-%d').date()
            avail['time_slot'] = datetime.strptime(avail['time_slot'], '%H:%M').time()
        
        return render_template('event.html',
                             event=event,
                             invites=invites,
                             availability=availability,
                             time_slots=time_slots,
                             dates=dates)
                             
    except Exception as e:
        print(f"Error accessing event: {str(e)}")
        flash('Error accessing event', 'error')
        return redirect(url_for('dashboard'))

def calculate_best_time(event):
    # Get all availability data for the event
    availabilities = Availability.query.filter_by(event_id=event.id).all()
    
    if not availabilities:
        return None
    
    # Group by date and time
    time_slots = {}
    for avail in availabilities:
        key = (avail.date, avail.time_slot)
        if key not in time_slots:
            time_slots[key] = {'available': 0, 'maybe': 0, 'unavailable': 0}
        time_slots[key][avail.status] += 1
    
    # Find best time slot
    best_slot = None
    max_available = -1
    min_unavailable = float('inf')
    
    for (date, time), counts in time_slots.items():
        if counts['available'] > max_available or \
           (counts['available'] == max_available and counts['unavailable'] < min_unavailable):
            max_available = counts['available']
            min_unavailable = counts['unavailable']
            best_slot = {'date': date, 'time_slot': time}
    
    return best_slot

# WebSocket handlers
@socketio.on('join_event')
def on_join(data):
    if not current_user.is_authenticated:
        print('Unauthorized WebSocket connection attempt')
        return False
    
    try:
        event_id = data['event_id']
        room = f'event_{event_id}'
        
        # Verify user has access to this event
        event = db.execute_query_one('get_event_by_id', (event_id,))
        if not event:
            print(f'Event {event_id} not found')
            return False
            
        # Check if user is creator or invited
        if event['creator_id'] != current_user.id:
            invite = db.execute_query_one('get_invite', (event_id, current_user.id))
            if not invite:
                print(f'User {current_user.id} not authorized for event {event_id}')
                return False
        
        join_room(room)
        print(f'User {current_user.id} joined room {room} (sid={request.sid})')
        
        # Get event data
        event = dict(event)
        # Convert time strings to time objects
        event['start_time'] = datetime.strptime(event['start_time'], '%H:%M').time()
        event['end_time'] = datetime.strptime(event['end_time'], '%H:%M').time()
        
        # Get availability data
        availability = db.execute_query('get_event_availability', (event_id,))
        availability = [dict(avail) for avail in availability]
        
        # Convert dates and times in availability data to strings
        for avail in availability:
            avail['date'] = avail['date']  # Already a string from DB
            avail['time_slot'] = avail['time_slot']  # Always use time_slot
            avail['status'] = avail['status']
            avail['email'] = avail['email']
            avail['user_id'] = avail['user_id']  # Add user_id to identify current user's selections
        
        # Get best time
        best_time = db.execute_query_one('get_best_time', (event_id,))
        if best_time:
            best_time = dict(best_time)
            best_time['date'] = best_time['date']  # Already a string from DB
            best_time['time_slot'] = best_time['time_slot']  # Always use time_slot
        
        # Send initial availability data
        emit('initial_availability', {
            'availability': availability,
            'best_time': best_time,
            'current_user_id': current_user.id
        }, room=room)
        
        return True
        
    except Exception as e:
        print(f'Error in on_join: {str(e)}')
        return False

@socketio.on('update_availability')
def on_update_availability(data):
    if not current_user.is_authenticated:
        print('Unauthorized WebSocket update attempt')
        return False
        
    try:
        event_id = data['event_id']
        date = data['date']  # Already a string
        time_slot = data['time_slot']  # Always use time_slot
        status = data['status']
        room = f'event_{event_id}'
        
        # Verify user has access to this event
        event = db.execute_query_one('get_event_by_id', (event_id,))
        if not event:
            print(f'Event {event_id} not found')
            return False
            
        # Check if user is creator or invited
        if event['creator_id'] != current_user.id:
            invite = db.execute_query_one('get_invite', (event_id, current_user.id))
            if not invite:
                print(f'User {current_user.id} not authorized for event {event_id}')
                return False
        
        print(f'Received update from user {current_user.id} for room {room} (sid={request.sid})')
        
        # Update availability
        db.execute_query('set_availability', (
            event_id,
            current_user.id,
            date,
            time_slot,
            status
        ))
        
        # Get updated availability data with counts
        availability = db.execute_query('get_event_availability', (event_id,))
        availability = [dict(avail) for avail in availability]
        
        # Calculate availability counts for each cell
        cell_counts = {}
        for avail in availability:
            key = f"{avail['date']}-{avail['time_slot']}"
            if key not in cell_counts:
                cell_counts[key] = {
                    'available': 0,
                    'maybe': 0,
                    'unavailable': 0,
                    'total': 0
                }
            cell_counts[key][avail['status']] += 1
            cell_counts[key]['total'] += 1
        
        # Add counts to availability data
        for avail in availability:
            key = f"{avail['date']}-{avail['time_slot']}"
            avail['counts'] = cell_counts[key]
        
        # Get best time
        best_time = db.execute_query_one('get_best_time', (event_id,))
        if best_time:
            best_time = dict(best_time)
            # Format the time range
            start_time = datetime.strptime(best_time['time_slot'], '%H:%M')
            end_time = start_time + timedelta(minutes=30)
            best_time['time_slot'] = f"{start_time.strftime('%I:%M %p')}-{end_time.strftime('%I:%M %p')}"
            best_time['date'] = best_time['date']  # Already a string from DB
        
        # Create the update data
        update_data = {
            'availability': availability,
            'best_time': best_time,
            'current_user_id': current_user.id,
            'updated_cell': {
                'date': date,
                'time_slot': time_slot,
                'status': status,
                'user_id': current_user.id
            }
        }
        print(f"Room members for {room}: {socketio.server.manager.rooms['/'].get(room, set())}")
        socketio.emit('availability_update', update_data, room=room)
        
        return True
        
    except Exception as e:
        print(f'Error in on_update_availability: {str(e)}')
        return False

def calculate_heatmap_level(event_id, date, time_slot):
    availabilities = Availability.query.filter_by(
        event_id=event_id,
        date=date,
        time_slot=time_slot,
        status='available'
    ).count()
    return availabilities


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@socketio.on('disconnect')
def on_disconnect():
    print(f"Socket disconnected: {request.sid}")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8080) 