#!/usr/bin/env python3

import os, sys, time
from run_process import get_fifo_paths, rm_id
from subprocess import Popen, PIPE


timeout = 0.1


def main():
    id = int(sys.argv[1])
    args = sys.argv[2:]
    in_fifo_path, out_fifo_path = get_fifo_paths(id)

    try:
        os.mkfifo(in_fifo_path)
        os.mkfifo(out_fifo_path)

        p = Popen(args, encoding='ascii', stdin=PIPE, stdout=PIPE)
        os.set_blocking(p.stdout.fileno(), False)
        while p.poll() is None:
            with open(in_fifo_path, 'r') as in_fifo, open(out_fifo_path, 'w') as out_fifo:
                p.stdin.write(in_fifo.read())
                p.stdin.flush()
                time.sleep(timeout)

                try:
                    response = p.stdout.read()
                except:
                    response = ''
                out_fifo.write(response)
    finally:
        try: p.kill()
        except: pass
        rm_id(id)
        os.unlink(in_fifo_path)
        os.unlink(out_fifo_path)


if __name__ == '__main__':
    main()
