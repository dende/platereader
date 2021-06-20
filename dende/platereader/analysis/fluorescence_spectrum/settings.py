from dende.platereader.analysis.fluorescence_spectrum.optic_settings import OpticSettings


class FluorescenceSpectrumSettings:

    def __init__(self, proto_info_sheet):
        self.flashes_per_well = proto_info_sheet[1][19]
        self.preset_name = proto_info_sheet[1][24]
        self.no_wavelength_scanpoints = proto_info_sheet[1][25]
        self.excitation_wavelength = proto_info_sheet[1][26]
        self.excitation_bandwith = proto_info_sheet[1][27]
        self.emission_wavelength = proto_info_sheet[1][28]
        self.emission_bandwidth = proto_info_sheet[1][24]

        self.optic_settings = OpticSettings(proto_info_sheet)
