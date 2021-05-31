class Settings:

    def __init__(self, samples=None, control=None, treatments=None, treatment_control=None, selected_sample=None):
        self.samples = samples if samples is not None else ["", "", "", "", "", ""]
        self.control = control
        self.treatments = treatments if treatments is not None else ["", "", ""]
        self.treatment_control = treatment_control
        self.selected_sample = selected_sample
