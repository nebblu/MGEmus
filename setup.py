import os
import sys
import re
#from setuptools import setup, Extension, sysconfig, find_packages
from setuptools import setup, find_packages
setup(
    name="MGEmu",
    author="Maria Tsedrik & Ben Bose",
    author_email="mtsedrik@ed.ac.uk;bbose@ed.ac.uk",
    version=0.3,
    packages=find_packages(),
    install_requires=["numpy", "matplotlib", "scipy", "packaging", "cosmopower", "setuptools",  "sphinx_rtd_theme", "gdown"]
)