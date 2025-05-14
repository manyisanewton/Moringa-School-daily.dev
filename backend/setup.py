from setuptools import setup, find_packages
import pathlib
here = pathlib.Path(__file__).parent
requirements = (here / "requirements.txt").read_text().splitlines()
setup(
    name="moringa_api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
)