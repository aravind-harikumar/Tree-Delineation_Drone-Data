# from osgeo import gdal, osr
import gdal
import os
import numpy as np
import rasterio
from tifffile import imsave
from ImageProcessor import RasterOperators
from skimage import io, data, img_as_float, img_as_uint

# drv = gdal.GetDriverByName('GTiff')
base_path = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/ProcessedMSData/20180710/Sliced_Data/'
in_file_name = '20180710_262062_5176477.tif'
out_file_name = '20180710_262062_5176477_1.tif'

def main():
    with rasterio.open(os.path.join(base_path,in_file_name)) as src:
        meta = src.meta
        print(src.count)

        with rasterio.open(os.path.join(base_path,out_file_name), 'w', **meta) as dst:
            for bandId in range(1,src.count+1):
                # print(src.read(bandId))
                band_item = src.read(bandId)
                # band_item = mask_saturation(band_item, nodata=0)
                # band_item[band_item>1500] = 0
                band_heq = img_as_uint(RasterOperators.HistogramEqualizeImage(band_item))
                dst.write_band(bandId, band_heq)

def mask_saturation(src, nodata=0):
    '''
    Masks out saturated values (surface reflectances of 16000). Arguments:
        src    A gdal.Dataset or NumPy array
        nodata  The NoData value; defaults to -9999.
    '''
    # Can accept either a gdal.Dataset or numpy.array instance
    if not isinstance(src, np.ndarray):
        src = src.ReadAsArray()

    # Create a baseline "nothing is saturated in any band" raster
    mask = np.empty((src.shape[0], src.shape[1]))
    mask.fill(False)

    # Update the mask for saturation in any band
    for i in range(1):
        np.logical_or(mask,
            np.in1d(src[i,...].ravel(), (3000,)).reshape(src[i,...].shape),
            out=mask)
    # Repeat the NoData value across the bands
    np.place(src, mask.repeat(1, axis=0), (nodata,))
    return src

main()