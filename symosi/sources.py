from .core import Block
import numpy

class SineGenerator(Block):
    def __init__(self, A, f, C, phase, name = "Sine"):
        super().__init__(name)
        self.addOutput("out")
        self.A = A
        self.f = f
        self.C = C
        self.phase = phase

    def output(self, t, y, u, o):
        o["out"] = self.A * numpy.sin(2 * numpy.pi * self.f * t + self.phase) + self.C

class Constant(Block):
    def __init__(self, C, name = "Constant"):
        super().__init__(name)
        self.addOutput("out")
        self.C = C

    def output(self, t, y, u, o):
        o["out"] = self.C


class UserDefinedSource(Block):
    def __init__(self, t, s, name = "UserSource"):
        super().__init__(name)
        self.time = t
        self.s = s
        self.addOutput("out")

    def output(self, t, y, u, o):
        o["out"] = numpy.interp(t,self.time,self.s)