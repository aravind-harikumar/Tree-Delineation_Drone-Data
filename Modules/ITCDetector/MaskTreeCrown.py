"""
.. module:: MetashapeProcessor
    :platform: Unix, Windows
    :synopsis: A module for generating orthorectified remote sensing images
    
..  :author:: Aravind Harikumar <aravindhari1@gmail.com>
"""

import os, sys
import numpy as np
import rasterio
import rasterio.mask
import fiona
from fiona.crs import from_epsg
from shapely.geometry import Point, LineString, Polygon, mapping
from shapely.geometry.multipolygon import MultiPolygon
from shapely import wkt
from skimage import exposure
import geopandas as gpd
from ImageProcessor import RasterOperators, VectorOperators, OtherUtils
from ProjectConstants import GlobalConstants as gc

def SaveTreeTop(TreeTopXY,BufferSize,OutFolder,clipFile):
    # Save Crown Span as Shp File and save ITCs
    sucess = False
    if(np.shape(TreeTopXY)[0]>0):
        gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy(TreeTopXY[:,0],TreeTopXY[:,1]))
        gdf.crs = {'init' : gc.PROJECTION_ID}
        # clip_polygon = gpd.read_file(clipFile)
        # gdf = gpd.clip(gdf, clip_polygon)
        gdf.to_file(os.path.join(OutFolder,'TreeBufferAll.shp'),driver ='ESRI Shapefile')        
        # VectorOperators.ClipShpFile(gdf, clipFile, os.path.join(OutFolder,'TreeBufferAll.shp'))  

        cnt = 1
        for index, row in gdf.iterrows():
            CrownBuffer = row['geometry'].buffer(BufferSize, cap_style=1)
            # if BufferType == 'WatershedBased':
            #     CrownBuffer = row['geometry'].buffer(BufferSize/100000, cap_style=1)          
            VectorOperators.SaveAsShpFile(CrownBuffer, 
                                        os.path.join(OutFolder, 'ITC-Buffer_' + str(cnt) + '_' 
                                        + str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.shp'))
            cnt = cnt + 1     
        sucess = True
    else:
        print("Tree top Count < 1 " + str(np.shape(TreeTopXY)[0]))

def CropITCFromOrthoImage(OrthoImageName, InShpFilePath, OutFolder):
    for subdir, dirs, files in os.walk(InShpFilePath):
        for FileName in files:
            if FileName.endswith(".shp") and 'TreeBufferAll' not in FileName:
                with fiona.open(os.path.join(subdir, FileName), 'r') as shapefile:
                    ShapeMask = [feature["geometry"] for feature in shapefile]
                    RasterOperators.CropImage(OrthoImageName, ShapeMask, os.path.join(OutFolder, str(FileName).split('.')[0]))

def MergeShpFiles(ITCDataFolder, merge_out_path):

    OtherUtils.TouchPath(merge_out_path)
    merged_out_file = os.path.join(merge_out_path,'shapefile_merged.shp')

    # loop through individual tile folders to detect TreeBufferAll.shp files
    shpfile_name_list = []
    for root, folders, files in os.walk(ITCDataFolder):
        for file_name in files:
            if file_name.rsplit(".")[0] in ["TreeBufferAll"] and file_name.rsplit(".")[1] in ["shp"] and file_name.rsplit(".")[0] not in ["All-ITC"]:
                shpfile_name_list.append(os.path.join(root,file_name))

    # Merge shape files
    if(np.shape(shpfile_name_list)[0] > 0):
        VectorOperators.MergeShpFiles(shpfile_name_list,merged_out_file)
        print('Shape Files Merged!')
    else:
        print('No shape files to merge')
