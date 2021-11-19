import os
import fiona
import numpy as np
from ImageProcessor import OtherUtils
from ProjectConstants import GlobalConstants as gc

# base_path = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/ImageSlices/20180514/'
base_path = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/'
date = '20180514'
base_path_out = os.path.join(base_path, date, gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, gc.CROWN_SHP_BUF_OUT_FOLDER)


# loop through individual tile folders to detect TreeBufferAll.shp files
shpfile_name_list = []
for root, folders, files in os.walk(base_path_out):
    for file_name in files:
        if os.path.splitext(file_name)[1] in [".shp"]:
            shpfile_name_list.append(os.path.join(root,file_name))

# Merge shape files
if(np.shape(shpfile_name_list)[0] >0):                        
    ref_file = shpfile_name_list[0]

    # OtherUtils.TouchPath(base_path_out)
    merged_file = os.path.join(base_path_out,'0_itc_poly_merged.shp')
    # merge files
    meta = fiona.open(ref_file).meta
    with fiona.open(merged_file, 'w', **meta) as output:
        for shpfile_path in shpfile_name_list:
            for features in fiona.open(shpfile_path):
                output.write(features)
else:
    print('No shape files to merge')