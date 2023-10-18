from server import db


class User(db.Model):
    email = db.Column(db.String(120), primary_key=True, nullable=False)
    key = db.Column(db.String(120), nullable=False)
    secret_key = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.key}', '{self.secret_key}')"


db.create_all()
