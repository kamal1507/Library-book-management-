# Library Book Management System — VULNERABLE VERSION

> ⚠️ **WARNING: This code is INTENTIONALLY INSECURE.**
> It is created purely for educational and documentation purposes as part of a
> Secure Web Development college assignment. Do NOT deploy this in any real environment.

---

## Purpose

This repository demonstrates **what NOT to do** when building a web application.
It is the "before" version — the insecure code — compared against the secure version
in the sister repository.

---

## Vulnerabilities Demonstrated

### 1. Hardcoded Secret Key (`app.py`)
```python
app.config['SECRET_KEY'] = 'mysecretkey123'
```
**Risk:** Anyone who reads the source code (e.g. on GitHub) can forge session cookies
and log in as any user without a password.

---

### 2. Plain Text Passwords (`routes/auth.py`, `database.py`)
```python
# Stored as-is in the database — no hashing
password='admin123'
```
**Risk:** If the database is ever accessed or leaked, every user's password is
immediately readable. A single database breach exposes all accounts.

---

### 3. Debug Mode ON (`app.py`)
```python
app.run(debug=True)
```
**Risk:** If deployed online, attackers get full Python stack traces and an
interactive browser console to run arbitrary code on the server.

---

### 4. No Input Validation (`routes/auth.py`, `routes/admin.py`)
```python
# No checks — empty or malformed data accepted silently
name  = request.form.get('name')
email = request.form.get('email')
```
**Risk:** Empty inputs can crash the app or insert garbage data. No email format
check means invalid accounts can be created.

---

### 5. Verbose Error Messages (`routes/auth.py`)
```python
flash(f'Wrong password for {email}. Try again.', 'error')
flash(f'No account found with email: {email}', 'error')
```
**Risk:** Attacker can enumerate valid email addresses by trying logins and
reading which error message appears.

---

### 6. Broken Access Control — No Role Check (`routes/admin.py`)
```python
@admin_bp.route('/dashboard')
@login_required       # only checks login — NOT the role
def dashboard():
```
**Risk:** Any logged-in student can visit `/admin/dashboard`, `/admin/add-book`,
`/admin/delete-book/<id>` etc. just by typing the URL directly.

---

### 7. Missing Ownership Check (`routes/student.py`)
```python
# No check that the record belongs to the current user
record = IssueRecord.query.get_or_404(record_id)
record.status = 'return_requested'
```
**Risk:** Student A can return Student B's book by sending a POST request to
`/student/return/<record_id>` with any valid record ID.

---

### 8. No CSRF Protection (all forms)
Forms have no CSRF tokens — any website can silently submit forms on behalf
of a logged-in user without their knowledge.

---

## Vulnerability Summary Table

| # | Vulnerability | OWASP Category |
|---|--------------|----------------|
| 1 | Hardcoded secret key | A02 - Cryptographic Failures |
| 2 | Plain text passwords | A02 - Cryptographic Failures |
| 3 | Debug mode ON | A05 - Security Misconfiguration |
| 4 | No input validation | A03 - Injection |
| 5 | Verbose error messages | A04 - Insecure Design |
| 6 | No role-based access control | A01 - Broken Access Control |
| 7 | No ownership check | A01 - Broken Access Control |
| 8 | No CSRF protection | A01 - Broken Access Control |

---

## Secure Version

See the companion repository: **Library-Secure** — which fixes all of the above.

---

## How to Run (for testing only)

```
pip install -r requirements.txt
python app.py
```
Open: http://localhost:5000
Admin: admin@library.com / admin123
