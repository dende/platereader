from typing import Optional


class Material:

    def __init__(self, name, control=False):
        self.name = name
        self.control = control

    def __str__(self):
        if self.control:
            return f"*{self.name}*"
        return self.name

    def __eq__(self, other):
        return self.name == other.name and self.control == other.control


class Treatment:

    def __init__(self, name, control=False):
        self.name = name
        self.control = control

    def __str__(self):
        if self.control:
            return f"*{self.name}*"
        return self.name

    def __eq__(self, other):
        return self.name == other.name and self.control == other.control


class Sample:

    def __init__(self, material: Material, treatment: Optional[Treatment] = None):
        self.material = material
        self.treatment = treatment

    def __str__(self):
        if self.treatment is None:
            return f"{self.material}"
        return f"{self.material} with {self.treatment}"

    def __repr__(self):
        return f"{self.material}${self.treatment}"

    def __eq__(self, other):
        return self.material == other.material and self.treatment == other.treatment


def create_sample_from_string(string: str) -> Sample:
    material, treatment = string.split("$")
    if material is None or not material:
        raise TypeError("Material can't be empty")
    if len(material) > 2 and (material[0] == material[-1] == "*"):
        material = Material(material[1:-1], True)
    else:
        material = Material(material)

    if treatment is None or not treatment:
        return Sample(material, None)

    if len(treatment) > 2 and (treatment[0] == treatment[-1] == "*"):
        treatment = Treatment(treatment[1:-1], True)
    else:
        treatment = Treatment(treatment)

    return Sample(material, treatment)