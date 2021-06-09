import tkinter as tk
from .nunc96 import WELL_PLATE_NAME as NUNC96_NAME
from .nunc96.well_plate import create_well_plate as create_nunc96_plate  # noqa


def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)


tk.Canvas.create_circle = _create_circle


def create_well_plate(data, proto_info, settings):
    return create_nunc96_plate(data, proto_info, settings)


WELL_PLATE_TYPES = [
    NUNC96_NAME
]
