from .core import Block
import numpy

class Add(Block):
    def __init__(self, nInputs, name = "Add"):
        super().__init__(name)
        self.nInput = nInputs
        self.addOutput("out")
        for i in range(nInputs):
            self.addInput(i)

        self.setStateDimension(0)

    def output(self, t, y, u, o):
        sum = 0
        for input in u.values():
            sum += input[t]

        o["out"] = sum


class Subtract(Block):
    def __init__(self, name = "Sub"):
        super().__init__(name)
        self.addOutput("out")
        self.addInput("in1")
        self.addInput("in2")

        self.setStateDimension(0)

    def output(self, t, y, u, o):
        o["out"] = u["in1"][t] - u["in2"][t]

class Multiply(Block):
    def __init__(self, name = "Mul"):
        super().__init__(name)
        self.addOutput("out")
        self.addInput("in1")
        self.addInput("in2")

        self.setStateDimension(0)

    def output(self, t, y, u, o):
        o["out"] = u["in1"][t] * u["in2"][t]

class Divide(Block):
    def __init__(self, name = "Div"):
        super().__init__(name)
        self.addOutput("out")
        self.addInput("in1")
        self.addInput("in2")

        self.setStateDimension(0)

    def output(self, t, y, u, o):
        o["out"] = u["in1"][t] / u["in2"][t]


class Integrate(Block):
    def __init__(self, name = "Int"):
        super().__init__(name)
        self.addOutput("out")
        self.addInput("in")

        self.setStateDimension(1)

    def output(self, t, y, u, o):
        o["out"] = y[0]

    def state(self, t, y, u):
        return numpy.array([u["in"][t]])

class Differentiate(Block):
    def __init__(self, name = "Diff"):
        super().__init__(name)
        self.addOutput("out")
        self.addInput("in")

        self.setStateDimension(0)

    def output(self, t, y, u, o):
        if(len(u["in"].t) == 0):
            o["out"] = 0
        else:
            if(t < u["in"].t[-1]):
                index = self.findIndex(u["in"].t, t)
                o["out"] = (u["in"].values[index] - u["in"].values[index - 1]) / (u["in"].t[index] - u["in"].t[index - 1])
            else:
                o["out"] = (u["in"][t] - u["in"].values[-1]) / (t - u["in"].t[-1])

    def findIndex(self, timeArray, t):
        tA = numpy.array(timeArray)
        for i in range(len(tA), 1, -1):
            if(tA[i] > t and tA[i-1] < t):
                return i

class LapaceFilter(Block):
    def __init__(self, b, a, name = "Laplace"):
        super().__init__(name)
        self.addOutput("out")
        self.addInput("in")

        self.a = a
        self.b = b
        n = len(a) - 1
        if(n > 1):
            self.A = numpy.append(numpy.zeros([1, n - 1]), numpy.identity(n - 1), axis = 1)
            self.A = numpy.append(self.A, -1*numpy.array([a[-1:0:-1]]) / a[0], axis = 0)
        else:
            self.A = numpy.array([-a[1] / a[0]])
        self.B = numpy.zeros(n)
        self.B[n - 1] = 1

        self.C = numpy.array(b[-1::-1]) / a[0]

        self.setStateDimension(n)

    def output(self, t, y, u, o):
        o["out"] = self.C.dot(y)

    def state(self, t, y, u):
        return self.A.dot(y) + self.B * u["in"][t]


class TimeDelay(Block):
    def __init__(self, delay, name = "TimeDelay"):
        super().__init__(name)
        self.addOutput("out")
        self.addInput("in")
        self.delay = delay
        self.setStateDimension(0)

    def output(self, t, y, u, o):
        o["out"] = u["in"][t - self.delay]