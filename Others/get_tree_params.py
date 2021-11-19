import os
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
from statistics import mean 
from skimage import io, data, img_as_float, img_as_uint
import fiona
from fiona.crs import from_epsg
import geopandas as gpd
from rasterio.mask import mask
from ImageProcessor import RasterOperators, VectorOperators
import shapely.wkt
# from shapely.geometry import Polygon
import pandas as pd 
from shapely.geometry import Point, LineString, Polygon, mapping
# from shapely.geometry import Point, LineString, Polygon, mapping

def main():
    in_shp_loc = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/ProcessedMSData/20180514/shapefile_merged.shp'
    out_shp_loc = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/ProcessedMSData/20180514/shapefile_merged_out.shp'
    OrthoFile = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20180514/full_image/20180514_Reprojected.tif'
    
    NDVIMapOut = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20180514/full_image/20180514_NDVI.tif'
    PRIMapOut = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20180514/full_image/20180514_PRI.tif'
    CCIMapOut = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20180514/full_image/20180514_CCI.tif'

    # getNDVIMap(OrthoFile,NDVIMapOut,PRIMapOut, CCIMapOut)

    # exit(0)
    # shape = fiona.open(in_shp_loc)
    treetopsshp = gpd.read_file(in_shp_loc)    

    # Define a polygon feature geometry with one attribute
    schema = {
        'geometry': 'Point',
        'properties': {'NDVI': 'float' ,'PRI': 'float', 'CCI': 'float'},
        # 'properties': {'PRI': 'int'},
        # 'properties': {'CCI': 'int'},
    }
    # Write a new Shapefile

    meanval_ndvi = []
    meanval_pri = []
    meanval_cci = []

    for index, row in treetopsshp.iterrows():
        CrownBuffer = row['geometry'].buffer(0.8, cap_style=1)
        # print(gpd.GeoSeries(Polygon(CrownBuffer)))
        # VectorOperators.SaveAsShpFile(CrownBuffer, os.path.join("ss.shp"))
        # with fiona.open("ss.shp", 'r') as shapefile:
            # ShapeMask = [feature["geometry"] for feature in shapefile]
            # print(ShapeMask)
            # print(ShapeMask)
        # RasterOperators.GetCropImage(NDVIMapOut, CrownBuffer)
        out_image_ndvi, out_transform_ndvi = rasterio.mask.mask(rasterio.open(NDVIMapOut), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
        out_image_pri, out_transform_pri = rasterio.mask.mask(rasterio.open(PRIMapOut), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
        out_image_cci, out_transform_cci= rasterio.mask.mask(rasterio.open(CCIMapOut), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
        # op = pd.DataFrame(np.asmatrix(out_image))
        arr = out_image_ndvi.flatten()
        meanval_ndvi.append(np.mean(arr[largest_indices(arr, 10)]))
        # if(meanval_ndvi<60000):
            # meanval_ndvi = 60000
        
        arr = out_image_pri.flatten()
        meanval_pri.append(np.mean(arr[largest_indices(arr, 10)]))
        # if(meanval_pri<60000):
        #     meanval_pri = 60000

        arr = out_image_cci.flatten()
        meanval_cci.append(np.mean(arr[largest_indices(arr, 10)]))
        # if(meanval_cci<60000):
        #     meanval_cci = 60000

    norm_ndvi = [float(i)/max(meanval_ndvi) for i in meanval_ndvi]
    norm_pri = [float(i)/max(meanval_pri) for i in meanval_pri]
    norm_cci = [float(i)/max(meanval_cci) for i in meanval_cci]
    # print(norm_ndvi)

    print(norm_ndvi[0])
    print(norm_pri[0])
    print(norm_pri[1])
    # exit(0)

    loopcnt = 0
    with fiona.open(out_shp_loc, 'w', crs=from_epsg(32619), driver='ESRI Shapefile', schema=schema) as c:
        treetopsshp = gpd.read_file(in_shp_loc)   
        for index, row in treetopsshp.iterrows():
            # CrownBuffer = row['geometry'].buffer(0.8, cap_style=1)
            # print(index)

                    ## If there are multiple geometries, put the "for" loop here
            c.write({
                'geometry': mapping(row['geometry']),
                'properties': {'NDVI': norm_ndvi[loopcnt], 'PRI': norm_pri[loopcnt], 'CCI': norm_cci[loopcnt]}
                # 'properties': {'PRI': meanval_pri},
                # 'properties': {'CCI': meanval_cci},
            })
            loopcnt = loopcnt + 1

            # exit(0)


    # in_shp_all = gpd.read_file(out_shp_loc)
    
    # # Create a custom polygon
    # polygon = gpd.read_file('/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Site_info/ArcGIS/StCasimir_SpruceUp_temp.shp')

    # clip_out = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/ProcessedMSData/20180514/shapefile_merged_out_clip.shp'
    # # world_clipped = gpd.clip(in_shp_all, polygon)
    # # print(type(world_clipped))
    # # world_clipped.to_file(clip_out)

    # world_clipped = in_shp_all['geometry'].difference(polygon)
    # print(type(world_clipped))
    # VectorOperators.SaveAsShpFileByType(world_clipped, clip_out,'Point')
 

def largest_indices(ary, n):
    """Returns the n largest indices from a numpy array."""
    flat = ary.flatten()
    indices = np.argpartition(flat, -n)[-n:]
    indices = indices[np.argsort(-flat[indices])]
    return np.unravel_index(indices, ary.shape)

def getNDVIMap(OrthoFile, NDVIMapOut, PRIMapOut, CCIMapOut):
    print('Generate NDVI Map')

    with rasterio.open(os.path.join(OrthoFile)) as ortho_src:
        meta = ortho_src.meta
        meta.update(count = 1)

        NIR = ortho_src.read(5)
        R = ortho_src.read(4)

        b528 = ortho_src.read(1)
        b570 = ortho_src.read(2)
        b645 = ortho_src.read(3)

        # with rasterio.open(os.path.join(NDVIMapOut), 'w', **meta) as ndvi_dst:
        #     nirminusr = np.subtract(NIR, R)
        #     nirplusr = np.add(NIR, R)
        #     ndvimat = np.divide(nirminusr,nirplusr)
        #     ndvi_dst.write_band(1, img_as_uint(ndvimat))
        meta.update(dtype  = 'float64')
        with rasterio.open(os.path.join(PRIMapOut), 'w', **meta) as pri_dst:
            b528mb570 = np.subtract(b528, b570)
            b528pl570 = np.add(b528, b570)
            primat = np.divide(b528mb570,b528pl570)

            pri_dst.write_band(1, primat)

        with rasterio.open(os.path.join(CCIMapOut), 'w', **meta) as cci_dst:
            b528mb645 = np.subtract(b528, b645)
            b528pl645 = np.add(b528, b645)
            ccimat = np.divide(b528mb645,b528pl645)
            # meta.update(dtype  = 'float64')
            cci_dst.write_band(1, ccimat)

main()

