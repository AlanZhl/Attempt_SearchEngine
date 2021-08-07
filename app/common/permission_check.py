from functools import wraps
from flask import session, abort
from app.models import Users, Roles


def permission_check(permission):
    # check if the current user (retrieved from session) has the given "permission"
    def decorator(f):
        @wraps(f)
        def wrapped_func(*args, **kwargs):
            try:
                current_user = Users.query.filter_by(user_id=session["user_id"]).first()
                succeed = False
                if current_user:
                    role = Roles.query.filter_by(role_id=current_user.role_id).first()
                    if role.permissions & permission == permission:
                        succeed = True
                if succeed:
                    return f(*args, **kwargs)
                else:
                    abort(403)
            except Exception as e:
                print(e)
                abort(403)
        return wrapped_func
    return decorator