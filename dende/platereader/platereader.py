import logging
import os
import pathlib
import sys
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.messagebox import showinfo

import dende.platereader
import dende.platereader.analysis
import dende.platereader.analysis.fluorescence_spectrum as fs
import dende.platereader.analysis.fluorescence_spectrum.layout as fsl
import dende.platereader.analysis.luminescence as lu
import dende.platereader.analysis.luminescence.layout as lul
import dende.platereader.analysis.multichromatic_fluorescence as mf
import dende.platereader.analysis.multichromatic_fluorescence.layout as mfl
import dende.platereader.layout
import dende.platereader.protocol_info
from dende.platereader.settings import Settings

logger = logging.getLogger(__name__)


class Platereader(tk.Tk):

    root: tk.Tk
    layout: dende.platereader.layout.Layout



    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.title(f"Clariostar analysis v{dende.platereader.__version__}")
        self.resizable(False, False)
        self.geometry('300x150')
        self.protocol("WM_DELETE_WINDOW", self.cleanup)

        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = pathlib.Path(__file__).parent.absolute()

        self.iconbitmap(os.path.join(base_path, 'platereader.ico'))

        open_button = ttk.Button(
            self,
            text='Open a File',
            command=self.select_file
        )

        open_button.pack(expand=True)

    def select_file(self):
        filetypes = (
            ('Clariostar plate reader results', '*.xlsx *.txt'),
        )

        filename = fd.askopenfilename(
            title='Open clariostar plate reader results',
            initialdir=os.getcwd(),
            filetypes=filetypes)

        if not filename:
            return

        logger.info(f"opening file: {filename}")

        try:
            data, proto_info = dende.platereader.protocol_info.open_file(filename)

        except Exception as e:
            showinfo(
                title='Error',
                message=str(e)
            )
            return

        self.resizable(True, True)
        self.geometry("1280x684")
        for widget in self.winfo_children():
            widget.destroy()

        toprow = tk.Frame(self, height=120, name="toprow")
        toprow.pack(side="top", fill="x")

        listbox = tk.Listbox(toprow, width=60, name="details_list")
        i = 0
        for attr_name in dir(proto_info):
            if not attr_name.startswith('__') and attr_name != "settings":
                listbox.insert(i, f"{attr_name}: {getattr(proto_info, attr_name)}")
                i = i + 1

        listbox.pack()

        bottomrow = ttk.Frame(self, name="bottomrow")
        bottomrow.pack(expand=1, fill="both")

        if proto_info and proto_info.measurement_type == fs.ANALYSIS_TYPE:
            self.layout = fsl.FlourescenceSpectrumLayout(self, data, proto_info)

        elif proto_info and proto_info.measurement_type == mf.ANALYSIS_TYPE:
            self.layout = mfl.MultichromaticFluorescenceLayout(self, data, proto_info)

        elif proto_info and proto_info.measurement_type == lu.ANALYSIS_TYPE:
            self.layout = lul.LuminescenceLayout(self, data, proto_info)

    def cleanup(self):
        self.quit()
        self.destroy()
        sys.exit()
