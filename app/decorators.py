from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("You don't have permission to access this page.", "danger")
                return redirect(url_for("main.index"))
            return f(*args, **kwargs)
        return decorated
    return decorator