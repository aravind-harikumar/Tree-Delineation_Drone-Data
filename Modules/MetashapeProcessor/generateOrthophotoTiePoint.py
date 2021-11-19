"""
.. module:: MetashapeProcessor
    :platform: Unix, Windows
    :synopsis: A module for generating orthorectified remote sensing images
    
..  :author:: Aravind Harikumar <aravindhari1@gmail.com>
"""

import Metashape
import os, sys, math, datetime, time, random
import numpy as np
import pandas as pnd
Metashape.app.gpu_mask = 1

class MetaShapeProcessingForTie:
    ''' Class for generating orthorectified remote sensing images.
    
    Args: \n 
        DataPath: full path of the input image files.
        SavePath: full path to sace the outputs.
    '''

    # class variables
    DataPath = SavePath = "" 

    # initialize paths
    def __init__(self,DataInfo):
        ''' initialize variables '''
        self.ID = DataInfo['ID']
        self.doc = Metashape.Document()
        self.chunk = self.doc.addChunk()
        self.DataPathList = DataInfo['DataPathList']
        self.WorkingFolder = DataInfo['WorkingFolder']

        if not(os.path.exists(self.DataPath)):
            raise ValueError("No such source file path exists!")
        

    def __LoadImagesFromList(self):
        print("*** Started...Loading Photos *** ", datetime.datetime.utcnow())
        photo_list = list()
        # for chunk in list(self.doc.chunks):
        #     if len(chunk.cameras):
        #         self.doc.remove(chunk)
        for files in self.DataPathList:
            for file in files:
                if file.rsplit(".",1)[1].lower() in  ["tif", "tiff"]:
                    print(os.path.join(root, file))
                    photo_list.append(os.path.join(root, file))
        self.chunk.addPhotos(photo_list)

        print("*** Finished - Loading Photos ***")


    def __EstimateCameraParameters(self):
        print("*** Started...Align Photos *** ", datetime.datetime.utcnow())
        
        self.__CalibrateReflectance()
        print('Images reflectance calibrated!')

        # # aligned cameras
        for frame in self.chunk.frames:
            frame.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, reference_preselection=True, keypoint_limit=40000, tiepoint_limit=4000)
        task = Metashape.Tasks.AlignCameras()
        task.adaptive_fitting = True
        task.reset_alignment = True
        task.apply(self.chunk)
        Metashape.app.update()
        print('Images aligned!')

        error_list,rmseErrorArr, realign_list = self.__getCameraAlignmentStatus()
        print(error_list.shape) # error_stats = error_list.describe()

        self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])
        self.doc.open(self.WorkingFolder+self.ID+'.psx')
        self.chunk = self.doc.chunk

        Metashape.app.update()

        # set crs
        self.chunk.crs = Metashape.CoordinateSystem("EPSG::4326")

        print("*** Finished - Align Photos ***")

    def GenerateOrthoImage(self):
        ''' create orthorectified image '''
        
        # self.doc.open(self.WorkingFolder+self.ID+'.psx')
        # self.chunk = self.doc.chunk

        # load input images
        self.__LoadImagesFromFolder()
        self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])
        # self.__SetRegionCenterSpan()
        
        # set primary channel to red edge
        self.chunk.primary_channel = 4

        # estimate camerea parameters
        self.__EstimateCameraParameters()
        self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])

def TestModuleLevelFuntion():
    print('here!')
