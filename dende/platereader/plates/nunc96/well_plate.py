import logging
import re
import tkinter as tk
import typing
from collections import defaultdict

import numpy as np
import pandas as pd

import dende.platereader.protocol_info as pi
import dende.platereader.analysis.sample

logger = logging.getLogger(__name__)


class Well:

    def __init__(self, well_plate, cur_col, cur_idx):
        self.well_plate = well_plate
        self.well_column = self.well_plate.well_plate.columns[cur_col]
        self.well_row = self.well_plate.well_plate.index[cur_idx]
        self.val = self.well_plate.well_plate[self.well_column][self.well_row]
        self.cur_col = cur_col
        self.cur_idx = cur_idx
        self.i = cur_col + 2
        self.j = cur_idx + 2
        self.circle = None
        self.draw()

    def draw(self):

        if self.circle:
            self.well_plate.canvas.delete(self.circle)

        samples = self.well_plate.settings.get_samples()

        if isinstance(self.val, np.bool_) or isinstance(self.val, bool):
            if self.val:
                self.circle = self.draw_circle(fill="white", handler=self.handle_well_click, hover=self.mouseover)
            else:
                self.circle = self.draw_circle(fill="black")
        elif self.val:
            sample = self.val
            try:
                sample_index = samples.index(sample)
                color = self.well_plate.colors[sample_index]
                self.circle = self.draw_circle(fill=color, handler=self.handle_well_click, hover=self.mouseover)
            except ValueError:
                # we deleted either the corresponding sample or treatment
                self.well_plate.well_plate.iloc[self.cur_idx, self.cur_col] = True
                self.circle = self.draw_circle(fill=None, handler=self.handle_well_click)

    def draw_circle(self, fill=None, handler=None, hover=None):
        tags = f"{self.i}${self.j}"
        circle = self.well_plate.canvas.create_circle(self.i * 35 + (35 / 2), self.j * 35 + (35 / 2), 15, fill=fill,
                                                      outline="black", tags=tags)
        if handler:
            self.well_plate.canvas.tag_bind(tags, "<Button-1>", handler)
        if hover:
            self.well_plate.canvas.tag_bind(tags, '<Enter>', hover)
        return circle

    def mouseover(self, event):
        self.well_plate.layout_frame.update_preview(self.well_row, self.well_column)

    def handle_well_click(self, event=None):
        if self.val == self.well_plate.settings.selected_sample:
            self.well_plate.well_plate.loc[self.well_row, self.well_column] = True
            self.val = True
        else:
            if self.well_plate.settings.selected_sample:
                self.well_plate.well_plate.loc[
                    self.well_row, self.well_column] = self.well_plate.settings.selected_sample
                self.val = self.well_plate.settings.selected_sample

        self.draw()


class WellPlate:
    colors = ["#00876c", "#3d9a70", "#64ad73", "#89bf77", "#afd17c", "#d6e184", "#fff18f",
              "#fdd576", "#fbb862", "#f59b56", "#ee7d4f", "#e35e4e", "#d43d51"]
    frame = None  # type: typing.Optional[tk.Frame]
    layout_frame = None
    proto_info: pi.ProtocolInfo

    def __init__(self, data, proto_info, settings):
        self.data = data
        self.proto_info = proto_info
        self.settings = settings
        self.samples = self.settings.get_samples()
        self.named_data = None
        self.merged_data = None
        self.wells = list(self.data.values())[0].columns.values.tolist()
        self.well_plate = pd.DataFrame(False, index=["A", "B", "C", "D", "E", "F", "G", "H"], columns=range(1, 13))
        self.well_objects = pd.DataFrame(False, index=["A", "B", "C", "D", "E", "F", "G", "H"], columns=range(1, 13))
        self.canvas = None
        self.last = None
        self.assigned_samples = None

        for identifier in self.wells:
            row_id = identifier[0]
            col_id = int(identifier[1:])
            self.well_plate.loc[row_id, col_id] = True

    def set_layout_frame(self, layout_frame):
        self.layout_frame = layout_frame

    def get_wells(self):
        return self.wells

    def get_well_mapping(self):
        well_mapping = defaultdict(list)
        for well_number in self.well_plate.columns:
            for well_letter in self.well_plate.index:
                sample_name = self.well_plate.loc[well_letter][well_number]
                if isinstance(sample_name, dende.platereader.analysis.sample.Sample):
                    well_identifier = f"{well_letter}{well_number:02}"
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
        canvas.create_text(i * 35 + (35 / 2), j * 35 + (35 / 2), fill="black", font="Helvetica 20 bold", text=text)

    def draw(self, root):

        self.canvas = tk.Canvas(root, width=500, height=360)
        self.canvas.pack(side=tk.LEFT)

        well_plate = self.well_plate
        for i, j in [(i, j) for i in range(len(well_plate.columns) + 2) for j in range(len(well_plate.index) + 2)]:
            cur_col = i - 2
            cur_idx = j - 2
            if i == 0 and j > 1:
                self.write_on_canvas(self.canvas, i, j, well_plate.index[cur_idx])
            elif j == 0 and i > 1:
                self.write_on_canvas(self.canvas, i, j, well_plate.columns[cur_col])
            elif i > 1 and j > 1:
                well_column = well_plate.columns[cur_col]
                well_row = well_plate.index[cur_idx]
                self.well_objects.loc[well_column, well_row] = Well(self, cur_col, cur_idx)

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
                named_data[content_type] = \
                    named_data[content_type][named_data[content_type].columns.difference(unused_column_names)]
            self.named_data = named_data
        return self.named_data.copy()

    def get_merged_data(self) -> pd.DataFrame:
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

    def get_assigned_samples(self):
        well_mapping = self.get_well_mapping()
        return list(well_mapping.keys())

    def has_autofluorescence(self):
        for sample in self.get_assigned_samples():
            if sample.material.control:
                for othersample in self.get_assigned_samples():
                    if sample.material.name != othersample.material.name and not othersample.material.control:
                        return True

        return False

    def has_control_for_sample(self, sample):
        samples = self.get_assigned_samples()
        if sample.material.control:
            return False
        control = self.settings.control
        control_sample = dende.platereader.analysis.sample.Sample(
            dende.platereader.analysis.sample.Material(control, True),
            sample.treatment)

        return control_sample in samples


def create_well_plate(data, proto_info, settings):
    return WellPlate(data, proto_info, settings)
