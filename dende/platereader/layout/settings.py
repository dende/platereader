from dende.platereader.analysis.sample import Sample


class Settings:

    def __init__(self, materials=None, control=None, treatments=None, treatment_control=None, selected_sample=None):
        self.materials = materials if materials is not None else ["", "", "", "", "", ""]
        self.control = control
        self.treatments = treatments if treatments is not None else ["", "", ""]
        self.treatment_control = treatment_control
        self.selected_sample = selected_sample

    def get_samples(self):
        materials = list(filter(None, self.materials))
        treatments = list(filter(None, self.treatments))

        samples = []
        for material in materials:
            if treatments:
                for treatment in treatments:
                    samples.append(Sample(material=material, treatment=treatment,))
            else:


        pass
