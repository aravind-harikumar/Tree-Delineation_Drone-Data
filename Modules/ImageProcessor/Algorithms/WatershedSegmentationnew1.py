import sys,os,math
import numpy as np
from PIL import Image
import cv2
from matplotlib import pyplot as plt
from skimage import data
from skimage.util import img_as_ubyte, img_as_float, img_as_uint
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ImageProcessor.RasterOperators import ReadImage, HistogramEqualizeImage, normalize
from ImageProcessor.VectorOperators import ReadShpFile
import geopandas as gpd

def getXY(pt):
    return (pt.x, pt.y)

# read image
img = ReadImage('Others/Images/demo.tif').read(1)
img = np.uint8(img)
img = HistogramEqualizeImage(img)
img = normalize(img)
img[np.isnan(img)] = 0

# stack image in an array
imgnew = np.float64(np.full((np.shape(img)[0],np.shape(img)[1],3),0))
imgnew[:,:,0] = img
imgnew[:,:,1] = img
imgnew[:,:,2] = img
imgnew[imgnew <= 0] = 0
img[np.isnan(img)] = 0
imgnew= img_as_ubyte(imgnew)

# get grey image from color
gray = cv2.cvtColor(imgnew,cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray,100,255,cv2.THRESH_BINARY_INV)# cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU

# Read Tree top markers
opt = gpd.read_file('/home/ensmingerlabgpu/Desktop/IOFiles/Output/ITC-Buffer/TreeBufferAll.shp')
centroidseries = opt['geometry'].centroid
x,y = [list(t) for t in zip(*map(getXY, centroidseries))]
coordinates = np.array([x,y])

# get empty array
buckets = [[0 for col in range(np.shape(gray)[1])] for row in range(np.shape(gray)[0])]
buckets = np.array(buckets)
for i in range(np.shape(coordinates)[1]):
    buckets[int(coordinates[0][i]),int(coordinates[1][i])] = 1
    # print([int(coordinates[0][i]),int(coordinates[1][i])])

# create buffer, Select foreground and background
kernel0 = np.ones((5,5),np.uint8)
buckets70 = cv2.dilate(np.float64(buckets),kernel0,iterations=15)
buckets70[buckets70>0]=1

sureBGnd = np.float64(np.full((np.shape(gray)[0],np.shape(gray)[1]),1))
sureBGnd = np.array(sureBGnd)

syureFGND = buckets70
sureBGnd[buckets70==1]=0

# # Finding sure foreground area
dist_transform = cv2.distanceTransform(np.uint8(sureBGnd),cv2.DIST_L2,3)

# # Threshold
ret, sure_fg = cv2.threshold(dist_transform,0.1*dist_transform.max(),255,0)

# # Finding unknown region
unknown = cv2.subtract(np.uint8(sureBGnd),np.uint8(sure_fg))

# Marker labelling
ret, markers = cv2.connectedComponents(np.uint8(sure_fg))

# Add one to all labels so that sure background is not 0, but 1
markers = markers+1

# Now, mark the region of unknown with zero
markers[unknown==1] = 0
imgnew = np.uint8(imgnew)

markers = cv2.watershed(imgnew,markers)
imgnew[markers == -1] = [255,0,0]

# Plot Images, and link x and y axis
f, ax1 = plt.subplots(2, 2, sharey=True, sharex=True)
ax1[0, 0].imshow(img)
ax1[0, 0].set_title('Input Image')

ax1[1, 0].imshow(dist_transform, 'gray')
ax1[1, 0].set_title("Otsu's binary threshold") #plt.xticks([]), plt.yticks([])

ax1[0, 1].imshow(unknown, 'gray')
ax1[0, 1].set_title('Diff image')

ax1[1, 1].imshow(imgnew, 'gray')
ax1[1, 1].set_title('Watershed')

plt.tight_layout()
plt.show()