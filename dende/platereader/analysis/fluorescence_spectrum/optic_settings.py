class OpticSettings:

    def __init__(self, proto_info_sheet):
        self.preset_name = proto_info_sheet[1][26]
        self.number_of_wavelength_scanpoints = proto_info_sheet[1][27]
        self.excitation_wavelength = proto_info_sheet[1][28]
        self.excitation_bandwidth = proto_info_sheet[1][29]
        self.emission_wavelength = proto_info_sheet[1][30]
        self.emission_bandwidth = proto_info_sheet[1][31]
        self.gain = proto_info_sheet[1][32]
        self.well_used_for_gain_adjustment = proto_info_sheet[1][33]
        self.wavelength_used_for_gain_adjustment = proto_info_sheet[1][34]
        self.focal_height = proto_info_sheet[1][35]
