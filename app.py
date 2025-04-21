# ─── IMPORTS ────────────────────────────────────────────────────────────────
from flask import Flask, render_template, request, redirect, url_for, session, Response, flash
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from gridfs import GridFS  # For storing large video files
from flask_socketio import SocketIO  # Real-time communication
import cv2
import numpy as np
import mss
import time
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os
from bson.objectid import ObjectId
import logging

# ─── LOGGING SETUP ──────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── INITIALIZATION ─────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secure_secret_key_here")
socketio = SocketIO(app)

# ─── MONGODB SETUP ──────────────────────────────────────────────────────────
try:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/livestream_db")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.server_info()  # Check MongoDB connection
    db = client['livestream_db']
    users = db['users']
    fs = GridFS(db, collection='videos')  # GridFS for storing uploaded videos
    logger.info("Connected to MongoDB successfully!")
except ServerSelectionTimeoutError as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise SystemExit("MongoDB connection failed. Exiting.")

# ─── CREATE ADMIN USER ──────────────────────────────────────────────────────
if users.count_documents({}) == 0:
    logger.info("No users found. Creating admin user.")
    users.create_index('username', unique=True)
    users.insert_one({
        '_id': '67f543c79842d98dcb52746e',
        'username': 'admin',
        'email': '',
        'password_hash': generate_password_hash('admin123'),
        'role': 'admin',
        'password': ''
    })

# ─── STREAM STATUS ──────────────────────────────────────────────────────────
stream_status = {
    'live': False,
    'viewers': 0
}
MAX_VIEWERS = 5

# ─── LOGIN REQUIRED DECORATOR ───────────────────────────────────────────────
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'username' not in session:
                flash('Login required', 'error')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('Unauthorized access', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ─── ROUTES ─────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return redirect(url_for('dashboard') if 'username' in session else 'login')

# ─── LOGIN ──────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.find_one({'username': username})
        if user:
            if user.get('password_hash') and check_password_hash(user['password_hash'], password):
                session['username'] = username
                session['role'] = user.get('role', 'viewer')
                logger.info(f"User {username} logged in successfully.")
                return redirect(url_for('dashboard'))
            elif user.get('password') == password:  # Legacy plaintext
                users.update_one({'username': username}, {'$set': {'password_hash': generate_password_hash(password)}})
                session['username'] = username
                session['role'] = user.get('role', 'viewer')
                logger.info(f"User {username} logged in with legacy password and updated to hash.")
                return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
        logger.warning(f"Failed login attempt for username: {username}")
    return render_template('login.html')

# ─── REGISTER ───────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Username and password are required', 'error')
            logger.warning("Registration failed: Missing username or password.")
        elif users.find_one({'username': username}):
            flash('Username already exists', 'error')
            logger.warning(f"Registration failed: Username {username} already exists.")
        else:
            users.insert_one({
                'username': username,
                'email': '',
                'password_hash': generate_password_hash(password),
                'role': 'viewer',
                'password': ''
            })
            flash('Registration successful! Please login', 'success')
            logger.info(f"User {username} registered successfully.")
            return redirect(url_for('login'))
    return render_template('register.html')

# ─── DASHBOARD ──────────────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required()
def dashboard():
    return render_template('dashboard.html', username=session['username'],
                           role=session.get('role', 'viewer'),
                           stream_status=stream_status)

# ─── VIDEO UPLOAD + LIST ────────────────────────────────────────────────────
@app.route('/recorded_videos', methods=['GET', 'POST'])
@login_required()
def recorded_videos():
    videos = [{
        'filename': v.filename,
        'id': str(v._id),
        'uploaded_by': v.metadata.get('uploaded_by', 'Unknown'),
        'upload_time': v.upload_date.strftime('%Y-%m-%d %H:%M:%S')
    } for v in fs.find()]

    if request.method == 'POST' and session.get('role') == 'admin':
        video = request.files.get('video')
        if not video or video.filename == '':
            flash('No selected video', 'error')
            logger.warning("Video upload failed: No video selected.")
        else:
            fs.put(video, filename=video.filename, metadata={
                'uploaded_by': session['username'],
                'upload_date': datetime.utcnow()
            })
            flash('Video uploaded successfully!', 'success')
            logger.info(f"Video {video.filename} uploaded by {session['username']}.")
            return redirect(url_for('recorded_videos'))

    return render_template('recorded_videos.html',
                           username=session['username'],
                           videos=videos,
                           is_admin=session.get('role') == 'admin')

# ─── DELETE VIDEO ───────────────────────────────────────────────────────────
@app.route('/delete_video/<video_id>', methods=['POST'])
@login_required(role='admin')
def delete_video(video_id):
    try:
        fs.delete(ObjectId(video_id))
        flash('Video deleted successfully!', 'success')
        logger.info(f"Video {video_id} deleted by {session['username']}.")
    except Exception as e:
        flash(f'Error deleting video: {e}', 'error')
        logger.error(f"Failed to delete video {video_id}: {e}")
    return redirect(url_for('recorded_videos'))

# ─── STREAM VIDEO ───────────────────────────────────────────────────────────
@app.route('/video/<video_id>')
def get_video(video_id):
    try:
        video = fs.get(ObjectId(video_id))
        return Response(video.read(), mimetype='video/mp4')
    except Exception as e:
        logger.error(f"Failed to stream video {video_id}: {e}")
        flash('Error streaming video', 'error')
        return redirect(url_for('recorded_videos'))

# ─── STREAM CONTROL ─────────────────────────────────────────────────────────
@app.route('/start_stream')
@login_required(role='admin')
def start_stream():
    stream_status['live'] = True
    logger.info(f"Stream started by {session['username']}.")
    return redirect(url_for('live_stream'))

@app.route('/stop_stream', methods=['POST'])
@login_required(role='admin')
def stop_stream():
    stream_status['live'] = False
    stream_status['viewers'] = 0
    socketio.emit('stream_ended')
    logger.info(f"Stream stopped by {session['username']}.")
    return redirect(url_for('dashboard'))

# ─── ADMIN STREAM PAGE ──────────────────────────────────────────────────────
@app.route('/live_stream')
@login_required(role='admin')
def live_stream():
    return render_template('live_stream.html', stream_status=stream_status)

# ─── VIEW STREAM ────────────────────────────────────────────────────────────
@app.route('/view_stream')
@login_required()
def view_stream():
    if not stream_status['live']:
        logger.info(f"User {session['username']} attempted to view offline stream.")
        return render_template('stream_offline.html')
    if stream_status['viewers'] >= MAX_VIEWERS:
        logger.warning(f"User {session['username']} denied stream access: Viewer limit reached.")
        return render_template('viewer_limit.html')
    stream_status['viewers'] += 1
    socketio.emit('viewer_count', stream_status['viewers'])
    logger.info(f"User {session['username']} joined stream. Viewers: {stream_status['viewers']}.")
    return render_template('view_stream.html', stream_status=stream_status)

# ─── VIDEO STREAMING (SCREEN CAPTURE) ───────────────────────────────────────
@app.route('/video_feed')
def video_feed():
    def generate():
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                while stream_status['live']:
                    img = sct.grab(monitor)
                    frame = cv2.resize(np.array(img), (1280, 720))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    ret, buffer = cv2.imencode('.jpg', frame)
                    if not ret:
                        logger.warning("Failed to encode frame for video feed.")
                        continue
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    time.sleep(0.05)
        except Exception as e:
            logger.error(f"Error in video feed: {e}")
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ─── VIEWER EXIT STREAM ─────────────────────────────────────────────────────
@app.route('/leave_stream')
def leave_stream():
    if 'username' in session:
        stream_status['viewers'] = max(0, stream_status['viewers'] - 1)
        socketio.emit('viewer_count', stream_status['viewers'])
        logger.info(f"User {session['username']} left stream. Viewers: {stream_status['viewers']}.")
    return redirect(url_for('dashboard'))

# ─── LOGOUT ─────────────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    if 'username' in session:
        stream_status['viewers'] = max(0, stream_status['viewers'] - 1)
        socketio.emit('viewer_count', stream_status['viewers'])
        logger.info(f"User {session['username']} logged out. Viewers: {stream_status['viewers']}.")
    session.clear()
    return redirect(url_for('login'))

# ─── SOCKET DISCONNECT EVENT ────────────────────────────────────────────────
@socketio.on('disconnect')
def handle_disconnect():
    stream_status['viewers'] = max(0, stream_status['viewers'] - 1)
    socketio.emit('viewer_count', stream_status['viewers'])
    logger.info(f"Socket disconnected. Viewers: {stream_status['viewers']}.")

# ─── RUN SERVER ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=os.getenv("FLASK_ENV") == "development")