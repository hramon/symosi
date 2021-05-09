from distutils.core import setup

with open("README.md", "r") as file:
    long_description = file.read()

setup(name='symosi',
    version='1.0',
    description='Python System Model Simulation Library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='hramon',
    packages=['symosi'],
    install_requires=[
        'numpy',
        'scipy'
    ]
)