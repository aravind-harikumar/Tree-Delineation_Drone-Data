from osgeo import gdal, ogr
import rasterio

# Filename of input OGR file
sample_vector = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Site_info/ArcGIS/StCasimir_SpruceUp_temp.shp'

# Filename of the raster Tiff that will be created
sample_raster = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20181015/ortho/20181015_261820_5176477.tif'

# Filename of the raster Tiff that will be created
output_raster = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20181015/full_dsm/20181015_261820_5176477_1.tif'

dataset = rasterio.open(sample_raster)
src = gdal.Open(sample_raster)
ulx, xres, xskew, uly, yskew, yres  = src.GetGeoTransform()
# print('Reading ' + dataset.name)
# print('Width:' + str(dataset.width) + ' Height:' + str(dataset.height) + ' Bands:' + str(dataset.count))
# print(ulx, xres, xskew, uly, yskew, yres)

bounds = dataset.bounds
left= bounds.left
bottom = bounds.bottom
right = bounds.right
top = bounds.top

print(left, bottom, xskew, right, top)


# Define pixel_size and NoData value of new raster
pixelSizeX = dataset.width # sample_raster.rasterUnitsPerPixelX()
pixelSizeY = dataset.height # sample_raster.rasterUnitsPerPixelY()
NoData_value = 0
print(pixelSizeX,pixelSizeY)

# Open the data source and read in the extent
source_ds = ogr.Open(sample_vector)
source_layer = source_ds.GetLayer()
x_min, x_max, y_min, y_max = source_layer.GetExtent()
# print(x_min, x_max, y_min, y_max)

# Create the destination data source
x_res = float((right - left) / pixelSizeX)
y_res = float((top - bottom) / pixelSizeY)

print(x_res,y_res)
exit(0)

target_ds = gdal.GetDriverByName('GTiff').Create(output_raster, x_res, y_res, 1, gdal.GDT_UInt16)
target_ds.SetGeoTransform((x_min, pixelSizeX, 0, y_max, 0, -pixelSizeY))
band = target_ds.GetRasterBand(1)
band.SetNoDataValue(NoData_value)

# Rasterize
gdal.RasterizeLayer(output_raster, [1], source_layer, burn_values=[0])


