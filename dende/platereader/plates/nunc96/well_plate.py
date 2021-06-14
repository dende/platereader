import logging
import re
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

    def __init__(self, data, proto_info, settings):
        self.data = data
        self.proto_info = proto_info
        self.settings = settings
        self.named_data = None
        self.merged_data = None
        self.wells = list(self.data.values())[0].columns.values.tolist()
        self.well_plate = pd.DataFrame(False, index=["A", "B", "C", "D", "E", "F", "G", "H"], columns=range(1, 13))

        for identifier in self.wells:
            row_id = identifier[0]
            col_id = int(identifier[1:])
            self.well_plate.loc[row_id, col_id] = True

    def set_layout_frame(self, layout_frame):
        self.layout_frame = layout_frame

    def get_samples(self):
        return self.settings.materials

    def get_wells(self):
        return self.wells

    def get_well_mapping(self):
        well_mapping = {}
        for well_number in self.well_plate.columns:
            for well_letter in self.well_plate.index:
                sample_name = self.well_plate.loc[well_letter][well_number]
                if isinstance(sample_name, str):
                    well_identifier = f"{well_letter}{well_number:02}"
                    if sample_name not in well_mapping:
                        well_mapping[sample_name] = []
                    well_mapping[sample_name].append(well_identifier)
        return well_mapping

    def get_sample_list(self):
        if self.settings.treatments:
            sample_list = [f"{sample}${treatment}"
                           for sample in self.settings.materials for treatment in self.settings.treatments]
        else:
            sample_list = [f"{sample}" for sample in self.settings.materials]
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

    def get_data(self):
        return self.data.copy()

    def get_named_data(self):
        if self.named_data is None:
            pattern = re.compile("^[A-Z][0-9]{2}$")
            named_data = self.data.copy()
            well_mapping = self.get_well_mapping()

            rename_dict = {column: f"{sample}§{i}"
                           for sample, columns in well_mapping.items()
                           for i, column in enumerate(columns)}

            for content_type in named_data:
                named_data[content_type].rename(columns=rename_dict, inplace=True)
                column_names = list(named_data[content_type].columns.values)
                unused_column_names = [column_name for column_name in column_names if pattern.match(column_name)]
                named_data[content_type] =\
                    named_data[content_type][named_data[content_type].columns.difference(unused_column_names)]
            self.named_data = named_data
        return self.named_data.copy()

    def get_merged_data(self):
        if self.merged_data is None:
            named_data = self.get_named_data()

            for lens_setting, df in named_data.items():
                if self.merged_data is None:
                    self.merged_data = df.copy()
                    self.merged_data.rename(columns=lambda x, ls=lens_setting: f"{ls}!{x}", inplace=True)
                else:
                    data = df.copy()
                    data.rename(columns=lambda x, ls=lens_setting: f"{ls}!{x}", inplace=True)
                    self.merged_data = pd.concat([self.merged_data, data], axis=1)
        return self.merged_data.copy()

def create_well_plate(data, proto_info, settings):
    return WellPlate(data, proto_info, settings)
