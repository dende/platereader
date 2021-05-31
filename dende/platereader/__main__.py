import logging
import os
import sys
import tkinter as tk
import typing
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.messagebox import showinfo

import dende.platereader.analysis
from dende.platereader.analysis.fluorescence_spectrum import init as fluorescence_spectrum_init
from dende.platereader.analysis.multichromatic_fluorescence import init as multichromatic_fluorescence_init
from dende.platereader.analysis.luminescence import init as luminescence_init

import dende.platereader.protocol_info
from dende.platereader import __version__
from dende.platereader.analysis import FLUORESCENCE_SPECTRUM, MULTICHROMATIC_FLUORESCENCE, LUMINESCENCE

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
        data_sheet, proto_info_sheet = dende.platereader.open_xlsx(filename)
        measurement_settings = dende.platereader.parse_proto_info(proto_info_sheet)

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
    for attr_name in dir(measurement_settings):
        if not attr_name.startswith('__'):
            listbox.insert(i, f"{attr_name}: {getattr(measurement_settings, attr_name)}")
            i = i + 1

    listbox.pack()

    bottomrow = ttk.Frame(root)
    bottomrow.pack(expand=1, fill="both")

    if measurement_settings and measurement_settings.measurement_type == FLUORESCENCE_SPECTRUM:
        fluorescence_spectrum_init(bottomrow, data_sheet, proto_info_sheet)

    elif measurement_settings and measurement_settings.measurement_type == MULTICHROMATIC_FLUORESCENCE:
        multichromatic_fluorescence_init(bottomrow, data_sheet, proto_info_sheet)

    elif measurement_settings and measurement_settings.measurement_type == LUMINESCENCE:
        luminescence_init(bottomrow, data_sheet, proto_info_sheet, listbox)


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
