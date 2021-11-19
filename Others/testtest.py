import fiona
import shapely
import os
import csv
from shapely.geometry import Point, mapping, shape
from fiona import collection
from fiona.crs import from_epsg
import pandas as pnd

path = '/home/ensmingerlabgpu/Documents/PythonScripts/EarthDataUtils/Data/Lansat8/Vector-Data/'

filename1 = 'ShapeFile1.shp'
filename2 = 'ShapeFile2.shp'
outfile = 'mergedfile.shp'

fullfilename1 = os.path.join(path,filename1)
fullfilename2 = os.path.join(path,filename2)
fulloutfile = os.path.join(path,outfile)

# Open and read shape file

# shpfiledata = fiona.open(fullfilename1)
# print(shpfiledata)
                 # or
# read shp files
# with fiona.open(fullfilename1) as inputfile:
#     for rows in inputfile:
#         print(rows)


# write shp files:
# schema =  {'geometry': 'Point',
#                'properties': {'dx': 'float:13.3',
#                 'dy': 'float:13.3',
#                 'dline': 'str',
#                 'dtrace': 'int',
#                 'ddepth': 'float:9.4',
#                 'dtrash': 'float:9.4'}}

# with fiona.open(fulloutfile, 'w', crs=from_epsg(4326), driver='ESRI Shapefile', schema=schema) as output:
#     exceldata = pnd.read_excel('/home/ensmingerlabgpu/Documents/PythonScripts/EarthDataUtils/Data/Lansat8/Vector-Data/tempxls.xlsx'
#     print(exceldata)
#     for rows in exceldata.iterrow():
#         print(rows)
#         point = Point(float(rows[0]), float(rows[1])
#         prop = {'dx': float(rows[2]),
#                 'dy': float(23),
#                 'dline': str(2),
#                 'dtrace': float(2),                    
#                 'ddepth': float(2),                    
#                 'dtrash': float(2)}
#         output.write({'geometry': mapping(point), 'properties':prop})

# merge files
# shpfile_name_list = [fullfilename1, fullfilename2]
# def MergeShpFiles(shpfile_name_list,merged_out_file):
#     # merge files
#     ref_file = shpfile_name_list[0]
#     meta = fiona.open(ref_file).meta
#     with fiona.open(merged_out_file, 'w', **meta) as output:
#         for shpfile_path in shpfile_name_list:
#             for features in fiona.open(shpfile_path):
#                 output.write(features)

# MergeShpFiles(shpfile_name_list,fulloutfile)

# Buffer
pointshpfilenamee = '/home/ensmingerlabgpu/Documents/PythonScripts/EarthDataUtils/Data/Lansat8/Vector-Data/out.shp'
def performbuffer(path,shpfile_name):
    with collection(shpfile_name, "r") as input:
        # schema = input.schema.copy()
        schema = { 'geometry': 'Polygon', 'properties': { 'id': 'str'} }
        with collection(
            os.path.join(path,"point_buffer1.shp"), "w", "ESRI Shapefile", schema) as output:
            for point in input:
                output.write({
                    'properties': {
                        'id': point['properties']['id']
                    },
                    'geometry': mapping(shape(point['geometry']).buffer(1.0))
                })

performbuffer(path, pointshpfilenamee)