import dende.platereader.analysis.luminescence
from dende.platereader.analysis.luminescence.optic_settings import OpticSettings
from dende.platereader.protocol_info import ProtocolInfo


class LuminescenceSettings(ProtocolInfo):

    def __init__(self, proto_info_sheet):
        super().__init__(proto_info_sheet)
        if self.measurement_type != dende.platereader.analysis.luminescence.ANALYSIS_TYPE:
            raise(Exception("Trying to create a LuminescenceSettings "
                  f"Object with measurement type {self.measurement_type}"))
        self.number_of_cycles = proto_info_sheet[1][19]
        self.cycle_time = proto_info_sheet[1][20]
        self.measurement_interval_time = proto_info_sheet[1][21]
        self.scan_mode = proto_info_sheet[1][24]
        self.scan_diameter = proto_info_sheet[1][25]

        self.optic_settings = OpticSettings(proto_info_sheet)
