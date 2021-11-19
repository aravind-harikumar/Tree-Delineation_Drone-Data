# from osgeo import gdal, osr
import gdal
import os
import numpy as np
import rasterio
from tifffile import imsave
from ImageProcessor import RasterOperators
from skimage import io, data, img_as_float, img_as_uint
import fiona
from rasterio.mask import mask
from fiona.crs import from_epsg


# drv = gdal.GetDriverByName('GTiff')
base_path = '/home/ensmingerlabgpu/Desktop/AgisoftProjects/20181015/'
ortho_photo = '20181015_1.tif'
clip_ortho_photo = '20181015_1_clipped.tif'
# ndsm_re = 'nDSM_reprojected.tif'
StudyAreaShp = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Site_info/ArcGIS/StCasimir_SpruceUp_temp_rh.shp'

def main():

    in_image = os.path.join(base_path, ortho_photo)
    out_image = os.path.join(base_path, clip_ortho_photo)

    Proj_iD = 'EPSG:32619'
    RasterOperators.ReprojectImage(in_image, in_image, Proj_iD)

    with fiona.open(StudyAreaShp, 'r') as shapefile:
        ShapeMask = [feature["geometry"] for feature in shapefile]
        RasterOperators.CropImage(os.path.join(base_path,in_image), ShapeMask, os.path.join(base_path,out_image))

main()