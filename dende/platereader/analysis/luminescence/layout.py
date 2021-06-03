import logging
from functools import partial
from tkinter import ttk

from .plot_frame import PlotFrame
from dende.platereader.layout import LayoutFrame, SamplesFrame, TreatmentsFrame, Settings
from dende.platereader.plates import create_well_plate
from .settings import LuminescenceSettings

logger = logging.getLogger(__name__)


def init(window, xlsx, proto_info_sheet, listbox):
    luminescence_settings = LuminescenceSettings(proto_info_sheet)
    root = window

    notebook = ttk.Notebook(root)
    settings = Settings(treatments=["", "", "", "", ""])

    well_plate = create_well_plate(xlsx, settings)

    samples_frame = SamplesFrame(notebook, settings)
    treatments_frame = TreatmentsFrame(notebook, settings)
    layout_frame = LayoutFrame(notebook, settings, well_plate,
                               continue_function=lambda n=notebook, w=well_plate, ls=luminescence_settings, lb=listbox:
                               draw_plot_window(n, w, ls, lb))

    samples_frame.draw()
    treatments_frame.draw()

    notebook.pack(expand=1, fill="both")

    frames = {frame.get_text(): frame for frame in [samples_frame, treatments_frame, layout_frame]}

    notebook.bind('<<NotebookTabChanged>>', partial(tab_change, frames))


def tab_change(frames, event):
    tab = None
    try:
        tab = event.widget.tab('current')['text']
    except Exception as e:
        # tab not found, probably because we deleted all tabs
        logger.warning(f"could not find the tab {e}")

    logger.info(f"changed to tab {tab}")

    if tab == "Layout":
        frames["Samples"].collect_samples()
        frames["Treatments"].collect_treatments()
        frames.get(tab).draw()
    elif tab == "Samples":
        frames["Treatments"].collect_treatments()
        frames.get(tab).draw()
    elif tab == "Treatments":
        frames["Samples"].collect_samples()
        frames.get(tab).draw()


def draw_plot_window(notebook, well_plate, luminescence_settings, listbox):
    for widget in notebook.winfo_children():
        widget.destroy()
    plot_frame = PlotFrame(notebook, well_plate.settings, well_plate, luminescence_settings, listbox)
    plot_frame.draw()
