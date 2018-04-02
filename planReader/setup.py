import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="PlanDetector",
    version="0.1",
    author="Dorian Konrad",
    author_email="dorian.konrad@gmail.com",
    description=("Construction Plan Reader for Eurobot 2018."),
    license="",
    keywords="",
    url="http://www.cvra.ch",
    packages=find_packages(),
    long_description=read('README'),
    classifiers=[],
)
