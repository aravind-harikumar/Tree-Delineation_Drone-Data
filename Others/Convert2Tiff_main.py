from osgeo import gdal, osr
import os
from tifffile import imsave
from arsf_envi_reader import numpy_bin_reader
from arsf_envi_reader import envi_header
from spectral import *
from ImageProcessor import RasterOperators

# drv = gdal.GetDriverByName('GTiff')
# # DataPath = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/20180516/100010_SCA_20180516_m1_2018_05_16_15_25_41'
# DataPath = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/20181015/100024_SCA_15102018_leg2_2018_10_15_17_20_14/'
# for root, folders, files in os.walk(DataPath):
#     for file in files:
#         if  "_rd_rf_or" in file and ".hdr" not in file:
#             print(os.path.join(root, file))
#             ds_in = gdal.Open(os.path.join(root, file))
#             ds_in = gdal.Translate(os.path.join('/home/ensmingerlabgpu/Documents/tst/ff/', file+'.tif'), ds_in)
#             print(os.path.join(root, file))

DataPath = '/mnt/4TBHDD/HS_DATA/20181015/clip/clip_20181015.tif'
dp = RasterOperators.ReadImage(DataPath)
print(dp.meta)

# DataPath = ''
