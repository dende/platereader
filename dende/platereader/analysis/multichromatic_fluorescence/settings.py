import dende.platereader.analysis.multichromatic_fluorescence
from dende.platereader.analysis.multichromatic_fluorescence.optic_settings import OpticSettings
from dende.platereader.protocol_info import ProtocolInfo


class MultichromaticFluorescenceSettings(ProtocolInfo):

    def __init__(self, proto_info_sheet):
        super().__init__(proto_info_sheet)
        if self.measurement_type != dende.platereader.analysis.multichromatic_fluorescence.ANALYSIS_TYPE:
            raise("Trying to create a MultichromaticFluorescenceSettings "
                  f"Object with measurement type {self.measurement_type}")
        self.number_of_cycles = proto_info_sheet[1][19]
        self.cycle_time = proto_info_sheet[1][20]
        self.number_of_flashes_per_well_and_cycle = proto_info_sheet[1][21]
        self.scan_mode = proto_info_sheet[1][24]
        self.scan_diameter = proto_info_sheet[1][25]

        self.optic_settings = OpticSettings(proto_info_sheet)
        self.test = "ASLDJK"
        pass
