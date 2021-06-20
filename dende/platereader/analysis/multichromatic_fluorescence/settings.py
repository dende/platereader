from dende.platereader.analysis.multichromatic_fluorescence.optic_settings \
    import create_multichromatic_fluorescence_optic_settings


class MultichromaticFluorescenceSettings():

    def __init__(self, number_of_cycles, cycle_time, number_of_flashes_per_well_and_cycle, scan_mode,
                 scan_diameter, optic_settings):
        self.number_of_cycles = number_of_cycles
        self.cycle_time = cycle_time
        self.number_of_flashes_per_well_and_cycle = number_of_flashes_per_well_and_cycle
        self.scan_mode = scan_mode
        self.scan_diameter = scan_diameter
        self.optic_settings = optic_settings


def create_multichromatic_flourescence_settings(proto_info_sheet):
    number_of_cycles = proto_info_sheet[1][19]
    cycle_time = proto_info_sheet[1][20]
    number_of_flashes_per_well_and_cycle = proto_info_sheet[1][21]
    scan_mode = proto_info_sheet[1][24]
    scan_diameter = proto_info_sheet[1][25]

    optic_settings = create_multichromatic_fluorescence_optic_settings(proto_info_sheet)

    return MultichromaticFluorescenceSettings(number_of_cycles, cycle_time, number_of_flashes_per_well_and_cycle,
                                              scan_mode, scan_diameter, optic_settings)
