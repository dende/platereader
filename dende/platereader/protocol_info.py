import logging
import os
import re
from typing import Dict

import pandas as pandas
import pandas as pd

import dende.platereader.analysis.fluorescence_spectrum as fs
import dende.platereader.analysis.fluorescence_spectrum.settings as fss
import dende.platereader.analysis.multichromatic_fluorescence as mf
import dende.platereader.analysis.luminescence as lu
import dende.platereader.analysis.luminescence.settings as lus
import dende.platereader.analysis.multichromatic_fluorescence.settings as mfs
import dende.platereader.plates as plates

logger = logging.getLogger(__name__)


class ProtocolInfo:

    def __init__(self,
                 test_id, test_name, date, time, name, username, analysis_type,
                 measurement_type, microplate_name, settings):

        self.test_id = test_id
        self.test_name = test_name
        self.date = date
        self.time = time
        self.name = name
        self.username = username
        self.analysis_type = analysis_type
        self.measurement_type = measurement_type
        self.microplate_name = microplate_name
        self.settings = settings

        if self.microplate_name not in plates.WELL_PLATE_TYPES:
            raise(Exception(f"Unknown measurement type: {self.microplate_name}"))


def get_protocol_info_from_txt(datas, proto_info_data):
    test_id = remove_prefix(proto_info_data[0][1], "Test name: ")
    test_name = remove_prefix(proto_info_data[0][1], "Test name: ")
    date = remove_prefix(proto_info_data[1][1], "Date: ")
    time = remove_prefix(proto_info_data[2][1], "Time: ")
    name = remove_prefix(proto_info_data[0][2], "ID1: ")
    username = remove_prefix(proto_info_data[1][2], "ID2: ")
    analysis_type = proto_info_data[0][3]
    measurement_type = proto_info_data[0][3]
    # todo(there is no info about the kind of plate given?!)
    microplate_name = plates.WELL_PLATE_TYPES[0]

    if measurement_type == fs.ANALYSIS_TYPE:
        settings = None # we dont need it?
    elif measurement_type == mf.ANALYSIS_TYPE:
        raise NotImplementedError
    elif measurement_type == lu.ANALYSIS_TYPE:
        settings = lus.create_luminescence_settings_from_txt(datas)
    else:
        raise(Exception(f"Unknown measurement type: {measurement_type}"))

    return ProtocolInfo(
        test_id, test_name, date, time, name, username, analysis_type, measurement_type, microplate_name, settings)


def get_protocol_info(proto_info_sheet):
    test_id = remove_prefix(proto_info_sheet[0][2], "Test ID: ")
    test_name = remove_prefix(proto_info_sheet[0][3], "Test Name: ")
    date = remove_prefix(proto_info_sheet[0][4], "Date: ")
    time = remove_prefix(proto_info_sheet[0][5], "Time: ")
    name = remove_prefix(proto_info_sheet[0][6], "ID1: ")
    username = remove_prefix(proto_info_sheet[0][7], "ID2: ")
    analysis_type = proto_info_sheet[0][8]
    measurement_type = proto_info_sheet[1][13]
    microplate_name = proto_info_sheet[1][14]

    if measurement_type == fs.ANALYSIS_TYPE:
        settings = None
    elif measurement_type == mf.ANALYSIS_TYPE:
        settings = mfs.create_multichromatic_flourescence_settings(proto_info_sheet)
    elif measurement_type == lu.ANALYSIS_TYPE:
        settings = lus.create_luminescence_settings(proto_info_sheet)
    else:
        raise(Exception(f"Unknown measurement type: {measurement_type}"))

    return ProtocolInfo(
        test_id, test_name, date, time, name, username, analysis_type, measurement_type, microplate_name, settings)


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def split_data_into_dict(data):
    content_types = data.iloc[:, 0].unique()

    datas = {}
    for content_type in content_types:
        mask = data.iloc[:, 0].str.contains(content_type.strip(), regex=False, na=False)
        content_type_data = data[mask].copy()
        del content_type_data['Content']
        content_type_data = content_type_data.set_index(content_type_data.columns[0])
        datas[content_type.strip()] = content_type_data

    return datas


def get_data_from_xlsx(data_sheet: pandas.DataFrame):
    data = data_sheet.iloc[13:, 0:].copy()  # type: pandas.DataFrame
    data = data.reset_index(drop=True)
    well_infos = data_sheet.iloc[11:13, 2:].copy()
    well_infos = well_infos.reset_index(drop=True)
    for column in well_infos:
        well_letter = well_infos.loc[0, column]
        well_number = well_infos.loc[1, column]
        well_identifier = f"{well_letter}{well_number:02}"  # eg. G09 or E11
        data.loc[0, column] = well_identifier

    data = data.rename(columns=data.iloc[0]).drop(data.index[0]).reset_index(drop=True)  # make the first row the header

    datas = split_data_into_dict(data)
    return datas


def get_data_and_proto_info_from_txt(df):

    proto_info_data = df.iloc[0:4, :].copy()
    proto_info_data = proto_info_data.dropna(axis=1, how='all')

    data = df.iloc[4:, :].copy()
    data = data.reset_index(drop=True)
    data = data.transpose()

    well_infos = data.iloc[0:1, 2:].copy()
    well_infos = well_infos.reset_index(drop=True)

    data = data.iloc[1:, :]
    data = data.reset_index(drop=True)

    for column in well_infos:
        well_identifier = well_infos.loc[0, column]
        data.loc[0, column] = well_identifier

    data = data.rename(columns=data.iloc[0]).drop(data.index[0]).reset_index(drop=True)  # make the first row the header

    pattern = re.compile(r"(?P<minutes>\d+) min ((?P<seconds>\d+) s)?")

    def convert_time(timestring):
        findings = [m.groupdict() for m in pattern.finditer(timestring)][0]
        time_in_seconds = int(findings['minutes']) * 60
        if findings['seconds'] is not None:
            time_in_seconds = time_in_seconds + int(findings['seconds'])
        return time_in_seconds

    if "Time" in data:
        data['Time'] = data['Time'].map(convert_time)
        data = data.rename(columns={"Time": "Time [s]"})

    for col in data:
        if col != "Content":
            data[col] = data[col].astype(float)

    datas = split_data_into_dict(data)

    proto_info = get_protocol_info_from_txt(datas, proto_info_data)

    return datas, proto_info


def open_file(path: str) -> (Dict[str, pd.DataFrame], ProtocolInfo):
    filename = os.path.basename(path)
    filename, extension = os.path.splitext(filename)
    logger.info(f"{filename}, {extension}")

    if extension == ".xlsx":
        xlsx = pandas.read_excel(path, sheet_name=None, header=None)
        proto_info_sheet = xlsx["Protocol Information"]
        for sheet_name, sheet in xlsx.items():
            if sheet_name.startswith("Row"):
                data = get_data_from_xlsx(sheet)
                proto_info = get_protocol_info(proto_info_sheet)
                return data, proto_info

    elif extension == ".txt":
        # find out which delimiter is used with a very sophisticated heuristic
        with open(path, 'r') as f:
            commas, semicolons = 0, 0
            for line in f.readlines():
                commas += line.count(",")
                semicolons += line.count(";")

        delimiter = ","
        if semicolons > commas:
            delimiter = ";"
            logger.info("Using semicolon as delimiter")

        with open(path, 'r') as f:
            col_count = [len(line.split(delimiter)) for line in f.readlines()]

        column_names = [i for i in range(0, max(col_count)-1)]

        csv = pandas.read_csv(path, header=None, delimiter=delimiter, names=column_names)

        data, proto_info = get_data_and_proto_info_from_txt(csv)
        return data, proto_info

    raise Exception("No Sheet with data found. Should start with \"Row X - Row Y\"")
