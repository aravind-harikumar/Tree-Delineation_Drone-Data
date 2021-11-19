import geopandas as gpd
import os
from ImageProcessor import OtherUtils, RasterOperators
import rasterio
import pandas as pd 
from shapely.geometry import Point, LineString, Polygon, mapping
import rasterio.mask
import fiona

in_shp_loc = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Site_info/ArcGIS/StCasimir_SpruceUp_temp.shp'

In_image_1 = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20180514/CoregisteredSlices/20180514.tif'
In_image_2 = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20180710/CoregisteredSlices/20180710.tif'
In_image_3 = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20181015/CoregisteredSlices/20181015.tif'

# In_image = '/home/ensmingerlabgpu/Desktop/AgisoftProjects/20181015/20181015.tif'
# reproj_image = '/home/ensmingerlabgpu/Desktop/AgisoftProjects/20180710/nDSM_rp.tif'
# Out_image = '/home/ensmingerlabgpu/Desktop/AgisoftProjects/20180710/nDSM1.tif'

RasterOperators.ReprojectImage(In_image_1, In_image_1, 'EPSG:32619')
with fiona.open(os.path.join( in_shp_loc), 'r') as shapefile:
        ShapeMask = [feature["geometry"] for feature in shapefile]
        RasterOperators.CropImage(In_image_1, ShapeMask, In_image_1)

RasterOperators.ReprojectImage(In_image_2, In_image_2, 'EPSG:32619')
with fiona.open(os.path.join( in_shp_loc), 'r') as shapefile:
        ShapeMask = [feature["geometry"] for feature in shapefile]
        RasterOperators.CropImage(In_image_2, ShapeMask, In_image_2)

RasterOperators.ReprojectImage(In_image_3, In_image_3, 'EPSG:32619')
with fiona.open(os.path.join( in_shp_loc), 'r') as shapefile:
        ShapeMask = [feature["geometry"] for feature in shapefile]
        RasterOperators.CropImage(In_image_3, ShapeMask, In_image_3)
                

# OtherUtils.TouchPath()
# treetopsshp = gpd.read_file(in_shp_loc)
# for index, row in treetopsshp.iterrows():
        # CrownBuffer = row['geometry'].buffer(0.8, cap_style=1)
        # NDVIFile = os.path.join(In_image)
        # out_image_ndvi, out_transform_ndvi = rasterio.mask.mask(rasterio.open(NDVIFile), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)



