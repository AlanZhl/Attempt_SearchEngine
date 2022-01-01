from passlib.hash import bcrypt_sha256
from . import db


class Permissions:
    JOB_FAVOR = 0X01
    JOB_CREATE = 0X02
    JOB_MANAGE = 0X04
    USER_MANAGE = 0X08


class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True)
    email = db.Column(db.String(100), unique = True, index=True)
    role_id = db.Column(db.Integer)
    password = db.Column(db.String(128))
    search_history = db.Column(db.Text)

    def __init__(self, name, email, role, password):
        self.name = name
        self.email = email
        if role == "company":
            self.role_id = 2
        elif role == "admin":
            self.role_id = 3
        else:
            self.role_id = 1
        self.password = bcrypt_sha256.encrypt(str(password))
        self.search_history = ""


class Roles(db.Model):
    __tablename__ = "roles"
    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    permissions = db.Column(db.Integer)

    def __init__(self, name):
        self.name = name


    @staticmethod
    def init_roles():
        # create or reset all the possible roles
        role_lst = ["jobseeker", "company", "admin"]
        permission_dict = {
            "jobseeker" : [Permissions.JOB_FAVOR],
            "company" : [Permissions.JOB_FAVOR, Permissions.JOB_CREATE, Permissions.JOB_MANAGE],
            "admin" : [Permissions.JOB_FAVOR, Permissions.USER_MANAGE]
        }
        try:
            for role_name in role_lst:
                role = Roles.query.filter_by(name=role_name).first()
                if role == None:
                    role = Roles(role_name)
                
                role.reset_permissions()
                for permission in permission_dict[role_name]:
                    role.add_permission(permission)

                db.session.add(role)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        db.session.close()


    def reset_permissions(self):
        self.permissions = 0


    def has_permission(self, permission):
        return (self.permissions & permission) == permission


    def add_permission(self, permission):
        self.permissions |= permission