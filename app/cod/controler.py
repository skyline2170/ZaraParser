import threading
import tkinter as tk
import Parse_class
import multiprocessing as mp

process_list = []


def f1(pipe_send, pipe_recv, listbox: tk.Listbox, win, radiobutton):
    response = pipe_recv.recv()
    print(response)
    if radiobutton == 0:
        pipe_send(response)
    else:
        listbox.config(listvariable=response)
        win.update()

    # response = tk.Variable(response)


# def f2(pipe_send, pipe_recv,listbox: tk.Listbox):
#
#     pipe.send(listbox)


def one_data_process(pipe_send, pipe_recv):
    parser = Parse_class.ParserZara()
    parser.run_2(pipe_send=pipe_send, pipe_recv=pipe_recv)


def get_all_data_process():
    parser = Parse_class.ParserZara()
    parser.run_2()


def run(listbox: tk.Listbox, win: tk.Tk, radiobutton):
    radiobutton = radiobutton.get()
    match radiobutton:
        case 0:  # надо получить все данные
            process_run = mp.Process(target=get_all_data_process())
            process_list.append(process_run)
            process_run.run()
        case 1:  # надо получить данные на выбор
            ...

    # pipe_send, pipe_recv = mp.Pipe()
    # th_1 = threading.Thread(target=f1, args=(pipe_send, pipe_recv, listbox, win, radiobutton), daemon=True)
    # th_1.start()
    # process_run = mp.Process(target=one_data_process, args=(pipe_send, pipe_recv))
    # process_list.append(process_run)
    # process_run.run()
# https://www.zara.com/tr/tr/tretorn-x-zara-duz-yagmur-botu-p13901010.html?v1=223982785&v2=2178484
# https://www.zara.com/tr/tr/tretorn-x-zara-duz-yagmur-botu-p13901010.html?v1=227313023&v2=2178484