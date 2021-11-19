import os,sys
import fiona
import numpy as np
from ImageProcessor import OtherUtils
from ProjectConstants import GlobalConstants as gc
import subprocess
from subprocess import Popen
from ImageProcessor import RasterOperators, VectorOperators
import matlab.engine
import rasterio
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, mapping
from ProjectConstants import GlobalConstants as gc

class ITCCrownShapeUtils:

    def __init__(self, FileDataInfo):
        # assert m > 1
        # self.u, self.centers = None, None
        self.base_path = FileDataInfo['BaseFolder']
        self.date = FileDataInfo['Date']
        self.RefShp = FileDataInfo['RefShp']
        self.MatlabFilPath = FileDataInfo['MatFilePath']
        self.SkipCoregStep = FileDataInfo['SkipCoregStep']
        self.operator_type = FileDataInfo['IndexOperatorType']
        self.skip = FileDataInfo['Skip']

    def GetCrownFromMatlab(self):
        print( 'Starting crown extraction in Matlab')
        Orig_dir = os.getcwd()
        os.chdir(self.MatlabFilPath)

        rest_path = os.path.join(self.base_path, self.date,gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, gc.CROWN_SHP_BUF_FOLDER)
        # rest_path = os.path.join(self.base_path, self.date, gc.CROPPED_DATA_FOLDER, gc.CROPPED_FCM_DATA_FOLDER)
        dsm_buf_file_path = os.path.join(self.base_path, self.date, gc.CROPPED_DATA_FOLDER, gc.CROPPED_NDSM_DATA_FOLDER)
        tt_shp_file_folder = os.path.join(self.base_path, self.date, gc.CROPPED_DATA_FOLDER, gc.CROPPED_SHP_DATA_FOLDER)
        out_shp_base_path = os.path.join(self.base_path, self.date,gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, gc.CROWN_SHP_OUT_FOLDER)
        OtherUtils.TouchPath(out_shp_base_path)

        print(rest_path)
        future = matlab.engine.start_matlab(background=True)
        eng = future.result()
        print(rest_path)
        print(dsm_buf_file_path)
        print(tt_shp_file_folder)
        print(out_shp_base_path)
        # exit(0)
        eng.test2D_New_Algo(rest_path, dsm_buf_file_path, tt_shp_file_folder, out_shp_base_path, nargout=0)
        # eng.test2D(rest_path, out_shp_base_path, nargout=0)
        eng.quit()

        print('Completed crown extraction in Matlab!')
        
        os.chdir(Orig_dir)
        # exit(0)


    def GetIndiceMapsArrays(self, treetopsshp, map_path, operator_type):
        meanval_ndvi, meanval_pri, meanval_cci = [], [], []
        for index, row in treetopsshp.iterrows():
            if(row['geometry']==None):
                print(row[['FID','geometry']])
                continue

            CrownBuffer = row['geometry'].buffer(0.8, cap_style=1)
            NDVIFile = os.path.join(map_path, 'NDVI.tif')
            
            crown_geom_obj = None
            if(operator_type == 'AllPixelMean'): 
                CrownShpFile = os.path.join(
                                    self.base_path,
                                    self.date,
                                    gc.ITC_DATA_FOLDER,
                                    gc.ALL_TREES_SHP_FOLDER,
                                    gc.CROWN_SHP_BUF_OUT_FOLDER,
                                    self.date + '_'+ str(row['geometry'].x) + '_' + str(row['geometry'].y) + '.shp')
                crown_geom_obj = gpd.read_file(CrownShpFile)
                # print(crown_geom_obj['geometry'])
                print(CrownShpFile)
            # 
            if(operator_type == 'AllPixelMean'):                
                out_image_ndvi, out_transform_ndvi = rasterio.mask.mask(rasterio.open(NDVIFile), gpd.GeoSeries(crown_geom_obj['geometry']), crop=True, filled=True, nodata = 0)
                Values_ndvi = out_image_ndvi
            else:
                out_image_ndvi, out_transform_ndvi = rasterio.mask.mask(rasterio.open(NDVIFile), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
                Indice, Values_ndvi = RasterOperators.GetLargestN(out_image_ndvi.flatten(), 25)
            meanval_ndvi.append(np.median(Values_ndvi))

            PRIFile = os.path.join(map_path, 'PRI.tif')
            
            if(operator_type == 'AllPixelMean'):
                out_image_pri, out_transform_pri = rasterio.mask.mask(rasterio.open(PRIFile), gpd.GeoSeries(crown_geom_obj['geometry']), crop=True, filled=True, nodata = 0)
                Values_pri = out_image_pri
            else:
                out_image_pri, out_transform_pri = rasterio.mask.mask(rasterio.open(PRIFile), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
                Indice, Values_pri = RasterOperators.GetLargestN(out_image_pri.flatten(), 25)
            meanval_pri.append(np.median(Values_pri))

            CCIFile = os.path.join(map_path, 'CCI.tif')
            
            if(operator_type == 'AllPixelMean'):
                out_image_cci, out_transform_cci = rasterio.mask.mask(rasterio.open(CCIFile), gpd.GeoSeries(crown_geom_obj['geometry']), crop=True, filled=True, nodata = 0)
                Values_cci = out_image_cci
            else:
                out_image_cci, out_transform_cci = rasterio.mask.mask(rasterio.open(CCIFile), gpd.GeoSeries(Polygon(CrownBuffer)), crop=True, filled=True, nodata = 0)
                Indice, Values_cci = RasterOperators.GetLargestN(out_image_cci.flatten(), 25)
            meanval_cci.append(np.median(Values_cci))
        
        norm_ndvi = meanval_ndvi
        norm_pri = meanval_pri
        norm_cci = meanval_cci

        return norm_ndvi, norm_pri, norm_cci

    def Write2Shp(self,norm_ndvi, norm_pri, norm_cci, in_shp_loc, out_shp_loc):
        loopcnt = 0

        # Define a polygon feature geometry with one attribute
        schema = {
            'geometry'   : 'Point',
            'properties' : {'NDVI': 'float' ,'PRI': 'float', 'CCI': 'float'},
        }

        with fiona.open(out_shp_loc, 'w', crs=gc.PROJECTION_ID, driver='ESRI Shapefile', schema=schema) as c: # from_epsg(32619)
            treetopsshp = gpd.read_file(in_shp_loc)   
            for index, row in treetopsshp.iterrows():
                if(row['geometry']==None):
                    print(row[['FID','geometry']])
                    continue
                # CrownBuffer = row['geometry'].buffer(0.8, cap_style=1)
                ## If there are multiple geometries, put the "for" loop here
                c.write({
                    'geometry': mapping(row['geometry']),
                    'properties': {'NDVI': norm_ndvi[loopcnt], 'PRI': norm_pri[loopcnt], 'CCI': norm_cci[loopcnt]}
                })
                loopcnt = loopcnt + 1

    def GenerateMaps(self, map_path, OrthoPhoto):
        # albedo = {"Center528": "0.63560", "Center 570": "0.64370", "Center645": "0.64750", "Center680": "0.62280", "Center900": "0.64420"} #values read from the file
        # Generate NDVI Map
        NDVIFile = os.path.join(map_path, 'NDVI.tif')
        print('NDVIFile')
        print(OrthoPhoto)
        RasterOperators.GetNDVIMap(OrthoPhoto, NDVIFile, 5, 4)
        
        # Generate PRI Map
        PRIFile = os.path.join(map_path, 'PRI.tif')
        RasterOperators.GetPRIMap(OrthoPhoto, PRIFile, 1, 2)
        
        # Generate CCI Map
        CCIFile = os.path.join(map_path, 'CCI.tif')
        RasterOperators.GetCCIMap(OrthoPhoto, CCIFile, 1, 3)

    def __getTreeLevelMaps(self):
        print('Deriving Spectral Index Maps')

        OrthoPhoto = os.path.join(self.base_path, self.date, gc.COREGISTER_OUT_FOLDER, self.date + '.tif')

        if(self.SkipCoregStep):
            OrthoPhoto = os.path.join(self.base_path, self.date, gc.NON_COR_ORTHOPHOTO_FOLDER, self.date + '.tif')
        
        outmapfilepath = os.path.join(self.base_path,self.date,gc.MAP_FOLDER)
        OtherUtils.TouchPath(outmapfilepath)

        # if(not(self.skip)):
        self.GenerateMaps(outmapfilepath, OrthoPhoto)
        
        # Get tree level data
        print('Deriving Tree Level Indices')
        inshapefile = os.path.join(self.base_path, self.date, gc.ITC_DATA_FOLDER,  gc.ALL_TREES_SHP_FOLDER, 'shapefile_merged.shp')
        treetopsshp = gpd.read_file(inshapefile)
        norm_ndvi,norm_pri,norm_cci = self.GetIndiceMapsArrays(treetopsshp,outmapfilepath,self.operator_type)

        # Write to shp
        outspath = os.path.join(self.base_path, self.date, gc.ITC_DATA_FOLDER,  gc.ALL_TREES_SHP_FOLDER, gc.ALL_TREES_SHP_OUT_FOLDER)
        OtherUtils.TouchPath(outspath)
        outshapefile = os.path.join(outspath, 'ITCSpectralInfo.shp')
        self.Write2Shp(norm_ndvi, norm_pri, norm_cci, inshapefile, outshapefile)

    def GetCrownBuffer(self):
        
        if(not(self.skip)):
            print('Started Crown Buffers Generation and Metadata Correctetion!')

            base_path = os.path.join(self.base_path, self.date, gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, gc.CROWN_SHP_OUT_FOLDER)
            base_path_out = os.path.join(self.base_path, self.date, gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, gc.CROWN_SHP_BUF_OUT_FOLDER)
            OtherUtils.TouchPath(base_path_out)

            shpfile_name_list = []
            for root, folders, files in os.walk(base_path):
                for file_name in files:
                    if os.path.splitext(file_name)[1] in [".shp"]:
                        full_in_file = os.path.join(root,file_name)
                        print(full_in_file)
                        meta = fiona.open(self.RefShp).meta # open ref file
                        updated_file = os.path.join(base_path_out,file_name)
                        with fiona.open(updated_file, 'w', **meta) as output:
                            for features in fiona.open(full_in_file): # open file
                                output.write(features)

            print('Crown Buffers Generated and Metadata Corrected!')

            # Merge shape files as a single shp file
            print('Started Merging Buffer Shape Files!')
            base_path_out = os.path.join(self.base_path, self.date, gc.ITC_DATA_FOLDER, gc.ALL_TREES_SHP_FOLDER, gc.CROWN_SHP_BUF_OUT_FOLDER)
            shpfile_name_list = []
            for root, folders, files in os.walk(base_path_out):
                for file_name in files:
                    if os.path.splitext(file_name)[1] in [".shp"]:
                        shpfile_name_list.append(os.path.join(root,file_name))

            if(np.shape(shpfile_name_list)[0] >0):                        
                ref_file = shpfile_name_list[0]
                merged_file = os.path.join(base_path_out,'0_itc_poly_merged.shp')
                # merge files
                meta = fiona.open(ref_file).meta
                with fiona.open(merged_file, 'w', **meta) as output:
                    for shpfile_path in shpfile_name_list:
                        for features in fiona.open(shpfile_path):
                            output.write(features)
                print('Shapes Merged!')
            else:
                print('No shape files to merge')
            
        self.__getTreeLevelMaps()