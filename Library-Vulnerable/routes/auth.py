# routes/auth.py (VULNERABLE VERSION - FOR EDUCATIONAL PURPOSES ONLY)
# This file demonstrates multiple authentication vulnerabilities.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from database import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))


# ---- Login (Vulnerable) ----
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # VULNERABILITY 4: No input validation - empty fields are accepted.
        # An attacker can submit blank data and cause unexpected behaviour.

        # VULNERABILITY 5: Password compared as plain text.
        # No hashing - if DB is leaked, all passwords are immediately visible.
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
        else:
            # VULNERABILITY 6: Verbose error reveals whether email exists.
            # Attacker can enumerate valid accounts.
            existing = User.query.filter_by(email=email).first()
            if existing:
                flash(f'Wrong password for {email}. Try again.', 'error')
            else:
                flash(f'No account found with email: {email}', 'error')

    return render_template('login.html')


# ---- Register (Vulnerable) ----
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # VULNERABILITY 7: No validation whatsoever.
        # - Any email format accepted (e.g. "abc", "@@@@")
        # - No minimum password length check
        # - No confirmation field check
        # - Empty fields pass through silently

        # VULNERABILITY 8: Password saved as plain text - no hashing.
        new_user = User(
            name=name,
            email=email,
            password=password,   # stored exactly as typed
            role='student'
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ---- Logout ----
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
