from typing import Optional


class Material:

    def __init__(self, name, control=False):
        self.name = name
        self.control = control

    def __str__(self):
        if self.control:
            return f"*{self.name}*"
        return self.name

    def __key(self):
        return self.name, self.control

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Material):
            return self.__key() == other.__key()
        return NotImplemented


class Treatment:

    def __init__(self, name, control=False):
        self.name = name
        self.control = control

    def __str__(self):
        if self.control:
            return f"*{self.name}*"
        return self.name

    def __key(self):
        return self.name, self.control

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Treatment):
            return self.__key() == other.__key()
        return NotImplemented


class Sample:

    def __init__(self, material: Material, treatment: Optional[Treatment] = None):
        self.material = material
        self.treatment = treatment

    def __str__(self):
        return f"{self.material}${self.treatment}"

    def __repr__(self):
        return self.__str__()

    def get_description(self):
        if self.treatment is None:
            return f"{self.material}"
        return f"{self.material.name} with {self.treatment}"

    def __key(self):
        return self.material, self.treatment

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Sample):
            return self.__key() == other.__key()
        return NotImplemented

    def __lt__(self, other):
        if self.material.control and not other.material.control:
            return True
        if not self.material.control and other.material.control:
            return False
        return self.__str__() < other.__str__()


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