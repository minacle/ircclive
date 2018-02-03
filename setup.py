from distutils.core import setup
from os.path import abspath, dirname, join
import re

with open(join(abspath(dirname(__file__)), "ircclive.py")) as f:
    version = re.search(r'\n__version__ = \"(.*?)\"\n', f.read()).group(1)

with open(join(abspath(dirname(__file__)), "README.rst")) as f:
    long_description = f.read()

setup(
    name="ircclive",
    version=version,
    author="Mayu Laierlence",
    author_email="minacle@live.com",
    url="https://github.com/minacle/ircclive",
    description="Simple IRCCloud session keeper; written in python3.",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
        "Topic :: Utilities",
    ],
    py_modules=["ircclive"],
    keywords=["irccloud"],
    entry_points={
        "console_scripts": ["ircclive = ircclive:_main"],
        "setuptools.installation": ["eggsecutable = ircclive:_main"],
    },
    zip_safe=True,
)
