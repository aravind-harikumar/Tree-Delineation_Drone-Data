import os
import numpy as np
from ImageProcessor import RasterOperators, OtherUtils
from ImageProcessor.Algorithms import LocalMaximaExtractor
from ITCDetector import TreeDetection, MaskTreeCrown
import rasterio
import Metashape
import cv2
from rasterio.warp import reproject
from rasterio.control import GroundControlPoint
from fiona.crs import from_epsg
import pandas as pnd
from rasterio.warp import calculate_default_transform, reproject, Resampling
import geopandas as gpd
import pandas as pd
import shapely.wkt
from shapely.geometry import Point, LineString, Polygon, mapping
import gdal
import fiona
from fiona.crs import from_epsg
from ProjectConstants import GlobalConstants as gc
# from arosics import COREG
# from arosics import DESHIFTER
# from sentinelhub import pixel_to_utm

class ITCDelineationUtils:

    def __init__(self, FileDataInfo):
        # assert m > 1
        # self.u, self.centers = None, None
        self.base_path = FileDataInfo['BaseFolder']
        self.date = FileDataInfo['Date']
        self.InShpPath = FileDataInfo['InShapeFolder']
        self.OutShpPath = FileDataInfo['OutShapeFolder']
        self.ImageFolder = FileDataInfo['ImageFolder']
        self.SpectralMapPath = FileDataInfo['SpectralMaps']
        self.SkipCoregStep = FileDataInfo['SkipCoregStep']

        # if(self.SkipCoregStep):
        #     FileDataInfo['CoregisterFolder']  = gc.NON_COR_ORTHOPHOTO_FOLDER

    def DelineateIndividaulTrees(self):       
        inshapefile = os.path.join(self.base_path, self.date, self.InShpPath, 'shapefile_merged.shp')
        outspath = os.path.join(self.base_path, self.date, self.OutShpPath)
        OtherUtils.TouchPath(outspath)
        outshapefile = os.path.join(outspath, 'ITCSpectralInfo.shp')
        
        # Get Treetop locations
        treetopsshp = gpd.read_file(inshapefile)

        # Get Orthophoto from Coregisterf folder
        OrthoPhoto = os.path.join(self.base_path, self.date, self.ImageFolder, self.date + '.tif')
        # If SkipCoregStep, then get Orthophoto from non-coregisterd folder
        if(self.SkipCoregStep): 
            OrthoPhoto = os.path.join(self.base_path, self.date, gc.NON_COR_ORTHOPHOTO_FOLDER, self.date + '.tif')
        
        # Generate spectral maps from Orthophoto
        outmapfilepath = os.path.join(self.base_path,self.date,self.SpectralMapPath)
        OtherUtils.TouchPath(outmapfilepath)
        # print('Generating Maps')
        self.GenerateMaps(outmapfilepath, OrthoPhoto)
        # exit(0)
        # Generate spectral maps
        
        norm_ndvi,norm_pri,norm_cci = self.GetIndiceMapsArrays(treetopsshp,outmapfilepath)
        # norm_ndvi[np.isnan] = 0
        # norm_ndvi[np.isnan] = 0
        # norm_ndvi[np.isnan] = 0

        # Write to shp
        self.Write2Shp(norm_ndvi, norm_pri, norm_cci, inshapefile, outshapefile)

    def GetIndiceMapsArrays(self, treetopsshp, map_path):
        meanval_ndvi, meanval_pri, meanval_cci = [], [], []
        for index, row in treetopsshp.iterrows():
            # print(row['FID'])
            # exit(0)
            CrownBuffer = row['geometry'].buffer(0.8, cap_style=1)
            NDVIFile = os.path.join(map_path, 'NDVI.tif')
            out_image_ndvi, out_transform_ndvi = rasterio.mask.mask(rasterio.open(NDVIFile), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
            Indice, Values = RasterOperators.GetLargestN(out_image_ndvi.flatten(), 25)
            meanval_ndvi.append(np.mean(Values))

            PRIFile = os.path.join(map_path, 'PRI.tif')
            out_image_pri, out_transform_pri = rasterio.mask.mask(rasterio.open(PRIFile), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
            Indice, Values = RasterOperators.GetLargestN(out_image_pri.flatten(), 25)
            meanval_pri.append(np.mean(Values))

            CCIFile = os.path.join(map_path, 'CCI.tif')
            out_image_cci, out_transform_cci = rasterio.mask.mask(rasterio.open(CCIFile), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
            Indice, Values = RasterOperators.GetLargestN(out_image_cci.flatten(), 25)
            meanval_cci.append(np.mean(Values))
        
        norm_ndvi = meanval_ndvi
        norm_pri = meanval_pri
        norm_cci = meanval_cci

        return norm_ndvi, norm_pri, norm_cci

    def Write2Shp(self,norm_ndvi, norm_pri, norm_cci, in_shp_loc, out_shp_loc):
        loopcnt = 0

        # Define a polygon feature geometry with one attribute
        schema = {
            'geometry'   : 'Point',
            'properties' : {'NDVI': 'float' ,'PRI': 'float', 'CCI': 'float'},
        }

        with fiona.open(out_shp_loc, 'w', crs=gc.PROJECTION_ID, driver='ESRI Shapefile', schema=schema) as c: # from_epsg(32619)
            treetopsshp = gpd.read_file(in_shp_loc)   
            for index, row in treetopsshp.iterrows():
                # CrownBuffer = row['geometry'].buffer(0.8, cap_style=1)
                ## If there are multiple geometries, put the "for" loop here
                c.write({
                    'geometry': mapping(row['geometry']),
                    'properties': {'NDVI': norm_ndvi[loopcnt], 'PRI': norm_pri[loopcnt], 'CCI': norm_cci[loopcnt]}
                })
                loopcnt = loopcnt + 1

    def GenerateMaps(self, map_path, OrthoPhoto):
        # Generate NDVI Map
        NDVIFile = os.path.join(map_path, 'NDVI.tif')
        print('NDVIFile')
        print(OrthoPhoto)
        RasterOperators.GetNDVIMap(OrthoPhoto, NDVIFile, 5, 4)
        
        # Generate PRI Map
        PRIFile = os.path.join(map_path, 'PRI.tif')
        RasterOperators.GetPRIMap(OrthoPhoto, PRIFile, 1, 2)
        
        # Generate CCI Map
        CCIFile = os.path.join(map_path, 'CCI.tif')
        RasterOperators.GetCCIMap(OrthoPhoto, CCIFile, 1, 3)
















        # def DelineateIndividaulTrees(self):
        
        #     # get list of images to to be coregistered, for each image-tile in ref folder (i.e., may)
        #     ref_folder = os.path.join(self.base_path, self.ref_date_folder, 'Sliced_Data')
        #     ImageListToCoregister = self.__GetImageListToCoregister(ref_folder)
        
        #     # loop sliced data folder (can be aany folder)        
        #     for root, folders, files in os.walk(self.base_path):
        #         for file in files:
                    
        #             filename_split_list = file.rsplit("_")
        #             slice_folder_name = filename_split_list[0] + '_' \
        #                                 + filename_split_list[1] + '_'  \
        #                                 + filename_split_list[2].rsplit(".")[0]