from app import db


class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    type = db.Column(db.String(5))
    userId = db.Column(db.String(33), index=True)
    groupId = db.Column(db.String(33), index=True)
    searchKey = db.Column(db.Text, index=True)
    count = db.Column(db.Integer, default=0)
    start = db.Column(db.Integer, default=0)


db.create_all()
db.session.commit()
