import os, sys
import numpy as np
from seaborn.categorical import countplot
from ImageProcessor import RasterOperators, OtherUtils
from ImageProcessor.Algorithms import LocalMaximaExtractor
from ITCDetector import TreeDetection, MaskTreeCrown
import rasterio
# from glob import glob
import shutil
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
import gdal
from ProjectConstants import GlobalConstants as gc
from shapely.ops import nearest_points
from scipy.spatial import cKDTree
from shapely.geometry import Point
import matplotlib.pyplot as plt
import tqdm
import scipy as sp
import time
import seaborn as sns
import statsmodels.api as sm

class AnalyzeUtils:

    def __init__(self, FileDataInfo):
        # assert m > 1
        # self.u, self.centers = None, None
        self.base_path = FileDataInfo['BaseFolder']
        self.dates = FileDataInfo['Dates']
        self.max_dist = FileDataInfo['MaxNeighbourDist']
        self.ref_file_shp = FileDataInfo['ref_file_shp']
        self.ref_100_file_shp = FileDataInfo['ref_100_file_shp']
        self.AllRefData= FileDataInfo['ALL_REF_DATA']
        self.RefSheetID = FileDataInfo['REF_SHEET_ID']
        self.AnalysisYears = FileDataInfo['AnalysisYears']
        self.AnalysisMonths = FileDataInfo['AnalysisMonths']
        self.GraphRSColumn = FileDataInfo['GraphRSColumn']
        self.GraphFieldColumn = FileDataInfo['GraphFieldColumn']

    def Generate_RS_REF_Merged_File(self):
        print('Creating shp file with reference Data')
        self.GenerateShpWithRef()

    def ModelPhenology(self):
        print('Modelling Phenological Data!')
        self.ModelPhenologyTreesInMultiImages()

    # def Preprocess100RefData(self):
    #     print('Phenological Data!')
    #     # RefData = gpd.read_file(self.Li6400Data)
    #     Li6400Dt = pd.read_excel(self.AllRefData,sheet_name=self.RefSheetID)
    #     Li6400Dt['Tree-Gen-ID'].replace('_','-',regex=True,inplace=True)
    #     print(Li6400Dt.head())

    #     PigmentsDt = pd.read_excel(self.PigmentsData ,sheet_name='Pigments-2018')
    #     # PigmentsDt['Tree-#'].replace('_','-',regex=True,inplace=True)
    #     print(PigmentsDt.head())

    #     SCADt = pd.read_excel(self.SCAData,sheet_name='2018')
    #     SCADt['Genotype'].replace('.','-',regex=True,inplace=True)
    #     print(SCADt.head())

    #     WaterPotentialDt = pd.read_excel(self.WaterPotentialData,sheet_name='Sheet3')
    #     WaterPotentialDt['Individual'].replace('.','-',regex=True,inplace=True)
    #     print(WaterPotentialDt.head())


    def ModelPhenologyTreesInMultiImages(self):        
        # Read RS dataset
        tempoutFolder = os.path.join(self.base_path, gc.PHENOLOGY_OUT_FOLDER, "XLS", "tmp")
        
        # Clear all temp files
        dir_path = tempoutFolder
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            print("Error: %s : %s" % (dir_path, e.strerror))
        OtherUtils.TouchPath(dir_path)

        # RS phenology file
        Phenology_out_file = os.path.join(self.base_path, gc.PHENOLOGY_OUT_FOLDER, "XLS", "out.xlsx")
        data_RS =  pd.read_excel(Phenology_out_file,'Sheet1',engine='openpyxl')
        data_RS.dropna(axis=0,how='all',inplace=True)
        
        # Read field dataset
        data_Field = pd.read_excel(self.AllRefData,self.RefSheetID,engine='openpyxl')
        data_Field.dropna(axis=0,how='all',inplace=True)

        # Merge DFs
        merged_df = pd.merge(data_Field, data_RS,  how='right', left_on=['Year','Month','Tree-Gen-ID'], right_on = ['Year','Month','tree_id'])
        merged_df['Year'] = merged_df['Year'].apply(lambda x: int(x))

        R22 =[] 
        for year in self.AnalysisYears:
            for month in self.AnalysisMonths:
                print('Processing Data from the {1} {0}'.format(year, month))
                specif_year_month_df = merged_df.loc[merged_df['Year'].isin([year]) & merged_df['Month'].isin([month])]
                # 100 Trees used for modelling
                specif_year_month_REF_TREES = specif_year_month_df.loc[specif_year_month_df['tree_id'].isin(data_Field['Tree-Gen-ID'])]
                specif_year_month_REF_TREES.reset_index()
                # specif_year_month_REF_TREES.fillna(0, inplace=True)
                specif_year_month_REF_TREES.dropna(axis=0, how='any',subset =[self.GraphFieldColumn], inplace=True)
                # Trees used for predicting
                specif_year_month_PRED_TREES = specif_year_month_df.loc[np.invert(specif_year_month_df['tree_id'].isin(data_Field['Tree-Gen-ID']))]
                specif_year_month_PRED_TREES.reset_index()
                # Append PREDICT Column
                specif_year_month_REF_TREES = specif_year_month_REF_TREES.assign(Predict=-1)
                specif_year_month_PRED_TREES = specif_year_month_PRED_TREES.assign(Predict=0)
                #### MODEL FvFm ####
                # print(specif_year_month_REF_TREES.head())
                # exit(0)
                # print(specif_year_month_REF_TREES.head())
                modelresults = sm.OLS(specif_year_month_REF_TREES[self.GraphFieldColumn],specif_year_month_REF_TREES[self.GraphRSColumn]).fit()
                # print(modelresults.summary())
                R22.append(modelresults.rsquared)
                specif_year_month_PRED_TREES.loc[:,self.GraphFieldColumn] = modelresults.predict(specif_year_month_PRED_TREES[self.GraphRSColumn])
                print(modelresults.summary())
                result_s_m_y = pd.concat([specif_year_month_REF_TREES,specif_year_month_PRED_TREES])
                result_s_m_y.reset_index()
                # Export file
                result_s_m_y.to_excel(os.path.join(tempoutFolder,str(year) +"_"+str(month)+".xlsx"))

        # Merge All Files in OutFolder
        final_df = pd.DataFrame(None)
        for root, folers, files in os.walk(tempoutFolder):
            for file in files:
                if("Combined" not in file):
                    filepath = os.path.join(root,file)
                    print(filepath)
                    final_df = pd.concat([final_df,pd.read_excel(filepath)])
        final_df.dropna(axis=0,how='all',inplace=True)
        final_df.to_excel(os.path.join(tempoutFolder, "Combined.xlsx"))

        # FOR PLOTS
        # years  = [2017,2018]
        # months = ['May','October','July']
        in_file = pd.read_excel(os.path.join(tempoutFolder, "Combined.xlsx"),engine='openpyxl')
        in_file = in_file.loc[in_file['Predict'].isin([-1])]
        # in_file=in_file.loc[in_file[par_val]<=0.2]
        # in_file=in_file.loc[in_file[par_val]>-0.3]

        tips = sns.load_dataset('tips')
        g = sns.lmplot(x=self.GraphRSColumn, y=self.GraphFieldColumn, data=in_file, robust = True,
                    col='Month', hue='Year', height=3, aspect=1)
        def annotate(data, **kws):
            r, p = sp.stats.pearsonr(data[self.GraphRSColumn], data[self.GraphFieldColumn])
            ax = plt.gca()
            ax.text(.05, .8, 'r={:.2f}, p={:.2g}'.format(r, p),
                    transform=ax.transAxes)
        g.map_dataframe(annotate,y=1.05)
        plt.suptitle("{0} Index Vs {1} Conc.".format(self.GraphRSColumn,self.GraphFieldColumn),fontsize=18,fontname="Times New Roman", fontweight='bold')
        plt.show()
        print(R22)

    def ExtractPhenology(self):
        print('Extracting Phenological Data!')
        # self.GetProximalTreesInImages()
        self.getITCIndicesForAllDates()
        # self.ModelPhenologyTreesInMultiImages()
        # self.plot_spectrum()
        
    def GetProximalTreesInImages(self):
        print("Detecting proximal trees")
        print(gc.PROJECTION_ID)

        # ITC_Data = gpd.GeoDataFrame()
        for date_index in range(len(self.dates)-1):
            print("Generating set:{0}".format(date_index))
            ITC_shape_File_1 = os.path.join(self.base_path,
                                            self.dates[0],
                                            gc.ITC_DATA_FOLDER, 
                                            gc.ALL_TREES_SHP_FOLDER, 
                                            gc.ALL_TREES_SHP_OUT_FOLDER,
                                            gc.ALL_TREES_SHP_OUT_FILE
                                            )
            print('Reading {0}'.format(ITC_shape_File_1))
            ITC_dataframe1 = gpd.read_file(ITC_shape_File_1)
            # dataset1 = [[index, row['geometry'].x, row['geometry'].y] for index, row in ITC_dataframe1.iterrows()]
            # print(dataset1)

            ITC_shape_File_2 = os.path.join(self.base_path,
                                self.dates[date_index+1],
                                gc.ITC_DATA_FOLDER, 
                                gc.ALL_TREES_SHP_FOLDER,
                                gc.ALL_TREES_SHP_OUT_FOLDER,
                                gc.ALL_TREES_SHP_OUT_FILE
                                )
                                                        
            print('Reading {0}'.format(ITC_shape_File_2))
            ITC_dataframe2 = gpd.read_file(ITC_shape_File_2)
            # dataset2 = [[index, row['geometry'].x, row['geometry'].y] for index, row in ITC_dataframe2.iterrows()]
            # print(dataset2)

            # Locating proximal points
            final_gdf = self.ckdnearest(ITC_dataframe1,ITC_dataframe2,date_index)
            final_gdf = final_gdf[final_gdf['dist'+str(date_index)]<self.max_dist]
            # print(final_gdf.head())
            # Save as shp
            out_shape_path = os.path.join(self.base_path,
                    self.dates[date_index+1],
                    gc.ITC_DATA_FOLDER, 
                    gc.ALL_TREES_SHP_FOLDER, 
                    gc.ALL_TREES_SHP_OUT_FOLDER,
                    "New" + str(date_index) + ".shp"
                    )
            print('Saving {0}'.format(out_shape_path))
            final_gdf.to_file(driver = 'ESRI Shapefile', filename = out_shape_path)
    
    
    def getITCIndicesForAllDates(self):
        # get reference date file
        ref_date_shp = os.path.join(self.base_path,
                        self.dates[0],
                        gc.ITC_DATA_FOLDER, 
                        gc.ALL_TREES_SHP_FOLDER, 
                        gc.ALL_TREES_SHP_OUT_FOLDER,
                        gc.ALL_TREES_SHP_OUT_FILE
                        )
        print('Reading Ref {0}'.format(ref_date_shp))
        ref_data_frame = gpd.read_file(ref_date_shp)

        # Loop through other dates
        for date_index in range(1,len(self.dates)):

            ITC_shape_File = os.path.join(self.base_path,
                                self.dates[date_index],
                                gc.ITC_DATA_FOLDER, 
                                gc.ALL_TREES_SHP_FOLDER, 
                                gc.ALL_TREES_SHP_OUT_FOLDER,
                                gc.ALL_TREES_SHP_OUT_FILE
                                )
                                                        
            print('Reading {0}'.format(ITC_shape_File))
            ITC_dataframe = gpd.read_file(ITC_shape_File)
            ITC_dataframe.columns = ['NDVI'+str(date_index), 'PRI'+str(date_index) ,'CCI'+str(date_index), 'geometry']
            # print(ITC_dataframe.head())
            # exit(0)

            final_gdf = self.ckdnearest(ref_data_frame, ITC_dataframe, date_index)
            final_gdf = final_gdf[final_gdf['dist'+str(date_index)]<self.max_dist]            
            ref_data_frame = final_gdf
        
        # save file
        ref_data_frame = ref_data_frame.dropna()
        # print(ref_data_frame.head())

        out_folder = os.path.join(self.base_path,
                        gc.PHENOLOGY_OUT_FOLDER)
        OtherUtils.TouchPath(out_folder)
        out_shape_path = os.path.join(out_folder, "TempFiles/ALL.shp")

        print('Saving Phenology Details to: {0}'.format(out_shape_path))
        ref_data_frame.to_file(driver = 'ESRI Shapefile', filename = out_shape_path)

    def GenerateShpWithRef(self):
        # first file 

        # REMOTE SENSING FILE
        in_shape_path = os.path.join(self.base_path, gc.PHENOLOGY_OUT_FOLDER, "TempFiles/ALL.shp")
        in_data_frame = gpd.read_file(in_shape_path)
        ref_data_frame = gpd.read_file(self.ref_file_shp)

        # REFERENCE DATA FILE
        final_gdf = self.ckdnearest(ref_data_frame,in_data_frame,0)
        # final_gdf = final_gdf[final_gdf['dist'+str(0)]<self.max_dist] 
        # final_gdf = final_gdf.dropna()
        final_gdf = final_gdf[['no_famille','genotype_i','no_bloc','Longitude','Latitude','A18_04_Hau','A18_04_DHP',
                                'NDVI','PRI','CCI',
                                'NDVI1','PRI1','CCI1',
                                'NDVI2','PRI2','CCI2',
                                'NDVI3','PRI3','CCI3',
                                'NDVI4','PRI4','CCI4',
                                'NDVI5','PRI5','CCI5',
                                'geometry']]
        final_gdf.rename(columns={"NDVI":"NDVIDate1" ,"PRI":"PRIDate1" ,"CCI" :"CCIDate1"},inplace = True)
        final_gdf.rename(columns={"NDVI1":"NDVIDate2","PRI1":"PRIDate2","CCI1":"CCIDate2"},inplace = True)
        final_gdf.rename(columns={"NDVI2":"NDVIDate3","PRI2":"PRIDate3","CCI2":"CCIDate3"},inplace = True)
        final_gdf.rename(columns={"NDVI3":"NDVIDate4","PRI3":"PRIDate4","CCI3":"CCIDate4"},inplace = True)
        final_gdf.rename(columns={"NDVI4":"NDVIDate5","PRI4":"PRIDate5","CCI4":"CCIDate5"},inplace = True)
        final_gdf.rename(columns={"NDVI5":"NDVIDate6","PRI5":"PRIDate6","CCI5":"CCIDate6"},inplace = True)

        final_gdf.rename(columns={"no_famille":"gen_id","genotype_i":"tree_id","no_bloc":"BlockNum","A18_04_Hau":"TreeHeight","A18_04_DHP":"StemDBH","NDVI2":"NDVIDate3","PRI2":"PRIDate3","CCI2":"CCIDate3"},inplace = True)
        print(final_gdf.head())

        # Get the 100 tree data to model
        TreeeRefData = gpd.read_file(self.ref_file_shp)   
        final_gdf = final_gdf[(final_gdf['tree_id'].isin(TreeeRefData['genotype_i'])) ]

        # final_gdf_rest = final_gdf[~(final_gdf['tree_id'].isin(Ref100Data['genotype_i'])) ] # Rest of the trees
        out_shape_path = os.path.join(self.base_path, gc.PHENOLOGY_OUT_FOLDER, "TreePhenologyWithRef.shp")
        print('Saving Phenology Details to: {0}'.format(out_shape_path))
        final_gdf.to_file(driver = 'ESRI Shapefile', filename = out_shape_path)

        in_data_frame1 = final_gdf.copy()
        in_data_frame1['Year'] =   '2017'
        in_data_frame1['Month'] =  'June'
        in_data_frame1 = in_data_frame1[['gen_id','tree_id','BlockNum','NDVIDate1','PRIDate1','CCIDate1','Year','Month']]
        in_data_frame1.rename({'NDVIDate1':'NDVI','PRIDate1':'PRI','CCIDate1':'CCI'},axis=1,inplace=True)

        in_data_frame2 = final_gdf.copy()
        in_data_frame2['Year']  =  '2017'
        in_data_frame2['Month'] =  'August'
        in_data_frame2 = in_data_frame2[['gen_id','tree_id','BlockNum','NDVIDate2','PRIDate2','CCIDate2','Year','Month']]
        in_data_frame2.rename({'NDVIDate2':'NDVI','PRIDate2':'PRI','CCIDate2':'CCI'},axis=1,inplace=True)
        
        in_data_frame3 = final_gdf.copy()
        in_data_frame3['Year']  =  '2017'
        in_data_frame3['Month'] =  'October'
        in_data_frame3 = in_data_frame3[['gen_id','tree_id','BlockNum','NDVIDate3','PRIDate3','CCIDate3','Year','Month']]
        in_data_frame3.rename({'NDVIDate3':'NDVI','PRIDate3':'PRI','CCIDate3':'CCI'},axis=1,inplace=True)
        
        in_data_frame4 = final_gdf.copy()
        in_data_frame4['Year'] =  '2018'
        in_data_frame4['Month'] =  'June'
        in_data_frame4 = in_data_frame4[['gen_id','tree_id','BlockNum','NDVIDate4','PRIDate4','CCIDate4','Year','Month']]
        in_data_frame4.rename({'NDVIDate4':'NDVI','PRIDate4':'PRI','CCIDate4':'CCI'},axis=1,inplace=True)
        
        in_data_frame5 = final_gdf.copy()
        in_data_frame5['Year']  =  '2018'
        in_data_frame5['Month']=  'August'
        in_data_frame5 = in_data_frame5[['gen_id','tree_id','BlockNum','NDVIDate5','PRIDate5','CCIDate5','Year','Month']]
        in_data_frame5.rename({'NDVIDate5':'NDVI','PRIDate5':'PRI','CCIDate5':'CCI'},axis=1,inplace=True)
        
        in_data_frame6 = final_gdf.copy()
        in_data_frame6['Year']  =  '2018'
        in_data_frame6['Month'] =  'October'
        in_data_frame6 = in_data_frame6[['gen_id','tree_id','BlockNum','NDVIDate6','PRIDate6','CCIDate6','Year','Month']]
        in_data_frame6.rename({'NDVIDate6':'NDVI','PRIDate6':'PRI','CCIDate6':'CCI'},axis=1,inplace=True)
        # in_data_frame6["tree_id"] = 'SCA-' + PigmentsDt2017["tree_id"].str.split("-").str[1] + '-' + PigmentsDt2017["tree_id"].str.split("-").str[0] + '-' + PigmentsDt2017["tree_id"].str.split("-").str[2]

        FinoFrame = pd.concat([in_data_frame1,in_data_frame2,in_data_frame3,in_data_frame4,in_data_frame5,in_data_frame6],axis=0)
        FinoFrame.to_excel('/mnt/4TBHDD/StCasimir-Multispectral-Analysis/2_Analysis-And-Results/ProcessedMSData1/Phenology/XLS/out.xlsx')

    def plot_spectrum(self):
        print("Plotting spectrum")

        out_folder = os.path.join(self.base_path,
                        gc.PHENOLOGY_OUT_FOLDER,
                        'TempFiles/ALL.shp')
        print('Reading {0}'.format(out_folder))
        ITC_dataframe = gpd.read_file(out_folder)
        ITC_dataframe["id"] = ITC_dataframe.index + 1
        ITC_dataframe.set_index('id', inplace=True)
        # ITC_dataframe = ITC_dataframe.reset_index()
        # ITC_dataframe.columns[13] = 'New_ID'
        # ITC_dataframe['New_ID'] = ITC_dataframe.index + 1
        print(ITC_dataframe)
        selectedIds = []
        ax = plt.gca()
        totalrows = len(ITC_dataframe)
        # fig,ax =  plt.subplots(1,3,tight_layout=True)
        for id, row in ITC_dataframe.iterrows():
            # print('NDVI:',row['NDVI'],row['NDVI1'],row['NDVI2'])
            NDVIList = [row['NDVI'],row['NDVI1'],row['NDVI2'],row['NDVI3'],row['NDVI4'],row['NDVI5']]
            # if((NDVIList[0]-NDVIList[1]) > 0 or (NDVIList[1]-NDVIList[2]) < 0):
            #     NDVIList = [0,0,0,0,0]
            selectedIds.append(id)
            # print('PRI:',row['PRI'],row['PRI1'],row['PRI2'])
            PRIList = [row['PRI'],row['PRI1'],row['PRI2'],row['PRI3'],row['PRI4'],row['PRI5']]
            # if((PRIList[0]-PRIList[1]) > 0 or (PRIList[1]-PRIList[2]) < 0):
            #     PRIList = [0,0,0,0,0]
            selectedIds.append(id)
            # print('CCI:',row['CCI'],row['CCI1'],row['CCI2'])
            CCIList = [row['CCI'],row['CCI1'],row['CCI2'],row['CCI3'],row['CCI4'],row['CCI5']]
            # if((CCIList[0]-CCIList[1]) > 0 or (CCIList[1]-CCIList[2]) < 0):
            #     CCIList = [0,0,0,0,0]
            selectedIds.append(id)
            # print(selectedIds)
            # print(len(PRIList),len(CCIList))

            # ax[0].plot(np.array(range(1,len(NDVIList)+1)).astype('int32'), NDVIList)
            # ax[0].set_xticks([1,2,3]) 
            # ax[0].set_xticklabels(['May', 'Jul' , 'Oct'], fontsize=12)
            # ax[1].plot(np.array(range(1,len(PRIList)+1)).astype('int32'), PRIList)
            # ax[1].set_xticks([1,2,3]) 
            # ax[1].set_xticklabels(['May', 'Jul' , 'Oct'], fontsize=12)
            # ax[2].plot(np.array(range(1,len(CCIList)+1)).astype('int32'), CCIList)
            # ax[2].set_xticks([1,2,3]) 
            # ax[2].set_xticklabels(['May', 'Jul' , 'Oct'], fontsize=12)

            # pnd.plot(kind='line',x='id',y='NDVI',ax=ax)
            # pnd.plot(kind='line',x='name',y='num_pets', color='red', ax=ax)
            # ax[0].hold, ax[1].hold, ax[2].hold = True, True, True

            self.printProgressBar(id,totalrows," Completed")

        # print(ITC_dataframe.dtypes)
        # print(type(selectedIds))
        # print(type(selectedIds[0]))
        selectedIds = list(set(selectedIds))
        print(ITC_dataframe.loc[selectedIds , : ])
        # print(ITC_dataframe[0,:])
        # print(ITC_dataframe(ITC_dataframe[id] == 1))
        # exit(0)
        # selectedIds = list(set(selectedIds)).astype(np.uint16)
        out_folder = os.path.join(self.base_path,
                        gc.PHENOLOGY_OUT_FOLDER)
        OtherUtils.TouchPath(out_folder)
        out_shape_path = os.path.join(out_folder, "TreeSpectralPhenology.shp")
        ITC_dataframe.loc[selectedIds , : ].to_file(driver = 'ESRI Shapefile', filename = out_shape_path)

        # ax[0].set_xlim([1, 3])
        # ax[0].set_ylim([-1, 2])
        # ax[0].set(xlabel='NDVI', ylabel='Month')

        # ax[1].set_xlim([1, 3])
        # ax[1].set_ylim([-1, 2])
        # ax[1].set(xlabel='PRI', ylabel='Month')

        # ax[2].set_xlim([1, 3])
        # ax[2].set_ylim([-1, 2])
        # ax[2].set(xlabel='CCI', ylabel='Month')
        # plt.show()

        # exit(0)
        ITC_dataframe = ITC_dataframe.loc[selectedIds , : ]
        ArrVal = np.array(['Date1','Date2','Date3','Date4','Date5','Date6'])
        l = len(ITC_dataframe.index)*6
        print(l)
        # exit(0)
        ii = np.repeat(ArrVal, len(ITC_dataframe.index))
        sns.set()
        dataarr = {
                'indextype'  : np.concatenate( ( np.repeat(1,l), np.repeat(2,l), np.repeat(3,l)), axis=0),
                'date' : np.concatenate( (ii, ii, ii), axis=0),
                'indexvalues': np.concatenate( (np.asarray(ITC_dataframe['NDVI']),np.asarray(ITC_dataframe['NDVI1']),np.asarray(ITC_dataframe['NDVI2']),np.asarray(ITC_dataframe['NDVI3']),np.asarray(ITC_dataframe['NDVI4']),np.asarray(ITC_dataframe['NDVI5']), np.asarray(ITC_dataframe['PRI']), np.asarray(ITC_dataframe['PRI1']), np.asarray(ITC_dataframe['PRI2']), np.asarray(ITC_dataframe['PRI3']), np.asarray(ITC_dataframe['PRI4']),np.asarray(ITC_dataframe['PRI5']), np.asarray(ITC_dataframe['CCI']), np.asarray(ITC_dataframe['CCI1']), np.asarray(ITC_dataframe['CCI2']), np.asarray(ITC_dataframe['CCI3']), np.asarray(ITC_dataframe['CCI4']),np.asarray(ITC_dataframe['CCI5'])), axis=0)
                }
        tm = pd.DataFrame(dataarr, columns = ['indextype','date', 'indexvalues'])
        sns.lineplot(x="date", y="indexvalues", hue="indextype", data=tm, palette=['red','green','blue'], ci=15, linewidth=2.5)
        # plt.ylim([0, 1])
        plt.show()


    def printProgressBar(self,i,max,postText):
        n_bar =10 #size of progress bar
        j= i/max
        sys.stdout.write('\r')
        sys.stdout.write(f"[{'=' * int(n_bar * j):{n_bar}s}] {int(100 * j)}%  {postText}")
        sys.stdout.flush()

    def ckdnearest(self, gdA, gdB, date_id):
        nA = np.array(list(zip(gdA.geometry.x, gdA.geometry.y)) )
        nB = np.array(list(zip(gdB.geometry.x, gdB.geometry.y)) )
        btree = cKDTree(nB)
        dist, idx = btree.query(nA, k=1)
        gdf_out = pd.concat(
            [gdB.loc[idx, gdB.columns != 'geometry'].reset_index(drop=True),
            gdA.reset_index(drop=True),
            pd.Series(dist, name='dist'+str(date_id))], axis=1)
        # print(len(gdf_out))
        # gdf_out.reindex(range(len(gdf_out)+1))
        return gdf_out

