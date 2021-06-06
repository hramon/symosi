# Python System Modeling and Simulation Library (SyMoSi)
SyMoSi is a python library for block model simulation of dynamic systems. It allows to define and combine dynamic blocks with either code or system equations to create complex systems.

# Requirements
* SciPy
* NumPy

# Install
```
pip install symosi
```

or download from github and

```
cd symosi
python setup.py install
```

# Usage

## Simple example

```python
#plotting
from matplotlib import pyplot as plt

# import library
import symosi

# initialize components and sources
step = symosi.sources.Step(0.1)
constant = symosi.sources.Constant(1)
add = symosi.components.Add()

# initialize simulation
system = symosi.DynamicSystem("FixedStep", dynamic_components)

# connect the components
system.connect((step, "out"), (add, 0)) # connect output "out" of step to input 0 of add
system.connect((constant, "out"), (add, 1)) # connect output "out" of constant to input 1 of add

# simulate
system.run(0.2)

# get output of adder
output = system.getOutputs(add)["out"]

# plot
plt.plot(output.t, output.values)
plt.show()
```

## More examples

Additional examples can be found in the `Examples` folder.


# Contributing
Fork the github repository and open a pull request. There are multiple ways you can conbribute:

* Create standard library components/blocks
* Contribute to the core code
* Write examples
