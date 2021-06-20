from dende.platereader.analysis.sample import Sample, Material, Treatment


class Settings:

    def __init__(self, materials=None, control=None, treatments=None, treatment_control=None, selected_sample=None):
        self.materials = materials if materials is not None else ["", "", "", "", "", ""]
        self.control = control
        self.treatments = treatments if treatments is not None else ["", "", ""]
        self.treatment_control = treatment_control
        self.selected_sample = selected_sample

    def get_samples(self) -> [Sample]:
        materials = list(filter(None, self.materials))
        treatments = list(filter(None, self.treatments))

        samples = []
        for material_name in materials:
            material = Material(material_name, material_name == self.control)
            if treatments:
                for treatment_name in treatments:
                    treatment = Treatment(treatment_name, treatment_name == self.treatment_control)
                    samples.append(Sample(material=material, treatment=treatment,))
            else:
                samples.append(Sample(material=material))
        return samples