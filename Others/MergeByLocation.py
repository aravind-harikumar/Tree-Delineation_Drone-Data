import sys,os
from numpy.core.defchararray import asarray
import pandas as pnd
import geopandas as gpd
from shapely import geometry
import rasterio
import rasterio.mask
from shapely.ops import nearest_points
from scipy.spatial import cKDTree
from shapely.geometry import Point
import numpy as np
import matplotlib.pyplot as plt
from ImageProcessor import RasterOperators, VectorOperators
from shapely.geometry import Point, Polygon ,LineString, mapping
from rasterio.warp import reproject
from rasterio.control import GroundControlPoint
from fiona.crs import from_epsg
import pandas as pnd
from shapely.ops import nearest_points
from scipy.spatial import cKDTree
from rasterio.warp import calculate_default_transform, reproject, Resampling
import fiona
# from Others import HeightEstimationUtils as heu
import gdal
import random
from random import randrange, uniform
from fiona.crs import from_epsg
from ProjectConstants import GlobalConstants as gc
import statsmodels.api as sm
from rasterio.plot import show
from matplotlib import pyplot
import seaborn as sns
import scipy as sp
import matplotlib.pyplot as plt

def ckdnearest(gdA, gdB):
    nA = np.array(list(zip(gdA.geometry.x, gdA.geometry.y)) )
    nB = np.array(list(zip(gdB.geometry.x, gdB.geometry.y)) )
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    gdf_out = pnd.concat(
        [gdB.loc[idx, gdB.columns != 'geometry'].reset_index(drop=True),
        gdA.reset_index(drop=True),
        pnd.Series(dist, name='dist'+str(0))], axis=1)
    # print(len(gdf_out))
    # gdf_out.reindex(range(len(gdf_out)+1))
    return gdf_out

D1_shp_path = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20170626/ITC-Data/All-ITC/shapefile_merged.shp'
D2_shp_path = "/home/ensmingerlabgpu/Desktop/AgisoftProjects/ALLSHpHT/ALL.shp"
left_df = gpd.read_file(D1_shp_path)
right_df = gpd.read_file(D2_shp_path)
# final_gdf_treetop = gpd.sjoin_nearest(left_df, right_df, str = 'inner')
# final_gdf_treetop = heu.GetProximalPoints(left_df,right_df,5)
final_gdf = ckdnearest(left_df, right_df)
# final_gdf = final_gdf[final_gdf['dist'+str(0)]<threshold] 
final_gdf.to_file(driver = 'ESRI Shapefile', filename= "/home/ensmingerlabgpu/Desktop/AgisoftProjects/ALLSHpHT/Allplusresult.shp")