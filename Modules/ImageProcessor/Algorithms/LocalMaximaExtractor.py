"""
.. module:: ImageProcessor
    :platform: Unix, Windows
    :synopsis: A module for generating local maxima in images (e.g. DEM)
    
..  :author:: Aravind Harikumar <aravindhari1@gmail.com>
"""

from skimage.feature import peak_local_max
import numpy as np
import rasterio
from matplotlib import pyplot

def GetLocalMaxima(InputImage,min_distance,ImageTransform):
        # print(InputImage)
        pyplot.imshow(InputImage)
        # pyplot.show()
        # exit(0)
        coordinates = peak_local_max(InputImage, min_distance=min_distance,threshold_rel=0.1)    
        # coordinates = np.asmatrix([coordinates[:,0],coordinates[:,1]])
        coordinates = np.asmatrix(rasterio.transform.xy(ImageTransform,coordinates[:,0],coordinates[:,1],offset='center'))
        return np.transpose(coordinates)
	
