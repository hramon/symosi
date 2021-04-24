from symosi import core, components, sources
from matplotlib import pyplot as plt
import numpy
import timeit

t = numpy.arange(0, 1e-6, 1e-12)
i = numpy.zeros(len(t))
i[t > 0.01e-6] = 1
i[t > 0.1e-6] = t[t > 0.1e-6] / 1e-6



step = sources.UserDefinedSource(t, i,)
filter1 = components.LapaceFilter([1000], [1/(2*numpy.pi*1e6), 1])
filter2 = components.LapaceFilter([1], [1/(2*numpy.pi*0.5e9), 1])
sum = components.Subtract()

system = core.DynamicSystem("BDF", [step, filter1, filter2, sum], maxStep = 1e-10)

system.connect(("out", step), ("in1", sum))
system.connect(("out", filter2), ("in2", sum))

system.connect(("out", sum), ("in", filter1))
system.connect(("out", filter1), ("in", filter2))

system.run(0.3e-6)

output = system.getOutputs(filter2)["out"]
output_step = system.getOutputs(step)["out"]
output_filter1 = system.getOutputs(filter1)["out"]
output_sum = system.getOutputs(sum)["out"]

plt.plot(output.t, output.values)
plt.plot(output_step.t, output_step.values)
plt.xlabel('t [s]')
plt.ylabel('output')
plt.legend(['Output', 'Input'])
plt.show()