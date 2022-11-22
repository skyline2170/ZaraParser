import threading
import tkinter as tk
import Parse_class
import multiprocessing as mp
from tkinter import ttk


def f1(pipe_send, pipe_recv, progres_bar: ttk.Progressbar):
    progress = 0
    while True:
        response = pipe_recv.recv()
        if response != "end":
            progress += response
            progres_bar.step(response)
        else:
            pipe_send.send(100 - progress)
            return None


def get_all_data_process(pipe_send, pipe_recv):
    parser = Parse_class.ParserZara()
    parser.run_2(headless=Parse_class.HeadlessStatus.headless_off, pipe_recv=pipe_recv, pipe_send=pipe_send)


def run(listbox: tk.Listbox, win: tk.Tk, radiobutton, progres_bar: ttk.Progressbar):
    radiobutton = radiobutton.get()
    pipe_send, pipe_recv = mp.Pipe()

    process_run = mp.Process(target=get_all_data_process, args=(pipe_send, pipe_recv))
    # process_list.append(process_run)
    process_run.start()

    th_1 = threading.Thread(target=f1, args=(pipe_send, pipe_recv, progres_bar), daemon=True)
    th_1.start()
