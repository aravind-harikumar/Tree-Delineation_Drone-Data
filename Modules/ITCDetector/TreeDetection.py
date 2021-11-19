"""
.. module:: MetashapeProcessor
    :platform: Unix, Windows
    :synopsis: A module for generating orthorectified remote sensing images
    
..  :author:: Aravind Harikumar <aravind.harikumar@utoronto.ca>
"""

import os, sys
import numpy as np
import rasterio
import fiona
import pandas as pd
import rasterio.mask
from skimage import exposure
import geopandas as gpd
from ImageProcessor import RasterOperators, VectorOperators
from ImageProcessor.Algorithms import LocalMaximaExtractor
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist
from Others import GetMatlabLocalmax

def DetectTreeTop(InputFileName, TreeTopInclusionBuffer, inter_tree_seperation, min_tree_height,FilterVariance):
    ''' Class for generating orthorectified remote sensing images.
    
    Args: \n 
        InputFileName: full path of input file.
        TreeTopSepeartion: minimum distance within 
                           which any detected local 
                           maxima will be considered. '''
    TreeObj = DetectTrees(InputFileName,
                         TreeTopInclusionBuffer,
                         inter_tree_seperation,
                         min_tree_height,
                         FilterVariance)
    TreeObj.LoadData()
    TreeObj.PreProcess()
    TreeObj.GetCanopyLocalMaxima()
    return TreeObj.GetTreeTops()

class DetectTrees:
    
    TreeTopXY = []

    # initialize paths
    def __init__(self, InputFileName, TreeTopInclusionBuffer, inter_tree_seperation, min_tree_height, filter_variance):
        ''' initialize variables '''

        if not(os.path.exists(InputFileName)):
            raise ValueError("File not found!")
        else:
            self.InputFileName = InputFileName

        if TreeTopInclusionBuffer < 0:
            raise ValueError("Minimum Distance should be greater than 0!")
        else:    
            self.min_distance = TreeTopInclusionBuffer
        
        if inter_tree_seperation < 0:
            raise ValueError("Inter tree top seperation should be greater than 0!")
        else:    
            self.inter_tree_seperation = inter_tree_seperation
        
        if min_tree_height < 0:
            raise ValueError("Minimum tree height should be greater than 0!")
        else:    
            self.min_tree_height = min_tree_height
        
        self.filter_variance = filter_variance

    def LoadData(self):
        # OrthorectifiedImage = RasterOperators.ReadImage(os.path.join(BaseFolder,'orthorectified_1o.tif'))
        # OrthorectifiedImage = OrthorectifiedImage.read(1)
        ImageObject = RasterOperators.ReadImage(self.InputFileName)
        ImageBandData = ImageObject.read(1)
        self.ImageBandData = ImageBandData
        self.ImageTransform = ImageObject.transform

    def PreProcess(self):
        print(np.amax(self.ImageBandData))
        print(np.amin(self.ImageBandData))
        self.ImageBandData[self.ImageBandData <= (self.min_tree_height/100)*np.amax(self.ImageBandData)] = 0
        # self.ImageBandData[self.ImageBandData >= 20] = 0
        # print(np.sum(np.isnan(self.ImageBandData)))        
        self.ImageBandData = RasterOperators.HistogramEqualizeImage(self.ImageBandData)
        self.ImageBandData = RasterOperators.normalize(self.ImageBandData)
        # self.ImageBandData = RasterOperators.MaxFilterImage(self.ImageBandData,0.5)
        # self.ImageBandData = RasterOperators.GaussianFilterImage(self.ImageBandData, self.filter_variance, 1/100)
        # self.ImageBandData = RasterOperators.SharpenFilterImage(self.ImageBandData)

        # RasterOperators.ShowImageSKT(self.ImageBandData)
        # exit(0)

    def GetCanopyLocalMaxima(self):
        print('here')
        print(self.InputFileName)

        
        GetMatlabLocalmax.GetCrownFromMatlab(self.InputFileName)
        coord_df = pd.read_csv('/home/ensmingerlabgpu/Desktop/out.csv', header=None)
        coordinates = np.round(np.asarray(coord_df),1)

        coordinates = np.transpose(np.asmatrix(rasterio.transform.xy(self.ImageTransform,coordinates[:,1],coordinates[:,0],offset='center')))
        # return np.transpose(coordinates)

        # print(coordinates)
        # print(np.shape(coordinates))
        # exit(0)
        
        # print(self.ImageBandData)
        # self.ImageBandData[np.isnan(self.ImageBandData)] = 0
        # coordinates = LocalMaximaExtractor.GetLocalMaxima(self.ImageBandData, self.min_distance, self.ImageTransform) 
        # if np.shape(coordinates)[0]>15000:
        #     print('subsamplimg local maxima as size is ' + str(np.shape(coordinates)[0]) + '(> 15000)!')
        #     indices = np.random.choice(coordinates.shape[0], 15000, replace=False)
        #     coordinates = coordinates[indices]

        treetopseperation = self.inter_tree_seperation
        out_mat = cdist(coordinates, coordinates)
        out_mat[out_mat<treetopseperation] = 0 # set all cell < treetopseperation to 0
        out_mat[out_mat>=treetopseperation] = 1 # set all cell > treetopseperation to 1
        out_mat = np.add(np.tril(out_mat,-1),np.triu(out_mat,-1)) # lower +  upper
        out_mat_sum = np.sum(out_mat,axis=1) # row-wise sum
        coordinates = coordinates[out_mat_sum==len(coordinates)]
        print(np.shape(coordinates))
        # exit(0)
        self.TreeTopXY = coordinates

    def GetTreeTops(self):
        return self.TreeTopXY