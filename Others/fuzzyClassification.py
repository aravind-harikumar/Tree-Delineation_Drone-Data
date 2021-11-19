from ImageProcessor.Algorithms import FuzzyCMeans
from fcmeans import FCM
from sklearn.datasets import make_blobs
from skimage import img_as_uint
from matplotlib import pyplot as plt
from seaborn import scatterplot as scatter
from ImageProcessor import RasterOperators
import numpy as np
import rasterio
import matplotlib.pyplot as plt


class FCMClassify:

    def __init__(self, inpath, outpath):
        self.inpath = inpath
        self.outpath = outpath
        self.imagebands = []
        self.dw = 0
        self.dh = 0
        self.bandcnt = 0

    def readata(self):
        #  read image
        
        # inpath = self.inpath
        # outpath = self.outpath
        # inpath = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/ProcessedMSData/20181015/CoregisteredSlices/20181015.tif'
        # outpath = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/ProcessedMSData/20181015/CoregisteredSlices/20181015_test_out.tif'
        # imagebands = RasterOperators.ReadImage(inpath)

        with rasterio.open(self.inpath) as src0:
            dw = src0.width
            dh = src0.height
            bandcnt= src0.count
            print(src0.width)
            print(src0.height)
            # Read each layer and write it to stack
            for i in range(1,src0.count+1):
                print(type(src0.read(i)))
                self.imagebands.append(src0.read(i).flatten())
        imagebands = np.array(imagebands).T
        print(np.shape(imagebands))

        self.dw,  self.dh,  self.bandcnt = src0.width, src0.height, src0.count

    def fcmclassify(self):
        # n_bins = 3  # use 3 bins for calibration_curve as we have 3 clusters here
        centers = [(2345, 2325, 2109, 1346, 16440), 
                    (203, 227, 352, 423, 4134), 
                    (1117, 1398, 1024, 709, 9345)]

        # X = imagebands #.astype('uint8')
        # fit the fuzzy-c-means
        fcm = FCM(n_clusters=3)
        fcm.fit(self.imagebands)

        # outputs
        fcm_centers = fcm.centers
        fcm_labels  = fcm.u.argmax(axis=1)

        fcm_labels = fcm_labels.reshape((self.dh, self.dw))

        # Read metadata of first file
        with rasterio.open(self.inpath) as src0:
            meta = src0.meta
            meta.update(count = 1)
            # Read each layer and write it to stack
            with rasterio.open(self.outpath, 'w', **meta) as dst:
                for i in range(1,2):
                    dst.write_band(i, img_as_uint(fcm_labels))

        # print('Done classification!')

        # f, axes = plt.subplots(1, 4, figsize=(11,5))
        # # plt.figure()
        # axes[0].imshow(fcm_labels==0)
        # axes[1].imshow(fcm_labels==1)
        # axes[2].imshow(fcm_labels==2)
        # axes[3].imshow(fcm_labels)

        # plt.show()
        # exit(0)
        # print(fcm_labels)

        # plot result
        # %matplotlib inline
        # f, axes = plt.subplots(1, 2, figsize=(11,5))
        # scatter(X[:,0], X[:,1], ax=axes[0])
        # scatter(X[:,0], X[:,1], ax=axes[1], hue=fcm_labels)
        # scatter(fcm_centers[:,0], fcm_centers[:,1], ax=axes[1],marker="s",s=200)
        # plt.show()