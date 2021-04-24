from symosi import core, components, sources
from matplotlib import pyplot as plt
import numpy

in1 = sources.SineGenerator(A = 1, f = 10, C = 0, phase = 0)
in2 = sources.Constant(C = 1)
in3 = sources.Constant(C = 2*numpy.pi*10)

sum = components.Add(2)
div = components.Divide()

inte = components.Integrate()
di = components.Differentiate()

delay = components.TimeDelay(10e-3)

system = core.DynamicSystem("FixedStep", [in1, in2, in3, sum, inte, di, div, delay], maxStep = 1e-3)

system.connect(("out", in1), (0, sum))
system.connect(("out", in2), (1, sum))

system.connect(("out", sum), ("in", inte))
system.connect(("out", sum), ("in", di))
system.connect(("out", di), ("in1", div))
system.connect(("out", in3), ("in2", div))
system.connect(("out", div), ("in", delay))

system.run(0.5)

output = system.getOutputs(sum)["out"]
inte_output = system.getOutputs(inte)["out"]
sine_output = system.getOutputs(in1)["out"]
div_output = system.getOutputs(div)["out"]
delay_output = system.getOutputs(delay)["out"]

plt.plot(output.t, output.values)
plt.plot(inte_output.t, inte_output.values)
plt.plot(sine_output.t, sine_output.values)
plt.plot(div_output.t, div_output.values)
plt.plot(delay_output.t, delay_output.values)
plt.xlabel('t [s]')
plt.ylabel('output')
plt.legend(['sum', 'integrator', 'input', 'divider', 'delay'])
plt.show()