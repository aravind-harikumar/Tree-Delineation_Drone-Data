import numpy as np
import matplotlib.pyplot as plt
from ImageProcessor import RasterOperators, VectorOperators, OtherUtils
# from sklearn.decomposition import PCA
import pywt
import pywt.data


# Load image
original = pywt.data.camera()
original = RasterOperators.ReadImage('/mnt/4TBHDD/HS_DATA/Others/tree_181015.tif')
# original = original.read(120)
originalarr = []
for i in range(1,original.count+1):
    originalarr.append(original.read(i))
print(np.shape(originalarr))
exit(0)
# pca = PCA(n_components=2)
# original = pca.fit_transform(originalarr)
# print(np.shape(original))
# exit(0)
# print(np.shape(original.read(122)))
# plt.imshow(original.read(122))
# plt.show()
# exit(0)
# Wavelet transform of image, and plot approximation and details
titles = ['Approximation', ' Horizontal detail',
          'Vertical detail', 'Diagonal detail']
coeffs2 = pywt.dwt2(original, 'bior1.3')
LL, (LH, HL, HH) = coeffs2
fig = plt.figure(figsize=(12, 3))
for i, a in enumerate([LL, LH, HL, HH]):
    ax = fig.add_subplot(1, 4, i + 1)
    ax.imshow(a, interpolation="nearest", cmap=plt.cm.plasma)
    ax.set_title(titles[i], fontsize=10)
    ax.set_xticks([])
    ax.set_yticks([])

fig.tight_layout()
plt.show()