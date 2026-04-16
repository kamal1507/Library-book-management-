# app.py  (VULNERABLE VERSION - FOR EDUCATIONAL PURPOSES ONLY)
# This version intentionally has security flaws to demonstrate what NOT to do.

from flask import Flask
from flask_login import LoginManager
from database import db, User
from werkzeug.security import generate_password_hash   # only used for admin seed

app = Flask(__name__)

# VULNERABILITY 1: Secret key is hardcoded directly in source code.
# Anyone who reads this file or sees the GitHub repo can steal sessions.
app.config['SECRET_KEY'] = 'mysecretkey123'

# SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_vuln.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.student import student_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(student_bp, url_prefix='/student')

with app.app_context():
    db.create_all()
    if User.query.count() == 0:
        admin = User(
            name='Library Admin',
            email='admin@library.com',
            # VULNERABILITY 2: Password stored as plain text - no hashing at all.
            password='admin123',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: admin@library.com / admin123")

if __name__ == '__main__':
    # VULNERABILITY 3: debug=True left on - exposes full error stack traces
    # and an interactive debugger to anyone on the network.
    app.run(debug=True)
