import logging
import tkinter as tk
import typing
from functools import partial

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class WellPlate:
    colors = ["#00876c", "#3d9a70", "#64ad73", "#89bf77", "#afd17c", "#d6e184", "#fff18f",
              "#fdd576", "#fbb862", "#f59b56", "#ee7d4f", "#e35e4e", "#d43d51"]
    frame = None  # type: typing.Optional[tk.Frame]
    layout_frame = None

    def __init__(self, xlsx, settings):
        self.settings = settings
        self.xlsx = xlsx
        self.wells = xlsx.iloc[11:13, 2:].copy().reset_index(drop=True)
        self.wells.columns = range(0, len(self.wells.columns))
        self.well_plate = pd.DataFrame(False, index=["A", "B", "C", "D", "E", "F", "G", "H"], columns=range(1, 13))

        for column in self.wells:
            row_id = self.wells[column][0]
            col_id = self.wells[column][1]
            self.well_plate.loc[row_id, col_id] = True

    def set_layout_frame(self, layout_frame):
        self.layout_frame = layout_frame

    def get_samples(self):
        return self.settings.samples

    def get_well_dict(self):
        well_dict = {}
        for column in self.wells:
            row_id = self.wells[column][0]
            col_id = self.wells[column][1]
            well_dict[f"{row_id}{col_id}"] = column
        return well_dict

    def get_well_mapping(self, well_dict):
        well_mapping = {}
        for column in self.well_plate.columns:
            for index in self.well_plate.index:
                sample_name = self.well_plate.loc[index][column]
                if isinstance(sample_name, str):
                    data_column = well_dict[f"{index}{column}"]
                    if sample_name not in well_mapping:
                        well_mapping[sample_name] = []
                    well_mapping[sample_name].append(data_column)
        return well_mapping

    def get_sample_list(self):
        if self.settings.treatments:
            sample_list = [f"{sample}${treatment}"
                           for sample in self.settings.samples for treatment in self.settings.treatments]
        else:
            sample_list = [f"{sample}" for sample in self.settings.samples]
        return sample_list

    def write_on_canvas(self, canvas, i, j, text):
        canvas.create_text(i * 35 + (35 / 2), j * 35 + (35 / 2), fill="black",
                           font="Helvetica 20 bold", text=text)

    def add_well(self, canvas, i, j, fill=None, handler=None):
        tags = f"{i}${j}"
        canvas.create_circle(i * 35 + (35 / 2), j * 35 + (35 / 2), 15, fill=fill, outline="black", tags=tags)
        if handler:
            canvas.tag_bind(tags, "<Button-1>", handler)

    def draw(self, root):
        # todo(dende): refactor into smaller parts, cyclomatic complexity is 12

        canvas = tk.Canvas(root, width=500, height=360)
        canvas.pack(side=tk.LEFT)

        sample_list = self.get_sample_list()

        # for i in range(len(self.well_plate.columns) + 2):
        #     for j in range(len(self.well_plate.index) + 2):

        well_plate = self.well_plate
        for i, j in [(i, j) for i in range(len(well_plate.columns)+2) for j in range(len(well_plate.index)+2)]:
            if i == 0 and j > 1:
                self.write_on_canvas(canvas, i, j, well_plate.index[j - 2])
            elif j == 0 and i > 1:
                self.write_on_canvas(canvas, i, j, well_plate.columns[i-2])
            elif i > 1 and j > 1:
                well_column = well_plate.columns[i-2]
                well_row = well_plate.index[j-2]
                val = well_plate[well_column][well_row]
                if isinstance(val, np.bool_) or isinstance(val, bool):
                    if val:
                        self.add_well(canvas, i, j, fill="white", handler=partial(self.handle_well_click, j-2, i-2))
                    else:
                        self.add_well(canvas, i, j)
                        self.write_on_canvas(canvas, i, j, "x")
                elif val:
                    sample = val
                    try:
                        sample_index = sample_list.index(sample)
                        color = self.colors[sample_index]
                        self.add_well(canvas, i, j, fill=color, handler=partial(self.handle_well_click, j-2, i-2))
                    except ValueError:
                        # we deleted either the corresponding sample or treatment
                        self.well_plate.iloc[j-2, i-2] = True
                        self.add_well(canvas, i, j, fill=None, handler=partial(self.handle_well_click, j-2, i-2))

    def handle_well_click(self, row, col, event=None):
        self.well_plate.iloc[row, col] = self.settings.selected_sample if \
            self.well_plate.iloc[row, col] != self.settings.selected_sample else True
        self.layout_frame.draw()

    def get_xlsx(self):
        return self.xlsx.copy()

    def get_data(self):
        return self.xlsx.iloc[13:, 1:].copy()


def create_well_plate(xlsx, settings):
    return WellPlate(xlsx, settings)
