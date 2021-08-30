import dende.platereader.analysis.fluorescence_spectrum.optic_settings as os


class FluorescenceSpectrumSettings:

    def __init__(self, flashes_per_well, preset_name, no_wavelength_scanpoints, excitation_wavelength,
                 excitation_bandwidth, emission_wavelength, emisssion_bandwidth, optic_settings):
        self.flashes_per_well = flashes_per_well
        self.preset_name = preset_name
        self.no_wavelength_scanpoints = no_wavelength_scanpoints
        self.excitation_wavelength = excitation_wavelength
        self.excitation_bandwidth = excitation_bandwidth
        self.emission_wavelength = emission_wavelength
        self.emisssion_bandwidth = emisssion_bandwidth
        self.optic_settings = optic_settings


def create_fluorescence_spectrum_settings(proto_info_sheet):
    flashes_per_well = proto_info_sheet[1][19]
    preset_name = proto_info_sheet[1][24]
    no_wavelength_scanpoints = proto_info_sheet[1][25]
    excitation_wavelength = proto_info_sheet[1][26]
    excitation_bandwith = proto_info_sheet[1][27]
    emission_wavelength = proto_info_sheet[1][28]
    emission_bandwidth = proto_info_sheet[1][24]

    optic_settings = os.create_fluorescence_spectrum_optic_settings(proto_info_sheet)

    return FluorescenceSpectrumSettings(flashes_per_well, preset_name, no_wavelength_scanpoints, excitation_wavelength,
                                        excitation_bandwith, emission_wavelength, emission_bandwidth, optic_settings)


def create_fluorescence_spectrum_settings_from_txt(df):
    optic_settings = os.create_fluorescence_spectrum_optic_settings_from_txt(df)

    return FluorescenceSpectrumSettings(None, None, None, None, None, None, None, optic_settings)
