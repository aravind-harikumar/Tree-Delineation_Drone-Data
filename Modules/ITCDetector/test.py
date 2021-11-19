import numpy as np

# centers = [(1, 2, 3, 4, 5), 
#            (6, 7, 8, 9, 10), 
#            (11, 12, 13, 14, 15)]

array = np.array(range(0,20)).flatten()
# centers = np.array(centers)
# print(centers)
reshaped= array.reshape((5,4))
print(reshaped)

reverted = array.reshape((10,2))
print(reverted)
