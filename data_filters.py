
import filters as f
import numpy as np
from log import ConsoleLog as log
from skimage import io, feature, color


def calcGlcm(image, distancesCount:int=5, anglesCount: int=None, anglesStep:float=45):
    '''
    Calculates GLCM for an image over number of distances and number of angles.
    Distances range [1, distancesCount] with step 1
    Angles range [0, 180] with a step of anglesStep (when anglesCount==None) and count of 180/anglesStep + 1
    Angles counts:
     5: every 45°
     7: every 30°
     9: every 22.5°
    13: every 15°
    See calcGlcmFor() for result format
    '''
    if anglesCount is None:
        anglesCount = int(180/anglesStep)+1
    distances = np.arange(1, distancesCount+1)
    angles = np.linspace(0, np.pi, anglesCount)
    return calcGlcmFor(image, distances, angles)

def calcGlcmFor(image, distances, angles):
    '''
    Calculates GLCM for given arrays of distances and angles.
    Result: {
        'contrast': {
            distance_0: {
                angle_0: contrast_0_0,
                angle_1: contrast_0_1,
                ...
            },
            distance_1: {
                angle_0: contrast_1_0,
                angle_1: contrast_1_1,
                ...
            } 
        },
        'dissimilarity': { ... },
        'homogeneity': { ... },
        'energy': { ... }
    }
    '''
    d_length = len(distances)
    a_length = len(angles)
    contrasts = np.zeros((d_length, a_length))
    dissimilarities = np.zeros((d_length, a_length))
    homogeneities = np.zeros((d_length, a_length))
    energies = np.zeros((d_length, a_length))

    result = {}
    # Calculate GLCM properties
    result = {
        'contrast': {},
        'dissimilarity': {},
        'homogeneity': {},
        'energy': {}
    }
    npimage = np.array(image)
    for i, d in enumerate(distances):
        for key in result.keys():
            result[key][d] = {}
        for j, a in enumerate(angles):
            glcm = feature.graycomatrix(npimage, [d], [a], levels=256)

            for key in result.keys():
                result[key][d][a] = feature.graycoprops(glcm, key)[0]

            # contrasts[i, j] = feature.graycoprops(glcm, 'contrast')
            # dissimilarities[i, j] = feature.graycoprops(glcm, 'dissimilarity')
            # homogeneities[i, j] = feature.graycoprops(glcm, 'homogeneity')
            # energies[i, j] = feature.graycoprops(glcm, 'energy')
    return result

class GlcmFilter(f.Filter):
    def __init__(self) -> None:
        super().__init__('GLCM')
        self._inputs.append(f.InputPin(self, 0))
        self._outputs.append(f.OutputPin(self, 0))

    def exec(self, inputPin: f.InputPin, frame: f.Frame):
        super().exec(inputPin, frame)
        image = frame.value()
        glcm = calcGlcm(image)
        self.pushOne(f.Frame(glcm, self, inputPin))
