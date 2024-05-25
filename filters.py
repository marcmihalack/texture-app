from log import ConsoleLog as log
from PyQt6.QtCore import pyqtSignal, QObject
# class IOutputPin:
#     def __init__(self) -> None:
#         pass

#     def send(self, value):
#         pass

#     def isConnected() -> bool:
#         pass

#     def input():
#         pass


# class IInputPin:
#     def __init__(self, parent) -> None:
#         pass

#     def receive(self, value):
#         pass

#     def canReceive(self, output: IOutputPin):
#         pass

#     def connect(self, output: IOutputPin):
#         pass

class Frame:
    def __init__(self, value, fromFilter, fromPin) -> None:
        self._value = value
        self._fromFilter = fromFilter
        self._fromPin = fromPin

    def value(self):
        return self._value
    
    def fromFilter(self):
        return self._fromFilter
    
    def fromPin(self):
        return self._fromPin


class OutputPin:
    def __init__(self, parent=None, id=None, inputPin=None) -> None:
        self._parent = parent
        self._inputPin = inputPin
        self._id = '-' if id is None else id

    def push(self, frame:Frame):
        if(self._inputPin is None):
            log.error(f'Output pin {self._parent.name()}:{self._id} is not connected')
        else:
            self._inputPin.receive(frame)

    def connect(self, inputPin):
        if inputPin.canReceive(self):
            self._inputPin = inputPin
        else:
            log.error(f'Output pin cannot receive input from {self._parent.name()} filter')


class InputPin:
    def __init__(self, parent, id=None) -> None:
        self._parent = parent
        self._id = '-' if id is None else id

    def receive(self, frame):
        self._parent.exec(self, frame)

    def canReceive(self, outputPin) -> bool:
        return True
    
    def id(self):
        return self._id

class Source:
    def __init__(self) -> None:
        self._data = None
        self._output = OutputPin(0)

    def exec(self, data=None):
        if data is None:
            data = self._data
        if data is None:
            log.error('Source has no data')
        for item in data:
            self._output.push(Frame(item, self, None))

    def output(self):
        return self._output


class Renderer:

    def __init__(self, name: str=None) -> None:
        self._name = name
        self._inputs = [InputPin(self, 0)]

    def name(self):
        return self._name

    def inputs(self) -> list[InputPin]:
        return self._inputs

    def input(self) -> InputPin:
        input = self._inputs[0]
        return input

    def exec(self, inputPin: InputPin, frame: Frame) -> None:
        self.render(frame)
    
    def render(self, frame: Frame) -> None:
        pass


class Filter(QObject):
    filter_executing = pyqtSignal(object, Frame)  # filter, frame
    filter_executed = pyqtSignal(object, Frame)  # filter, frame

    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name
        self._inputs = []
        self._outputs = []
        self._renderer = None

    def name(self):
        return self._name
    
    def exec(self, inputPin: InputPin, frame:Frame) -> None:
        self.filter_executing.emit(self, frame)

    # def pushToPin(self, pinIndex, outputValue):
    #     self.filter_executed.emit(self, outputValue)
    #     length = len(self._outputs)
    #     if pinIndex >= 0 and pinIndex < length:
    #         self._outputs[pinIndex].push(outputValue)
    #     else:
    #         log.error(f'Filter {self.name()} has no pin {pinIndex}')

    def pushMany(self, outputFrames):
        length = len(outputFrames)
        index = 0
        for outputPin in self._outputs:
            if index >= length:
                log.warn(f'No more values for output pin {index}')
                break
            outputFrame = outputFrames[index]
            self.filter_executed.emit(self, outputFrame)
            outputPin.push(outputFrame)
            index += 1
        
    def pushOne(self, outputFrame):
        self.filter_executed.emit(self, outputFrame)
        if len(self._outputs):
            for outputPin in self._outputs:
                outputPin.push(outputFrame)
        else:
            log.warn(f'No output pins for {self.name}')

    def outputs(self) -> list[OutputPin]:
        return self._outputs
    
    def output(self, index=0) -> OutputPin:
        output = self._outputs[index]
        return output

    def inputs(self) -> list[InputPin]:
        return self._inputs
    
    def input(self) -> InputPin:
        input = self._inputs[0]
        return input

    def addOutput(self, outputPin=None) -> None:
        if outputPin is None:
            outputPin = OutputPin(self, len(self._outputs))
        self._outputs.append(outputPin)


class Pipeline:
    def __init__(self, sourceFilter: Source=None) -> None:
        self._source = sourceFilter
    
    def exec(self, data):
        self._source.exec(data)

    def connect(input, output):
        pass


