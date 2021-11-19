from arosics import COREG
from geoarray import GeoArray

im_reference = '/home/ensmingerlabgpu/Desktop/AgisoftProjects/20171011/nDSM.tif'  
im_target    = '/home/ensmingerlabgpu/Desktop/AgisoftProjects/20170809/nDSM.tif' 
im_target1    = '/home/ensmingerlabgpu/Desktop/AgisoftProjects/20170809/nDSM_CLcorrected.tif' 

CR = COREG(im_reference, im_target, wp=(262102.51, 5176533.91),path_out=im_target1)
CR.calculate_spatial_shifts()

geoArr  = GeoArray(im_reference)

ref_ndarray = geoArr[:]            # numpy.ndarray with shape (10980, 10980)
ref_gt      = geoArr.geotransform  # GDAL geotransform: (300000.0, 10.0, 0.0, 5900040.0, 0.0, -10.0)
ref_prj     = geoArr.projection    # projection as WKT string ('PROJCS["WGS 84 / UTM zone 33N....')
# get a sample numpy array with corresponding geoinformation as target image

geoArr  = GeoArray(im_target)
tgt_ndarray = geoArr[:]            # numpy.ndarray with shape (10980, 10980)
tgt_gt      = geoArr.geotransform  # GDAL geotransform: (300000.0, 10.0, 0.0, 5900040.0, 0.0, -10.0)
tgt_prj     = geoArr.projection    # projection as WKT string ('PROJCS["WGS 84 / UTM zone 33N....')
# create in-memory instances of GeoArray from the numpy array data, the GDAL geotransform tuple and the WKT
# projection string

geoArr_reference = GeoArray(ref_ndarray, ref_gt, ref_prj)
geoArr_target    = GeoArray(tgt_ndarray, tgt_gt, tgt_prj)

CR.calculate_spatial_shifts()
CR.correct_shifts()