import fiona
from fiona.crs import from_epsg
from shapely.geometry import Point, LineString, Polygon, mapping
import geopandas as gpd

def SaveAsShpFile(PolygonObj, shpFileName):
        # Define a polygon feature geometry with one attribute
        schema = {
            'geometry': 'Polygon',
            'properties': {'id': 'int'},
        }
        # Write a new Shapefile
        with fiona.open(shpFileName, 'w', crs=from_epsg(32619), driver='ESRI Shapefile', schema=schema) as c:
        ## If there are multiple geometries, put the "for" loop here
            c.write({
                'geometry': mapping(PolygonObj),
                'properties': {'id': 123},
            })


def ClipShpFile(inShape, clipFile, outShape):
    inshp = gpd.read_file(inShape)
    polygon = gpd.read_file(clipFile)
    clipped = gpd.clip(inshp, polygon)
    clipped.to_file(outShape)


def SaveAsShpFileByType(PolygonObj, shpFileName, geomType):
        # Define a polygon feature geometry with one attribute
        schema = {
            'geometry': geomType,
            'properties': {'id': 'int'},
        }
        # Write a new Shapefile
        with fiona.open(shpFileName, 'w', crs=from_epsg(32619), driver='ESRI Shapefile', schema=schema) as c:
        ## If there are multiple geometries, put the "for" loop here
            c.write({
                'geometry': mapping(PolygonObj),
                'properties': {'id': 123},
            })

def ReadShpFile(shpFileName):
        # Define a polygon feature geometry with one attribute
        shape = fiona.open(shpFileName)
        return shape

def MergeShpFiles(shpfile_name_list,merged_out_file):
    # merge files
    ref_file = shpfile_name_list[0]
    
    meta = fiona.open(ref_file).meta
    with fiona.open(merged_out_file, 'w', **meta) as output:
        for shpfile_path in shpfile_name_list:
            for features in fiona.open(shpfile_path):
                output.write(features)



