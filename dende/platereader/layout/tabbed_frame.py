import abc
import logging
import tkinter as tk
from tkinter import ttk

from .settings import Settings

logger = logging.getLogger(__name__)


class TabbedFrame(abc.ABC):
    frame: ttk.Frame
    notebook: ttk.Notebook

    def __init__(self, root: tk.Tk, settings: Settings, text: str):
        self.root = root
        self.notebook = root.nametowidget("bottomrow.notebook")
        self.settings = settings
        self.text = text
        self.frame = ttk.Frame(self.notebook, name=text.lower())
        self.frame.pack(side="bottom", fill="both", expand=True)
        self.notebook.add(self.frame, text=text)

    def get_text(self):
        return self.text

    @abc.abstractmethod
    def draw(self):
        pass
