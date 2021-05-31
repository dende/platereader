class DichroicFilter:

    def __init__(self, dichroic_filter):
        _, dichroic_filter_parts = dichroic_filter.split(":")
        pass_type, wavelength = dichroic_filter_parts.strip().split(" ")
        self.pass_type = pass_type
        self.wavelength = int(wavelength)


class Excitation:

    def __init__(self, excitation):
        _, excitation_parts = excitation.split(":")
        excitation_wavelength, excitation_bandwith = excitation_parts.split("-")
        self.wavelength = int(excitation_wavelength)
        self.bandwidth = int(excitation_bandwith)


class Emission:

    def __init__(self, emission):
        _, emission_parts = emission.split(":")
        emission_wavelength, emission_bandwith = emission_parts.split("-")
        self.wavelength = int(emission_wavelength)
        self.bandwidth = int(emission_bandwith)


class OpticPreset:

    def __init__(self, name, excitation, dichroic_filter, emission, gain):
        self.name = name
        self.excitation = Excitation(excitation)
        self.dichroic_filter = DichroicFilter(dichroic_filter)
        self.emission = Emission(emission)
        self.gain = gain


class OpticSettings:

    def __init__(self, proto_info_sheet):
        optic_start = None
        optic_end = None
        for i, cell in enumerate(proto_info_sheet[0]):
            cell = str(cell)
            cell = cell.strip()
            if cell == "Optic settings" and optic_start is None:
                optic_start = i

            elif cell == "Optic settings" and optic_start is not None:
                optic_end = i

        optic_settings_subtable = proto_info_sheet.iloc[optic_start+2:optic_end-2, :].copy()
        optic_settings_subtable.columns = optic_settings_subtable.iloc[0]
        optic_settings_subtable = optic_settings_subtable.drop(optic_settings_subtable.index[0])
        optic_settings_subtable = optic_settings_subtable.set_index(optic_settings_subtable.columns[0])

        self.presets = {}

        for i, row in optic_settings_subtable.iterrows():
            self.presets[i] = OpticPreset(row["Presetname"], row["Excitation"], row["Dichroic filter"], row["Emission"],
                                          row["Gain"])

        self.wells_used_for_gain_adjustment = proto_info_sheet[1][optic_end + 2]
        self.focal_height = proto_info_sheet[1][optic_end + 3]
