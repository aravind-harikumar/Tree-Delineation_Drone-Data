import os
import numpy as np
from ImageProcessor import RasterOperators,VectorOperators, OtherUtils
from ImageProcessor.Algorithms import LocalMaximaExtractor
from ITCDetector import TreeDetection, MaskTreeCrown

class ITCUtils:

    def __init__(self, FileDataInfo):
        # assert m > 1
        # self.u, self.centers = None, None
        self.base_path = FileDataInfo['BaseFolder']
        self.image_date = FileDataInfo['ImageDate']
        self.itc_buffer_size = FileDataInfo['ITCBufferSize']
        self.tree_top_seperation = FileDataInfo['TreeTopInclusionBuffer']
        self.inter_tree_seperation = FileDataInfo['InterTreeSepeartion']
        self.min_tree_height = FileDataInfo['MinTreeHeight']
        self.filter_variance = FileDataInfo['FilterVariance']
        self.clipShpFile = FileDataInfo['clipShpFile']

    def TouchIOPath(self, slice_folder):
        ''' check validity of input and output paths  '''
        dsm_slice_Folder = os.path.join(self.base_path, self.image_date, 'nDSM-Tiles')  

        orthoimage_slice_folder = os.path.join(self.base_path, self.image_date, 'OrthoPhoto-Tiles')
        
        ITCDataFolder = os.path.join(self.base_path, self.image_date, 'ITC-Data')

        ShpFileFolder = os.path.join(self.base_path, self.image_date, 'ITC-Data', slice_folder, 'ITC-Shape')
        OtherUtils.TouchPath(ShpFileFolder)

        ITCImagesFolder = os.path.join(self.base_path, self.image_date, 'ITC-Data', slice_folder, 'ITC-Clipped')
        OtherUtils.TouchPath(ITCImagesFolder)

        return {
                'OrthoImagesSliceFolder':orthoimage_slice_folder,
                'DSMSliceFolder':dsm_slice_Folder, 
                'ShpFileFolder':ShpFileFolder,
                'ITCImagesFolder':ITCImagesFolder,
                'ITCDataFolder':ITCDataFolder
                }

    def DetectIndividaulTrees(self):
        print('###################Detecting Individual Trees!############################')
        # loop sliced data folder (can be aany folder)
        data_slice_path = os.path.join(self.base_path, self.image_date,'OrthoPhoto-Tiles')
        print('Looping: ' + data_slice_path)

        for root, folders, files in os.walk(data_slice_path):
            for file in files:
                # print(file)
                filename_split_list = file.rsplit("_")
            
                # if (filename_split_list[0] == '20181015') and (filename_split_list[1] == '261820') and (filename_split_list[2].rsplit(".")[0] == '5176477'):

                # slice_folder
                slice_folder_name = filename_split_list[0] + '_' \
                                    + filename_split_list[1] + '_'  \
                                    + filename_split_list[2].rsplit(".")[0]

                # check existance of sub folders in slice_folder
                # print(slice_folder_name)

                in_out_folders = self.TouchIOPath(slice_folder_name)

                if(not(os.path.exists(os.path.join(in_out_folders['DSMSliceFolder'], slice_folder_name+'.tif')))):
                    print('Skipping folder')
                    print(os.path.join(in_out_folders['DSMSliceFolder'], slice_folder_name+'.tif'))
                    # exit(0)
                    continue

                # Detect tree tops
                print('Detecting tree tops')
                DetectedTreeTops = TreeDetection.DetectTreeTop(
                                    os.path.join(in_out_folders['DSMSliceFolder'], slice_folder_name+'.tif'),
                                    self.tree_top_seperation,
                                    self.inter_tree_seperation,
                                    self.min_tree_height,
                                    self.filter_variance
                                    )
                # print(DetectedTreeTops)

                # Save tree tops and create crown buffer shp files
                print("Clipping TreeTop Shape File")
                MaskTreeCrown.SaveTreeTop(
                            DetectedTreeTops, 
                            self.itc_buffer_size,
                            in_out_folders["ShpFileFolder"],
                            self.clipShpFile
                            )
                

        # Merge all ITC shp files in individual orthophoto tile folders
        merge_out_path = os.path.join(in_out_folders["ITCDataFolder"],'All-ITC')
        MaskTreeCrown.MergeShpFiles(in_out_folders["ITCDataFolder"], merge_out_path)
        VectorOperators.ClipShpFile(os.path.join(merge_out_path,'shapefile_merged.shp'), self.clipShpFile, os.path.join(merge_out_path,'shapefile_merged.shp')) 

    # MergeShpFiles(ITCDataFolder, merge_out_path)
                # # co-register images

                # # # Crop tree crowns using crown buffers
                # MaskTreeCrown.CropITCFromOrthoImage(
                #     os.path.join(in_out_folders["OrthoImagesSliceFolder"], slice_folder_name+'.tif'), 
                #     in_out_folders["ShpFileFolder"], in_out_folders["ITCImagesFolder"])

