import numpy as np
from skimage.feature import peak_local_max
from skimage import io, data, img_as_float, img_as_uint
img1 = np.zeros((7, 7))

img1[3, 4] = 0.7
img1[3, 3] = 0.3
img1[3, 2] = 0.5
img1[5, 2] = 0.1
# img1[0, :] = 1.2

# img1 = np.array(img1).astype('Float32')
array_min, array_max = img1.min(), img1.max()
img = img_as_float((img1 - array_min) / (array_max - array_min))

print(img1)
print(peak_local_max(img1, min_distance=1,threshold_rel=0.1))