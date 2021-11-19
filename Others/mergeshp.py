import os
import fiona
import numpy as np
from ImageProcessor import OtherUtils


# base_path = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/ImageSlices/20180514/'
# base_path = '/home/ensmingerlabgpu/Desktop/2018/Nano-Hyperspec/ProcessedMSData/20180514/ITC-Data/'
base_path = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20181015/op_new/out/Plots_out_files/Snake_bounday/'
# loop through individual tile folders to detect TreeBufferAll.shp files
shpfile_name_list = []
for root, folders, files in os.walk(base_path):
    for file_name in files:
        print(file_name.rsplit(".")[1])
        # if file_name.rsplit(".")[0] in ["TreeBufferAll"] and file_name.rsplit(".")[1] in ["shp"]:
        if file_name.rsplit(".")[3] in ["shp"]:
            # print(file_name)
            shpfile_name_list.append(os.path.join(root,file_name))

# Merge shape files
if(np.shape(shpfile_name_list)[0] >0):                        
    ref_file = shpfile_name_list[0]

    # create output folder
    OtherUtils.TouchPath(os.path.join(base_path,'All-ITC'))
    # merged_file = os.path.join(base_path,'All-ITC/shapefile_merged.shp')
    merged_file = os.path.join(base_path,'shapefile_merged.shp')

    # merge files
    meta = fiona.open(ref_file).meta
    with fiona.open(merged_file, 'w', **meta) as output:
        for shpfile_path in shpfile_name_list:
            for features in fiona.open(shpfile_path):
                output.write(features)
else:
    print('No shape files to merge')