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

def Coregister():
        print("Started Coregistation")
        base_path = '/mnt/4TBHDD/HS_DATA/20180711/out'
        # files_to_be_coregd = ['/mnt/4TBHDD/HS_DATA/20180516/hs_data_full.tif',
                            #   '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20180516/op_new/20180516.tif']    
        files_to_be_coregd = ['/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/ProcessedMSData/20180516/op_new/20180516.tif',
                              '/mnt/4TBHDD/HS_DATA/20180711/hs_data_full.tif']     

        # get tie points from AGISoft
        tiepointarray, success = AGISOftCoreg(base_path,files_to_be_coregd, True)

        # if tiepoints are detected
        if(success and (len(tiepointarray) >0)):

            tiepointarray = pnd.DataFrame(tiepointarray)
            tiepointarray.columns =['photo_id','tie_point_id','xval','yval']

            # get unique photo_ids
            photo_id_list = list(tiepointarray["photo_id"].unique())
            print(photo_id_list)
            # exit(0)
            # get GCPs from reference image
            refdf0, TreeTopXY, remaining_photo_id_list = getRefPhotoGCPs(
                                                        base_path,
                                                        photo_id_list, 
                                                        tiepointarray, 
                                                        files_to_be_coregd,
                                                        False)
            print(refdf0.head())
            # refdf0.to_csv(base_path+'/opt.csv')
            # exit(0)
            # assign ref cooridnates from ref GCPs to corresponding tie points in the image
            # print(remaining_photo_id_list)
            # exit(0)
            for photo_id in remaining_photo_id_list:
                print(photo_id)
                # exit(0)
                reproj_raster(files_to_be_coregd[1], base_path, photo_id, files_to_be_coregd, tiepointarray, refdf0)
                # reproj_raster(files_to_be_coregd[0], base_path, photo_id, files_to_be_coregd, tiepointarray, refdf0)

        else:
            print("Agosoft Error / no tie points detected") 

def AGISOftCoreg(base_path, photo_list, save_agi_obj_file):
        success = True
        point_proj = [] #list of strings
        try:
            Metashape.app.gpu_mask = 1
            doc = Metashape.Document()
            chunk = doc.addChunk()
            chunk.crs = Metashape.CoordinateSystem("EPSG::32619")
            chunk.addPhotos(photo_list)
            chunk.primary_channel = 2
            Metashape.app.update()
            # # aligned cameras
            for frame in chunk.frames:
                frame.matchPhotos(accuracy=Metashape.MediumAccuracy, generic_preselection=False, reference_preselection=True, keypoint_limit=40000, tiepoint_limit=4000)
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
            # print('here')
            for point_id in range(0, npoints):
                point_ids[points[point_id].track_id] = point_id
            # print('here')
            if(save_agi_obj_file):  
                doc.save(path = os.path.join(base_path,'AgiObj.psx'), chunks = [doc.chunk])
                # print('here')
            # print(chunk.cameras)
            if(chunk.cameras is None):
                teststr = 'empty'

            for camera in chunk.cameras:
                print(camera)
                # exit(0)
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
            doc.save(path = os.path.join(base_path,'AgiObj.psx'), chunks = [doc.chunk])
        return point_proj, success

def reproj_raster(inpath,out_path, photo_id, files_to_be_coregd_ortho, tiepointarray, refdf0):
        
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

        print('Reprojecting Orthophoto')
        RasterOperators.newproj(inpath, out_path + "/" + 'outfiletiff' +".tif",points, gdal.GDT_Float32)

def getRefPhotoGCPs(base_path,photo_id_list, tiepointarray,files_to_be_coregd, saveGCPasShp):

        # get ref photo name
        ref_photo_id = photo_id_list[0]
        # for idd in photo_id_list:
        #     if(self.ref_date_folder in str(idd)):
        #         ref_photo_id = idd
        print('ref_photo_id : ' + ref_photo_id)

        # get ref photo path
        ref_photo_path = files_to_be_coregd[0]
        print(np.shape(files_to_be_coregd))
        # exit(0)
        # for i in range(0,np.shape(files_to_be_coregd)[0]):
        #     vall = files_to_be_coregd[i]
        #     if(self.ref_date_folder in str(vall)):
        #         ref_photo_path = vall
        #         print(ref_photo_path)

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
        outpath = os.path.join(base_path, filename_val)
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

Coregister()