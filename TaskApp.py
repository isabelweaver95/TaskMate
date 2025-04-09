from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from TaskDurationPredictor import TaskDurationPredictor
import sqlite3
import logging
from contextlib import closing

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this for production!

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize task predictor
predictor = TaskDurationPredictor()

# Database configuration
DATABASE = 'tasks.db'

# User model
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Task model
class Task:
    PRIORITY_WEIGHTS = {'low': 1, 'medium': 2, 'high': 3}
    
    def __init__(self, name, priority, category, duration):
        self.name = name
        self.priority = priority
        self.category = category
        self.duration = duration  # in minutes
        self.weight = self.PRIORITY_WEIGHTS[priority]

# Database initialization
def init_db():
    with closing(sqlite3.connect(DATABASE)) as conn:
        with conn:
            # Users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')
            
            # Tasks table (now with user_id)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    category TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    scheduled_date TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create default admin if none exists
            if not conn.execute('SELECT 1 FROM users WHERE username = "admin"').fetchone():
                conn.execute(
                    'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    ('admin', generate_password_hash('admin123'))
                )

# Initialize database
init_db()

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    with closing(sqlite3.connect(DATABASE)) as conn:
        conn.row_factory = sqlite3.Row
        user = conn.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
    return User(user['id'], user['username']) if user else None

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with closing(sqlite3.connect(DATABASE)) as conn:
            conn.row_factory = sqlite3.Row
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            login_user(User(user['id'], user['username']))
            return redirect(url_for('home'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        try:
            with closing(sqlite3.connect(DATABASE)) as conn:
                conn.execute(
                    'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    (username, password)
                )
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
    
    return render_template('register.html')

# Main application routes
@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('index.html', current_user=current_user)

@app.route('/plan', methods=['GET', 'POST'])
@login_required
def plan():
    if request.method == 'POST':
        try:
            total_tasks = int(request.form.get('total_tasks', 1))
            available_hours = float(request.form.get('time_period', 8))
            
            tasks = []
            for i in range(total_tasks):
                task_input = {
                    'priority': request.form.get(f'priority_{i}'),
                    'category': request.form.get(f'category_{i}'),
                    'urgency': 0.5
                }
                
                duration = predictor.predict_duration(task_input)
                
                tasks.append(Task(
                    name=request.form.get(f'task_name_{i}').strip(),
                    priority=task_input['priority'],
                    category=task_input['category'],
                    duration=duration
                ))

            scheduler = DayScheduler(tasks, available_hours)
            schedule = scheduler.create_schedule()
            
            save_scheduled_tasks(schedule)
            
            return render_template('index.html', 
                                schedule=schedule,
                                available_hours=available_hours,
                                current_user=current_user,
                                step=3)
            
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            return render_template('index.html', 
                                error=str(e),
                                current_user=current_user,
                                step=2)

    return render_template('index.html', current_user=current_user, step=1)

@app.route('/history')
@login_required
def history():
    try:
        with closing(sqlite3.connect(DATABASE)) as conn:
            conn.row_factory = sqlite3.Row
            tasks = conn.execute('''
                SELECT scheduled_date as date, name, priority, category, 
                       start_time, end_time, duration
                FROM tasks
                WHERE user_id = ?
                ORDER BY scheduled_date DESC, start_time ASC
            ''', (current_user.id,)).fetchall()
            
            return render_template('history.html', 
                                tasks=tasks,
                                current_user=current_user)
                
    except Exception as e:
        logging.error(f"Error fetching history: {str(e)}")
        return render_template('history.html', 
                            error=str(e),
                            current_user=current_user)

# Helper classes and functions
class DayScheduler:
    def __init__(self, tasks, available_hours):
        self.tasks = sorted(tasks, key=lambda x: x.weight, reverse=True)
        self.available_minutes = available_hours * 60
        
    def create_schedule(self):
        scheduled = []
        remaining_time = self.available_minutes
        current_time = datetime.now().replace(hour=9, minute=0)  # Start at 9 AM
        
        for task in self.tasks:
            if task.duration <= remaining_time:
                end_time = current_time + timedelta(minutes=task.duration)
                scheduled.append({
                    'name': task.name,
                    'start': current_time.strftime('%H:%M'),
                    'end': end_time.strftime('%H:%M'),
                    'duration': f'{int(task.duration)} mins',
                    'priority': task.priority.capitalize(),
                    'category': task.category.capitalize()
                })
                current_time = end_time
                remaining_time -= task.duration
        
        return {
            'scheduled_tasks': scheduled,
            'total_scheduled': len(scheduled),
            'remaining_time': f'{int(remaining_time // 60)}h {int(remaining_time % 60)}m'
        }

def save_scheduled_tasks(schedule):
    try:
        with closing(sqlite3.connect(DATABASE)) as conn:
            with conn:
                for task in schedule['scheduled_tasks']:
                    conn.execute('''
                        INSERT INTO tasks 
                        (user_id, name, priority, category, duration, scheduled_date, start_time, end_time)
                        VALUES (?, ?, ?, ?, ?, date('now'), ?, ?)
                    ''', (
                        current_user.id,
                        task['name'],
                        task['priority'].lower(),
                        task['category'].lower(),
                        int(task['duration'].split()[0]),
                        task['start'],
                        task['end']
                    ))
        return True
    except Exception as e:
        logging.error(f'Error saving tasks: {str(e)}')
        return False

if __name__ == '__main__':
    app.run(debug=True)