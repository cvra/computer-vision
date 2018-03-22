import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "PlanDetector",
    version = "0.1",
    author = "Dorian Konrad",
    author_email = "dorian.konrad@gmail.com",
    description = ("Construction Plan Reader for Eurobot 2018."),
    license = "",
    keywords = "",
    url = "http://www.cvra.ch",
    packages=['', ''],
    long_description=read('README'),
    classifiers=[],
)