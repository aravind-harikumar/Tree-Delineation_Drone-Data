import matplotlib.pyplot as plt
from skimage.color import rgb2gray
import numpy as np
from skimage import data
from skimage.filters import gaussian
from skimage.segmentation import active_contour
from ImageProcessor import RasterOperators

imgg = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/UAV/StCasimir/2018/Nano-Hyperspec/ProcessedMSData/20180514/ITC-Data/All-ITC/ITC-Crown-Shp/20180514261998.1243169399_5176699.635638298.tif'

# img = data.astronaut()
imgobj = RasterOperators.ReadImage(imgg)
wd = imgobj.width
ht = imgobj.height
img = np.array(imgobj.read(1))
img = rgb2gray(img)

s = np.linspace(0, 2*np.pi, 80)
r = ht/2 + 3 + 50*np.sin(s)
c = wd/2 + 3 + 50*np.cos(s)
init = np.array([r, c]).T
print(ht/2 + 3)
print(wd/2 + 3)

snake = active_contour(gaussian(img, 1),
                       init, 
                       alpha=0.5, # Snake length shape parameter. Higher values makes snake contract faster.
                       beta= 10, # Snake smoothness shape parameter. Higher values makes snake smoother.
                       gamma=1, # Explicit time stepping parameter
                       w_line = 0, # Controls attraction to brightness. Use negative values to attract toward dark regions. 
                       max_iterations = 100,
                       w_edge = -6 # Controls attraction to edges. Use negative values to repel snake from edges.
                       )

# Options.Iterations=100;
# Options.Wedge=2; % Controls attraction to edges. Use negative values to repel snake from edges.
# Options.Wline=0; % Controls attraction to brightness. Use negative values to attract toward dark regions. 
# Options.Wterm=0;
# Options.Kappa=4; % Weight of external image force, default 2
# Options.Sigma1=1;
# Options.Sigma2=1;
# Options.Alpha=0.5; %Membrame energy  (first order), default 0.2
# Options.Beta=0.2; % Thin plate energy (second order), default 0.2
# Options.Mu=0.2;
# Options.Delta=0.5;  % Baloon force,
# Options.Gamma = 1; % Time step, default 1
# Options.GIterations=600;

fig, ax = plt.subplots(figsize=(7, 7))
ax.imshow(img, cmap=plt.cm.gray)
ax.plot(init[:, 1], init[:, 0], '--r', lw=3)
ax.plot(snake[:, 1], snake[:, 0], '-b', lw=3)
ax.set_xticks([]), ax.set_yticks([])
ax.axis([0, img.shape[1], img.shape[0], 0])

plt.show()