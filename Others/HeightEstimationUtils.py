from ImageProcessor import RasterOperators, VectorOperators
import rasterio
import geopandas as gpd
import numpy as np
import pandas as pnd
from shapely.geometry import Point, Polygon ,LineString, mapping
from scipy.spatial import cKDTree
import random
from random import randrange, uniform
import statsmodels.api as sm

def GetProximalPoints(ref_data_frame,ITC_dataframe,threshold):
    final_gdf = ckdnearest(ref_data_frame, ITC_dataframe)
    final_gdf = final_gdf[final_gdf['dist'+str(0)]<threshold] 
    return final_gdf

def GetTreeHeight(treetopsshp, ndsm_path):
    meanval_ndvi = []
    for index, row in treetopsshp.iterrows():
        # print(row['genotype_i'])
        # exit(0)
        CrownBuffer = row['geometry'].buffer(0.1, cap_style=1)
        # NDVIFile = os.path.join(ndsm_path, 'nDSM.tif')
        out_image_ndvi, out_transform_ndvi = rasterio.mask.mask(rasterio.open(ndsm_path), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
        Indice, Values = RasterOperators.GetLargestN(out_image_ndvi.flatten(), 5)
        meanval_ndvi.append(np.mean(Values))
#     print([meanval_ndvi])
#     print(np.size(meanval_ndvi))
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

# def getEstimatedHeight(df_in):
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