import sys,os
from numpy.core.defchararray import asarray
import pandas as pnd
import geopandas as gpd
from shapely import geometry
import rasterio
# from ITCDetector import TreeDetection, MaskTreeCrown
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
from rasterio.warp import calculate_default_transform, reproject, Resampling
import fiona
import gdal
import random
from random import randrange, uniform
from fiona.crs import from_epsg
from ProjectConstants import GlobalConstants as gc
import statsmodels.api as sm

def GetProximalPoints(ref_data_frame,ITC_dataframe,threshold):
    final_gdf = ckdnearest(ref_data_frame, ITC_dataframe)
    final_gdf = final_gdf[final_gdf['dist'+str(0)]<threshold] 
    return final_gdf

def mainfunct():


    # D100TreeRefData = '//home/ensmingerlabgpu/Desktop/AgisoftProjects/20170626/Estimates/Height/Ref_Trees/refdata.shp'
    # treetopsshp = gpd.read_file(D100TreeRefData)
    # treetopsshp.dropna(subset=['Height','TreeHeight'],inplace=True)
    # # treetopsshp.rename(columns={"tree_id":"genotype_i"},inplace=True)

    # model = getEstimatedHeight(treetopsshp)
    # predictions = model.predict(treetopsshp['Height'])
    # treetopsshp['HeightEst'] = predictions
    
    # Reference Data of 100 Trees
    # nDSM from Data 1
    D100TreeRefData = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Site_info/ReferenceData/StCas_TREE_RS_DATA.shp'
    # D100TreeRefData = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Site_info/ReferenceData/SC_100_TREE_REFERENCE_DATA.shp'
    treetopsshp = gpd.read_file(D100TreeRefData)
    D1_nDSM_Path = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20170626/nDSM/nDSM.tif'
    D1_shp_path = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20170626/ITC-Data/All-ITC/shapefile_merged.shp'
    D1_shp_data = gpd.read_file(D1_shp_path)
    # print(treetopsshp.head())
    # print(D1_shp_data.head())
    treetopsshp.rename(columns={"tree_id":"genotype_i"},inplace=True)
    # print(treetopsshp.head())
    # exit(0)
    # Get the tree tops in Date 1
    final_gdf_treetop = GetProximalPoints(treetopsshp,D1_shp_data,5)    
    # print(final_gdf_treetop.head())
    # print(final_gdf_treetop['FID'].count())
    # exit()
    # Get tree height frrm DSM for the tree
    meanval_ndvi = GetTreeHeight(final_gdf_treetop, D1_nDSM_Path)

    final_gdf_treetop.insert(2, "IDC", [i for i in range(final_gdf_treetop['FID'].count())], True)
    # print(final_gdf_treetop)

    print(np.array(meanval_ndvi))
    
    data = {'Height':np.array(meanval_ndvi),'IDC':[i for i in range(final_gdf_treetop['FID'].count())]}
    testdf = pnd.DataFrame(data)
    # print(testdf)

    # testdf.insert(1, "IDA", [i for i in range(112)], True) 
    # testdf.rename(columns = {'IDA':'IDC'}, inplace=True)

    final_gdf_treetop = final_gdf_treetop.merge(testdf, how='inner', on='IDC')

    # Get height estimate from DSM DN value
    model = getEstimatedHeight(final_gdf_treetop)
    predictions = model.predict(final_gdf_treetop['Height'])
    final_gdf_treetop['HeightEst'] = predictions

    print(final_gdf_treetop[['genotype_i','Height','HeightEst','geometry']])

    outshpfile = '/home/ensmingerlabgpu/Desktop/AgisoftProjects/20170626/Estimates/Height/Ref_Trees/refdata.shp'
    final_gdf_treetop.to_file(driver= 'ESRI Shapefile', filename = outshpfile)

    # D1_Data = gpd.read_file(D1_Data_Path)

    # nDSM from Data 2
    # D2_Data_Path = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20170809/nDSM/nDSM-Original/20170809_nDSM_Image.tif'
    # D2_Data = gpd.read_file(D2_Data_Path)

    # data = gpd.read_file(D100TreeRefData)
    # data = data[['genotype_i','geometry']]

    # print(data.head())

    # Locating proximal points
    # final_gdf = ckdnearest(D1_Data, D2_Data, 1)
    # final_gdf = final_gdf[final_gdf['dist'+str(1)]<1]

def GetTreeHeight(treetopsshp, ndsm_path):
    meanval_ndvi = []
    for index, row in treetopsshp.iterrows():
        # print(row['genotype_i'])
        # exit(0)
        CrownBuffer = row['geometry'].buffer(0.3, cap_style=1)
        # NDVIFile = os.path.join(ndsm_path, 'nDSM.tif')
        out_image_ndvi, out_transform_ndvi = rasterio.mask.mask(rasterio.open(ndsm_path), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
        Indice, Values = RasterOperators.GetLargestN(out_image_ndvi.flatten(), 5)
        meanval_ndvi.append(np.mean(Values))
    print([meanval_ndvi])
    print(np.size(meanval_ndvi))
    return meanval_ndvi

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


def getEstimatedHeight(df_in):
    df_in.dropna(inplace=True)
    X = df_in["RefHeight"]
    y = df_in["nDSMValHeight"]
    # Note the difference in argument order
    listvals = list(zip(X,y))
    print(len(listvals))
    randlist= random.sample(listvals, k=200)
    tmpFile = gpd.GeoDataFrame(columns=['X','Y'])
    for a, b in randlist:
        tmpFile = tmpFile.append({'X': a, 'Y': b}, ignore_index=True)
    model = sm.OLS(tmpFile['Y'], tmpFile['X'],M=sm.robust.norms.HuberT()).fit()
    print(model.summary())
    return model
    
# def getEstimatedHeight(df_in):
#     # print(X)
#     df_in.dropna(inplace=True)

#     X = df_in["Height"]
#     y = df_in["TreeHeight"]/100
#     # Note the difference in argument order
#     listvals = list(zip(X,y))
#     randlist= random.sample(listvals, k=100)
#     tmpFile = gpd.GeoDataFrame(columns=['X','Y'])
#     for a, b in randlist:
#         tmpFile = tmpFile.append({'X': a, 'Y': b}, ignore_index=True)
#     model = sm.OLS(tmpFile['Y'], tmpFile['X']).fit()
#     # print(model.summary())
#             # predictions = model.predict(X) # make the predictions by the model
#     # finalfile = gpd.GeoDataFrame(columns=['Y_predictions','X','Y'])
#     # aaa = list(zip(predictions,X,y))
#     # for a, b, c in aaa:
#     #     finalfile = finalfile.append({'Y_predictions': a, 'X': b, 'Y': c}, ignore_index=True) # yuck
#     # print(finalfile.head())
#             # df_in['HeightEst'] = predictions
#             # # exit(0)
#             # return df_in

#     return model

mainfunct()