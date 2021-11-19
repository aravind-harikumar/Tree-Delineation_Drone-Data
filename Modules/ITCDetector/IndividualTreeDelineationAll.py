import os
import numpy as np
from ImageProcessor import RasterOperators, OtherUtils
from ImageProcessor.Algorithms import LocalMaximaExtractor
from ITCDetector import TreeDetection, MaskTreeCrown
import rasterio
from shutil import copyfile
import Metashape
import cv2
from rasterio.warp import reproject
from rasterio.control import GroundControlPoint
from fiona.crs import from_epsg
import pandas as pnd
from rasterio.warp import calculate_default_transform, reproject, Resampling
import geopandas as gpd
import pandas as pd
from ProjectConstants import GlobalConstants as gc
import gdal
# from arosics import COREG
# from arosics import DESHIFTER
# from sentinelhub import pixel_to_utm

class ITCDelineationUtils:

    def __init__(self, FileDataInfo):
        # assert m > 1
        # self.u, self.centers = None, None
        self.base_path = FileDataInfo['CoBaseFolder']
        self.skipCorStep = FileDataInfo['SkipCorStep'],
        self.ref_date_folder = FileDataInfo['RefDateFolder']
        self.saveGCPasShp = FileDataInfo['SaveGCPFromAgisoft']
        self.save_agi_obj_file = FileDataInfo['SaveAgisoftFile']
        if(self.skipCorStep):
            self.coreg_out = gc.NON_COR_ORTHOPHOTO_FOLDER
        else:
            self.coreg_out = gc.COREGISTER_OUT_FOLDER

    def TouchIOPath(self, slice_folder):

        ITCImagesFolder = os.path.join(self.base_path, self.image_date, slice_folder, 'ITC_Clipped')
        if not os.path.exists(ITCImagesFolder):
            print("Output folder does not exists! creating folder!")
            os.makedirs(ITCImagesFolder)

        return {
                'ITCImagesFolder':ITCImagesFolder
                }


    def __GetImageListToCoregister(self,ref_folder, Sliced_Data_folder):

        list_immediate_subfolders = [f.path for f in os.scandir(self.base_path) if f.is_dir() and "AgiObj.files" not in f.name]

        ImageListToCoregister = {}
        for root, folders, files in os.walk(ref_folder):
            cnt = 0
            for file in files:
                
                if(file.endswith(".tif") or file.endswith(".tiff")):
                    print(file)
                    # print("File: " + file)
                    # get lat long values from file name
                    filename_split_list = file.rsplit("_")

                    ref_lat = filename_split_list[1]
                    ref_lon = filename_split_list[2]
                    print(filename_split_list[2])
                    # exit(0)
                    imges_to_be_coregistered_list = []
                    # loop through different date folders (may,  july , oct)
                    for date_foldr in list_immediate_subfolders:

                        date_image_path = os.path.join(date_foldr, Sliced_Data_folder)
                        # loop the date folder for lat _long in the name
                        for root, folders, files in os.walk(date_image_path):
                            for file0 in files:
                                filename_split_list = file0.rsplit("_")
                                if (filename_split_list[1] == ref_lat) and (filename_split_list[2] == ref_lon):
                                    imges_to_be_coregistered_list.append(os.path.join(root,file0))

                    ImageListToCoregister[filename_split_list[0]] = [imges_to_be_coregistered_list]
                    cnt = cnt+1

        return ImageListToCoregister


    def __getRefPhotoGCPs(self, photo_id_list, tiepointarray,files_to_be_coregd, saveGCPasShp):
        # get ref photo name
        ref_photo_id = ''
        for idd in photo_id_list:
            if(self.ref_date_folder in str(idd)):
                ref_photo_id = idd

        print('ref_photo_id : ' + ref_photo_id)

        # get ref photo path
        ref_photo_path = []
        for i in range(0,np.shape(files_to_be_coregd)[1]):
            vall = files_to_be_coregd[0][i]
            if(self.ref_date_folder in str(vall)):
                ref_photo_path = vall
                print(ref_photo_path)

        ref_df0 = pd.DataFrame()
        temp_df = tiepointarray[tiepointarray['photo_id'] == ref_photo_id]
        srcrst = gdal.Open(ref_photo_path) 
        val = np.asmatrix(
                        [ [ref_photo_id, 
                        rows[1][1], # point id
                        rows[1][2], # pixel row
                        rows[1][3], # pixel column
                        RasterOperators.pixel2coord(srcrst, round(rows[1][2]),round(rows[1][3]))[0], 
                        RasterOperators.pixel2coord(srcrst, round(rows[1][2]),round(rows[1][3]))[1] 
                        ] 
                        for rows in temp_df.iterrows() 
                        ])                                    
        tempdf0 = pd.DataFrame(val)
        ref_df0 = pd.concat([ref_df0, tempdf0])
        ref_df0.columns = ['photo_id','tie_point_id','xval','yval','lat','lon']

        TreeTopXY=[]
        for rows in ref_df0.iterrows():
            TreeTopXY.append([rows[1][4] ,rows[1][5]])
        TreeTopXY = np.asmatrix(TreeTopXY)
        # print(TreeTopXY)

        gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy(TreeTopXY[:,0],TreeTopXY[:,1]))
        gdf.crs = {'init' : gc.PROJECTION_ID}
        filename_split_lis = ref_photo_id.rsplit("_")
        filename_val = filename_split_lis[0]
        outpath = os.path.join(self.base_path, filename_val, self.coreg_out)
        if not os.path.exists(outpath):
            print("Output folder does not exists! creating folder!")
            os.makedirs(outpath)
        # save GCPs obtained from ref image
        if(saveGCPasShp):
            print('GCPs' + os.path.join(outpath,ref_photo_id+'.shp'))
            gdf.to_file(os.path.join(outpath,ref_photo_id+'.shp'),driver ='ESRI Shapefile')

        photo_id_list.remove(ref_photo_id)
        print(photo_id_list)
        return ref_df0, TreeTopXY, photo_id_list

    def checkfoldervalidity(self,files_to_be_coregd):
        flag = True
        i = 0
        sizeofList = np.shape(files_to_be_coregd)[1]

        while i < sizeofList:
            print(str(files_to_be_coregd[0][i]))

            if not os.path.exists(files_to_be_coregd[0][i]):                
                flag = False
                break

            if os.path.exists(files_to_be_coregd[0][i]):                
                op = RasterOperators.GetImageInfo(str(files_to_be_coregd[0][i]))
                # print(op.width)
                if(op.width<1000):
                    flag = False
                    break
                
            i += 1
        return flag

    def Coregister(self):
        print("Started Coregistation")

        # get list of orthophotos to to be coregistered, for each image-tile in ref folder
        ortho_data_folder = 'OrthoPhoto'
        ref1_folder = os.path.join(self.base_path, self.ref_date_folder, ortho_data_folder)
        ImageOrthoListToCoregister = self.__GetImageListToCoregister(ref1_folder, ortho_data_folder)
        print(ImageOrthoListToCoregister)
        
        print('Copying ref Orthophoto to Orthorectified Folder')
        self.copydataset(ImageOrthoListToCoregister)
        # exit(0)

        # exit(0)
        # get list of nDSMs to to be coregistered, for each image-tile in ref folder
        ndsm_data_folder = 'nDSM/nDSM_Aligned'
        ref_folder = os.path.join(self.base_path, self.ref_date_folder, ndsm_data_folder)
        ImageListToCoregister = self.__GetImageListToCoregister(ref_folder, ndsm_data_folder)
        # print(ImageListToCoregister)

        print('Copying ref nDSM to nDSM Folder')   
        self.copydatasetndsm(ImageListToCoregister)


        # exit(0)
        for item in ImageListToCoregister:
            print(item)
            # if("20180514" in item):
            #     print('skippn')
            #     continue

            files_to_be_coregd_ortho = ImageOrthoListToCoregister[item]

            files_to_be_coregd = ImageListToCoregister[item]

            # files_to_be_coregd_ortho = ImageOrthoListToCoregister[item]
            # create folder if not exist
            if not self.checkfoldervalidity(files_to_be_coregd):
                print("skipping the tile as it is not common to all dates")
                continue            

            # get tie points from AGISoft
            tiepointarray, success = self.AGISOftCoreg(files_to_be_coregd, self.save_agi_obj_file)

            # if tiepoints are detected
            if(success and (len(tiepointarray) >0)):

                tiepointarray = pnd.DataFrame(tiepointarray)
                tiepointarray.columns =['photo_id','tie_point_id','xval','yval']

                # get unique photo_ids
                photo_id_list = list(tiepointarray["photo_id"].unique())

                # get GCPs from reference image
                refdf0, TreeTopXY, remaining_photo_id_list = self.__getRefPhotoGCPs(
                                                            photo_id_list, 
                                                            tiepointarray, 
                                                            files_to_be_coregd, 
                                                            self.saveGCPasShp)

                # assign ref cooridnates from ref GCPs to corresponding tie points in the image
                for photo_id in remaining_photo_id_list:
                    print(photo_id)
                    self.__reproj_raster(photo_id, files_to_be_coregd, files_to_be_coregd_ortho, tiepointarray, refdf0)

            else:
                print("Agosoft Error / no tie points detected")    

    def __reproj_raster(self, photo_id, files_to_be_coregd, files_to_be_coregd_ortho, tiepointarray, refdf0):
        # create output path
        filename_split_lis = photo_id.rsplit("_")
        filename_val = filename_split_lis[0]
        outpath = os.path.join(self.base_path, filename_val, self.coreg_out)
        OtherUtils.TouchPath(outpath)

        # input path
        inpath = []
        for i in range(0,np.shape(files_to_be_coregd_ortho)[1]): # self.ref_date_folder
            vall = files_to_be_coregd_ortho[0][i]
            if(filename_val in str(vall)):
                inpath = vall
                print(inpath)

        # input path ndsm
        inpath_ndsm = []
        for i in range(0,np.shape(files_to_be_coregd)[1]): # self.ref_date_folder
            vall = files_to_be_coregd[0][i]
            if(filename_val in str(vall)):
                inpath_ndsm = vall
                print(inpath_ndsm)
        
        temparr = []
        temp_df = tiepointarray[tiepointarray['photo_id'] == photo_id]
        for rows in temp_df.iterrows():
            df0refvals = refdf0[refdf0['tie_point_id'] == str(rows[1][1])]
            if(len(df0refvals)>0):
                temparr.append([rows[1][1], rows[1][2], rows[1][3], df0refvals['lat'].values[0], df0refvals['lon'].values[0]])
        temparr = pd.DataFrame(temparr)
        # build GCP array to be used to georeference
        points =[]
        for idd, rows in temparr.iterrows():
            points.append(gdal.GCP(np.float(rows[3]),np.float(rows[4]),np.float(0),np.round(rows[1]),np.round(rows[2])))

        # # coregister
        # RasterOperators.newproj(inpath, inpath, points)
        # RasterOperators.newproj(inpath_ndsm, inpath_ndsm, points)
        print('Reprojecting Orthophoto')
        RasterOperators.newproj(inpath, outpath + "/" + filename_val +".tif",points, gdal.GDT_UInt16)
        print('Reprojecting nDSM')
        RasterOperators.newproj(inpath_ndsm, outpath + "/" + filename_val + '_ndsm' + ".tif",points, gdal.GDT_UInt16)

    def copydataset(self,ImageOrthoListToCoregister):

        print('Copying ref Orthophoto to Orthorectified Folder')
        OutFileName= ''
        InFileName = ''
        for item in ImageOrthoListToCoregister:
            print(item)
            files_to_be_coregd_ortho = ImageOrthoListToCoregister[item]
            
        for filenames in files_to_be_coregd_ortho[0]:
            if(self.ref_date_folder in str(filenames)):
                # print(filenames)
                InFileName = filenames

                filenamesplit = filenames.split('/')
                print(filenamesplit[-1])
                date_name = filenamesplit[-1].split('_')[0]
                OutFileName = '/'
                for i in range(1,len(filenamesplit)-2):
                    OutFileName = os.path.join(OutFileName,str(filenamesplit[i]))                
                print(os.path.join(OutFileName, 'CoregisteredSlices'))

                OtherUtils.TouchPath(os.path.join(OutFileName, 'CoregisteredSlices'))
                OutFileName = os.path.join(OutFileName, 'CoregisteredSlices', str(date_name)+'.tif')

        RasterOperators.CopyImage(InFileName,OutFileName)
    
    # copydatasetndsm

    def copydatasetndsm(self,ImageOrthoListToCoregister):
        print('Copying ref Orthophoto to Orthorectified Folder')
        OutFileName= ''
        InFileName = ''
        for item in ImageOrthoListToCoregister:
            print(item)
            files_to_be_coregd_ortho = ImageOrthoListToCoregister[item]
            
        for filenames in files_to_be_coregd_ortho[0]:
            if(self.ref_date_folder in str(filenames)):
                # print(filenames)
                InFileName = filenames

                filenamesplit = filenames.split('/')
                print(filenamesplit[-1])
                date_name = filenamesplit[-1].split('_')[0]
                OutFileName = '/'
                for i in range(1,len(filenamesplit)-3):
                    OutFileName = os.path.join(OutFileName,str(filenamesplit[i]))                
                print(os.path.join(OutFileName, 'CoregisteredSlices'))

                OtherUtils.TouchPath(os.path.join(OutFileName, 'CoregisteredSlices'))
                OutFileName = os.path.join(OutFileName, 'CoregisteredSlices', str(date_name)+'_ndsm.tif')

        RasterOperators.CopyImage(InFileName,OutFileName)

    def copydatasetndsmorig(self,ImageOrthoListToCoregister):
        print('Copying ref Orthophoto to Orthorectified Folder')
        OutFileName= ''
        InFileName = ''
        for item in ImageOrthoListToCoregister:
            print(item)
            files_to_be_coregd_ortho = ImageOrthoListToCoregister[item]
            
        for filenames in files_to_be_coregd_ortho[0]:
            if(self.ref_date_folder in str(filenames)):
                # print(filenames)
                InFileName = filenames

                filenamesplit = filenames.split('/')
                print(filenamesplit[-1])
                date_name = filenamesplit[-1].split('_')[0]
                OutFileName = '/'
                for i in range(1,len(filenamesplit)-3):
                    OutFileName = os.path.join(OutFileName,str(filenamesplit[i]))                
                print(os.path.join(OutFileName, 'CoregisteredSlices'))

                OtherUtils.TouchPath(os.path.join(OutFileName, 'CoregisteredSlices','nDSM-Original'))
                OutFileName = os.path.join(OutFileName, 'CoregisteredSlices','nDSM-Original', str(date_name)+'_ndsm.tif')

        RasterOperators.CopyImage(InFileName,OutFileName)

    def Coregister_orig_dim_dem(self):
        print("Started Coregistation of dem Orig Dim")

        # get list of nDSMs to to be coregistered, for each image-tile in ref folder
        ndsm_data_folder_org_dim = 'nDSM/nDSM_Original'
        ref_folder = os.path.join(self.base_path, self.ref_date_folder, ndsm_data_folder_org_dim)
        ImageListToCoregisterOrigDim = self.__GetImageListToCoregister(ref_folder, ndsm_data_folder_org_dim)
        print(ImageListToCoregisterOrigDim)

        self.copydatasetndsmorig(ImageListToCoregisterOrigDim)

        # exit(0)
        for item in ImageListToCoregisterOrigDim:

            print(item)
            files_to_be_coregd_org_dim = ImageListToCoregisterOrigDim[item]

            # files_to_be_coregd_ortho = ImageOrthoListToCoregister[item]
            # create folder if not exist
            if not self.checkfoldervalidity(files_to_be_coregd_org_dim):
                print("skipping the tile as it is not common to all dates")
                continue            

            # get tie points from AGISoft
            tiepointarray, success = self.AGISOftCoreg(files_to_be_coregd_org_dim, self.save_agi_obj_file)

            # if tiepoints are detected
            if(success and (len(tiepointarray) >0) ):

                tiepointarray = pnd.DataFrame(tiepointarray)
                tiepointarray.columns =['photo_id','tie_point_id','xval','yval']

                # get unique photo_ids
                photo_id_list = list(tiepointarray["photo_id"].unique())

                # get GCPs from reference image
                refdf0, TreeTopXY, remaining_photo_id_list = self.__getRefPhotoGCPs(
                                                            photo_id_list, 
                                                            tiepointarray, 
                                                            files_to_be_coregd_org_dim, 
                                                            self.saveGCPasShp)

                # assign ref cooridnates from ref GCPs to corresponding tie points in the image
                for photo_id in remaining_photo_id_list:
                    print(photo_id)
                    self.__reproj_raster_od(photo_id, files_to_be_coregd_org_dim, tiepointarray, refdf0)

            else:
                print("Agosoft Error / no tie points detected")


    def __reproj_raster_od(self, photo_id, files_to_be_coregd, tiepointarray, refdf0):
        # create output path
        filename_split_lis = photo_id.rsplit("_")
        filename_val = filename_split_lis[0]

        outpath = os.path.join(self.base_path, filename_val, self.coreg_out, 'nDSM-Original')
        OtherUtils.TouchPath(outpath)

        # input path ndsm
        inpath_ndsm = []
        for i in range(0,np.shape(files_to_be_coregd)[1]): # self.ref_date_folder
            vall = files_to_be_coregd[0][i]
            if(filename_val in str(vall)):
                inpath_ndsm = vall
                print(inpath_ndsm)
        
        temparr = []
        temp_df = tiepointarray[tiepointarray['photo_id'] == photo_id]
        for rows in temp_df.iterrows():
            df0refvals = refdf0[refdf0['tie_point_id'] == str(rows[1][1])]
            if(len(df0refvals)>0):
                temparr.append([rows[1][1], rows[1][2], rows[1][3], df0refvals['lat'].values[0], df0refvals['lon'].values[0]])
        temparr = pd.DataFrame(temparr)
        # build GCP array to be used to georeference
        points =[]
        for idd, rows in temparr.iterrows():
            points.append(gdal.GCP(np.float(rows[3]),np.float(rows[4]),np.float(0),np.round(rows[1]),np.round(rows[2])))

        # coregister
        print('Reprojecting nDSM Original Resolution.')
        RasterOperators.newproj(inpath_ndsm, outpath + "/" + filename_val +'_ndsm' + ".tif",points, gdal.GDT_UInt16)

    def AGISOftCoreg(self, photo_list, save_agi_obj_file):
        success = True
        point_proj = [] #list of strings
        try:
            Metashape.app.gpu_mask = 1
            doc = Metashape.Document()
            chunk = doc.addChunk()
            chunk.crs = Metashape.CoordinateSystem("EPSG::32619")
            chunk.addPhotos(photo_list)
            Metashape.app.update()
            # # aligned cameras
            for frame in chunk.frames:
                frame.matchPhotos(accuracy=Metashape.MediumAccuracy, generic_preselection=True, reference_preselection=True, keypoint_limit=40000, tiepoint_limit=4000)
            Metashape.app.update()
            task = Metashape.Tasks.AlignCameras()
            task.adaptive_fitting = True
            task.reset_alignment = True
            task.apply(chunk)

            point_cloud = chunk.point_cloud
            points = point_cloud.points
            npoints = len(points)
            tie_points = chunk.point_cloud
            projections = chunk.point_cloud.projections
            point_ids = [-1] * len(point_cloud.tracks)

            for point_id in range(0, npoints):
                point_ids[points[point_id].track_id] = point_id

            if(save_agi_obj_file):  
                doc.save(path = os.path.join(self.base_path,'AgiObj.psx'), chunks = [doc.chunk])

            if(chunk.cameras is None):
                teststr = 'empty'

            for camera in chunk.cameras:
                for proj in projections[camera]:
                    
                    track_id = proj.track_id
                    point_id = point_ids[track_id]

                    if point_id < 0:
                        continue
                    if not points[point_id].valid:
                        continue
                    # print(point_id)
                    point_geoc = chunk.transform.matrix * points[point_id].coord
                    point_geoc.size = 3
                    point_geog = chunk.crs.project(point_geoc)

                    line = [camera.label, point_id, proj.coord.x, proj.coord.y]
                    point_proj.append(line)
        except Exception as err:
            success = False
            print("AGISoft error: {0}".format(err))

        if(save_agi_obj_file):
            doc.save(path = os.path.join(self.base_path,'AgiObj.psx'), chunks = [doc.chunk])
        return point_proj, success

    def DelineateIndividaulTrees(self):
    
        # get list of images to to be coregistered, for each image-tile in ref folder (i.e., may)
        ref_folder = os.path.join(self.base_path, self.ref_date_folder, 'Sliced_Data')
        ImageListToCoregister = self.__GetImageListToCoregister(ref_folder)
    
        # loop sliced data folder (can be aany folder)        
        for root, folders, files in os.walk(self.base_path):
            for file in files:
                
                filename_split_list = file.rsplit("_")
                slice_folder_name = filename_split_list[0] + '_' \
                                    + filename_split_list[1] + '_'  \
                                    + filename_split_list[2].rsplit(".")[0]

                # check existance of out folder
                in_out_folders = self.TouchIOPath(slice_folder_name)

                # # # Crop tree crowns using crown buffers
                MaskTreeCrown.CropITCFromOrthoImage(
                    os.path.join(in_out_folders["OrthoImagesSliceFolder"], slice_folder_name+'.tif'), 
                    in_out_folders["ShpFileFolder"], in_out_folders["ITCImagesFolder"])