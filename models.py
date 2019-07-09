from app import db
from helpers import (
    timestamp, source_type, source_user_id, source_group_id
)


class Source:
    timestamp = db.Column(db.DateTime)
    sourceType = db.Column(db.String(5))
    sourceUserId = db.Column(db.String(33), index=True)
    sourceGroupId = db.Column(db.String(33), index=True)

    def __init__(self, event):
        self.timestamp = timestamp(event)
        self.sourceType = source_type(event)
        self.sourceUserId = source_user_id(event)
        self.sourceGroupId = source_group_id(event)


class Search(Source, db.Model):
    __tablename__ = 'searches'

    id = db.Column(db.Integer, primary_key=True)
    searchKey = db.Column(db.Text, index=True)
    count = db.Column(db.Integer, default=0)
    start = db.Column(db.Integer, default=0)

    def __init__(self, event, search_key):
        super().__init__(event)
        self.searchKey = search_key

    @staticmethod
    def last(event):
        return Search.query.filter(
            Search.sourceUserId == source_user_id(event),
            Search.sourceGroupId == source_group_id(event)
        ).order_by(Search.timestamp.desc()).first()


class RunningProcess(Source, db.Model):
    __tablename__ = 'running_process'

    id = db.Column(db.Integer, primary_key=True)
    exec = db.Column(db.String(20))
    runId = db.Column(db.Integer)

    def __init__(self, event, exec, run_id):
        super().__init__(event)
        self.exec = exec
        self.runId = run_id

    @staticmethod
    def latest_in_group(event):
        return RunningProcess.query.filter(
            RunningProcess.sourceGroupId == source_group_id(event)
        ).order_by(RunningProcess.timestamp.desc()).first()


db.create_all()
db.session.commit()
