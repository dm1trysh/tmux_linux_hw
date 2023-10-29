#!/usr/bin/env python3

import argparse
import libtmux
import os
import os.path
import typing
import random
import string
import re

base_dir = "./"
session_name = "notebooks"
base_session_name = session_name + "0"
server =  libtmux.Server()
port_min_idx = 5000
port_max_idx = 8888


def start_n(session_nm : str = base_session_name, number_of_wins: int = 1):
    session = server.find_where({"session_name": session_nm})
    if session is None:
        session = server.new_session(session_nm)

    max_win_idx = 0
    start_win = session.find_where({"window_name": "bash"})
    windows = session.windows
    for win in windows:
        win_name = win.window_name
        lst_idxes = re.findall(r'\d+', win_name)
        if len(lst_idxes) > 0:
            win_idx = int(lst_idxes[0])
            max_win_idx = max(max_win_idx, win_idx)
    if max_win_idx != 0:
        max_win_idx = max_win_idx + 1
    
    for win_num in range(max_win_idx, max_win_idx + number_of_wins):
        win_name = "win" + str(win_num)
        if (start_win is not None) and win_num == 0:
            win = start_win.rename_window(win_name)
            #win = start_win
        else:
            win = session.new_window(attach=False, window_name=win_name)
        pane = win.split_window(attach=False)
        dir_path = os.path.join(base_dir, "dir" + str(win_num))
        os.makedirs(dir_path, exist_ok=True)
        notebook_port = random.randint(port_min_idx, port_max_idx)
        notebook_token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        pane.send_keys("jupyter notebook --port {" + str(notebook_port) + "} --NotebookApp.token={" + str(notebook_token) + "} --NotebookApp.notebook_dir={" + str(dir_path) + "}")

        print(win_name + ": Port - " + str(notebook_port) + ", Token - " + str(notebook_token))
    print(session.windows)
    pass
    

def stop_i(session_nm : str = base_session_name, number_of_win : int = 0):
    curr_session = server.find_where({"session_name": session_nm})
    if curr_session is not None:
        win = curr_session.find_where({"window_name": "win" + str(number_of_win)})
        if win is not None:
            win.kill_window()
            dir_name = "dir" + str(number_of_win)
            os.rmdir(dir_name)
    pass


def stop_all(session_nm: str = base_session_name):
    curr_session = server.find_where({"session_name": session_nm})
    if curr_session is not None:
        for win in curr_session.windows:
            win_name = win.window_name
            if win_name == "bash":
                continue
            lst_idxes = re.findall(r'\d+', win_name)
            win_idx = 0
            if len(lst_idxes) > 0:
                win_idx = int(lst_idxes[0])
            dir_name = "dir" + str(win_idx)
            os.rmdir(dir_name)
        os.system("tmux kill-session -t " + curr_session.session_name)
    pass


def main():
    parser = argparse.ArgumentParser(description='catch jupyter commands')
    parser.add_argument('cmds', type=str, nargs='+', help='there are 3 options: 1) start N 2)stop i 3) stop_all')
    args = parser.parse_args()
    command_words = args.cmds
    
    if command_words[0] == 'start':
        cnt_of_notebooks = int(command_words[1])
        start_n(number_of_wins = cnt_of_notebooks)
    
    elif command_words[0] == 'stop_all':
        if len(command_words) > 1:
            stop_session = command_words[1]
            stop_all(session = stop_session)
        else:
            stop_all()

    else:
        num_of_win = int(command_words[1])
        if len(command_words) > 2:
            stop_session = command_words[2]
            stop_i(session_nm = stop_session, number_of_win = num_of_win)
        else:
            stop_i(number_of_win = num_of_win)


if __name__ == "__main__":
    main()
