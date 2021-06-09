import logging
from functools import partial
from tkinter import ttk

from .plot_frame import PlotFrame
from dende.platereader.layout import LayoutFrame, SamplesFrame, TreatmentsFrame, Settings
from dende.platereader.plates import create_well_plate

logger = logging.getLogger(__name__)


def init(root, data, proto_info):


    notebook = ttk.Notebook(root)
    treatments = ["No Treatment", "H202", "DTT"]
    settings = Settings(treatments=treatments, treatment_control=treatments[0])

    well_plate = create_well_plate(data, proto_info, settings)

    samples_frame = SamplesFrame(notebook, settings)
    treatments_frame = TreatmentsFrame(notebook, settings)
    layout_frame = LayoutFrame(notebook, settings, well_plate,
                               continue_function=lambda notebook=notebook, well_plate=well_plate:
                               draw_plot_window(notebook, well_plate))

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


def draw_plot_window(notebook, well_plate):
    for widget in notebook.winfo_children():
        widget.destroy()
    plot_frame = PlotFrame(notebook, well_plate.settings, well_plate)
    plot_frame.draw()
