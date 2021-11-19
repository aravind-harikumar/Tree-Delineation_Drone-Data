import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from functools import reduce

####################################################################################################################
#                                             DATA LOCATION                                                        #
####################################################################################################################

#### Pigments #####
Pigments2017 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Pigments/2017/Copy of SCA_JuneAugOct2017_ZH.xlsx'
Pigments2018 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Pigments/2018/SCA_2018_May_Jul_HPLC_data.xlsx'
Pigments2018 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Pigments/2018/SpruceUp_SCA_2018_pigments_spectrophotometry_data_final.xlsx'
# dframe_wp_2017 = pd.read_excel(Pigments2017)
# dframe_wp_2018 = pd.read_excel(Pigments2018)

##### Dual pam - fluorescence ##### 
file1 =  '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Dual PAM/St Casimir/Processed Master Files/SCA_MASTER.xlsx'
file2 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Dual PAM/St Casimir/Processed Master Files/SCA_MASTER_20170828.xlsx'

##### water potential #####
path_water_potential = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Scholander/SCA_Master_final.xlsx'

##### Photosynthetic Gas exchange. Li 6400 ######
file1_photo1 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Li-6400/StCasimir/2017/processed/201706_LI6400_data.xlsx'
file1_photo2 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Li-6400/StCasimir/2017/processed/201708_LI6400_data.xlsx'
file1_photo3 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Li-6400/StCasimir/2017/processed/201710_LI6400_data.xlsx'
file1_photo4 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Li-6400/StCasimir/2018/'

####################################################################################################################
#                                                    LOAD DATA                                                     #
####################################################################################################################

# Photosynthetic gas exchange data 
dframe_wp = pd.read_excel(path_water_potential)
dframe_wp.set_axis(['Month', 'Year', 'Individual', 'Genotype', 'Barr', 'MPa'], axis=1, inplace=False)
dframe_wp['Individual'] = dframe_wp['Individual'].str.replace('.','_')
for index, items in dframe_wp.iterrows():
    spltlist = items['Individual'].split('_')
    print(spltlist)
    dframe_wp.loc[index,'Individual'] = spltlist[1] + '_' + spltlist[0] + '_' + spltlist[2]
print(dframe_wp.head())
dframe_wp.set_index('Individual')

# Water potential data
dframe_wp_2017_data = pd.read_excel(file1_photo1,sheet_name='Combine')
dframe_wp_2017_data.set_index('Tree-#')
print(dframe_wp_2017_data.head())

joineddf = dframe_wp.set_index('key').join(dframe_wp_2017_data.set_index('key'))

exit(0)

####################################################################################################################
#                                                        LOOP                                                      #
####################################################################################################################

# Get unique genotypes
genotype_list = dframe_wp.Genotype.unique().tolist()

def test_sum(series):
    return reduce(lambda x, y: x + y, series)/10

# get aggregate values for a column group by columns
grouped_multiple = dframe_wp.groupby(['Genotype', 'Month']).agg({'Barr': ['mean','std', 'max','min', test_sum],'MPa': ['mean','std', 'max','min', test_sum]})
grouped_multiple = grouped_multiple.sort_values(["Genotype", "Month"], ascending = (True, True))
grouped_multiple.columns = ['Barr_mean', 'Barr_std', 'Barr_max', 'Barr_min', 'Bdarr_reduce','Barr_meand', 'Barr_midn', 'Badrr_max', 'Badrr_min', 'Bdardr_reduce']
grouped_multiple = grouped_multiple.reset_index()
print(grouped_multiple)

plt.figure(figsize=(20, 9))
genotype_list = grouped_multiple.Genotype.unique().tolist()
i = 1
width = 0.15
for genotype in genotype_list:
    plt.subplot(2, 5, i)
    genotype_tree_rows = grouped_multiple.loc[grouped_multiple['Genotype'] == genotype]
    x = np.arange(len(genotype_tree_rows['Month']))
    rects1 = plt.bar(x- width-width/2, genotype_tree_rows['Barr_mean'],width, label='Mean')
    rects1 = plt.bar(x- width/2, genotype_tree_rows['Barr_max'],width, label='Max')
    rects2 = plt.bar(x+ width/2, genotype_tree_rows['Barr_std'],width, label='Std')
    rects1 = plt.bar(x+ width+width/2, genotype_tree_rows['Barr_min'],width, label='Min')
    plt.title("Genotype:"+str(genotype))
    # genotype_tree_rows.plot.bar(x="Month", y="Barr_mean", rot=70, title="Genotype:"+str(genotype))
    i = i+1
    plt.xlabel('Month')
    plt.ylabel('Value')
    plt.legend()
plt.show(block=True)