import app
import os
import re
import run_process

from app import db
from config import Config
from helpers import get_text, get_source_group_id
from linebot.models import TextSendMessage
from models import RunningProcess


roms_dir = os.path.join(Config.APP_ROOT, 'roms')
root_save_dir = os.path.join(Config.APP_ROOT, 'saves')
rom_names = sorted(os.listdir(roms_dir))
rom_paths = [os.path.join(roms_dir, path) for path in rom_names]


def make_save_dir(group_id, rom_name):
    dir = os.path.join(root_save_dir, group_id, rom_name)
    os.makedirs(dir, exist_ok=True)
    return dir


class Dfrotz:
    metadata = {}

    @staticmethod
    def matcher(event):
        text = get_text(event)
        return re.match(r'new game \d+', text) or \
               re.match(r'list roms', text) or \
               re.match(r'\.', text) and RunningProcess.latest_in_group(event)

    @staticmethod
    def response(event):
        return Dfrotz(event).get_response()


    def __init__(self, event):
        self.event = event
        self.cmd_type = None

        text = get_text(self.event)
        m = re.match(r'new game (\d+)', text)
        if m:
            self.rom_id = int(m.group(1))
            self.save_dir = make_save_dir(
                get_source_group_id(self.event),
                rom_names[self.rom_id]
            )
            self.cmd_type = 'new'
            self.running_process = RunningProcess(
                self.event,
                'dfrotz',
                run_process.new(
                    ('dfrotz', rom_paths[self.rom_id]),
                    cwd=self.save_dir
                )
            )
            db.session.add(self.running_process)
            db.session.commit()

        m = re.match(r'list roms', text)
        if m:
            self.cmd_type = 'list'

        m = re.match(r'\.', text)
        if m:
            self.cmd_type = 'input'
            self.running_process = RunningProcess.latest_in_group(self.event)

    def get_response(self):
        if self.cmd_type == 'new':
            run_id = self.running_process.runId
            return [
                TextSendMessage(
                    f'new game [{rom_names[self.rom_id]}]\n'
                    f'runId: {run_id}\n'
                    f'saveDir: {self.save_dir}'
                ),
                TextSendMessage(run_process.get_response(run_id, ''))
            ]
        elif self.cmd_type == 'list':
            return [
                TextSendMessage(
                    '\n'.join([f'{i}: {name}' for i, name in enumerate(rom_names)])
                )
            ]
        elif self.cmd_type == 'input':
            run_id = self.running_process.runId
            input = get_text(self.event)[1:] + '\n'
            return [
                TextSendMessage(run_process.get_response(run_id, input))
            ]
