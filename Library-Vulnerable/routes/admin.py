# routes/admin.py (VULNERABLE VERSION - FOR EDUCATIONAL PURPOSES ONLY)
# This file demonstrates broken access control and other vulnerabilities.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db, User, Book, IssueRecord
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


# ---- Admin Dashboard ----
# VULNERABILITY 9: No role check at all.
# Any logged-in student can visit /admin/dashboard just by typing the URL.
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_books = Book.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_issued = IssueRecord.query.filter_by(status='issued').count()
    pending_requests = IssueRecord.query.filter_by(status='pending').count()
    total_returned = IssueRecord.query.filter_by(status='returned').count()
    recent_issues = IssueRecord.query.order_by(IssueRecord.issue_date.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_books=total_books,
                           total_students=total_students,
                           total_issued=total_issued,
                           pending_requests=pending_requests,
                           total_returned=total_returned,
                           recent_issues=recent_issues)


# ---- View All Books ----
# VULNERABILITY 9 (continued): No role check - any student can see admin book list
@admin_bp.route('/books')
@login_required
def books():
    all_books = Book.query.order_by(Book.added_at.desc()).all()
    return render_template('admin/books.html', books=all_books)


# ---- Add a New Book ----
# VULNERABILITY 9 + 10: No role check AND no input validation.
# Any student can add books. Any input (including empty string) is accepted.
@admin_bp.route('/add-book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        category = request.form.get('category')
        isbn = request.form.get('isbn')
        copies = request.form.get('copies', 1)

        # VULNERABILITY 10: No validation - empty title/author accepted,
        # copies field not checked to be a number.
        book = Book(
            title=title,
            author=author,
            category=category,
            isbn=isbn,
            total_copies=int(copies),
            available_copies=int(copies)
        )
        db.session.add(book)
        db.session.commit()

        flash(f'Book "{title}" added!', 'success')
        return redirect(url_for('admin.books'))

    return render_template('admin/add_book.html')


# ---- Edit a Book ----
# VULNERABILITY 9: No role check
@admin_bp.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.category = request.form.get('category')
        book.isbn = request.form.get('isbn')
        copies = int(request.form.get('copies', 1))
        diff = copies - book.total_copies
        book.total_copies = copies
        book.available_copies = max(0, book.available_copies + diff)
        db.session.commit()
        flash('Book updated!', 'success')
        return redirect(url_for('admin.books'))

    return render_template('admin/edit_book.html', book=book)


# ---- Delete a Book ----
# VULNERABILITY 9: No role check - any student can delete any book
@admin_bp.route('/delete-book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    IssueRecord.query.filter_by(book_id=book_id).delete()
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.', 'success')
    return redirect(url_for('admin.books'))


# ---- View All Issue Records ----
# VULNERABILITY 9: No role check
@admin_bp.route('/issued-books')
@login_required
def issued_books():
    status_filter = request.args.get('status', 'all')
    if status_filter == 'all':
        records = IssueRecord.query.order_by(IssueRecord.issue_date.desc()).all()
    else:
        records = IssueRecord.query.filter_by(status=status_filter)\
                                   .order_by(IssueRecord.issue_date.desc()).all()
    return render_template('admin/issued_books.html', records=records, status_filter=status_filter)


# ---- Approve a Request ----
# VULNERABILITY 9: No role check
@admin_bp.route('/approve/<int:record_id>', methods=['POST'])
@login_required
def approve_issue(record_id):
    record = IssueRecord.query.get_or_404(record_id)
    record.status = 'issued'
    record.issue_date = datetime.utcnow()
    record.due_date = datetime.utcnow() + timedelta(days=14)
    record.book.available_copies = max(0, record.book.available_copies - 1)
    db.session.commit()
    flash('Approved.', 'success')
    return redirect(url_for('admin.issued_books'))


# ---- Reject a Request ----
@admin_bp.route('/reject/<int:record_id>', methods=['POST'])
@login_required
def reject_issue(record_id):
    record = IssueRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash('Rejected.', 'info')
    return redirect(url_for('admin.issued_books'))


# ---- Confirm Return ----
@admin_bp.route('/confirm-return/<int:record_id>', methods=['POST'])
@login_required
def confirm_return(record_id):
    record = IssueRecord.query.get_or_404(record_id)
    record.status = 'returned'
    record.return_date = datetime.utcnow()
    record.book.available_copies = min(record.book.total_copies,
                                       record.book.available_copies + 1)
    db.session.commit()
    flash('Return confirmed.', 'success')
    return redirect(url_for('admin.issued_books'))


# ---- View All Students ----
@admin_bp.route('/students')
@login_required
def students():
    all_students = User.query.filter_by(role='student').order_by(User.created_at.desc()).all()
    return render_template('admin/students.html', students=all_students)
