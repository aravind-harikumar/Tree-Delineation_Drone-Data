"""
..   module:: Module to perform drone-optical data preprocessing function
    :platform: Unix, Windows
    :synopsis: A module for preprocessing drone-optical data using agisoft-api.
    :requires: AgiSoft Software with a valid license
..  :author:: Aravind Harikumar <aravind.harikumar@utoronto.ca>
"""

from math import fabs
import os, sys, random
import numpy as np
import rasterio
import gdal, ogr, osr
import fiona
import rasterio.mask
from skimage import exposure
import geopandas as gpd
from ImageProcessor import RasterOperators, VectorOperators, OtherUtils, getnDSM
from ImageProcessor.Algorithms import LocalMaximaExtractor
from matplotlib import pyplot
from ProjectConstants import GlobalConstants as gc

class Preprocessor:
    def __init__(self, FileDataInfo):
        # assert m > 1
        # self.u, self.centers = None, None
        self.base_path = FileDataInfo['BaseFolder']
        self.ortho_photo = FileDataInfo['OrthoPhoto']
        self.rs_data_type = FileDataInfo['RSDataType']
        self.ref_date  = FileDataInfo['RefDateFolder']
        self.out_folder_hyper = FileDataInfo['OutFolderHyper']
        self.out_folder_multi = FileDataInfo['OutFolderMulti']
        self.image_folder = FileDataInfo['ImageFolder']
        self.selected_band_list = FileDataInfo['SelectedBands']
        self.skipCorStep = FileDataInfo['SkipCorStep']
        self.nDSM = FileDataInfo['nDSM']
        self.DataType = FileDataInfo['DataType']
        self.dsmresolution = FileDataInfo['dsmresolution']
        self.span_image = FileDataInfo['RefSpanImage']
        self.study_area_shp_file = FileDataInfo['StudyAreaShp']
        self.RefnDSMImage  = FileDataInfo['RefnDSMImage']
        if(self.skipCorStep):
            self.coregister_folder = gc.NON_COR_ORTHOPHOTO_FOLDER
        else:
            self.coregister_folder = gc.COREGISTER_OUT_FOLDER

    def PreProcessData(self):
        if(self.rs_data_type.lower() == 'mulispectral'):
            out_base_folder = self.out_folder_multi
        else:
            out_base_folder = self.out_folder_hyper

        out_ortho_file_path = os.path.join(out_base_folder, self.image_folder, gc.ORTHOPHOTO_FOLDER)
        OtherUtils.TouchPath(out_ortho_file_path)

        # Get destiation file datatype
        ds_DataTypeMax = self.MinMaxofDatatype(self.DataType)[1]

        # generate nDSM (if required)
        # getnDSM.GenerateNDSM(os.path.join(self.base_path, self.image_folder))

        # Stack Selected Orthophoto Bands (stacking of nDSM not required)
        in_ortho_file = os.path.join(self.base_path, self.image_folder, self.ortho_photo)
        crop_ShpFile = self.study_area_shp_file

        out_ortho_file_path = os.path.join(out_base_folder, self.image_folder, gc.ORTHOPHOTO_FOLDER)
        OtherUtils.TouchPath(out_ortho_file_path)
        out_ortho_file = os.path.join(out_ortho_file_path, self.image_folder + '_Ortho_Photo.tif')
        print('Reading: ' + in_ortho_file)

        # ################# Orthophoto Preprocessing #################
        # Stack Orthophoto and save in local folder
        self.StackSelectedImageBands(in_ortho_file, out_ortho_file, self.DataType, ds_DataTypeMax)
  
        # Crop Orthophoto and save in local folder
        self.CropOrthoPhoto(out_ortho_file, crop_ShpFile, out_ortho_file, ds_DataTypeMax)
        
        # Reproject Orthophoto and save in local folder
        self.ReprojectOrthoPhoto(out_ortho_file, out_ortho_file, ds_DataTypeMax)
        
        ################# nDSM Preprocessing #################
        # import nDSM local folder and reproject
        in_ndsm_file = os.path.join(self.base_path, self.image_folder, self.nDSM) 
        self.ReprojectnDSMs(in_ndsm_file,out_base_folder,ds_DataTypeMax)

        ################# Resample NDSM and Orthophoto #################
        # Align Orthophoto and nDSM
        self.GenerateAlignedRaster(out_base_folder,ds_DataTypeMax)

        # Tile Data
        self.TileData()

    def StackSelectedImageBands(self, in_image_path, out_image_path, data_type, NoDataVal=0):
        # stack selected bands
        print('Stacking Selected Bands From Orthophoto...')
        RasterOperators.StackSelectedImageBands(self.selected_band_list,
                                                in_image_path,
                                                out_image_path,
                                                self.rs_data_type,
                                                data_type,
                                                NoDataVal)
        print('Done Stacking!')

    def ReprojectOrthoPhoto(self, in_file_path, out_filepath, NoDataVal=0):
        # reproject ortho image
        print('Reprojecting Orthophoto...')
        RasterOperators.ReprojectImage(in_file_path, 
                                        out_filepath, 
                                        False,
                                        gc.PROJECTION_ID,
                                        NoDataVal)
        print('Done Reprojecting Orthophoto!')

    def CropOrthoPhoto(self, in_file, crop_ShpFile, out_file, NoDataVal=0):
        # reproject ortho image
        print('Cropping Orthophoto...')
        RasterOperators.CropImage_direct(in_file,
                                        crop_ShpFile,
                                        out_file,NoDataVal)
        print('Done Cropping Orthophoto!')


    def CopyNDSM(self, in_ndsm_file, out_ndsm_file):
        print("Copiying NDSM...")
        RasterOperators.CopyImage(in_ndsm_file,out_ndsm_file)


    def ReprojectnDSMs(self,in_ndsm_file,out_base_folder,NoDataVal):
        # Reproject nDSM
        out_ndsm_folder = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.ALIGNED_OUT_FOLDER_NDSM)
        OtherUtils.TouchPath(out_ndsm_folder)
        out_ndsm_file = os.path.join(out_ndsm_folder, self.image_folder +'_nDSM_Image.tif')
        self.ReprojectnDSM(in_ndsm_file, out_ndsm_file, True, NoDataVal)

        # Reproject nDSM original resolution (alternate to making a copy)
        out_ndsm_org_res_path = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM)
        OtherUtils.TouchPath(out_ndsm_org_res_path)
        out_ndsm_org_res_file = os.path.join(out_ndsm_org_res_path, self.image_folder +'_nDSM_Image.tif')
        self.ReprojectnDSM(in_ndsm_file, out_ndsm_org_res_file, True, NoDataVal)
    

    def ReprojectnDSM(self, in_ndsm_file, out_ndsm_file,ForceReprojection,NoDataVal=0):
        ''' Reproject nDSM.

        @string in_ndsm_file     Input File Path
        @string out_ndsm_file:   Reprojected Output File Path
        @bool ForceReprojection  Force Reprojection True or False
        @int NoDataVal: No data value
        @return:        NULL
    '''
        # reproject dsm
        print('Reprojecting nDSM...')
        RasterOperators.ReprojectImage(in_ndsm_file, 
                                        out_ndsm_file,
                                        ForceReprojection,
                                        gc.PROJECTION_ID,
                                        NoDataVal)
        print('Done Reprojecting nDSM!')

    def TileData(self):
        if(self.rs_data_type.lower() == 'mulispectral'):
            out_base_folder = self.out_folder_multi
        else:
            out_base_folder = self.out_folder_hyper
        # Tile Orthophoto and nDSM
        self.TileOrthoPhoto(out_base_folder)
        self.TilenDSM(out_base_folder)    

    def TileOrthoPhoto(self, out_base_folder):
        print('Starting Data Tiling Orthophto')
        # tile ortho image
        sliced_image_path = os.path.join(out_base_folder, self.image_folder, gc.ORTHOPHOTO_TILE_FOLDER)
        OtherUtils.TouchPath(sliced_image_path)

        reproj_image_path = os.path.join(out_base_folder, self.image_folder, self.coregister_folder, self.image_folder + '.tif')
        print('Reading:' + reproj_image_path)
        print('Reading:' + self.coregister_folder)

        RasterOperators.TileImage(reproj_image_path, 
                                    sliced_image_path, 
                                    self.image_folder, 
                                    self.span_image,
                                    'orthoimagetype',
                                    self.dsmresolution,
                                    self.study_area_shp_file)
        print('Done Tiling Orthophoto!')

    def TilenDSM(self, out_base_folder):
        print('Starting Data Tiling nDSM')
        # check existance of dsm tile output folder
        DSM_out_folder = os.path.join(out_base_folder, self.image_folder, self.coregister_folder)
        
        DSM_out_tile_path = os.path.join(out_base_folder, self.image_folder,gc.NDSM_TILE_FOLDER)
        OtherUtils.TouchPath(DSM_out_tile_path)

        # generate DSM_Slice
        out_dsm_path = os.path.join(DSM_out_folder, gc.COREGISTER_OUT_FOLDER_NDSM, self.image_folder + '_ndsm.tif')
        RasterOperators.TileImage(out_dsm_path,
                                    DSM_out_tile_path, 
                                    self.image_folder, 
                                    self.span_image, 
                                    'dsmimagetype',
                                    self.dsmresolution,
                                    self.study_area_shp_file)
        print('Done Tiling nDSM!')
    

    def GenerateAlignedRaster(self,out_base_folder,ds_DataTypeMax):
        print('Aligning Orthophoto and nDSM...')
        inputfile = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.ALIGNED_OUT_FOLDER_NDSM, self.image_folder +'_nDSM_Image.tif')
        referencefile = os.path.join(out_base_folder, self.image_folder, gc.ORTHOPHOTO_FOLDER, self.image_folder + '_Ortho_Photo.tif')
        
        outputfile =  inputfile # os.path.join(out_base_folder, self.image_folder, 'nDSM', self.image_folder +'_nDSM_reproj.tif')
        outputfileOrtho = referencefile # os.path.join(out_base_folder, self.image_folder, 'OrthoPhoto', self.image_folder +'_Ortho_reproj.tif')

        out_ndsm_org_res_path = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM)
        OtherUtils.TouchPath(out_ndsm_org_res_path)
        out_ndsm_org_res_file = os.path.join(out_ndsm_org_res_path, self.image_folder +'_nDSM_Image.tif')
        # outputfile_orig_res = os.path.join(out_base_folder, self.image_folder, 'nDSM/nDSM-Original', self.image_folder +'_nDSM_Image.tif')

        # align rasters
        RasterOperators.AlignRaster(inputfile, referencefile, outputfile, out_ndsm_org_res_file, outputfileOrtho,ds_DataTypeMax)

        print('Aligning nDSM and ref-nDSM...')
        inputfile_ndsm = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM, self.image_folder +'_nDSM_Image.tif')
        referencefile =  self.RefnDSMImage #os.path.join(out_base_folder, self.ref_date , self.coregister_folder, gc.COREGISTER_OUT_FOLDER_NDSM , self.ref_date + '_ndsm.tif')
        outputfile = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM, self.image_folder +'_nDSM_Image.tif')       
        RasterOperators.AlignRasterNDSM(inputfile_ndsm, referencefile, outputfile)

        print('Smoothening nDSM image...')
        InFileName = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM, self.image_folder +'_nDSM_Image.tif')
        OutFileName = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM, self.image_folder +'_nDSM_Image.tif')
        RasterOperators.CopySmoothenImage(InFileName,OutFileName, 0.1) ###############################

        print('Copying non coregistered images to non coregistered folder...')
        # copy image to op_new (i.e., folder without coregistration)
        InFileName_ndsm_org = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM, self.image_folder +'_nDSM_Image.tif')
        InFileName_ortho = os.path.join(out_base_folder, self.image_folder, gc.ORTHOPHOTO_FOLDER, self.image_folder + '_Ortho_Photo.tif')
        InFileName_ndsm_realigned = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.ALIGNED_OUT_FOLDER_NDSM, self.image_folder +'_nDSM_Image.tif')

        OutFileName_ndsm_org = os.path.join(out_base_folder, self.image_folder, self.coregister_folder, gc.COREGISTER_OUT_FOLDER_NDSM, self.image_folder +'_ndsm.tif')
        OutFileName_ortho = os.path.join(out_base_folder, self.image_folder, self.coregister_folder, self.image_folder + '.tif')
        OutFileName_ndsm_realigned = os.path.join(out_base_folder, self.image_folder, self.coregister_folder , self.image_folder + '_ndsm.tif')
        OtherUtils.TouchPath(os.path.join(out_base_folder, self.image_folder, self.coregister_folder, gc.COREGISTER_OUT_FOLDER_NDSM))

        RasterOperators.CopyImage(InFileName_ndsm_org, OutFileName_ndsm_org)
        RasterOperators.CopyImage(InFileName_ortho, OutFileName_ortho)
        RasterOperators.CopyImage(InFileName_ndsm_realigned, OutFileName_ndsm_realigned)

    def MinMaxofDatatype(self,datatype):
        if(datatype == "uint16"):
            return [np.iinfo(np.uint16).min, np.iinfo(np.uint16).max]
        elif(datatype == "uint8"):
            return [np.iinfo(np.uint8).min, np.iinfo(np.uint8).max]
        elif(datatype == "float32"):
            return [np.iinfo(np.uint16).min, np.iinfo(np.uint16).max]
        elif(datatype == "float64"):
            return [np.iinfo(np.uint16).min, np.iinfo(np.uint16).max]
    
    