import logging

import pandas as pandas

from dende.platereader.plates import WELL_PLATE_TYPES

logger = logging.getLogger(__name__)


class ProtocolInfo:

    def __init__(self, proto_info_sheet):
        self.test_id = remove_prefix(proto_info_sheet[0][2], "Test ID: ")
        self.test_name = remove_prefix(proto_info_sheet[0][3], "Test Name: ")
        self.date = remove_prefix(proto_info_sheet[0][4], "Date: ")
        self.time = remove_prefix(proto_info_sheet[0][5], "Time: ")
        self.name = remove_prefix(proto_info_sheet[0][6], "ID1: ")
        self.username = remove_prefix(proto_info_sheet[0][7], "ID2: ")
        self.analysis_type = proto_info_sheet[0][8]
        self.measurement_type = proto_info_sheet[1][13]
        self.microplate_name = proto_info_sheet[1][14]

        if self.microplate_name not in WELL_PLATE_TYPES:
            raise(Exception(f"Unknown measurement type: {self.microplate_name}"))


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def read_xlsx(path):
    return pandas.read_excel(path, sheet_name=0, header=None)


def open_xlsx(path):
    xlsx = pandas.read_excel(path, sheet_name=None, header=None)
    proto_info_sheet = xlsx["Protocol Information"]
    for sheet_name, sheet in xlsx.items():
        if sheet_name.startswith("Row"):
            return sheet, proto_info_sheet

    raise Exception("No Sheet with data found. Should start with \"Row X - Row Y\"")


def parse_proto_info(proto_info_sheet):

    protocol_info = ProtocolInfo(proto_info_sheet)

    return protocol_info
