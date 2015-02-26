from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    result_all = db.Column(JSON)

    def __init__(self, result_all):
        self.result_all = result_all

    def __repr__(self):
        return '<id {}>'.format(self.id)
