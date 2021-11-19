import sys,os
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

# aimg = cv2.imread('Others/Images/coins.png')

# print(type(aimg))
# print(aimg.dtype)

img = np.float64(np.uint8(ReadImage('Others/Images/demo.tif').read(1)))
print(type(img))
print(img.dtype)
# def circ(r, x, y):
#     return (x)**2 + (y)**2 <= r**2

# img = img_as_float(img)
print(type(img))
print(np.shape(img))
gray = img
gray[gray <= 0] = 0
gray = HistogramEqualizeImage(gray)
gray = normalize(gray)
# gray= img_as_ubyte(gray)
print(np.shape(gray))
# print(np.max(gray))

# ####################

# readshp = ReadShpFile('/home/ensmingerlabgpu/Desktop/IOFiles/Output/ITC-Buffer/TreeBufferAll.shp')
opt = gpd.read_file('/home/ensmingerlabgpu/Desktop/IOFiles/Output/ITC-Buffer/TreeBufferAll.shp')
# print(opt.head())

def getXY(pt):
    return (pt.x, pt.y)

centroidseries = opt['geometry'].centroid
x,y = [list(t) for t in zip(*map(getXY, centroidseries))]
coordinates = np.array([x,y])
# print(np.transpose(coordinates))

# get empty array
buckets = [[0 for col in range(np.shape(gray)[1])] for row in range(np.shape(gray)[0])]
buckets = np.array(buckets)
for i in range(np.shape(coordinates)[1]):
    buckets[int(coordinates[0][i]),int(coordinates[1][i])] = 1
    # print([int(coordinates[0][i]),int(coordinates[1][i])])

print(type(buckets))
print(np.shape(buckets))

# # # noise removal


kernel0 = np.ones((40,40),np.uint8)
buckets70 = cv2.dilate(img_as_ubyte(buckets),kernel0,iterations=1)
buckets70[buckets70>0]=1
buckets70 = img_as_ubyte(buckets70)

kernel1 = np.ones((30,30),np.uint8)
buckets50 = cv2.dilate(img_as_ubyte(buckets),kernel1,iterations=1)
buckets50[buckets50>0]=1
buckets50 = img_as_ubyte(buckets50)

kernel2 = np.ones((10,10),np.uint8)
buckets25 = cv2.dilate(img_as_ubyte(buckets),kernel2,iterations=1)
buckets25[buckets25>0]=1
buckets25 = img_as_ubyte(buckets25)

unknown5025 = cv2.subtract(buckets50,buckets25)

sureBGnd = [[1 for col in range(np.shape(gray)[1])] for row in range(np.shape(gray)[0])]
sureBGnd = np.array(sureBGnd)
sureBGnd[buckets70==1]=0
sureBGnd = img_as_ubyte(sureBGnd)

syureFGND = buckets70
# unknown[unknown==1] = 255

# plt.imshow(sureBGnd)
# plt.show()


###################

# # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# ret, thresh = cv2.threshold(gray,180,1,cv2.THRESH_BINARY_INV) # cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU
# thresh[thresh==0] = -1
# thresh[thresh==1] = 0
# thresh[thresh==-1] = 1

# # # # noise removal
# kernel = np.ones((2,2),np.uint8)
# # #opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
# closing = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel, iterations = 2)

# # # sure background area
# sure_bg = cv2.dilate(closing,kernel,iterations=1)
# sure_bg[sure_bg==255] = 1

# # # Finding sure foreground area
# dist_transform = cv2.distanceTransform(sure_bg,cv2.DIST_L2,3)

# # # Threshold
# ret, sure_fg = cv2.threshold(dist_transform,0.1*dist_transform.max(),1,0)

# # # Finding unknown region
# sure_fg = np.uint8(sure_fg)

# # unknown = cv2.subtract(sure_bg,sure_fg)
# unknown = cv2.subtract(sure_bg,sure_fg)
# sure_bg[sure_bg==1] = 255

# # # Marker labelling
# ret, markers = cv2.connectedComponents(sure_fg)

# markers = markers+1
# markers[unknown==255] = 0

# # markers = np.int32(markers) gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# ret, thresh = cv2.threshold(gray,180,1,cv2.THRESH_BINARY_INV) # cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU
# thresh[thresh==0] = -1
# thresh[thresh==1] = 0
# thresh[thresh==-1] = 1

# # # # noise removal
# kernel = np.ones((2,2),np.uint8)
# # #opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
# closing = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel, iterations = 2)

# # # sure background area
# sure_bg = cv2.dilate(closing,kernel,iterations=1)
# sure_bg[sure_bg==255] = 1

# # Finding sure foreground area
# dist_transform = cv2.distanceTransform(sureBGnd,cv2.DIST_L2,3)

# plt.imshow(dist_transform)
# plt.show()

# # Threshold
# ret, sure_fg = cv2.threshold(dist_transform,0.1*dist_transform.max(),1,0)

# # Finding unknown region
# sure_fg = np.uint8(sure_fg)

# unknown = cv2.subtract(sure_bg,sure_fg)
unknown = cv2.subtract(sureBGnd,syureFGND)
sureBGnd[sureBGnd==1] = 255

# # Marker labelling
ret, markers = cv2.connectedComponents(syureFGND)

markers = markers+1
markers[unknown==255] = 0
markers = np.int32(markers)

# plt.imshow(gray)
# plt.show()

# plt.imshow(sureBGnd)
# plt.show()

# plt.imshow(syureFGND)
# plt.show()

# plt.imshow(unknown)
# plt.show()

# plt.imshow(img_as_uint(np.array(gray)))
# plt.show()

# plt.imshow(markers)
# plt.show()

print(type(gray))
print(markers.dtype)

# # Add one to all labels so that sure background is not 0, but 1
# # markers = markers+1

# # Now, mark the region of unknown with zero
# # markers[unknown==255] = 0
# # print(type(markers))
gray
# buckets[unknown==255] = 0

gray = np.uint8(gray)

markers = markers.astype('int32')

print(markers.dtype)

plt.imshow(markers)
plt.show()

# img = cv2.imread('Results\Feb_16-0.jpg',1)

img = np.uint8(img)

print(np.shape(img))
print(img.dtype)
print(np.shape(markers))
print(markers.dtype)
# img = img_as_ubyte(cv2.imread('Others/Images/coins.png'))
# img = ReadImage('Others/Images/demo.tif').read(1)


markers = cv2.watershed(img,markers)
# img[markers == -1] = [255,0,0]

# # plt.subplot(421),plt.imshow(img)
# # plt.title('Input Image'), plt.xticks([]), plt.yticks([])
# # plt.subplot(422),plt.imshow(unknown, 'gray')
# # plt.title("Otsu's binary threshold"), plt.xticks([]), plt.yticks([])

# # plt.subplot(423),plt.imshow(closing, 'gray')
# # plt.title("morphologyEx:Closing:2x2"), plt.xticks([]), plt.yticks([])
# # plt.subplot(424),plt.imshow(sure_bg, 'gray')
# # plt.title("Dilation"), plt.xticks([]), plt.yticks([])

# # plt.subplot(425),plt.imshow(dist_transform, 'gray')
# # plt.title("Distance Transform"), plt.xticks([]), plt.yticks([])
# # plt.subplot(426),plt.imshow(sure_fg, 'gray')
# # plt.title("Thresholding"), plt.xticks([]), plt.yticks([])

# plt.subplot(427),plt.imshow(buckets, 'gray')
# plt.title("Unknown"), plt.xticks([]), plt.yticks([])

# # plt.subplot(428),plt.imshow(img, 'gray')
# # plt.title("Result from Watershed"), plt.xticks([]), plt.yticks([])

# plt.tight_layout()
# plt.show()

# plt.imshow(sureBGnd)
# plt.show()

# plt.imshow(syureFGND)
# plt.show()

# plt.imshow(unknown)
# plt.show()

# plt.imshow(markers)
# plt.show()

# print(type(gray))
# print(markers.dtype)

# # Add one to all labels so that sure background is not 0, but 1
# # markers = markers+1

# # Now, mark the region of unknown with zero
# # markers[unknown==255] = 0
# # print(type(markers))

# print(gray.dtype)
# print(buckets.dtype)

# # plt.imshow(buckets)
# # plt.show()

# buckets[unknown==255] = 0



# markers = cv2.watershed(gray,markers)
# img[markers == -1] = [255,0,0]

# # plt.subplot(421),plt.imshow(img)
# # plt.title('Input Image'), plt.xticks([]), plt.yticks([])
# # plt.subplot(422),plt.imshow(unknown, 'gray')
# # plt.title("Otsu's binary threshold"), plt.xticks([]), plt.yticks([])

# # plt.subplot(423),plt.imshow(closing, 'gray')
# # plt.title("morphologyEx:Closing:2x2"), plt.xticks([]), plt.yticks([])
# # plt.subplot(424),plt.imshow(sure_bg, 'gray')
# # plt.title("Dilation"), plt.xticks([]), plt.yticks([])

# # plt.subplot(425),plt.imshow(dist_transform, 'gray')
# # plt.title("Distance Transform"), plt.xticks([]), plt.yticks([])
# # plt.subplot(426),plt.imshow(sure_fg, 'gray')
# # plt.title("Thresholding"), plt.xticks([]), plt.yticks([])

# plt.subplot(427),plt.imshow(buckets, 'gray')
# plt.title("Unknown"), plt.xticks([]), plt.yticks([])

# # plt.subplot(428),plt.imshow(img, 'gray')
# # plt.title("Result from Watershed"), plt.xticks([]), plt.yticks([])

# plt.tight_layout()
# plt.show()


