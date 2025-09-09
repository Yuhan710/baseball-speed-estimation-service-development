# from flask_login import UserMixin
from db import get_db

class User(UserMixin):
    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE email = ?", ("some8od1@gmail.com",)
    ).fetchone()

    id = user[0]
    print("name = ", user[1])