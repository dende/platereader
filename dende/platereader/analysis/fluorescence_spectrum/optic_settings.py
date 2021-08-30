class OpticSettings:

    def __init__(self, preset_name, number_of_wavelength_scanpoints, excitation_wavelength, excitation_bandwidth,
                 emission_wavelength, emission_bandwidth, gain, well_used_for_gain_adjustment,
                 wavelength_used_for_gain_adjustment, focal_height):
        self.preset_name = preset_name
        self.number_of_wavelength_scanpoints = number_of_wavelength_scanpoints
        self.excitation_wavelength = excitation_wavelength
        self.excitation_bandwidth = excitation_bandwidth
        self.emission_wavelength = emission_wavelength
        self.emission_bandwidth = emission_bandwidth
        self.gain = gain
        self.well_used_for_gain_adjustment = well_used_for_gain_adjustment
        self.wavelength_used_for_gain_adjustment = wavelength_used_for_gain_adjustment
        self.focal_height = focal_height


def create_fluorescence_spectrum_optic_settings(proto_info_sheet):
    preset_name = proto_info_sheet[1][26]
    number_of_wavelength_scanpoints = proto_info_sheet[1][27]
    excitation_wavelength = proto_info_sheet[1][28]
    excitation_bandwidth = proto_info_sheet[1][29]
    emission_wavelength = proto_info_sheet[1][30]
    emission_bandwidth = proto_info_sheet[1][31]
    gain = proto_info_sheet[1][32]
    well_used_for_gain_adjustment = proto_info_sheet[1][33]
    wavelength_used_for_gain_adjustment = proto_info_sheet[1][34]
    focal_height = proto_info_sheet[1][35]

    return OpticSettings(preset_name, number_of_wavelength_scanpoints, excitation_wavelength, excitation_bandwidth,
                         emission_wavelength, emission_bandwidth, gain, well_used_for_gain_adjustment,
                         wavelength_used_for_gain_adjustment, focal_height)


def create_fluorescence_spectrum_optic_settings_from_txt(data):
    pass

