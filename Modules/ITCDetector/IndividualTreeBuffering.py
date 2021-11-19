import os
from matlab.engine import connect_matlab
from matplotlib.colors import Normalize
import numpy as np
from shapely.geometry.base import CAP_STYLE
from ImageProcessor import RasterOperators, VectorOperators, OtherUtils
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
from ImageProcessor.Algorithms import FuzzyCMeans
from fcmeans import FCM
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from skimage import img_as_uint
from matplotlib import pyplot as plt
from seaborn import scatterplot as scatter
from ProjectConstants import GlobalConstants as gc
import subprocess
# import rpy2.robjects as robjects
# from rpy2.robjects.packages import importr
# from Others import testRexecution
# from Others import testtest
# from arosics import COREG
# from arosics import DESHIFTER
# from sentinelhub import pixel_to_utm

class ITCBufferUtils:

    def __init__(self, FileDataInfo):
        # assert m > 1
        # self.u, self.centers = None, None
        self.base_path = FileDataInfo['BaseFolder']
        self.date = FileDataInfo['Date']
        self.ClipSize = FileDataInfo['ClipSize']
        self.RefCenter = FileDataInfo['RefCenter']
        self.NumOfClusters = FileDataInfo['NumOfClusters']
        self.SkipCoregStep = FileDataInfo['SkipCoregStep']
        self.R_ArgFilename = FileDataInfo['R_ArgFilename']
        self.R_ScriptName = FileDataInfo['R_ScriptName']

    def __GenerateClippedData(self):
        inshapefile = os.path.join(self.base_path, self.date, gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, 'shapefile_merged.shp')
        print(inshapefile)
        outspath = os.path.join(self.base_path, self.date, gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, gc.CROWN_SHP_OUT_FOLDER)
        print(outspath)
        OtherUtils.TouchPath(outspath)

        treetopsshp = gpd.read_file(inshapefile)
        print(treetopsshp['FID'].size)
        # if np.shape(treetopsshp)[0]>10:
        #     treetopsshp = treetopsshp.loc[list([1,2])]
            # print('Subsamplimg local maxima as size is ' + str(np.shape(treetopsshp)[0]) + '(> 10)!')
            # indices = np.random.choice(treetopsshp.shape[0], 10, replace=False)
            # print(indices)
            # treetopsshp = treetopsshp.loc[list(indices)]
        print(np.shape(treetopsshp))
        
        ## IN PATHS
        # Orthophoto path
        in_ortho_photo = os.path.join(self.base_path, self.date, gc.COREGISTER_OUT_FOLDER, self.date + '.tif')
        if(self.SkipCoregStep):
            in_ortho_photo = os.path.join(self.base_path, self.date, gc.NON_COR_ORTHOPHOTO_FOLDER, self.date + '.tif')
        # src0 = rasterio.open(in_ortho_photo)

        # ndsm path
        in_ndsm_photo = os.path.join(self.base_path, self.date, gc.COREGISTER_OUT_FOLDER, self.date + '_ndsm.tif')
        if(self.SkipCoregStep):
            in_ndsm_photo = os.path.join(self.base_path, self.date, gc.NON_COR_ORTHOPHOTO_FOLDER, self.date + '_ndsm.tif')
        # src0 = rasterio.open(in_ndsm_photo)

        # ndsm path
        inTreeTopFile = os.path.join(self.base_path, self.date, gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, 'shapefile_merged.shp')

        ## OUT PATHS
        # Orthophoto clip path
        out_buffered_ortho_path = os.path.join(self.base_path, self.date, gc.CROPPED_DATA_FOLDER, gc.CROPPED_ORTHO_DATA_FOLDER)
        OtherUtils.TouchPath(out_buffered_ortho_path)

        # ndsm clip path
        out_buffered_ndsm_path = os.path.join(self.base_path, self.date, gc.CROPPED_DATA_FOLDER, gc.CROPPED_NDSM_DATA_FOLDER)
        OtherUtils.TouchPath(out_buffered_ndsm_path)

        # tree-tops-shp clip path
        out_buffered_shp_path = os.path.join(self.base_path, self.date, gc.CROPPED_DATA_FOLDER, gc.CROPPED_SHP_DATA_FOLDER)
        OtherUtils.TouchPath(out_buffered_shp_path)

        ## Loop for all tree tops
        for index, row in treetopsshp.iterrows():        

            if(row['geometry']==None):
                print(row[['FID','geometry']])
                continue

            CrownBuffer = row['geometry'].buffer(self.ClipSize, cap_style=1)

            # Save Orthophoto clips
            print(str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.tif')
            out_buffered_ortho_file_name = os.path.join(out_buffered_ortho_path, self.date + '_' + str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.tif')
            RasterOperators.CropImageForShpObjAndEqualize(in_ortho_photo, CrownBuffer, out_buffered_ortho_file_name)

            # Save ndsm clips
            out_buffered_ndsm_file_name = os.path.join(out_buffered_ndsm_path, self.date + '_' + str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.tif')
            RasterOperators.CropImageForShpObjAndEqualize(in_ndsm_photo, CrownBuffer, out_buffered_ndsm_file_name)

            # Save tree-top-shp clips
            out_buffered_shape_file_name = os.path.join(out_buffered_shp_path, self.date + '_' + str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.shp')
            treeTops = gpd.read_file(inTreeTopFile)
            within_treetops = treeTops[treeTops.geometry.within(Polygon(CrownBuffer))]
            within_treetops.to_file(out_buffered_shape_file_name,driver='ESRI Shapefile')
            

        # Save the clipped Orthophotp

    def RunRScript(self,script_path):
    # return subprocess.check_call(["Rscript"] + list(["/home/ensmingerlabgpu/Documents/Code_Fuzzy/RProgram/FCM-MRF_PYTHON.R"]))
        return subprocess.call("/usr/bin/Rscript --vanilla " + str(script_path), shell=True)
    

    def RBufferIndividaulTrees(self):

        self.__GenerateClippedData()
        # exit(0)

        # Input folder path
        out_buffered_ortho_path = os.path.join(self.base_path, self.date, gc.CROPPED_DATA_FOLDER, gc.CROPPED_ORTHO_DATA_FOLDER)

        # FCM out path        
        out_buffered_fcm_path = os.path.join(self.base_path, self.date,gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, gc.CROWN_SHP_BUF_FOLDER)
        # outspath = os.path.join(self.base_path, self.date, gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, gc.CROWN_SHP_OUT_FOLDER)
        # out_buffered_fcm_path = os.path.join(self.base_path, self.date, gc.CROPPED_DATA_FOLDER, gc.CROPPED_FCM_DATA_FOLDER)
        OtherUtils.TouchPath(out_buffered_fcm_path)

        # Loop through all images in folder and genereate fuzzy maps
        ArrFinal = []
        for root, folders, files in os.walk(out_buffered_ortho_path):            
            for file_name in files:
                indata = os.path.join(root, file_name)
                outspath = os.path.join(out_buffered_fcm_path, file_name)
                print(outspath)
                # Location of the temporary text file
                base_filename =  self.R_ArgFilename  # '/home/ensmingerlabgpu/Documents/Code_Fuzzy/RProgram/FCM-MRF_PYTHON.R_Filename.txt'
                lon = file_name.split('_')[1].replace('.tif','')
                lat = file_name.split('_')[2].replace('.tif','')
                # values = [(root,file_name,outspath,lon,lat)]
                ArrFinal.append((root,file_name,outspath,lon,lat))

            np.savetxt(base_filename, ArrFinal, fmt='%s', delimiter=',')
        
        self.RunRScript(self.R_ScriptName) # '/home/ensmingerlabgpu/Documents/Code_Fuzzy/RProgram/FCM-MRF_PYTHON1.R'
        # os.path.join(outspath, self.date + '_' + str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.tif')


    def BufferIndividaulTrees(self):       
        inshapefile = os.path.join(self.base_path, self.date, gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, 'shapefile_merged.shp')
        print(inshapefile)
        outspath = os.path.join(self.base_path, self.date, gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, gc.CROWN_SHP_BUF_FOLDER)
        print(outspath)
        OtherUtils.TouchPath(outspath)

        print('generating clipped data')
        self.__GenerateClippedData()

        treetopsshp = gpd.read_file(inshapefile)
        print(treetopsshp['FID'].size)
        # if np.shape(treetopsshp)[0]>10:
        #     treetopsshp = treetopsshp.loc[list([1,2])]

        # if np.shape(treetopsshp)[0]>10:
        #     print('subsamplimg local maxima as size is ' + str(np.shape(treetopsshp)[0]) + '(> 10)!')
        #     indices = np.random.choice(treetopsshp.shape[0], 10, replace=False)
        #     print(indices)
        #     treetopsshp = treetopsshp.loc[list(indices)]
        # print(np.shape(treetopsshp))

        in_ortho_photo = os.path.join(self.base_path, self.date, gc.COREGISTER_OUT_FOLDER, self.date + '.tif')
        if(self.SkipCoregStep):
            in_ortho_photo = os.path.join(self.base_path, self.date, gc.NON_COR_ORTHOPHOTO_FOLDER, self.date + '.tif')  

        # for index, row in treetopsshp.iterrows():
        fcm = FCM(n_clusters=self.NumOfClusters)
        
        centers = [(1596.7317761806983, 1975.1729466119095, 2490.9775154004105, 2477.970020533881, 7778.758778234086), 
            (276.0103881902679, 236.98742482230728, 199.20120284308365, 197.78184800437398, 4746.6642974302895), 
            (1480.2945476698142, 1991.3612549497411, 1407.201949436491, 919.6667681998173, 11280.89186719464)]
        
        src0 = rasterio.open(in_ortho_photo) 

        for index, row in treetopsshp.iterrows():

            if(row['geometry']==None):
                print(row[['FID','geometry']])
                continue

            # break
            CrownBuffer = row['geometry'].buffer(self.ClipSize, cap_style=1)

            # try:
            out_ortho_cropped, out_transform_ortho_cropped = rasterio.mask.mask(rasterio.open(in_ortho_photo), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
            # except:
                # continue
            out_ortho_cropped = RasterOperators.HistogramEqualizeImage(out_ortho_cropped)

            imagebands = []
            for i in range(0,np.shape(out_ortho_cropped)[0]): 
                imagebands.append(out_ortho_cropped[i,:,:].flatten())
            # print(np.shape(imagebands))
            imagebands = np.array(imagebands).T
            bandcnt, dw, dh = np.shape(out_ortho_cropped)

            # fit the fuzzy-c-means
            fcm.fit(imagebands)
            fcm_u = np.array(fcm.u).T
            nearest_cluster_index = self.findNearestCenter(self.RefCenter, fcm.centers)            
            fcm_labels = fcm.u.argmax(axis=1)            
            fcm_labels = fcm_labels.reshape((dw, dh))
            fcm_u = fcm_u.reshape((self.NumOfClusters,dw, dh))            

            # f, axes = plt.subplots(1, 4, figsize=(11,5))
            # plt.figure()
            # axes[0].imshow(fcm_labels==0)
            # axes[1].imshow(fcm_labels==1)
            # axes[2].imshow(fcm_labels==2)
            # axes[3].imshow(fcm_labels)
            # plt.show()

            # Read metadata of first file                
            # with rasterio.open(in_ortho_photo) as src0:                
            meta = src0.meta
            transform, width, height = calculate_default_transform(
            gc.PROJECTION_ID, gc.PROJECTION_ID, dw, dh, *CrownBuffer.bounds)
            meta.update(width = width)
            meta.update(height = height)
            meta.update(count = 1)
            meta.update(transform =  transform,)
            # meta.update(bounds = CrownBuffer.bounds)
            # Read each layer and write it to stack
            outshapefile = os.path.join(outspath, self.date + '_' + str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.tif')
            # print(outshapefile)
            with rasterio.open(outshapefile, 'w', **meta) as dst:
                for i in range(1,2):
                    tmp = img_as_uint(fcm_labels==nearest_cluster_index)
                    tmp[tmp>0] = 1
                    # tmp[tmp>0] = 1
                    selected_u_band = img_as_uint(fcm_u[nearest_cluster_index,:,:])
                    # selected_u_band[selected_u_band!=nearest_cluster_index] = 0
                    dst.write_band(i,  np.multiply(selected_u_band,tmp))
                    # dst.write_band(i, img_as_uint(fcm_labels==nearest_cluster_index))           
            
            print('Done delineation of tree {0}'.format(str(index)))
            # exit(0)
        
    def findNearestCenter(self, ref_center, cluster_centers):
        dist = []
        for i in range(np.shape(cluster_centers)[0]):
            tempcenter = cluster_centers[i,:]
            dist.append(abs(np.linalg.norm(ref_center-tempcenter)))
        # print(dist)
        argminindex = np.argmin(dist)
        return argminindex
        

            