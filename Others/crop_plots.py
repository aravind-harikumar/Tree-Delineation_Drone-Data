import os
from ITCDetector import TreeDetection, MaskTreeCrown
import rasterio
from ImageProcessor import RasterOperators, VectorOperators, OtherUtils
from shapely.geometry import Point, LineString, Polygon, mapping
import geopandas as gpd
import numpy as np
from fiona.crs import from_epsg
from ImageProcessor.Algorithms import FuzzyCMeans
from fcmeans import FCM
import matplotlib.pyplot as plt
from rasterio.warp import calculate_default_transform, reproject, Resampling
from ProjectConstants import GlobalConstants as gc
from skimage import img_as_uint

in_ortho_photo = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20180516_0/op_new/20180516.tif'
in_ndsm = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20180516_0/nDSM/nDSM-Original/20180516_nDSM_Image.tif'
in_dem = '/home/ensmingerlabgpu/Desktop/AgisoftProjects/20180516/DEM.tif'
in_dsm = '/home/ensmingerlabgpu/Desktop/AgisoftProjects/20180516/DSM.tif'
inshapefile = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20181015/op_new/out/Plot_centers/PlorCenters.shp'
inTreeTopFile = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20180516_0/ITC-Data/All-ITC/shapefile_merged.shp'
outFolder = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20181015/op_new/out/Plots_out_files/'
ClipSize = 10
NumOfClusters = 2
RefCenter = [1480, 1991, 1407, 919, 11280]

centers = [(1596.7317761806983, 1975.1729466119095, 2490.9775154004105, 2477.970020533881, 7778.758778234086), 
    (276.0103881902679, 236.98742482230728, 199.20120284308365, 197.78184800437398, 4746.6642974302895), 
    (1480.2945476698142, 1991.3612549497411, 1407.201949436491, 919.6667681998173, 11280.89186719464)]

def main():
    treetopsshp = gpd.read_file(inshapefile)
    src0 = rasterio.open(in_ortho_photo)

    for index, row in treetopsshp.iterrows():

        # print(row['geometry'])
        # print(Point(261960.4986338798,5176607.815729483))


        # 20180710_261960.4986338798_5176607.815729483
        
        CrownBuffer = row['geometry'].buffer(ClipSize, cap_style=1)
        VectorOperators.SaveAsShpFileByType(CrownBuffer, os.path.join(outFolder,'Plot_Buffer', str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.shp'), 'Polygon')
        # exit(0)

        treeTops = gpd.read_file(inTreeTopFile)
        within_chicago = treeTops[treeTops.geometry.within(Polygon(CrownBuffer))]
        # print(within_chicago)
        out_file = os.path.join(outFolder,'Plot_tree_tops',str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.shp')
        within_chicago.to_file(out_file,driver='ESRI Shapefile')
        # exit(0)
        
        VectorOperators.SaveAsShpFileByType(CrownBuffer, os.path.join(outFolder,'Plot_Buffer', str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.shp'), 'Polygon')

        # try:
        out_ortho_cropped_orig, out_transform_ortho_cropped = rasterio.mask.mask(rasterio.open(in_ortho_photo), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
        # except:
            # continue
        out_ortho_cropped = RasterOperators.HistogramEqualizeImage(out_ortho_cropped_orig)
        
        imagebands = []
        for i in range(0,np.shape(out_ortho_cropped)[0]): 
            imagebands.append(out_ortho_cropped[i,:,:].flatten())
        # print(np.shape(imagebands))
        imagebands = np.array(imagebands).T
        bandcnt, dw, dh = np.shape(out_ortho_cropped)

        fcm = FCM(n_clusters=NumOfClusters)
        # fit the fuzzy-c-means
        fcm.fit(imagebands)
        fcm_u = np.array(fcm.u).T
        nearest_cluster_index, next_nearest_cluster_index = findNearestCenter(RefCenter, fcm.centers)  
        # print(nearest_cluster_index, next_nearest_cluster_index)
        # exit(0)          
        fcm_labels = fcm.u.argmax(axis=1)            
        fcm_labels = fcm_labels.reshape((dw, dh))
        fcm_u = fcm_u.reshape((NumOfClusters,dw, dh))

        meta = src0.meta
        transform, width, height = calculate_default_transform(
        gc.PROJECTION_ID, gc.PROJECTION_ID, dw, dh, *CrownBuffer.bounds)
        meta.update(width = width)
        meta.update(height = height)
        meta.update(count = 1)
        meta.update(transform =  transform,)
        # meta.update(bounds = CrownBuffer.bounds)
        # Read each layer and write it to stack
        outshapefile = os.path.join(outFolder, 'Plot_Fuzzy_maps', str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.tif')
        # print(outshapefile)
        with rasterio.open(outshapefile, 'w', **meta) as dst:
            for i in range(1,2):
                tmp = img_as_uint(fcm_labels==nearest_cluster_index)
                tmp[tmp>0] = 1
                # tmp[tmp>0] = 1
                selected_u_band = img_as_uint(fcm_u[nearest_cluster_index,:,:])
                # selected_u_band[selected_u_band!=nearest_cluster_index] = 0
                dst.write_band(i, np.multiply(selected_u_band,tmp))
                # dst.write_band(i, img_as_uint(fcm_labels==nearest_cluster_index))   
 
        outshapefile_ortho = os.path.join(outFolder, 'Plots_Multipectral_Data', str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.tif')
        RasterOperators.CropImageForShpObj(in_ortho_photo, CrownBuffer, outshapefile_ortho)    

        outshapefile_ndsm = os.path.join(outFolder, 'Plot_nDSM', str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.tif')
        RasterOperators.CropImageForShpObj(in_ndsm, CrownBuffer, outshapefile_ndsm)  

        outshapefile_dem = os.path.join(outFolder, 'Plot_DEM', str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.tif')
        RasterOperators.CropImageForShpObj(in_dem, CrownBuffer, outshapefile_dem)  

        outshapefile_dsm = os.path.join(outFolder, 'Plot_DSM', str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.tif')
        RasterOperators.CropImageForShpObj(in_dsm, CrownBuffer, outshapefile_dsm)  


        # Plot_nDSM
        
        print('Done delineation of tree {0}'.format(str(index)))
        # exit(0)

def findNearestCenter(ref_center, cluster_centers):
    dist = []
    for i in range(np.shape(cluster_centers)[0]):
        tempcenter = cluster_centers[i,:]
        dist.append(abs(np.linalg.norm(ref_center-tempcenter)))
    # print(dist)
    argminindex = np.argmin(dist)
    # print(dist)
    dist.remove(dist[argminindex])
    argminindex1 = np.argmin(dist)
    # print(dist)
    # exit(0)
    return argminindex,argminindex1

main()