import os, sys, random
import numpy as np
import rasterio
import gdal, ogr, osr
import fiona
import rasterio.mask
from skimage import exposure
import geopandas as gpd
from ImageProcessor import RasterOperators, VectorOperators
from ImageProcessor.Algorithms import LocalMaximaExtractor
from matplotlib import pyplot
from fcmeans import FCM


class FCMClass:
# Fuzzy C-means4

  def __init__(self, n_clusters=10, max_iter=150, m=2, error=1e-5, random_state=42):
    assert m > 1
    self.u, self.centers = None, None
    self.n_clusters = n_clusters
    self.max_iter = max_iter
    self.m = m
    self.error = error
    self.random_state = random_state

  def initparms(self,band_array):

    Bands,M,N = np.shape(band_array)

    # Actual window size is 2*WSize+1
    WSize = 1

    # Max number of neighbours
    Nn = ((WSize*2+1)^2)-1

    #Fuzzification Factor
    m = 2.2

    # number of classes
    Ncl = 5

    # The weightage to spatial and spectral components
    lambdav =  0.7

    maxDN = 255
    Neigh_Coord  = np.zeros((M, N, Bands), dtype=float)
    Weight = np.zeros((2*WSize+1, 2*WSize+1), dtype=float)

    MeanClassVal = np.zeros((Bands,Ncl), dtype=float)
    MeanClassVal[:,0] = [77,36,88]
    MeanClassVal[:,1] = [77,36,88]
    MeanClassVal[:,2] = [77,36,88]
    MeanClassVal[:,3] = [77,36,88]
    MeanClassVal[:,4] = [77,36,88]
    # print(MeanClassVal)

    # Randomly initialize membership values
    MembValArray = np.random.rand(M,N,Ncl)
    for i in range(0,Ncl):
      MembValArray[:,:,i] = MembValArray[:,:,i]/np.sum(np.sum(MembValArray[:,:,i]))  # print(np.shape(MembValArray[:,:,1]))
  