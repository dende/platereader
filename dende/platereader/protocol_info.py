import logging

import pandas as pandas

logger = logging.getLogger(__name__)

measurement_types = ["Fluorescence (FI) spectrum", "Fluorescence (FI), multichromatic"]


def read_xlsx(path):
    return pandas.read_excel(path, sheet_name=0, header=None)


def get_protocol_information_from_xlsx(path):
    xlsx = pandas.read_excel(path, sheet_name=None, header=None)
    protocol_information = xlsx["Protocol Information"]

    proto_info = {
        "test_id": remove_prefix(protocol_information[0][2], "Test ID: "),
        "test_name": remove_prefix(protocol_information[0][3], "Test Name: "),
        "date": remove_prefix(protocol_information[0][4], "Date: "),
        "time": remove_prefix(protocol_information[0][5], "Time: "),
        "name": remove_prefix(protocol_information[0][6], "ID1: "),
        "username": remove_prefix(protocol_information[0][7], "ID2: "),
        "analysis_type": protocol_information[0][8],
        "measurement_type": protocol_information[1][13],
        "microplate_name": protocol_information[1][14],
    }

    return proto_info


def check_protocol_info(proto_info):
    microplate_names = ["NUNC 96"]

    if proto_info["analysis_type"] != proto_info["measurement_type"]:
        logger.error(f"analysis_type: {proto_info['analysis_type']},"
                     f" measurement_type: {proto_info['measurement_type']}")
        raise Exception("analysis type and measurement type specified in the protocol info do not match")

    if proto_info["microplate_name"] not in microplate_names:
        raise Exception(f"Unknown microplate type: {proto_info['microplate_name']}")

    if proto_info["measurement_type"] not in measurement_types:
        raise Exception(f"Unknown measurement type: {proto_info['measurement_type']}")


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever
