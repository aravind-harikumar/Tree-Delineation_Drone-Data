import fiona
import geopandas

inshp = geopandas.read_file('/home/ensmingerlabgpu/Desktop/2018/ProcessedMSData/20170626/ITC-Data/All-ITC/shapefile_merged.shp')
polygon = geopandas.read_file('/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Site_info/ArcGIS/StCasimir_SpruceUp_temp1.shp')
clipped = geopandas.clip(inshp, polygon)
clipped.to_file('/home/ensmingerlabgpu/Desktop/2018/ProcessedMSData/20170626/ITC-Data/All-ITC/shapefile_merged_clip.shp')

# def ClipShpFile(PolygonObj, shpFileName, geomType, clipFile):
#         # Define a polygon feature geometry with one attribute
#         schema = {
#             'geometry': geomType,
#             'properties': {'id': 'int'},
#         }
#         # Write a new Shapefile
#         with fiona.open(shpFileName, 'w', crs=from_epsg(32619), driver='ESRI Shapefile', schema=schema) as c:
#         ## If there are multiple geometries, put the "for" loop here
#             c.write({
#                 'geometry': mapping(PolygonObj),
#                 'properties': {'id': 123},
#             })