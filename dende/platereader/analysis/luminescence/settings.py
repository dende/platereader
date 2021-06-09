from dende.platereader.analysis.luminescence.optic_settings import create_luminescence_optic_settings, \
    create_luminescence_optic_settings_from_txt


class LuminescenceSettings():

    def __init__(self, number_of_cycles, cycle_time, measurement_interval_time, scan_mode, scan_diameter, optic_settings):
        self.number_of_cycles = number_of_cycles
        self.cycle_time = cycle_time
        self.measurement_interval_time = measurement_interval_time
        self.scan_mode = scan_mode
        self.scan_diameter = scan_diameter
        self.optic_settings = optic_settings


def create_luminescence_settings(proto_info_sheet):
    number_of_cycles = proto_info_sheet[1][19]
    cycle_time = proto_info_sheet[1][20]
    measurement_interval_time = proto_info_sheet[1][21]
    scan_mode = proto_info_sheet[1][24]
    scan_diameter = proto_info_sheet[1][25]

    optic_settings = create_luminescence_optic_settings(proto_info_sheet)

    return LuminescenceSettings(number_of_cycles, cycle_time, measurement_interval_time, scan_mode, scan_diameter,
                                optic_settings)


def create_luminescence_settings_from_txt(df):
    optic_settings = create_luminescence_optic_settings_from_txt(df)

    return LuminescenceSettings(None, None, None, None, None, optic_settings)
