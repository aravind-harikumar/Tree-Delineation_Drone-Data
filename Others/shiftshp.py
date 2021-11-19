import os
import fiona
import numpy as np
from ImageProcessor import OtherUtils
import geopandas as gp
from shapely.geometry import Point, LineString, Polygon, mapping

base_path = "/home/ensmingerlabgpu/Desktop/shps/Sébastien/"
full_file_name = os.path.join(base_path,'ref1.shp')
out_file_name = os.path.join(base_path,'ref1_new.shp')

# read file
counties = gp.read_file(full_file_name)
# counties.geometry = Point(counties.geometry.x counties.geometry.y)

for i, row in counties.iterrows():
    counties.at[i,'geometry'] = Point(row['geometry'].x-1.032,row['geometry'].y+2.857)
    # print(counties['geometry'][i])

# print(counties.geometry)

# # select columns
# counties_row_col_sel = counties_row_sel.loc[:, ['arb', 'Arbre_X', 'Arbre_Y', 'clas']]

# # write to file
counties.to_file(out_file_name)