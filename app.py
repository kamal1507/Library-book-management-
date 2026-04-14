# app.py
# Main entry point for the Library Book Management System.
# Start the app by running: python app.py

from flask import Flask
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from database import db, User
from extensions import limiter, csrf
import os
from dotenv import load_dotenv

# ---- Create and configure the Flask app ----
app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('FLASK_APP_KEY')

# SQLite database - stored as a local file (easy for college projects)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connect the database to the app
db.init_app(app)

# ---- Enable CSRF Protection on all forms ----
# Prevents Cross-Site Request Forgery attacks on every POST form
csrf.init_app(app)

# ---- Login Rate Limiting ----
# Max 10 login attempts per minute per IP - stops brute-force attacks
limiter.init_app(app)

# ---- Setup Flask-Login (handles sessions) ----
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'       # redirect here if not logged in
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    # Flask-Login calls this to find the logged-in user from the session
    return User.query.get(int(user_id))

# ---- Register route blueprints ----
# Each blueprint handles a section of the app
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.student import student_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(student_bp, url_prefix='/student')

# ---- Create tables and seed default admin ----
with app.app_context():
    db.create_all()  # creates all tables if they don't exist

    # Create a default admin account if there are no users yet
    if User.query.count() == 0:
        admin = User(
            name='Library Admin',
            email='admin@library.com',
            password=generate_password_hash('Admin@15'),  # hashed password
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: admin@library.com")

# ---- Run the app ----
if __name__ == '__main__':
    # debug is read from .env - set DEBUG=True only during development
    # In production this must be False to hide error details from users
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
