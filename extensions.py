# extensions.py
# This file holds shared Flask extensions (limiter, csrf, db).
# Keeping them here avoids circular imports between app.py and routes.

from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

# Rate limiter - applied to specific routes (e.g. login)
limiter = Limiter(
    get_remote_address,
    default_limits=[],
    storage_uri='memory://'
)

# CSRF protection - activated globally in app.py
csrf = CSRFProtect()
