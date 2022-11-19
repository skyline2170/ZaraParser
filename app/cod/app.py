import time
import tkinter as tk
import tkinter.ttk as ttk
import controler


# from tkinter.ttk import Progressbar


def finish():
    main_window.destroy()
    print("программа закрыта")


main_window = tk.Tk()
main_window.title("Parser Zara")
main_window.resizable(False, False)
main_window.geometry("400x150+100+100")
main_window.protocol("WM_DELETE_WINDOW", finish)


def list_box_active(win: tk.Tk, list_box, radiobutton: tk.IntVar):
    r = radiobutton.get()
    if r == 0:
        list_box.pack_forget()
        win.geometry("400x150+100+100")
    else:
        list_box.pack()
        win.geometry("400x330+100+100")
    win.update()


def run(listbox, win, radiobutton):
    controler.run(listbox, win, radiobutton)


def main():
    # main_window.update()

    r_var_1 = tk.IntVar()
    r_var_1.set(0)

    label_url = tk.Label(main_window, text="https://www.zara.com/tr/tr/kadin-ayakkabilar-l1251.html?v1=2113973",
                         justify=tk.CENTER, padx=10, pady=10)

    frame_radiobutton = tk.Frame(main_window)

    radiobutton_1 = tk.Radiobutton(frame_radiobutton, text="Всё сразу", variable=r_var_1, value=0,
                                   command=lambda: list_box_active(main_window, list_box, r_var_1))
    radiobutton_2 = tk.Radiobutton(frame_radiobutton, text="На выбор", variable=r_var_1, value=1,
                                   command=lambda: list_box_active(main_window, list_box, r_var_1))

    button_pars = tk.Button(main_window, text="Начать парсинг", background="orange", padx=2, pady=2,
                            command=lambda: run(list_box, main_window, r_var_1))

    list_box = tk.Listbox(main_window)

    label_url.pack(side=tk.TOP)
    #
    frame_radiobutton.pack(side=tk.TOP)
    radiobutton_1.pack(side=tk.TOP)
    radiobutton_2.pack(side=tk.TOP)
    button_pars.pack(side=tk.TOP, padx=10, pady=10)

    #
    list_box.pack(side=tk.TOP)
    list_box.pack_forget()

    main_window.mainloop()


if __name__ == '__main__':
    main()
