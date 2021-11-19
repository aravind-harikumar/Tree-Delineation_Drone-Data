import os,sys
from ImageProcessor import RasterOperators, VectorOperators, OtherUtils
import geopandas as gpd
from pyproj import Proj, transform
from shapely.geometry import Polygon, Point, LineString, mapping,shape
import rasterio
from rasterio.mask import mask
from matplotlib import pyplot
import numpy as np
import time
import skimage
from skimage import io, data, img_as_float, img_as_uint, exposure

datelist = ['20180516','20180711','20181015']
basepath = '/mnt/4TBHDD/HS_DATA/'
outpath = '/mnt/4TBHDD/HS_DATA/output'

refdatedata = os.path.join(basepath, datelist[0], '0_Ref_data_shp', 'treeslonglat_V2.shp')
treerefdata = gpd.read_file(refdatedata)
TreeGenotypeIDList = treerefdata['arb'].unique()
# print(treegendata)

import pandas as pd
import random

for date in datelist:
    for TreeGenotypeID in TreeGenotypeIDList:
        DataPath = os.path.join(basepath,date,'Clip', date + '_clip.tif')

        RefShpPath = os.path.join(basepath,date, '0_Ref_data_shp', 'treeslonglat_V2.shp')
        RefShpPathInner = gpd.read_file(RefShpPath)
        print(TreeGenotypeID)
        # print(RefShpPathInner)
        # Projected
        row = RefShpPathInner.loc[(RefShpPathInner['arb'] == TreeGenotypeID)] # & (RefShpPathInner['clas'] == 'Predicted')]
        row = row.iloc[0]
        # print(row)        
        # exit(0)
        # print(row['geometry'].x)
        # x,y = [row['geometry'].coords[0][0],row['geometry'].coords[0][1]]
        x,y = [row['geometry'].x, row['geometry'].y]
        myProj = Proj("+proj=utm +zone=19 +datum=WGS84 +units=m +no_defs")
        UTMx, UTMy = myProj(float(x), float(y))
        CrownBuffer = Point(UTMx, UTMy).buffer(2.5)
        print(UTMx,UTMy)
        out_image, out_transform = rasterio.mask.mask(rasterio.open(DataPath), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0) 
        out_image_wv = wavelt(out_image)
        # RasterOperators
        OtherUtils.TouchPath(os.path.join(outpath, date))
        OutFileName = os.path.join(outpath, date, 'Tree' + '_' + str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.tif')
        # RasterOperators.CropImageForShpObjAndEqualize(in_ndsm_photo, CrownBuffer, out_buffered_ndsm_file_name)
        out_meta = rasterio.open(DataPath).meta.copy()
        out_meta.update({"driver": "GTiff",
            "height": out_image_ndvi.shape[1],
            "width": out_image_ndvi.shape[2],
            "transform": out_transform_ndvi,
            "dtype": 'uint16'}) #uint16, float64
        # out_meta.update(dtype = 'float64')        
        out_image = img_as_float(exposure.equalize_hist(skimage.img_as_float(out_image_ndvi)))
        out_image = skimage.img_as_uint(out_image)
        # with rasterio.open(OutFileName+".tif", "w", **out_meta) as dest:
        with rasterio.open(OutFileName, "w", **out_meta) as dest:
            dest.write(out_image)
        print(np.shape(out_image_ndvi))
        # pyplot.imshow(out_image_ndvi[119,:,:])
        # pyplot.show()
        
        # print(iop)
        # exit(0)

        # print(DataPath)
        # print(RefShpPath)

        # # Read raster file. # read file bands
        # imagedata = RasterOperators.ReadImage(DataPath)
        # # exit(0)

        # # For rows in reference shape file
        # shpdata = gpd.read_file(RefShpPath)

        # signaturearr = []
        # shpdata = gpd.read_file(RefShpPath)
        # myProj = Proj("+proj=utm +zone=19 +datum=WGS84 +units=m +no_defs")
        # for index, row in shpdata.iterrows():
        #     # x,y = [row['geometry'].coords[0][0],row['geometry'].coords[0][1]]
        #     # UTMx, UTMy = myProj(float(x), float(y))
        #     # CrownBuffer = Point(UTMx, UTMy).buffer(1000)
        #     # print(UTMx,UTMy)
        #     # CrownBuffer = row['geometry'].buffer(0.8, cap_style=1)
        #     out_image_ndvi, out_transform_ndvi = rasterio.mask.mask(rasterio.open(DataPath), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)        
        #     print(np.shape(out_image_ndvi))
        #     pyplot.imshow(out_image_ndvi)
        #     pyplot.show()
        #     exit(0)
        #     # get average pixel value
        #     TreeID = shpdata['0']
        #     NDVI = 0
        #     PRI  = 0
        #     CCI  = 0
        #     # Indice, Values = RasterOperators.GetLargestN(out_image_pri.flatten(), 25)
        #     # meanval_pri.append(np.mean(Values))
        #     print('Reading:Band1')
        #     signaturearr.append([NDVI,PRI,CCI])
        #     exit(0)

        #     # stack selected bands
        #     # CrownBuffer = row['geometry'].buffer(0.8, cap_style=1)
        #     # NDVIFile = os.path.join(map_path, 'NDVI.tif')
        #     # out_image_ndvi, out_transform_ndvi = rasterio.mask.mask(rasterio.open(NDVIFile), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
        #     # Indice, Values = RasterOperators.GetLargestN(out_image_ndvi.flatten(), 25)
        #     # meanval_ndvi.append(np.mean(Values))

        print('Done Stacking Orthophoto!')

    
    # ss = VectorOperator
    # myProj = Proj("+proj=utm +zone=32 +datum=WGS84 +units=m +no_defs")
    # # for index, row in data.iterrows():
    # UTMx, UTMy = myProj(float(row[1]), float(row[0]))
    # shpdata = gpd.read_file(RefShpPath)
    
    # print(shpdata.head())


    exit(0)


# Clip data
# Save