from distutils.core import setup

setup(name='symosi',
      version='1.0',
      description='Python System Model Simulation Library',
      author='hramon',
      packages=['symosi'],
      install_requires=[
            'numpy',
            'scipy'
      ]
     )