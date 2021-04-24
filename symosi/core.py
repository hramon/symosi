from scipy.integrate import RK45, BDF
import numpy

class Block:
    def __init__(self, name = "Block"):
        self.dimension = {"A": 0, "U": 0, "O": 0}
        self.name = name
        self.inputs = []
        self.outputs = []

    def state(self, t, y, u):
        raise Exception("state method should be implemented")

    def output(self, t, y, u, o):
        raise Exception("output method should be implemented")

    def getDiminsion(self):
        return self.dimension

    def addInput(self, input):
        self.inputs.append(input)
        self.dimension["U"] += 1

    def addOutput(self, output):
        self.outputs.append(output)
        self.dimension["O"] += 1

    def setStateDimension(self, dimension):
        self.dimension["A"] = dimension

class DynamicSystem:
    def __init__(self, solverType, blocks = [], maxStep = numpy.inf, maxIterations = 500):
        self.solverType = solverType
        self.blocks = blocks
        self.connections = []
        self.inputs = {}
        self.outputs = {}
        self.t = []
        self.numberOfOutputs = 0
        self.maxIterations = maxIterations
        self.maxStep = maxStep

    def run(self, stopTime):

        self.uniqueBlockNames()
        self.prepareOutputs()
        self.prepareInputs()
        self.t.clear()

        solverClass= None
        if(self.solverType == 'RK45'):
            solverClass = RK45
        elif(self.solverType == 'BDF'):
            solverClass = BDF
        elif(self.solverType == 'FixedStep'):
            solverClass = FixedStepSolver
        else:
            raise Exception("Solver {} not supported".format(self.solverType))

        solver = solverClass(self.getStepFunction(), 0, numpy.zeros(self.getFullStateDimension()), stopTime, max_step = self.maxStep)

        previousDelta = 0
        self.evaluateOutputs(0, numpy.zeros(self.getFullStateDimension()))
        self.promoteAllOutputs(0)
        self.t.append(0)
        while solver.status == 'running':
            solver.step()
            t = solver.t
            y =  solver.y
            self.evaluateOutputs(t, y)
            self.promoteAllOutputs(t)
            self.t.append(t)
            if(int(t/stopTime*100) % 5 < previousDelta):
                print("Current time: {:.2g}s, {:.1f}% finished".format(t, t/stopTime*100))
            previousDelta = int(t/stopTime*100) % 5

    def getFullStateDimension(self):
        dim = 0
        for block in self.blocks:
            dim += block.getDiminsion()["A"]

        return dim

    def getStepFunction(self):
        def stepFunction(t, y):
            dy = numpy.zeros(len(y))
            runningNumberOfStates = 0
            self.evaluateOutputs(t, y)
            for block in self.blocks:
                blockDimension = block.getDiminsion()["A"]
                if(blockDimension > 0):
                    dy[runningNumberOfStates:runningNumberOfStates + blockDimension] = block.state(t, y[runningNumberOfStates:runningNumberOfStates + blockDimension], self.inputs[block.name])
                    runningNumberOfStates += blockDimension
            return dy

        return stepFunction


    def addBlocks(self, blocks):
        self.blocks.extend(blocks)

    def connect(self, outputA, inputB):
        self.connections.append((outputA, inputB))

    def uniqueBlockNames(self):
        names = {}
        for block in self.blocks:
            if block.name not in names:
                names[block.name] = 1
            else:
                names[block.name] += 1
                block.name += str(names[block.name])

    def prepareInputs(self):
        for connection in self.connections:
            if connection[1][1].name not in self.inputs:
                self.inputs[connection[1][1].name] = {}
            self.inputs[connection[1][1].name][connection[1][0]] = self.outputs[connection[0][1].name][connection[0][0]]



    def prepareOutputs(self):
        self.numberOfOutputs = 0
        for block in self.blocks:
            tempDict = {}
            for output in block.outputs:
                tempDict[output] = Signal(self.t)
            self.outputs[block.name] = tempDict
            self.numberOfOutputs += len(block.outputs)

    def evaluateOutputs(self, t, y):
        previousOutput = numpy.zeros(self.numberOfOutputs)
        converged = False
        iteration = 0
        while((not converged) and (iteration < self.maxIterations)):
            converged = True
            runningOutput = 0
            runningNumberOfStates = 0
            for block in self.blocks:
                tempDict = {}
                for oName in block.outputs:
                    tempDict[oName] = 0
                block.output(t, y[runningNumberOfStates:runningNumberOfStates + block.getDiminsion()["A"]], self.inputs[block.name] if block.name in self.inputs else None, tempDict)
                runningNumberOfStates += block.getDiminsion()["A"]
                for oName in block.outputs:
                    if(previousOutput[runningOutput] - tempDict[oName] > 1e-15):
                        converged = False
                    previousOutput[runningOutput] = tempDict[oName]
                    self.outputs[block.name][oName].addCandidate(t, previousOutput[runningOutput])
                    runningOutput += 1
            iteration += 1

        if(iteration == self.maxIterations):
            raise Exception("Maximum number of iterations reached, possible infinite loop. Consider increasing the number of iterations or introduce a delay element in the loop.")


    def getOutputs(self, block):
        return self.outputs[block.name]

    def promoteAllOutputs(self, t):
        for blockOutputs in self.outputs.values():
            for output in blockOutputs.values():
                output.promoteCandidate(t)

class Signal:
    def __init__(self, t):
        self.values = []
        self.t = t
        self._candidate = (0, 0)

    def __getitem__(self, t):

        if(t < 0):
            return 0

        if(len(self.t) > 0):
            if(t <= self.t[-1]):
                return numpy.interp(t, self.t, self.values)
            elif(t < self._candidate[0]):
                return (self._candidate[1] - self.values[-1]) / (self._candidate[0] - self.t[-1]) * (t - self.t[-1]) + self.values[-1]
            else:
                return self._candidate[1]
        else:
            return self._candidate[1]

    def addCandidate(self, t, value):
        self._candidate = (t, value)

    def promoteCandidate(self, t):
        if(t == self._candidate[0]):
            self.values.append(self._candidate[1])
        else:
            raise Exception("Oops, something went wrong!")

class FixedStepSolver:
    def __init__(self, fun, t0, y0, t_bound, max_step):
        self.timeStep = max_step
        self.fun = fun
        self.t = t0
        self.y = y0
        self.t_bound = t_bound
        self.status = "running"

    def step(self):
        self.t += self.timeStep
        self.y += self.fun(self.t, self.y) * self.timeStep

        if(self.t + self.timeStep >= self.t_bound):
            self.status = "finished"