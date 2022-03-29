from api.api_users.src import db
from datetime import datetime


class Base(db.Model):
    """ Base class implements default fields needed in all models """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_modified = db.Column(db.DateTime, default=datetime.now)


class User(Base):
    """ Class represents user of application.
    Table name is set to 'user'.
    """

    __tablename__ = "user"

    name = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, unique=True, nullable=False)

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "port": self.port,
            "date_created": self.date_created,
            "date_modified": self.date_modified
        }

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, port={self.port})"
