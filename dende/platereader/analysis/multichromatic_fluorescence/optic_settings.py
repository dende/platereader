def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


class DichroicFilter:

    def __init__(self, dichroic_filter):
        dichroic_filter = str(dichroic_filter)
        if dichroic_filter.startswith("F: "):
            self.auto = False
            _, dichroic_filter_parts = dichroic_filter.split(":")
            pass_type, wavelength = dichroic_filter_parts.strip().split(" ")
            self.pass_type = pass_type
            self.wavelength = float(wavelength)
        elif dichroic_filter.startswith("auto "):
            self.auto = True
            self.pass_type = None
            self.wavelength = float(remove_prefix(dichroic_filter, "auto "))
        else:
            self.auto = False
            self.pass_type = None
            self.wavelength = float(dichroic_filter)


class Excitation:

    def __init__(self, excitation):
        _, excitation_parts = excitation.split(":")
        excitation_wavelength, excitation_bandwith = excitation_parts.split("-")
        self.wavelength = int(excitation_wavelength)
        self.bandwidth = int(excitation_bandwith)

    def __str__(self):
        return f"F: {self.wavelength}-{self.bandwidth}"

    def get_description(self):
        return f"{self.wavelength}nm"


class Emission:

    def __init__(self, emission):
        _, emission_parts = emission.split(":")
        emission_wavelength, emission_bandwith = emission_parts.split("-")
        self.wavelength = int(emission_wavelength)
        self.bandwidth = int(emission_bandwith)

    def __str__(self):
        return f"F: {self.wavelength}-{self.bandwidth}"


class OpticPreset:

    def __init__(self, name, excitation, dichroic_filter, emission, gain, preset_number):
        self.name = name
        self.excitation = Excitation(excitation)  # type: Excitation
        self.dichroic_filter = DichroicFilter(dichroic_filter)
        self.emission = Emission(emission)
        self.gain = gain
        self.preset_number = preset_number

    def __str__(self):
        return f"Raw Data ({self.excitation}/{self.emission} {self.preset_number})"


class OpticSettings:

    def __init__(self, presets, wells_used_for_gain_adjustment, focal_height):
        self.presets = presets  # type: dict[int, OpticPreset]
        self.wells_used_for_gain_adjustment = wells_used_for_gain_adjustment
        self.focal_height = focal_height


def create_multichromatic_fluorescence_optic_settings(proto_info_sheet):
    optic_start = None
    optic_end = None
    for i, cell in enumerate(proto_info_sheet[0]):
        cell = str(cell)
        cell = cell.strip()
        if cell == "Optic settings" and optic_start is None:
            optic_start = i

        elif cell == "Optic settings" and optic_start is not None:
            optic_end = i

    optic_settings_subtable = proto_info_sheet.iloc[optic_start + 2:optic_end - 2, :].copy()
    optic_settings_subtable.columns = optic_settings_subtable.iloc[0]
    optic_settings_subtable = optic_settings_subtable.drop(optic_settings_subtable.index[0])
    optic_settings_subtable = optic_settings_subtable.set_index(optic_settings_subtable.columns[0])

    presets = {}

    for i, row in optic_settings_subtable.iterrows():
        presets[i] = OpticPreset(row["Presetname"], row["Excitation"], row["Dichroic filter"], row["Emission"],
                                 row["Gain"], i)

    wells_used_for_gain_adjustment = proto_info_sheet[1][optic_end + 2]
    focal_height = proto_info_sheet[1][optic_end + 3]

    return OpticSettings(presets, wells_used_for_gain_adjustment, focal_height)
