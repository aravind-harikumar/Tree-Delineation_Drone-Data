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

img = ReadImage('Others/Images/demo.tif').read(1)
img = np.uint8(img)
img = HistogramEqualizeImage(img)
img = normalize(img)
img[np.isnan(img)] = 0

imgnew = np.float64(np.full((np.shape(img)[0],np.shape(img)[1],3),0))
imgnew[:,:,0] = img
imgnew[:,:,1] = img
imgnew[:,:,2] = img
imgnew[imgnew <= 0] = 0
img[np.isnan(img)] = 0
print(type(imgnew))
print(np.shape(imgnew))
print(imgnew.dtype)

imgnew= img_as_ubyte(imgnew)

gray = cv2.cvtColor(imgnew,cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray,100,255,cv2.THRESH_BINARY_INV)# cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU



# ####################

# readshp = ReadShpFile('/home/ensmingerlabgpu/Desktop/IOFiles/Output/ITC-Buffer/TreeBufferAll.shp')
opt = gpd.read_file('/home/ensmingerlabgpu/Desktop/IOFiles/Output/ITC-Buffer/TreeBufferAll.shp')
# print(opt.head())

def getXY(pt):
    return (pt.x, pt.y)

centroidseries = opt['geometry'].centroid
x,y = [list(t) for t in zip(*map(getXY, centroidseries))]
coordinates = np.array([x,y])

# get empty array
buckets = [[0 for col in range(np.shape(gray)[1])] for row in range(np.shape(gray)[0])]
buckets = np.array(buckets)
for i in range(np.shape(coordinates)[1]):
    buckets[int(coordinates[0][i]),int(coordinates[1][i])] = 1
    # print([int(coordinates[0][i]),int(coordinates[1][i])])


# # # noise removal
kernel0 = np.ones((40,40),np.uint8)
buckets70 = cv2.dilate(np.float64(buckets),kernel0,iterations=1)
buckets70[buckets70>0]=1
# buckets70 = img_as_ubyte(buckets70)

kernel1 = np.ones((30,30),np.uint8)
buckets50 = cv2.dilate(np.float64(buckets),kernel1,iterations=1)
buckets50[buckets50>0]=1
# buckets50 = img_as_ubyte(buckets50)

kernel2 = np.ones((10,10),np.uint8)
buckets25 = cv2.dilate(np.float64(buckets),kernel2,iterations=1)
buckets25[buckets25>0]=1
# buckets25 = img_as_ubyte(buckets25)

unknown5025 = cv2.subtract(buckets50,buckets25)

sureBGnd = [[1 for col in range(np.shape(gray)[1])] for row in range(np.shape(gray)[0])]
sureBGnd = np.array(sureBGnd)
sureBGnd[buckets70==1]=0
# sureBGnd = img_as_ubyte(sureBGnd)

syureFGND = buckets70
###################

# noise removal
kernel = np.ones((2,2),np.uint8)
#opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
closing = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel, iterations = 1)

# sure background area
sure_bg = cv2.dilate(closing,kernel,iterations=1)

# Finding sure foreground area
dist_transform = cv2.distanceTransform(sure_bg,cv2.DIST_L2,3)

# Threshold
ret, sure_fg = cv2.threshold(dist_transform,0.1*dist_transform.max(),255,0)

# Finding unknown region
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg,sure_fg)

# Marker labelling
ret, markers = cv2.connectedComponents(sure_fg)

# Add one to all labels so that sure background is not 0, but 1
markers = markers+1

# Now, mark the region of unknown with zero
markers[unknown==255] = 0
imgnew = np.uint8(imgnew)

print(np.shape(imgnew))
print(imgnew.dtype)
print(np.shape(markers))
print(markers.dtype)

markers = cv2.watershed(imgnew,markers)
imgnew[markers == -1] = [255,0,0]

plt.subplot(421),plt.imshow(img)
plt.title('Input Image'), plt.xticks([]), plt.yticks([])
plt.subplot(422),plt.imshow(unknown, 'gray')
plt.title("Otsu's binary threshold"), plt.xticks([]), plt.yticks([])

plt.subplot(423),plt.imshow(closing, 'gray')
plt.title("morphologyEx:Closing:2x2"), plt.xticks([]), plt.yticks([])
plt.subplot(424),plt.imshow(sure_bg, 'gray')
plt.title("Dilation"), plt.xticks([]), plt.yticks([])

plt.subplot(425),plt.imshow(dist_transform, 'gray')
plt.title("Distance Transform"), plt.xticks([]), plt.yticks([])
plt.subplot(426),plt.imshow(sure_fg, 'gray')
plt.title("Thresholding"), plt.xticks([]), plt.yticks([])

plt.subplot(427),plt.imshow(unknown, 'gray')
plt.title("Unknown"), plt.xticks([]), plt.yticks([])

plt.subplot(428),plt.imshow(imgnew, 'gray')
plt.title("Result from Watershed"), plt.xticks([]), plt.yticks([])

plt.tight_layout()
plt.show()