
class Emission:

    def __init__(self, emission):
        try:
            emission_wavelength, emission_bandwith = emission.split("-")
            self.filter = True
            self.wavelength = int(emission_wavelength)
            self.bandwidth = int(emission_bandwith)
        except ValueError:
            self.filter = False
            self.wavelength = None
            self.bandwidth = None

    def __str__(self):
        if self.filter:
            return f"{self.wavelength}-{self.bandwidth}"
        else:
            return "No filter"


class OpticPreset:

    def __init__(self, name, emission,  gain):
        self.name = name
        self.emission = Emission(emission)
        self.gain = gain

    def __str__(self):
        return f"({self.name}) Emission: {self.emission}, Gain: {self.gain}"


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

        self.presets = {}  # type:dict[OpticPreset]

        for i, row in optic_settings_subtable.iterrows():
            self.presets[i] = OpticPreset(row["Presetname"], row["Emission"], row["Gain"])

        self.wells_used_for_gain_adjustment = proto_info_sheet[1][optic_end + 2]
        self.focal_height = proto_info_sheet[1][optic_end + 3]

    def has_filter_setting(self):
        for setting in self.presets.values():
            if setting.emission.filter:
                return True
        return False

    def has_no_filter_setting(self):
        for setting in self.presets.values():
            if not setting.emission.filter:
                return True
        return False

    def get_filter_setting(self):
        for key, setting in self.presets.items():
            if setting.emission.filter:
                return key, setting
        return None

    def get_no_filter_setting(self):
        for key, setting in self.presets.items():
            if not setting.emission.filter:
                return key, setting
        return None
