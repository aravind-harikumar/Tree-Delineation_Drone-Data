import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# # sns.set()
# # ArrVal = np.array([['Date1','Date2','Date3']])
# # fmri = pd.DataFrame({
# #                      'X': np.repeat(ArrVal,10),
# #                      'Y': np.random.choice(10,30)
# #                     })
# # print(pd.concat([fmri['Y'] ,fmri['Y']],axis=0))
# # # sns.relplot(x="X", y="Y", kind="line", data=fmri)
# # # # print(fmri)
# # # plt.show()

# fmri = sns.load_dataset("fmri")
# # sns.relplot(x="timepoint", y="signal",
# #             hue="event", style="event",
# #             kind="line", data=fmri);

# l = len(fmri.index)
# d =  {'VALUE': pd.concat([fmri['signal'],fmri['signal']], axis=0), 'DATEID': np.concatenate( ( np.repeat(1,l), np.repeat(2,l)), axis=0) }
# fmr2 = pd.DataFrame(data=d)

# print(fmr2)

# ArrVal = np.array(['Date1','Date2','Date3'])
# l = len(fmri.index)*3
# print(l)
# print( len( np.repeat(ArrVal,l) ) )
# print(np.concatenate( ( np.repeat(ArrVal, len(ArrVal)*3), np.repeat(3,l) ), axis=0))

# print( len(np.concatenate((np.repeat(ArrVal, l),np.repeat(ArrVal, l)),axis=0) ) )
# # print(np.concatenate( ( np.repeat(1,l), np.array([1,2,3]) ), axis=0))
# print(np.asarray(fmr2['DATEID']))
# print(np.concatenate( (np.asarray(fmr2['DATEID']), np.asarray(fmr2['DATEID']), np.random.choice(1,3) ), axis=0))

import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")

# Load an example dataset with long-form data
fmri = sns.load_dataset("fmri")

dataarr = {
           'region' : [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, 2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
           'timepoint' : ['1A','1A','1A','1A','1A','1A','1A','1A','1A','1A','2A','2A','2A','2A','2A','2A','2A','2A','2A','2A','3A','3A','3A','3A','3A','3A','3A','3A','3A','3A','1A','1A','1A','1A','1A','1A','1A','1A','1A','1A','2A','2A','2A','2A','2A','2A','2A','2A','2A','2A','3A','3A','3A','3A','3A','3A','3A','3A','3A','3A'],
           'indexvalues': [3, 4, 1, 1, 15, 14, 1, 2, 2, 1, 12, 2, 4, 4, 5, 6, 7, 8, 9, 10, 12, 22, 34, 44, 65, 46, 27, 98, 29, 10,34, 43, 14, 15, 15, 14, 31, 25, 62, 41, 12, 22, 34, 44, 65, 46, 27, 98, 29, 10, 12, 22, 34, 44, 65, 46, 27, 98, 29, 10]
          }
tm = pd.DataFrame(dataarr, columns = ['region','timepoint', 'indexvalues'])
# tm = tm.set_index(tm.dateid)

print(tm)

# # Plot the responses for different events and regions
sns.lineplot(x="timepoint", y="NDVI123", hue="region", data=tm, palette=['red','green'], ci=99, linewidth=2.5)

# print(fmri)
plt.show()

# plt.show()