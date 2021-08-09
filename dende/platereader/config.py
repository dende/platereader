import pathlib

import appdirs
import yaml


class Config:

    def __init__(self):
        self.appdir = appdirs.AppDirs("platerader", "dende", roaming=True)
        self.path = pathlib.Path(self.appdir.user_config_dir)

        self.path.mkdir(parents=True, exist_ok=True)

        self.file = self.path / "conf.yaml"

        if not self.file.is_file():
            open(self.file, 'a').close()

    def load_color_for_sample(self, sample):
        raise NotImplementedError()
        with open(self.file, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
                print(config)
            except yaml.YAMLError as exc:
                print(exc)

    def save_color_for_sample(self, sample, color):
        raise NotImplementedError()
