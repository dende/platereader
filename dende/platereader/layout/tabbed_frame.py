import logging
from tkinter import ttk

from .settings import Settings

logger = logging.getLogger(__name__)


class TabbedFrame:
    frame = None
    notebook = None

    def __init__(self, notebook, settings: Settings, text):
        self.notebook = notebook
        self.settings = settings
        self.text = text
        self.frame = ttk.Frame(notebook)
        self.frame.pack(side="bottom", fill="both", expand=True)
        self.notebook.add(self.frame, text=text)

    def get_text(self):
        return self.text

    def draw(self):
        pass
