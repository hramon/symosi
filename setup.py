from setuptools import setup

setup(name='symosi',
    version='1.0',
    description='Python System Model Simulation Library',
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author='hramon',
    packages=['symosi'],
    install_requires=[
        'numpy',
        'scipy'
    ]
)