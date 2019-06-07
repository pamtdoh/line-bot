import os
import pickle
import signal

from config import Config
from subprocess import Popen


fifo_dir = os.path.join(Config.APP_ROOT, 'process_fifo')
run_list_path = os.path.join(Config.APP_ROOT, 'run_list')
adapter_exec = os.path.join(Config.APP_ROOT, 'adapter.py')
os.makedirs(fifo_dir, exist_ok=True)


def get_run_list():
    if not os.path.exists(run_list_path):
        with open(run_list_path, 'wb') as f:
            pickle.dump([], f)

    with open(run_list_path, 'rb') as f:
        run_list = pickle.load(f)
    return run_list


def add_run_list(id, pid):
    run_list = get_run_list()
    run_list.append((id, pid))
    with open(run_list_path, 'wb') as f:
        pickle.dump(run_list, f)


def get_all_id():
    return [run[0] for run in get_run_list()]


def get_pid(id):
    for run in get_run_list():
        if run[0] == id:
            return run[1]


def find_new_id():
    id = 0
    while id in get_all_id():
        id += 1
    return id


def rm_id(id):
    run_list = get_run_list()
    index = [run[0] for run in run_list].index(id)
    run_list.pop(index)
    with open(run_list_path, 'wb') as f:
        pickle.dump(run_list, f)


def get_fifo_paths(id):
    return os.path.join(fifo_dir, f'in_{id}'), os.path.join(fifo_dir, f'out_{id}')


def new(args, **kwargs):
    id = find_new_id()
    pid = Popen((adapter_exec, str(id)) + tuple(args), **kwargs).pid
    add_run_list(id, pid)
    return id


# def kill(id):
#     os.kill(get_pid(id), signal.SIGTERM)


def get_response(id, input):
    if id not in get_all_id():
        raise Exception('id not available')

    in_fifo_path, out_fifo_path = get_fifo_paths(id)
    with open(in_fifo_path, 'w') as in_fifo:
        in_fifo.write(input)
    with open(out_fifo_path, 'r') as out_fifo:
        return out_fifo.read()
