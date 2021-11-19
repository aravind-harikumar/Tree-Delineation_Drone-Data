import os,sys
import fiona
import numpy as np
from ImageProcessor import OtherUtils
from ProjectConstants import GlobalConstants as gc
import subprocess
from subprocess import Popen
from ImageProcessor import RasterOperators, VectorOperators
import matlab.engine
import rasterio
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, mapping

def GetCrownFromMatlab(rest_path):
    print( 'Starting crown extraction in Matlab')
    Orig_dir = os.getcwd()

    path = '/home/ensmingerlabgpu/Documents/MATLAB/BasicSnake_version2f'
    os.chdir(path)

    future = matlab.engine.start_matlab(background=True)
    eng = future.result()
    eng.GetTreeTops(rest_path,nargout=0)
    eng.quit()
    print('Completed crown extraction in Matlab!')

    os.chdir(Orig_dir)

# rest_path ='/home/ensmingerlabgpu/Desktop/4TBHDD/StCasimir-Multispectral-Analysis/2_Analysis-And-Results/ProcessedMSData1/20180516/nDSM/nDSM_Aligned/20180516_nDSM_Image.tif'
# GetCrownFromMatlab(rest_path)