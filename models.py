from app import db
from helpers import (
    get_timestamp, get_keyword, get_search_key,
    get_source_type, get_source_user_id, get_source_group_id
)


class Source:
    sourceType = db.Column(db.String(5))
    sourceUserId = db.Column(db.String(33), index=True)
    sourceGroupId = db.Column(db.String(33), index=True)

    def __init__(self, event):
        self.sourceType = get_source_type(event)
        self.sourceUserId = get_source_user_id(event)
        self.sourceGroupId = get_source_group_id(event)


class Search(Source, db.Model):
    __tablename__ = 'searches'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    searchKey = db.Column(db.Text, index=True)
    count = db.Column(db.Integer, default=0)
    start = db.Column(db.Integer, default=0)

    def __init__(self, message_event):
        super().__init__(message_event)
        self.timestamp = get_timestamp(message_event)
        self.searchKey = get_search_key(message_event)

    @staticmethod
    def latest(message_event):
        return Search.query.filter(
            Search.sourceUserId == get_source_user_id(message_event),
            Search.sourceGroupId == get_source_group_id(message_event)
        ).order_by(Search.timestamp.desc()).first()


class RunningProcess(Source, db.Model):
    __tablename__ = 'running_process'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    exec = db.Column(db.String(20))
    runId = db.Column(db.Integer)

    def __init__(self, message_event, exec, run_id):
        super().__init__(message_event)
        self.timestamp = get_timestamp(message_event)
        self.exec = exec
        self.runId = run_id

    @staticmethod
    def latest_in_group(message_event):
        return RunningProcess.query.filter(
            RunningProcess.sourceGroupId == get_source_group_id(message_event)
        ).order_by(RunningProcess.timestamp.desc()).first()


db.create_all()
db.session.commit()
