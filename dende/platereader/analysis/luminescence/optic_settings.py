from typing import Dict

import dende.platereader.helper as helper


class Emission(helper.EqualsMixin):

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

    def get_description(self):
        return f"{self.wavelength}nm" if self.filter else self.__str__()

    def __str__(self):
        if self.filter:
            return f"{self.wavelength}-{self.bandwidth}"
        else:
            return "No filter"

    def __key(self):
        return self.filter, self.wavelength, self.bandwidth


class OpticPreset(helper.EqualsMixin):

    def __init__(self, name, emission, gain, preset_number):
        self.name = name
        self.emission = Emission(emission)
        self.gain = gain
        self.preset_number = preset_number

    def __str__(self):
        return f"Raw Data ({self.emission} {self.preset_number})"

    def __key(self):
        return self.name, self.emission, self.gain, self.preset_number


class OpticDiff(helper.EqualsMixin):

    def __init__(self, minuend: OpticPreset, subtrahend: OpticPreset):
        self.minuend = minuend
        self.subtrahend = subtrahend

    def __key(self):
        return self.minuend, self.subtrahend

    def __str__(self):
        return f"{self.minuend}|{self.subtrahend}"


class OpticSettings(helper.EqualsMixin):

    def __init__(self, presets: Dict[int, OpticPreset], wells_used_for_gain_adjustment: int = None,
                 focal_height: int = None):
        self.presets = presets
        self.wells_used_for_gain_adjustment = wells_used_for_gain_adjustment
        self.focal_height = focal_height

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

    def get_filter_setting(self) -> (int, OpticPreset):
        for key, setting in self.presets.items():
            if setting.emission.filter:
                return key, setting
        return None

    def get_no_filter_setting(self) -> (int, OpticPreset):
        for key, setting in self.presets.items():
            if not setting.emission.filter:
                return key, setting
        return None

    def __key(self):
        return self.presets, self.wells_used_for_gain_adjustment, self.focal_height


def create_luminescence_optic_settings(proto_info_sheet):
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
        presets[i] = OpticPreset(row["Presetname"], row["Emission"], row["Gain"], i)

    wells_used_for_gain_adjustment = proto_info_sheet[1][optic_end + 2]
    focal_height = proto_info_sheet[1][optic_end + 3]

    return OpticSettings(presets, wells_used_for_gain_adjustment, focal_height)


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def remove_suffix(text: str, suffix):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text


def create_luminescence_optic_settings_from_txt(data):
    presets = {}

    for description in data.keys():
        description = remove_prefix(description, "Raw Data (")
        description = remove_suffix(description, ")")
        parts = description.split(" ")
        preset_num = parts.pop()
        emission = " ".join(parts)
        presets[int(preset_num)] = OpticPreset(None, emission, None, preset_num)

    return OpticSettings(presets, None, None)
