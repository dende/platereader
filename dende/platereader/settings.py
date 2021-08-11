import pathlib

import appdirs
import yaml


class Settings:

    def __init__(self):
        self.appdir = appdirs.AppDirs("platerader", "dende", roaming=True)
        self.path = pathlib.Path(self.appdir.user_config_dir)

        self.path.mkdir(parents=True, exist_ok=True)

        self.file = self.path / "settings.yaml"

        if not self.file.is_file():
            open(self.file, 'a').close()

        with open(self.file, 'r') as stream:
            try:
                self.settings = yaml.safe_load(stream)
                print(self.settings)
            except yaml.YAMLError as exc:
                print(exc)

    def load_color_for_sample(self, sample):
        raise NotImplementedError()
        # with open(self.file, 'r') as stream:
        #     try:
        #         config = yaml.safe_load(stream)
        #         print(config)
        #     except yaml.YAMLError as exc:
        #         print(exc)

    def save_color_for_sample(self, sample, color):
        raise NotImplementedError()

    def get_latex_mode(self):
        return self.settings['latex-mode']
