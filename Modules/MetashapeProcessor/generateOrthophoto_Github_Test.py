"""
    Module:: MetashapeProcessor
    Platform: Unix, Windows
    Synopsis: A module for generating Orthomosiaic from UAV remote sensing images
    Requirement: Agisoft Professional Software    
    Author:: Aravind Harikumar <aravindhari1@gmail.com>
"""

import os, sys
import math, random
import datetime, time
import numpy as np
import pandas as pnd
import Metashape
Metashape.app.gpu_mask = 1 # Default On

def GenerateOrthoImage():
    """ Genereate Orthomosaic \n """   
    
    DataInfo = {
    'ID'                 : '20170815_CSI_4M', # User Defined Project Name
    'DataPath'           : '/media/ensmingerlabgpu/Seagate Backup Plus Drive/UAV/OntarioGenomics/FM/20170624/', # Root Data Folder
    'OutFolder'          : '/media/ensmingerlabgpu/Seagate/2018/', # Output Folder
    'LoadContolPointFile': False, # Load Control Points (True/False)
    'ContolPointFile'    : '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/GPS/only_targets/SCA_GPS_final_edit_petra.csv', # used if LoadContolPointFile == True
    'OpenExistingProj'   : False, # required to run from an intermediate step mentioned below (True/False)
    'Primary_Channel'    : 4, # Primary Channel
    'EPSGcrs'            : 'EPSG::4326', # Reference System EPSG
    }

    msp= MetaShapeProcessing(DataInfo).GetInstance()    
    # load input images
    msp.LoadImagesFromFolder()
    # estimate camerea parameters
    msp.EstimateCameraParameters()
    #  build dense point cloud
    msp.BuildDensePointCloud()
    #  build DEM and DSM
    msp.BuildElevationModel()
    #  build mesh model
    msp.BuildMeshModel()
    #  build texture map
    msp.BuildTexture()
    # create orthorectified image
    msp.BuildOrthoImage()

class MetaShapeProcessing():
    
    # class variables
    DataPath = SavePath = "" 

    # initialize paths
    def __init__(self,DataInfo):
        """ Class Constructor   
        
        Keyword Arguments: \n 
            DataPath: -- full path of the input image files.
            SavePath: -- full path to sace the outputs.
        """
        
        # initialize variables '''
        self.ID = DataInfo['ID']
        self.doc = Metashape.Document()
        self.chunk = self.doc.addChunk()
        self.DataPath = DataInfo['DataPath']
        self.ContolPointFile = DataInfo['ContolPointFile']
        self.LoadContolPointFile = DataInfo['LoadContolPointFile']
        self.WorkingFolder = DataInfo['OutFolder']
        self.OpenExistingProj = DataInfo['OpenExistingProj']
        self.primary_channel = DataInfo['Primary_Channel']
        self.crs = Metashape.CoordinateSystem(DataInfo['EPSGcrs'])
        self.IsNewProjectFile = True

        if not(os.path.exists(self.DataPath)):
            raise ValueError("No such source file path exists!")
        
        # Checl validity of output directory
        if not os.path.exists(os.path.join(self.WorkingFolder,self.ID)):
            # print("Input file does not exist at the dest, and hence creating one!")
            os.makedirs(os.path.join(self.WorkingFolder,self.ID))

    def LoadImagesFromFolder(self):
        """ load the optical images with high overlap and sidelap \n 
        
        Keyword Arguments: \n 
            self: -- this object
        """

        if(self.OpenExistingProj):
            self.doc.open(self.WorkingFolder+self.ID+'.psx')
            self.chunk = self.doc.chunk
        else:
            print("*** Started...Loading Photos *** ", datetime.datetime.utcnow())
            photo_list = list()
            for root, folders, files in os.walk(self.DataPath):
                for file in files:
                    if file.rsplit(".",1)[1].lower() in  ["tif", "tiff"]:
                        print(os.path.join(root, file))
                        photo_list.append(os.path.join(root, file))
            self.chunk.addPhotos(photo_list,Metashape.MultiplaneLayout)

            if(self.LoadContolPointFile):
                self.loadcontrolpoints()
            print("*** Finished - Loading Photos ***")
            # set primary channel to red edge
            self.chunk.primary_channel = self.primary_channel
            # Save
            self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])  

    def CalibrateReflectance(self):
        """ Calibrate the reflectance using the Reference Reflectance for the white panel used \n 
        
        Keyword Arguments: \n 
            self: -- this object
        """

        print("*** Started - Reflectance Calibration *** ", datetime.datetime.utcnow())  
        self.chunk.locateReflectancePanels()        
        for sensor in self.chunk.sensors:
            sensor.normalize_sensitivity = True
        Metashape.app.update()
        albedo = {"Center528": "0.63560", "Center 570": "0.64370", "Center645": "0.64750", "Center680": "0.62280", "Center900": "0.64420"} #values read from the file
        for camera in self.chunk.cameras:
            # if camera.group.label != "Calibration images":
                # continue
            for plane in camera.planes:
                plane.meta["ReflectancePanel/Calibration"] = albedo[plane.sensor.bands[0]]  
        task = Metashape.Tasks.CalibrateReflectance()
        task.use_reflectance_panels = True
        task.use_sun_sensor = False
        task.apply(self.chunk)
        print("*** Finished - Reflectance Calibration *** ", datetime.datetime.utcnow())  

    def EstimateCameraParameters(self):
        """ Estimate the camera parameters \n 
        
        Keyword Arguments: \n 
            self: -- this object
        """

        print("*** Started - Aligning Photos *** ", datetime.datetime.utcnow())        
        self.CalibrateReflectance()
        # print('Images reflectance calibrated!')
        # self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])

        # # aligned cameras
        for frame in self.chunk.frames:
            frame.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, reference_preselection=True, keypoint_limit=40000, tiepoint_limit=4000)
        task = Metashape.Tasks.AlignCameras()
        task.adaptive_fitting = True
        task.reset_alignment = True
        task.apply(self.chunk)
        Metashape.app.update()
        print('Images aligned!')

        error_list,rmseErrorArr, realign_list = self.getCameraAlignmentStatus()
        print(error_list.shape) # error_stats = error_list.describe()

        self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])
        self.doc.open(self.WorkingFolder+self.ID+'.psx')
        self.chunk = self.doc.chunk

        # select cameras with error more than threshold (e.g., median of values)
        error_list_new0 = error_list[error_list['Err'] > 20]
        error_list_new1 = error_list[(error_list['Err'] > 20) & (error_list['Err'] < 60)]
        error_list_new2 = error_list[error_list['Err'] >= 60]

        # print(list(error_list_new['label']))
        count = 0
        for camera in self.chunk.cameras:
            # print(camera.label)
            if camera.label in list(error_list_new0['label']):
                print(camera.label)
                count +=1
                camera.transform = None
        print("Resetting " + str(count) + " cameras..." )

        # ALIGN FIRST TIME
        print("*** Started...realigning first set of unaligned photos *** ", datetime.datetime.utcnow())
        count = 0
        realign_list = list()
        for camera in self.chunk.cameras:
            if camera.transform == None and camera.label in list(error_list_new1['label']):
                realign_list.append(camera)
                count +=1
        print(str(count) + "Some cameras are not aligned, and thus realigning..." )
        self.chunk.alignCameras(cameras = realign_list)
        Metashape.app.update()

        # ALIGN SECOND TIME
        print("*** Started...realigning second set of unaligned photos *** ", datetime.datetime.utcnow())
        count = 0
        realign_list = list()
        for camera in self.chunk.cameras:
            if camera.transform == None and camera.label in list(error_list_new2['label']):
                realign_list.append(camera)
                count +=1
        print(str(count) + "Some cameras are not aligned, and thus realigning..." )
        self.chunk.alignCameras(cameras = realign_list)
        Metashape.app.update()

        self.chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=False, fit_b2=False, 
                          fit_k1=True, fit_k2=True, fit_k3=True, fit_k4=False, 
                          fit_p1=True, fit_p2=True, fit_p3=False, fit_p4=False, 
                          adaptive_fitting=False, tiepoint_covariance=False)

        self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])

        self.ReduceError_RU(self.chunk)
        self.ReduceError_PA(self.chunk)
        self.ReduceError_RE(self.chunk)

        Metashape.app.update()

        # set crs
        self.chunk.crs = self.crs
        Metashape.app.update()

        print("*** Finished - Aligning Photos ***")

        self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])

    def getCameraAlignmentStatus(self):
        """ Estiamte Camera Alignment Errors \n 
        
        Keyword Arguments: \n 
            self: -- this object
        """

        realign_list = list()
        error_list = pnd.DataFrame([],columns = ["label", "Err", "ErrX", "ErrY", "ErrZ"])
        total_error = Metashape.Vector([0,0,0])
        n = 0        
        for camera in self.chunk.cameras:
            if camera.transform:
                if camera.reference.location is not None:
                    estimated_geoc = self.chunk.transform.matrix.mulp(camera.center)
                    reference_geoc = self.chunk.crs.unproject(camera.reference.location)
                    error = Metashape.Vector(estimated_geoc-reference_geoc)
                    m = self.chunk.crs.localframe(self.chunk.transform.matrix.mulp(Metashape.Vector(camera.center)))
                    error = m.mulv(error)

                    to_append = [camera.label, error.norm(), error.x, error.y, error.z]
                    a_series = pnd.Series(to_append, index = error_list.columns)
                    error_list = error_list.append(a_series, ignore_index=True)

                    total_error += Metashape.Vector([error.x ** 2, error.y **2, error.z **2])
                    n += 1
            else:
                realign_list.append(camera)

        rmseErrorArr = list()
        for i in range(len(total_error)): #printing total X, Y, Z errors
            rmseErrorArr.append(math.sqrt(total_error[i] / n))

        return error_list, rmseErrorArr, realign_list

    def BuildElevationModel(self):
        """ Build Digital Surface Model from Point Cloud / 3D Mesh \n 
        
        Keyword Arguments: \n 
            self: -- this object
        """
        self.doc.open(self.WorkingFolder+self.ID+'.psx')
        self.chunk = self.doc.chunk

        # Classify ground points
        print("*** Point Classification - Started *** ", datetime.datetime.utcnow())
        self.chunk.dense_cloud.classifyGroundPoints(max_angle=15.0, max_distance=1.0, cell_size=50.0, source = Metashape.PointClass.Created)
        print("*** Point Classification - Finished *** ", datetime.datetime.utcnow())
        Metashape.app.update()

        # Generate DEM
        print("*** Build DEM - Started *** ", datetime.datetime.utcnow())
        self.BuildDEM('DEM')
        print("*** Build DEM - Finished *** ", datetime.datetime.utcnow())
        self.chunk.exportDem(os.path.join(self.WorkingFolder,self.ID,"DEM.tif"), nodata=-32767, write_kml=False, write_world=True)
        Metashape.app.update()

        # Generate DSM
        print("*** Build DSM - Started *** ", datetime.datetime.utcnow())
        self.BuildDEM('DSM')
        print("*** Build DSM - Finished *** ", datetime.datetime.utcnow())
        self.chunk.exportDem(os.path.join(self.WorkingFolder,self.ID,"DSM.tif"), nodata=-32767, write_kml=False, write_world=True)
        Metashape.app.update()

        self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])


    def BuildDensePointCloud(self):
        """ Build Dense Point Cloud / 3D Mesh \n 
        
        Keyword Arguments: \n 
            self: -- this object
        """

        # Generate depth maps
        print("*** Build Depth Map - Started ***", datetime.datetime.utcnow())
        self.chunk.buildDepthMaps(quality=Metashape.MediumQuality, filter=Metashape.AggressiveFiltering)
        print("*** Finished - Build Depth Map *** ", datetime.datetime.utcnow())
        Metashape.app.update()
        
        # Generate dense point cloud from estimated internal and external parameters
        print("*** Build Dense Cloud - Started ***", datetime.datetime.utcnow())
        self.chunk.buildDenseCloud(point_colors = True)
        print("*** Finished - Build Dense Cloud *** ", datetime.datetime.utcnow())
        Metashape.app.update()

        self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])

    def BuildDEM(self, ModelType):
        """ Build Digital Elevation Model \n
        
        Keyword Arguments: \n 
            self:       -- this object
            ModelType:  -- Model type (E.g., DEM or DSM)
        """

        print("*** Build DEM/DSM - Started *** ", datetime.datetime.utcnow())
        if ModelType == 'DEM':
            self.chunk.buildDem(source=Metashape.DenseCloudData, classes=[Metashape.PointClass.Ground])
        else: # i.e., If DSM
            self.chunk.buildDem(source=Metashape.DenseCloudData, classes=[Metashape.PointClass.Created])
        print("*** Build DEM/DSM - Finished *** ", datetime.datetime.utcnow())
        Metashape.app.update()

    def BuildMeshModel(self):
        """ Build Digital 3D Mesh Model \n
        
        Keyword Arguments: \n 
            self:       -- this object
        """

        print("*** Build Mesh - Started *** ", datetime.datetime.utcnow())
        if not self.chunk.model:
            self.chunk.buildModel(surface=Metashape.HeightField, interpolation=Metashape.EnabledInterpolation, face_count=Metashape.MediumFaceCount, source=Metashape.DenseCloudData)
        else:
            print( "Model already exists" )
        Metashape.app.update()
        print("*** Build Mesh - Finished *** ", datetime.datetime.utcnow())

        self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])
    
    def BuildTexture(self):
        """ Build Texture Model \n
        
        Keyword Arguments: \n 
            self:       -- this object
        """

        print("*** Build Texture - Started *** ", datetime.datetime.utcnow())
        self.chunk.buildUV(mapping = Metashape.GenericMapping, count = 1)
        self.chunk.buildTexture(blending = Metashape.MosaicBlending, size = 4096)
        Metashape.app.update()
        print("*** Build Texture - Finished *** ", datetime.datetime.utcnow())

    def BuildOrthoImage(self):
        """ Build Single OrthoMosaic Image From Individual Othophotos \n
        
        Keyword Arguments: \n 
            self:       -- this object
        """

        print("*** Build OrthoMosaic - Started *** ", datetime.datetime.utcnow())
        # self.chunk.buildOrthomosaic(surface=Metashape.DataSource.ModelData,blending=Metashape.BlendingMode.MosaicBlending,fill_holes=True)
        self.chunk.buildOrthomosaic(surface=Metashape.DataSource.ElevationData,blending=Metashape.BlendingMode.MosaicBlending,fill_holes=True)
        Metashape.app.update()
        print("*** Build OrthoMosaic - Finished *** ", datetime.datetime.utcnow())
        # export orthorectified image
        print("*** Exporting OrthoMosaic - Started *** ", datetime.datetime.utcnow())
        self.chunk.exportOrthomosaic(os.path.join(self.WorkingFolder, self.ID , self.ID + '.tif'))
        print("*** Exportingl OrthoMosaic - Finished *** ", datetime.datetime.utcnow())

        self.doc.save(path = os.path.join(self.WorkingFolder+self.ID+'.psx'), chunks = [self.doc.chunk])

    def GetResolution(self,chunk):
        """ Get resolution of the Digital Surface Model derived from the Point Cloud \n
        
        Keyword Arguments: \n 
            self:       -- this object
            chunk:      -- Metashape chunk object
        """

        DEM_resolution = float(chunk.dense_cloud.meta['dense_cloud/resolution']) * chunk.transform.scale
        Image_resolution = DEM_resolution / int(chunk.dense_cloud.meta['dense_cloud/depth_downscale'])
        return DEM_resolution, Image_resolution

    def ReduceError_RU(self,chunk, init_threshold=10):
        """ Reduce RU Error \n
        
        Keyword Arguments: \n 
            self:            -- this object
            chunk:           -- Metashape chunk object
            init_threshold:  -- Error threshold
        """

        print('Entered RU')
        # This is used to reduce error based on reconstruction uncertainty
        tie_points = chunk.point_cloud
        fltr = Metashape.PointCloud.Filter()
        fltr.init(chunk, Metashape.PointCloud.Filter.ReconstructionUncertainty)
        threshold = init_threshold
        loopcnt = 0
        while fltr.max_value > 10 or loopcnt<5:
            fltr.selectPoints(threshold)
            nselected = len([p for p in tie_points.points if p.selected])
            if nselected >= len(tie_points.points) / 2 and threshold <= 50:
                fltr.resetSelection()
                threshold += 1
                continue
            self.UnselectPointMatch(chunk)
            nselected = len([p for p in tie_points.points if p.selected])
            if nselected == 0:
                break
            print('Delete {} tie point(s)'.format(nselected))
            tie_points.removeSelectedPoints()
            chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=False, fit_b2=False, 
                                fit_k1=True, fit_k2=True, fit_k3=True, fit_k4=False, 
                                fit_p1=True, fit_p2=True, fit_p3=False, fit_p4=False, 
                                adaptive_fitting=False, tiepoint_covariance=False)
            fltr.init(chunk, Metashape.PointCloud.Filter.ReconstructionUncertainty)
            threshold = init_threshold
            loopcnt = loopcnt+1
            print('left RU')            
            
    def ReduceError_PA(self,chunk, init_threshold=2.0):
        """ Reduce PA error \n
        
        Keyword Arguments: \n 
            self:            -- this object
            chunk:           -- Metashape chunk object
            init_threshold:  -- Error threshold
        """

        # This is used to reduce error based on projection accuracy
        tie_points = chunk.point_cloud
        fltr = Metashape.PointCloud.Filter()
        fltr.init(chunk, Metashape.PointCloud.Filter.ProjectionAccuracy)
        threshold = init_threshold
        loopcnt = 0
        while fltr.max_value > 2 or loopcnt<5:
            fltr.selectPoints(threshold)
            nselected = len([p for p in tie_points.points if p.selected])
            if nselected >= len(tie_points.points) / 2 and threshold <= 3.0:
                fltr.resetSelection()
                threshold += 0.1
                continue
            self.UnselectPointMatch(chunk)
            nselected = len([p for p in tie_points.points if p.selected])
            if nselected == 0:
                break
            print('Delete {} tie point(s)'.format(nselected))
            tie_points.removeSelectedPoints()
            chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=False, fit_b2=False, 
                                fit_k1=True, fit_k2=True, fit_k3=True, fit_k4=False, 
                                fit_p1=True, fit_p2=True, fit_p3=False, fit_p4=False, 
                                adaptive_fitting=False, tiepoint_covariance=False)
            fltr.init(chunk, Metashape.PointCloud.Filter.ProjectionAccuracy)
            threshold = init_threshold
        # This is to tighten tie point accuracy value
        chunk.tiepoint_accuracy = 0.1
        chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=True, fit_b2=True, 
                            fit_k1=True, fit_k2=True, fit_k3=True, fit_k4=True, 
                            fit_p1=True, fit_p2=True, fit_p3=True, fit_p4=True, 
                            adaptive_fitting=False, tiepoint_covariance=False)
        loopcnt = loopcnt+1
        
    def ReduceError_RE(self, chunk, init_threshold=0.3):
        """ Reduce RE error \n
        
        Keyword Arguments: \n 
            self:            -- this object
            chunk:           -- Metashape chunk object
            init_threshold:  -- Error threshold
        """

        # This is used to reduce error based on repeojection error
        print('Enteresssd RU')
        tie_points = chunk.point_cloud
        fltr = Metashape.PointCloud.Filter()
        fltr.init(chunk, Metashape.PointCloud.Filter.ReprojectionError)
        threshold = init_threshold
        loopcnt = 0.0
        while fltr.max_value > 0.3 or loopcnt<5.0:
            fltr.selectPoints(threshold)
            nselected = len([p for p in tie_points.points if p.selected])
            if nselected >= len(tie_points.points) / 10:
                fltr.resetSelection()
                threshold += 0.01
                continue

            self.UnselectPointMatch(chunk)
            nselected = len([p for p in tie_points.points if p.selected])
            if nselected == 0:
                break
            print('Delete {} tie point(s)'.format(nselected))
            tie_points.removeSelectedPoints()
            chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=True, fit_b2=True, 
                                fit_k1=True, fit_k2=True, fit_k3=True, fit_k4=True, 
                                fit_p1=True, fit_p2=True, fit_p3=True, fit_p4=True, 
                                adaptive_fitting=False, tiepoint_covariance=False)
            fltr.init(chunk, Metashape.PointCloud.Filter.ReprojectionError)
            threshold = init_threshold
            loopcnt = loopcnt+1.0

    def UnselectPointMatch(self, chunk, *band):
        """ Unselect points which have less than a few projections \n
        
        Keyword Arguments: \n 
            self:   -- this object
            chunk:  -- Metashape chunk object
            band:   -- image band
        """

        print('UnselectPointMatch RU')
        point_cloud = chunk.point_cloud
        points = point_cloud.points
        point_proj = point_cloud.projections
        npoints = len(points)

        mx = []
        for j in range(0,len(points)):
            mx.append(points[j].track_id)

        n_proj = dict()
        point_ids = [-1] * (max(np.asarray(mx))+10000)

        for point_id in range(0, len(points)):
            # print('a '+ str(points[point_id].track_id) + ' b ' + str(point_id))
            point_ids[points[point_id].track_id] = point_id

        # Find the point ID using projections' track ID
        for camera in chunk.cameras:
            if camera.type != Metashape.Camera.Type.Regular:
                continue
            if not camera.transform:
                continue

            for proj in point_proj[camera]:
                track_id = proj.track_id
              
                point_id = point_ids[track_id]
                
                if point_id < 0:
                    continue
                if not points[point_id].valid:
                    continue

                if point_id in n_proj.keys():
                    n_proj[point_id] += 1
                else:
                    n_proj[point_id] = 1

        # Unselect points which have less than three projections
        for i in n_proj.keys():
            if n_proj[i] < 3:
                points[i].selected = False

    def SetRegionCenterSpan(self):
        """ Automatically Center the Generated Point Cloud \n
        
        Keyword Arguments: \n 
            self:   -- this object
        """

        # T = self.chunk.transform.matrix

        # m = Metashape.Vector([38.01446082806382, -91.60752564932997, 5.844116179961301])
        # M = -m

        # for point in self.chunk.point_cloud.points:
        #     if not point.valid:
        #         continue
        #     coord = T * point.coord	
        #     for i in range(3):
        #         m[i] = min(m[i], coord[i])
        #         M[i] = max(M[i], coord[i])
                
        # center = (M + m) / 2
        # size = M - m
        # self.chunk.region.center = T.inv().mulp(center)
        # self.chunk.region.size = Metashape.Vector([259.37428160632777, 64.57857111102506, 20.92779889759])

        # self.chunk.region.rot = T.rotation().t()

        # self.chunk.region = self.region

        # print(self.chunk.region.center)
        # print(self.chunk.region.size)
        # print(self.chunk.transform.scale)
        # print(self.chunk.transform.matrix)

        # Vector([-28.194055204994278, 32.41988422410615, -17.130805898770404])
        # Vector([260.5789802869161, 104.49209254582723, 43.077346070607504])
        # 3.0762907297400326
        # Matrix([[-1.7372489077070628, 2.5201031598230115, 0.30758893088853906, 1345876.058867097],
        #        [-2.1667449813549227, -1.2774889482992307, -1.7711021502530684, -4170286.143397967],
        #        [-1.323157992202115, -1.2168264891544152, 2.496427622994159, 4619055.680846961],
        #        [0.0, 0.0, 0.0, 1.0]])


        # selected = [camera for camera in self.chunk.cameras if camera.transform and (camera.type == Metashape.Camera.Type.Regular)]
        # camera = selected[0]
        # R = Metashape.Matrix().Rotation(camera.transform.rotation()*Metashape.Matrix().Diag([1,-1,1]))
        # print(R)

        # origin = (-1) * camera.center
        # T = self.chunk.transform.matrix
        # R = Metashape.Matrix().Rotation(camera.transform.rotation()*Metashape.Matrix().Diag([1,-1,1]))
        # origin = R.inv().mulp(origin)
        # self.chunk.transform.matrix = T.scale() * Metashape.Matrix().Translation(origin) * R.inv()
        # print(self.chunk.transform.matrix)

        # new_center = Metashape.Vector([38.01446082806382, -91.60752564932997, 5.844116179961301]) #coordinates in the chunk coordinate system
        # new_size = Metashape.Vector([259.37428160632777, 64.57857111102506, 20.92779889759]) #size in the coordinate system units
        # new_matrix = Metashape.Matrix([[1.7227973892230573, -1.6794759959197902, 0.9578887250831064, 1345780.02168169],[1.7062748862476786, 0.7172852203718213, -1.8111734317901507, -4170233.249367702],[0.9092944754437803, 1.8360510795158362, 1.5837680591431438, 4619133.168862987],[0.0, 0.0, 0.0, 1.0]])
        # new_scale = 2.589637286344536

        # self.chunk.transform.matrix = new_matrix
        # self.chunk.transform.scale = new_scale
        # self.chunk.region.center = new_center
        # self.chunk.region.size = new_size

        # crs = self.chunk.crs

        # region = self.chunk.region
        # # region.center = T.inv().mulp(crs.unproject(new_center))
        # region.size = new_size / S
        # self.chunk.region = region
        
    def loadcontrolpoints(self):
        """ Load Control Points Required for Fine Georeferencing \n
        
        Keyword Arguments: \n 
            self:   -- this object
        """

        if(len(self.chunk.markers))>0:
            print('Markers already added!')
        else:
            pdorig = pnd.read_csv(os.path.join(self.ContolPointFile))
            for index, row in pdorig.iterrows():
                photos_total = len(self.chunk.cameras)		#number of photos in chunk
                markers_total = len(self.chunk.markers)		#number of markers in chunk                
                marker_name = row['IDENT'] 		            #marker label
                cx = float(row['X_coord'])			        #world x- coordinate of the current marker
                cy = float(row['Y_coord'])			        #world y- coordinate of the current marker
                cz = float(row['Z_coord'])			        #world z- coordinate of the current marker
                marker = self.chunk.addMarker()
                marker.label = marker_name
                marker.reference.location = Metashape.Vector([cx, cy, cz])
            print("Imported ground control points!")  #information message

    def GetInstance(self):
        return self

# if __name__ == "__GenerateOrthoImage__":
GenerateOrthoImage()