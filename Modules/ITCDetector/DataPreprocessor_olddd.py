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

    def ProcessData(self):
        
        if(self.rs_data_type.lower() == 'mulispectral'):
            out_base_folder = self.out_folder_multi
        else:
            out_base_folder = self.out_folder_hyper

        out_ortho_file_path = os.path.join(out_base_folder, self.image_folder, gc.ORTHOPHOTO_FOLDER)
        OtherUtils.TouchPath(out_ortho_file_path)

        # generate nDSM
        # getnDSM.GenerateNDSM(os.path.join(self.base_path, self.image_folder))

        # Stack Selected Orthophoto Bands (stacking of nDSM not required)
        in_ortho_file = os.path.join(self.base_path, self.image_folder, self.ortho_photo)
        crop_ShpFile = self.study_area_shp_file

        out_ortho_file_path = os.path.join(out_base_folder, self.image_folder, gc.ORTHOPHOTO_FOLDER)
        OtherUtils.TouchPath(out_ortho_file_path)
        out_ortho_file = os.path.join(out_ortho_file_path, self.image_folder + '_Ortho_Photo.tif')
        print('Reading: ' + in_ortho_file)

        self.StackReprojCropPhoto(in_ortho_file, out_ortho_file,self.DataType,crop_ShpFile)

        exit(0)


        self.StackOrthoPhoto(in_ortho_file, out_ortho_file)
        # Reproject Orthophoto

        self.ReprojectOrthoPhoto(out_ortho_file, out_ortho_file,65535)
        # Crop Orthophoto        

        self.CropOrthoPhoto(out_ortho_file, crop_ShpFile, out_ortho_file,65535)
        
        RasterOperators.CropImage_direct(out_ortho_file, crop_ShpFile, out_ortho_file,65535)
        # exit(0)

        # Reproject nDSM
        in_ndsm_file = os.path.join(self.base_path, self.image_folder, self.nDSM) 
        out_ndsm_folder = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.ALIGNED_OUT_FOLDER_NDSM)
        OtherUtils.TouchPath(out_ndsm_folder)
        out_ndsm_file = os.path.join(out_ndsm_folder, self.image_folder +'_nDSM_Image.tif')
        self.ReprojectnDSM(in_ndsm_file, out_ndsm_file)

        # Reproject nDSM original resolution (alternate to making a copy)
        out_ndsm_org_res_path = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM)
        OtherUtils.TouchPath(out_ndsm_org_res_path)
        out_ndsm_org_res_file = os.path.join(out_ndsm_org_res_path, self.image_folder +'_nDSM_Image.tif')
        self.ReprojectnDSM(in_ndsm_file, out_ndsm_org_res_file)
        
        # Align Orthophoto and nDSM
        self.GenerateAlignedRaster(out_base_folder)

        # Tile Data
        self.TileData()

    def GenerateAlignedRaster(self,out_base_folder):
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
        RasterOperators.AlignRaster(inputfile, referencefile, outputfile, out_ndsm_org_res_file, outputfileOrtho)

        print('Aligning nDSM and ref-nDSM...')
        inputfile_ndsm = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM, self.image_folder +'_nDSM_Image.tif')
        referencefile =  self.RefnDSMImage #os.path.join(out_base_folder, self.ref_date , self.coregister_folder, gc.COREGISTER_OUT_FOLDER_NDSM , self.ref_date + '_ndsm.tif')
        outputfile = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM, self.image_folder +'_nDSM_Image.tif')       
        RasterOperators.AlignRasterNDSM(inputfile_ndsm, referencefile, outputfile)

        print('Smoothening nDSM image...')
        InFileName = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM, self.image_folder +'_nDSM_Image.tif')
        OutFileName = os.path.join(out_base_folder, self.image_folder, gc.NDSM_FOLDER, gc.COREGISTER_OUT_FOLDER_NDSM, self.image_folder +'_nDSM_Image.tif')
        RasterOperators.CopySmoothenImage(InFileName,OutFileName, 1) ###############################

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

    def TileData(self):
        if(self.rs_data_type.lower() == 'mulispectral'):
            out_base_folder = self.out_folder_multi
        else:
            out_base_folder = self.out_folder_hyper
        # Tile Orthophoto and nDSM
        self.TileOrthoPhoto(out_base_folder)
        self.TilenDSM(out_base_folder)

    def StackReprojCropPhoto(self, in_image_path, out_image_path, data_type, AreaShpFile):
        # stack selected bands
        print('Stacking Selected Bands From Orthophoto...')
        RasterOperators.StackReprojCropPhoto(self.selected_band_list, 
                                                in_image_path, 
                                                out_image_path, 
                                                self.rs_data_type,
                                                data_type,
                                                AreaShpFile)
        # print('Done Stacking Orthophoto!')


    def StackOrthoPhoto(self, in_image_path, out_image_path):
        # stack selected bands
        print('Stacking Selected Bands From Orthophoto...')
        RasterOperators.StackSelectedImageBands(self.selected_band_list, 
                                                in_image_path, 
                                                out_image_path, 
                                                self.rs_data_type)
        # print('Done Stacking Orthophoto!')

    def ReprojectOrthoPhoto(self, in_file_path, out_filepath,NDV):
        # reproject ortho image
        print('Reprojecting Orthophoto...')
        RasterOperators.ReprojectImage(in_file_path, 
                                        out_filepath, 
                                        gc.PROJECTION_ID,NDV)
        # print('Done Reprojecting Orthophoto!')

    def CropOrthoPhoto(self, in_file, crop_ShpFile,out_file,NDV=65535):
        # reproject ortho image
        print('Reprojecting Orthophoto...')
        RasterOperators.CropImage_direct(in_file, 
                                        crop_ShpFile, 
                                        out_file,NDV)
        # print('Done Reprojecting Orthophoto!')

    def ReprojectnDSM(self, in_ndsm_file, out_ndsm_file):
        # reproject dsm
        print('Reprojecting nDSM...')
        RasterOperators.ReprojectImage(in_ndsm_file, 
                                        out_ndsm_file, 
                                        gc.PROJECTION_ID)
        print('Done Reprojecting nDSM!')

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
    
    