import io
import os.path

from setuptools import setup, find_namespace_packages


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with io.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name='dende-platereader',
    version=get_version("dende/platereader/__init__.py"),
    packages=find_namespace_packages(include=['dende.*']),
    install_requires=[
        'matplotlib==3.2.2',
        'pandas',
        'numpy',
        'openpyxl',
    ],
    extras_require={
        'dev': [
            'pytest',
            'flake8',
            'pyinstaller'
        ]
    }

)