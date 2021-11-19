import os
from osgeo import gdal, osr
from tifffile import imsave

drv = gdal.GetDriverByName('GTiff')
# DataPath = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/20180516/100010_SCA_20180516_m1_2018_05_16_15_25_41'
DataPath = '/home/ensmingerlabgpu/Documents/tst/'
for root, folders, files in os.walk(DataPath):
    for file in files:
        # if "rd_rf" in file and len(file.rsplit(".",1))<2:
        print(os.path.join(root, file))
        ds_in = gdal.Open(os.path.join(root, file))
        print(ds_in)

        # for i in range(1,ds_in.RasterCount,1):
        #     print(os.path.join(root, file + '_' + str(i)))
        #     band = ds_in.GetRasterBand(i)
        #     # print(band.GetMetadata())
        #     # ds_out = drv.CreateCopy(file + '_' + str(i) + '.tif', band.ReadAsArray())
        #     imsave(os.path.join(root,'dd',file + '_' + str(i) + '.tif'), band.ReadAsArray())
        # # srs = osr.SpatialReference()
        # # srs.ImportFromEPSG(4326)
        # # ds_out.SetProjection(srs.ExportToWkt())
        # # ds_in = None
        # # ds_out = None