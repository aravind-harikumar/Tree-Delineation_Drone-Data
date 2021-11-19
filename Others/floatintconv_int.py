from osgeo import gdal, osr
import os
import skimage
from tifffile import imsave
from skimage import img_as_uint, img_as_float32
import rasterio

drv = gdal.GetDriverByName('GTiff')

# DataPath = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/20180516/100010_SCA_20180516_m1_2018_05_16_15_25_41'
in_DataPath = '/home/ensmingerlabgpu/Desktop/22_2.tif'
OutFileName = '/home/ensmingerlabgpu/Desktop/22_5.tif'

# ds_in = gdal.Open(in_DataPath)
# for i in range(1,ds_in.RasterCount,1):
#     band = ds_in.GetRasterBand(i)
#     # print(band.GetMetadata())
#     # ds_out = drv.CreateCopy(file + '_' + str(i) + '.tif', band.ReadAsArray())
#     imsave(os.path.join(root,file + '_' + str(i) + '.tif'), band.ReadAsArray())
with rasterio.open(in_DataPath) as src0:
    meta = src0.meta
    meta.update(dtype = 'float32')
    # meta.update(nodata = 0)
    # driver: the name of the desired format driver
    # width: the number of columns of the dataset
    # height: the number of rows of the dataset
    # count: a count of the dataset bands dtype: the data type of the dataset
    # crs: a coordinate reference system identifier or description
    # transform: an affine transformation matrix, and
    # nodata: a “nodata” value
        
    # Read each layer and write it to stack
    with rasterio.open(OutFileName, 'w', **meta) as dst:
        for i in range(1,src0.count+1):
            bandarr = src0.read(i)
            # bandarr[bandarr>4086] = 4086
            # bandarr = skimage.filters.gaussian(bandarr, sigma=0)
            bandarr  = bandarr * 255.0/bandarr.max()#.astype('float32')
            dst.write_band(i, bandarr.astype('float32'))

print('Done Copying!')
# return True