import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from functools import reduce

# water potential
path_water_potential = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Scholander/SCA_Master_final.xlsx'
dframe_wp = pd.read_excel(path_water_potential)
dframe_wp.set_axis(['Month', 'Year', 'Individual', 'Genotype', 'Barr', 'MPa'], axis=1, inplace=False)
dframe_wp.set_index('Individual')

# Pigments
Pigments2017 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Pigments/2017/Copy of SCA_JuneAugOct2017_ZH.xlsx'
Pigments2018 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Pigments/2018/SCA_2018_May_Jul_HPLC_data.xlsx'
Pigments2018 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Pigments/2018/SpruceUp_SCA_2018_pigments_spectrophotometry_data_final.xlsx'
dframe_wp_2017 = pd.read_excel(Pigments2017)
dframe_wp_2018 = pd.read_excel(Pigments2018)

# Dual pam - fluorescence 
file1 =  '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Dual PAM/St Casimir/Processed Master Files/SCA_MASTER.xlsx'
file2 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Dual PAM/St Casimir/Processed Master Files/SCA_MASTER_20170828.xlsx'

# Photosynthetic Gas exchange. Li 6400
file1_photo1 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Li-6400/StCasimir/2017/processed/201706_LI6400_data.xlsx'
file1_photo2 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Li-6400/StCasimir/2017/processed/201708_LI6400_data.xlsx'
file1_photo3 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Li-6400/StCasimir/2017/processed/201710_LI6400_data.xlsx'
file1_photo4 = '/mnt/4TBHDD/Spruce_Up_New_Copy/SpruceUp/Li-6400/StCasimir/2018/'

# Print figure
# colsnamesdict =  dict(zip(range(1,dframe_wp.shape[1]), dframe_wp.columns.values))
# plt.figure(figsize=(15, 4))
# for i in range(1,dframe_wp.shape[1],1):
#     plt.subplot(2, 3, i)
#     plt.scatter(dframe_wp['Barr'], dframe_wp['MPa'], marker='o')
#     plt.title(str(colsnamesdict[i]))
# plt.show()

# Get unique genotypes
# print(dframe_wp.Genotype.unique().tolist())
Month_list = dframe_wp.Month.unique().tolist()
genotype_list = dframe_wp.Genotype.unique().tolist()
# dframe_wp.Barr = dframe_wp.Barr/10

def test_sum(series):
    return reduce(lambda x, y: x + y, series)/10

dframe_wp['e'] = pd.Series(dframe_wp['Barr']**2, index=dframe_wp.index)

# print(dframe_wp.head())
# print(dframe_wp.index)
# grouped_multiple = dframe_wp.groupby(['Genotype', 'Month']).agg({'Barr': ['mean', 'std', 'max']})
grouped_multiple = dframe_wp.groupby(['Genotype', 'Month']).agg({'Barr': ['mean','std', 'max','sum', test_sum],'MPa': ['mean','std', 'max','sum', test_sum]})
grouped_multiple = grouped_multiple.sort_values(["Genotype", "Month"], ascending = (True, True))
# grouped_multiple.columns = ['Barr_mean', 'Barr_min', 'Barr_max', 'Barr_sum', 'Bdarr_reduce','Bdarr_square','e']
grouped_multiple = grouped_multiple.reset_index()
print(grouped_multiple)

# print(type(genotype_list))
# print(dframe_wp.head())
    # for genotype, month in genotype_list, Month_list:
    #     genotype_tree_rows = dframe_wp.loc[dframe_wp['Genotype'] == genotype]
    #     print(genotype_tree_rows)
    #     print([genotype_tree_rows.Barr.mean(axis=0, skipna = True) , genotype_tree_rows.Barr.std(axis=0, skipna = True)])

# genotype_list = dframe_wp.Genotype.unique().tolist()
# for genotype in genotype_list:
#     genotype_tree_rows = dframe_wp.loc[dframe_wp['Genotype'] == genotype]
#     print([genotype_tree_rows.Barr.mean(axis=0, skipna = True) , genotype_tree_rows.Barr.std(axis=0, skipna = True)])
