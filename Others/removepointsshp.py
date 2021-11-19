import geopandas as gpd
import numpy as np  

# infile = gpd.open('')
treetopsshp = gpd.read_file('/mnt/4TBHDD/StCasimir-Multispectral-Analysis/0_SpruceUp-Raw-Data/Site_info/ReferenceData/SC_TREE_REFERENCE_DATA_1.shp')

row_to_remove_list = []
for index, row in treetopsshp.iterrows():
    if(row['geometry']== None):
        print(row['FID'])
        row_to_remove_list.append(row['FID'])
        # continue
print(row_to_remove_list)
# print('row_to_remove_list' + list(np.array(row_to_remove_list)))

selected_buildings = treetopsshp.loc[~treetopsshp['FID'].isin(row_to_remove_list)]
selected_buildings.to_file(driver = 'ESRI Shapefile', filename = '/mnt/4TBHDD/StCasimir-Multispectral-Analysis/0_SpruceUp-Raw-Data/Site_info/ReferenceData/SC_TREE_REFERENCE_DATA_2.shp')