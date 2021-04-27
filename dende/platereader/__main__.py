import logging
import os
import sys
import tkinter as tk
import typing
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.messagebox import showinfo

import dende.platereader.flourescence_spectrum
import dende.platereader.protocol_info
import dende.platereader.time_course
from dende.platereader import __version__

root = None  # type: typing.Optional[tk.Tk]

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S')
logger = logging.getLogger()


def select_file():
    global root
    filetypes = (
        ('Clariostar plate reader results', '*.xlsx'),
    )

    filename = fd.askopenfilename(
        title='Open clariostar plate reader results',
        initialdir=os.getcwd(),
        filetypes=filetypes)

    logger.info(f"opening file: {filename}")

    try:
        proto_info = dende.platereader.get_protocol_information_from_xlsx(filename)
        dende.platereader.check_protocol_info(proto_info)
        xlsx = dende.platereader.read_xlsx(filename)

    except Exception as e:
        showinfo(
            title='Error',
            message=str(e)
        )
        return

    root.resizable(True, True)
    root.geometry("684x684")
    for widget in root.winfo_children():
        widget.destroy()

    toprow = tk.Frame(root, height=120)
    toprow.pack(side="top", fill="x")

    listbox = tk.Listbox(toprow, width=60)
    i = 0
    for key, value in proto_info.items():
        listbox.insert(i, f"{key}: {value}")
        i = i + 1

    listbox.pack()

    bottomrow = ttk.Frame(root)
    bottomrow.pack(expand=1, fill="both")

    if proto_info and proto_info["measurement_type"] == "Fluorescence (FI) spectrum":
        dende.platereader.flourescence_spectrum.init(bottomrow, xlsx)

    if proto_info and proto_info["measurement_type"] == "Fluorescence (FI), multichromatic":
        dende.platereader.time_course.init(bottomrow, xlsx)


def main():
    global root
    # create the root window
    root = tk.Tk()
    root.title(f"Clariostar analysis v{__version__}")
    root.resizable(False, False)
    root.geometry('300x150')
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    root.iconbitmap(os.path.join(base_path, 'platereader.ico'))

    open_button = ttk.Button(
        root,
        text='Open a File',
        command=select_file
    )

    open_button.pack(expand=True)

    # run the application
    root.mainloop()


if __name__ == "__main__":
    main()
