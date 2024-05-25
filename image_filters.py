import filters as f
from PIL import Image, ImageQt
import dlib
import numpy as np
from log import ConsoleLog as log
import cv2

class LoadImage(f.Filter):
    def __init__(self) -> None:
        super().__init__('Image Load')
        self._inputs.append(f.InputPin(self, 0))
        self._outputs.append(f.OutputPin(self, 0))

    def exec(self, inputPin, frame:f.Frame):
        super().exec(inputPin, frame)
        file_path = frame.value()
        image = Image.open(file_path)
        log.info(f'Loaded image mode={image.mode}')
        self.pushOne(f.Frame(image, self, inputPin))

class CropImage(f.Filter):
    def __init__(self, rect=None) -> None:
        super().__init__('Image Crop')
        self._inputs.append(f.InputPin(self, 0))
        self._outputs.append(f.OutputPin(self, 0))
        
        self._cropRect = rect
    
    def setCropRect(self, rect):
        self._cropRect = rect

    def exec(self, inputPin, frame:f.Frame):
        super().exec(inputPin, frame)
        image = frame.value()
        cropped = image.crop(self._cropRect)
        self.pushOne(f.Frame(cropped, self, inputPin))


class ResizeImage(f.Filter):
    def __init__(self, dim=None, keepAspectRatio: bool=True, upsize: bool=True) -> None:
        super().__init__('Image Size')
        self._inputs.append(f.InputPin(self, 0))
        self._outputs.append(f.OutputPin(self, 0))

        self._dim = dim
        self._upsize = upsize
        self._keepAspectRatio = keepAspectRatio

    def setSize(self, dim, keepAspectRatio: bool=True, upsize: bool=True):
        self._dim = dim
        self._upsize = upsize
        self._keepAspectRatio = keepAspectRatio

    def exec(self, inputPin, frame: f.Frame):
        super().exec(inputPin, frame)
        image = frame.value()
        width = self._dim[0]
        height = self._dim[1]
        if image.width > width or (self._upsize and image.width < width):
            r = self._dim[0] / image.width
            dim = (self._dim[0], int(image.height * r))
            sized = image.resize(dim)
        else:
            sized = image

        self.pushOne(f.Frame(sized, self, inputPin))

from skimage.restoration import inpaint

class ImageInpaint(f.Filter):
    def __init__(self) -> None:
        super().__init__('Image Inprint')
        self._inputs.append(f.InputPin(self, 0))
        self._outputs.append(f.OutputPin(self, 0))
    
    def exec(self, inputPin: f.InputPin, frame: f.Frame) -> None:
        super().exec(inputPin, frame)
        lower_white = np.array([255, 255, 255])
        upper_white = np.array([255, 255, 255])

        image = np.array(frame.value())
        white_intensity = 255
        _, mask = cv2.threshold(image, white_intensity-3, white_intensity, cv2.THRESH_BINARY)
        inpainted_img_cv = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
        result = Image.fromarray(inpainted_img_cv)

        # mask = cv2.inRange(image, lower_white, upper_white)
        # result = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
        #mask = image >= 0.9
        #result = inpaint.inpaint_biharmonic(image, mask, multichannel=True)
        self.pushOne(f.Frame(result, self, inputPin))


class ConvertImage(f.Filter):
    def __init__(self, targetFormat, sourceFormats=None) -> None:
        super().__init__(f'Image Convert')
        self._targetFormat = targetFormat
        self._sourceFormats = sourceFormats
        self._inputs.append(f.InputPin(self, 0))
        self._outputs.append(f.OutputPin(self, 0))

    def name(self):
        return f'Image Convert ({self._name})'

    def exec(self, inputPin:f.InputPin, frame:f.Frame):
        super().exec(inputPin, frame)
        image = frame.value()
        image = image.convert(self._targetFormat)
        self.pushOne(f.Frame(image, self, inputPin))


class SobelEdge(f.Filter):
    def __init__(self) -> None:
        super().__init__(f'Sobel Edge')
        self._inputs.append(f.InputPin(self, 0))
        self._outputs.append(f.OutputPin(self, 0))
        self._outputs.append(f.OutputPin(self, 1))

    def exec(self, inputPin: f.InputPin, frame: f.Frame):
        super().exec(inputPin, frame)
        image = frame.value()
        arrayed = np.asarray(image)
        edged = dlib.sobel_edge_detector(arrayed)
        self.pushMany([
            f.Frame(Image.fromarray(edged[0]).convert('L'), self, inputPin),
            f.Frame(Image.fromarray(edged[1]).convert('L'), self, inputPin)])
        # length = len(self._outputs)
        # if length > 0:
        #     log.verbose('Pushing Sobel:0')
        #     self.pushToPin(0, Image.fromarray(edged[0]).convert('L'))
        #     if length > 1:
        #         log.verbose('Pushing Sobel:1')
        #         self.pushToPin(1, Image.fromarray(edged[1]).convert('L'))


class Histogram(f.Filter):
    def __init__(self) -> None:
        super().__init__('Histogram')
        self._inputs.append(f.InputPin(self, 0))
        self._outputs.append(f.OutputPin(self, 0))

    def exec(self, inputPin: f.InputPin, frame: f.Frame):
        super().exec(inputPin, frame)
        image = frame.value()
        arrayed = np.asarray(image)
        histogram = dlib.get_histogram(arrayed, 256)
        self.pushOne(f.Frame(histogram, self, inputPin))

# class HistogramRenderer(f.Renderer):
#     def __init__(self) -> None:
#         super().__init__('Histogram Renderer')

#     def render(self, frame: f.Frame) -> None:
#         histogram = frame.value()