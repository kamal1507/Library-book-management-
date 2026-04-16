# routes/student.py (VULNERABLE VERSION - FOR EDUCATIONAL PURPOSES ONLY)
# Demonstrates missing ownership checks and no input sanitisation.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db, Book, IssueRecord
from datetime import datetime

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@login_required
def dashboard():
    my_issued = IssueRecord.query.filter_by(user_id=current_user.id, status='issued').count()
    my_pending = IssueRecord.query.filter_by(user_id=current_user.id, status='pending').count()
    my_returned = IssueRecord.query.filter_by(user_id=current_user.id, status='returned').count()
    total_available = Book.query.filter(Book.available_copies > 0).count()

    return render_template('student/dashboard.html',
                           my_issued=my_issued,
                           my_pending=my_pending,
                           my_returned=my_returned,
                           total_available=total_available)


@student_bp.route('/books')
@login_required
def browse_books():
    search = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    query = Book.query

    if search:
        query = query.filter(
            (Book.title.ilike(f'%{search}%')) |
            (Book.author.ilike(f'%{search}%')) |
            (Book.category.ilike(f'%{search}%'))
        )
    if category:
        query = query.filter_by(category=category)

    books = query.order_by(Book.title).all()
    categories = db.session.query(Book.category).distinct().all()
    categories = [c[0] for c in categories]

    my_pending_books = [r.book_id for r in
                        IssueRecord.query.filter_by(user_id=current_user.id)
                        .filter(IssueRecord.status.in_(['pending', 'issued'])).all()]

    return render_template('student/browse_books.html',
                           books=books, search=search, category=category,
                           categories=categories, my_pending_books=my_pending_books)


@student_bp.route('/issue/<int:book_id>', methods=['POST'])
@login_required
def issue_book(book_id):
    book = Book.query.get_or_404(book_id)

    if book.available_copies < 1:
        flash('Book not available.', 'error')
        return redirect(url_for('student.browse_books'))

    record = IssueRecord(
        book_id=book_id,
        user_id=current_user.id,
        status='pending'
    )
    db.session.add(record)
    db.session.commit()

    flash('Book requested!', 'success')
    return redirect(url_for('student.my_books'))


@student_bp.route('/my-books')
@login_required
def my_books():
    records = IssueRecord.query.filter_by(user_id=current_user.id)\
                               .order_by(IssueRecord.issue_date.desc()).all()
    return render_template('student/my_books.html', records=records)


@student_bp.route('/return/<int:record_id>', methods=['POST'])
@login_required
def return_book(record_id):
    record = IssueRecord.query.get_or_404(record_id)

    # VULNERABILITY 11: No ownership check.
    # Student A can return Student B's book by guessing the record ID in the URL.
    # e.g. POST /student/return/5  — works for any logged-in student

    record.status = 'return_requested'
    db.session.commit()

    flash('Return requested.', 'info')
    return redirect(url_for('student.my_books'))


@student_bp.route('/profile')
@login_required
def profile():
    total_issued = IssueRecord.query.filter_by(user_id=current_user.id).count()
    currently_issued = IssueRecord.query.filter_by(user_id=current_user.id, status='issued').count()
    books_returned = IssueRecord.query.filter_by(user_id=current_user.id, status='returned').count()

    return render_template('student/profile.html',
                           total_issued=total_issued,
                           currently_issued=currently_issued,
                           books_returned=books_returned)
