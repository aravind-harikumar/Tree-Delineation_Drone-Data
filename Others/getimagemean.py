# from osgeo import gdal, osr
import gdal
import os
import numpy as np
import rasterio
from tifffile import imsave
from ImageProcessor import RasterOperators
from skimage import io, data, img_as_float, img_as_uint

# drv = gdal.GetDriverByName('GTiff')
base_path = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/ProcessedMSData/20180514/ITC-Data/All-ITC/'
in_file_name = 'tree_part.tif'
# out_file_name = '20180710_262062_5176477_1.tif'

def main():
    with rasterio.open(os.path.join(base_path,in_file_name)) as src:
        meta = src.meta
        print(src.count)

        meanArr = []
        for i in range(1,src.count+1):
            band = np.array(src.read(i))
            zerobandinx = [band != 0]
            # print(np.mean(band[zerobandinx].flatten()))
            meanArr.append(np.mean(band[zerobandinx].flatten()))
        print(meanArr)
        

        # with rasterio.open(os.path.join(base_path,out_file_name), 'w', **meta) as dst:
        #     for bandId in range(1,src.count+1):
        #         # print(src.read(bandId))
        #         band_item = src.read(bandId)
        #         # band_item = mask_saturation(band_item, nodata=0)
        #         # band_item[band_item>1500] = 0
        #         band_heq = img_as_uint(RasterOperators.HistogramEqualizeImage(band_item))
        #         dst.write_band(bandId, band_heq)
main()