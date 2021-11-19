import io,sys,os
import shapely as shp
import fiona
import pandas as pd
import geopandas as gpd
from fiona import collection
from fiona.crs import from_epsg
from shapely.geometry import Polygon, Point, mapping
import csv
import numpy
from pyproj import Proj, transform
import random 

data = gpd.read_file('/mnt/4TBHDD/HS_DATA/20180516/0_Ref_data_shp/treeslonglat_V2.shp')
print(data.head())

schema = {'geometry':'Point', 
          'properties':{'arb':'str','Arbre_X':'int','Arbre_Y':'int','clas':'str'}}

# Define shp file to write to
shpOut = '/mnt/4TBHDD/HS_DATA/20180516/0_Ref_data_shp/polygon_new.shp'

# Shape File CRS
crs_dat = from_epsg(32619) # Unique ID for UTM 32N from EPSG
# Create and write to output shp file
with collection(shpOut, "w", "ESRI Shapefile", schema, crs=crs_dat) as output:
    # # Loop through dataframe and populate shp file
    myProj = Proj("+proj=utm +zone=19 +datum=WGS84 +units=m +no_defs")   # see  https://epsg.io to get proj string (i.e., here for 32632)
    for index, row in data.iterrows():
        # Convert lat long to UTM Proj
        UTMx, UTMy = myProj(float(row["geometry"].x), float(row["geometry"].y))
        # Generate Polygon Object (e.g., circlular buffer, or any shape)
        PointObject = Point([float(UTMx-0.9), float(UTMy+2.4)]) # creating circular buffer object for input point
        # Write output to Shape file
        output.write({
            'properties': {'arb': row["arb"],'Arbre_X': row["Arbre_X"],'Arbre_Y': row["Arbre_Y"],'clas': row["clas"]}, 
            'geometry': mapping(PointObject)
        })


# import io,sys,os
# import shapely as shp
# import fiona
# import pandas as pd
# import geopandas as gpd
# from fiona import collection
# from fiona.crs import from_epsg
# from shapely.geometry import Polygon, Point, mapping
# import csv
# import numpy
# from pyproj import Proj, transform
# import random 

# # data =  pd.read_csv(".\\out\\test_shp_oper_data\\LatLongData\\LatLong.csv", delimiter=',')
# # print(data)
# # sdata = fiona.open('/mnt/4TBHDD/HS_DATA/20180516/0_Ref_data_shp/treeslonglat_V2.shp')
# # data = []
# # for f in sdata:
# #     g = f["geometry"]
# #     print(g["coordinates"])
# #     data.append(g["coordinates"])
# # # data = sdata
# # newarr = pd.DataFrame(data)
# # print(newarr.head())
# # exit(0)

# data = gpd.read_file('/mnt/4TBHDD/HS_DATA/20180516/0_Ref_data_shp/treeslonglat_V2.shp')
# print(data.head())

# schema = {'geometry':'Point', 
#           'properties':{'arb':'str','Arbre_X':'int','Arbre_Y':'int','clas':'str'}}
# # Define shp file to write to
# shpOut = '/mnt/4TBHDD/HS_DATA/20180516/0_Ref_data_shp/polygon.shp'
# # Shape File CRS
# crs_dat = from_epsg(32619) # Unique ID for UTM 32N from EPSG
# # Create and write to output shp file
# with collection(shpOut, "w", "ESRI Shapefile", schema, crs=crs_dat) as output:
#     # # Loop through dataframe and populate shp file
#     myProj = Proj("+proj=utm +zone=19 +datum=WGS84 +units=m +no_defs")   # see  https://epsg.io to get proj string (i.e., here for 32632)
#     for index, row in data.iterrows():
#         # Convert lat long to UTM Proj
#         UTMx, UTMy = myProj(float(row["geometry"].x), float(row["geometry"].y))
#         # Generate Polygon Object (e.g., circlular buffer, or any shape)
#         PointObject = Point([float(UTMx), float(UTMy)]) # creating circular buffer object for input point
#         # Write output to Shape file
#         output.write({
#             'properties': {'arb': row["arb"],'Arbre_X': row["Arbre_X"],'Arbre_Y': row["Arbre_Y"],'clas': row["clas"]}, 
#             'geometry': mapping(PointObject)
#         })


# import io,sys,os
# import shapely as shp
# import fiona
# import pandas as pd
# import geopandas as gpd
# from fiona import collection
# from fiona.crs import from_epsg
# from shapely.geometry import Polygon, Point, mapping
# import csv
# import numpy
# from pyproj import Proj, transform
# import random 

# data = gpd.read_file('/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/GPS/trees_&_targets/SCA 26-07-2017.shp')
# print(data.head())

# schema = {'geometry':'Point', 
#           'properties':{'OBJNAME':'str','Name':'str','POINT_X':'float','POINT_Y':'float','POINT_Z':'float','POINT_M':'float'}}

# # Define shp file to write to
# shpOut = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/GPS/trees_&_targets/SCA 26-07-2017_UTM19.shp'

# # Shape File CRS
# crs_dat = from_epsg(32619) # Unique ID for UTM 19N from EPSG WGS84
# # Create and write to output shp file
# with collection(shpOut, "w", "ESRI Shapefile", schema, crs=crs_dat) as output:
#     # # Loop through dataframe and populate shp file
#     myProj = Proj("+proj=utm +zone=19 +datum=WGS84 +units=m +no_defs")   # see  https://epsg.io to get proj string (i.e., here for 32632)
#     for index, row in data.iterrows():
#         # Convert lat long to UTM Proj
#         UTMx, UTMy = myProj(float(row["geometry"].x), float(row["geometry"].y))
#         # Generate Polygon Object (e.g., circlular buffer, or any shape)
#         PointObject = Point([float(UTMx), float(UTMy)]) # creating circular buffer object for input point
#         # Write output to Shape file
#         output.write({
#             'properties': {'OBJNAME': row["OBJNAME"],'Name': row["Name"],'POINT_X': row["POINT_X"],'POINT_Y': row["POINT_Y"],'POINT_Z': row["POINT_Z"],'POINT_M': row["POINT_M"]}, 
#             'geometry': mapping(PointObject)
#         })