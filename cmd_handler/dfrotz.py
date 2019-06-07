import os
import run_process

from app import db
from helpers import get_keyword, get_text
from linebot.models import TextSendMessage
from models import RunningProcess


roms_dir = os.path.join(os.getcwd(), 'roms')


class Dfrotz:
    metadata = {}

    @staticmethod
    def matcher(event):
        return get_text(event) == 'new process' or \
               get_text(event)[0] == '.' and RunningProcess.latest_in_group(event)

    @staticmethod
    def response(event):
        if get_text(event) == 'new process':
            id = Dfrotz.new(event).running_process.runId
            return [
                TextSendMessage(
                    f'new process\n'
                    f'runId: {id}'
                ),
                TextSendMessage(run_process.get_response(id, ''))
            ]
        else:
            return Dfrotz.latest_in_group(event).default_response()


    def __init__(self, event):
        self.event = event
        self.running_process = None

    @staticmethod
    def new(event):
        d = Dfrotz(event)
        d.running_process = RunningProcess(
            event,
            'dfrotz',
            run_process.new(('dfrotz', os.path.join(roms_dir, 'hhgg.z5')))
        )
        db.session.add(d.running_process)
        db.session.commit()
        return d

    @staticmethod
    def latest_in_group(event):
        d = Dfrotz(event)
        d.running_process = RunningProcess.latest_in_group(event)
        return d

    def default_response(self):
        input = get_text(self.event)[1:] + '\n'
        return [
            TextSendMessage(run_process.get_response(self.running_process.runId, input))
        ]
