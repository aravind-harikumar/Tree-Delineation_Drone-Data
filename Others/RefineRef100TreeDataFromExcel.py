from posix import listdir
import pandas as pd
import numpy as np
import os

#############################################
## Li 6400 Data Refining

# Li6400Data = '/mnt/4TBHDD/100_Tree_Ref_Data/Li6400.xlsx'
# Li6400_sheet_Li6400 = pd.read_excel(Li6400Data,sheet_name='Li6400')
# Li6400_sheet_Li6400['Tree-#'].replace('_','-',regex=True,inplace=True)

# UniqueDates = Li6400_sheet_Li6400['Day'].unique()
# print(UniqueDates)

# UniqueFreq = np.round(Li6400_sheet_Li6400['PARi'],-1).unique()
# print(UniqueFreq)

# cnt = 1

# for uniqedate in UniqueDates:
#     Li6400_sheet_DateX = Li6400_sheet_Li6400[Li6400_sheet_Li6400['Day'] ==  uniqedate]
#     # for freq in UniqueFreq:
#     #     # Li6400_sheet_DateXAndUFreq = Li6400_sheet_DateX[Li6400_sheet_DateX['Day'] ==  uqdate]
#     Li6400_sheet_Li6400_1 = Li6400_sheet_DateX[np.round(Li6400_sheet_DateX['PARi'],-1).isin([UniqueFreq[0]])]
#     Li6400_sheet_Li6400_1 = Li6400_sheet_Li6400_1.rename(columns=dict(zip(Li6400_sheet_Li6400_1.columns, Li6400_sheet_Li6400_1.columns+ '_'+ str(1))))

#     Li6400_sheet_Li6400_2 = Li6400_sheet_DateX[np.round(Li6400_sheet_DateX['PARi'],-1).isin([UniqueFreq[1]])]
#     Li6400_sheet_Li6400_2 = Li6400_sheet_Li6400_2.rename(columns=dict(zip(Li6400_sheet_Li6400_2.columns, Li6400_sheet_Li6400_2.columns+ '_'+ str(2))))

#     Li6400_sheet_Li6400_3 = Li6400_sheet_DateX[np.round(Li6400_sheet_DateX['PARi'],-1).isin([UniqueFreq[2]])]
#     Li6400_sheet_Li6400_3 = Li6400_sheet_Li6400_3.rename(columns=dict(zip(Li6400_sheet_Li6400_3.columns, Li6400_sheet_Li6400_3.columns+ '_'+ str(3))))

#     Li6400_sheet_Li6400_4 = Li6400_sheet_DateX[np.round(Li6400_sheet_DateX['PARi'],-1).isin([UniqueFreq[3]])]
#     Li6400_sheet_Li6400_4 = Li6400_sheet_Li6400_4.rename(columns=dict(zip(Li6400_sheet_Li6400_4.columns, Li6400_sheet_Li6400_4.columns+ '_'+ str(4))))

#     Joint_data_1 = Li6400_sheet_Li6400_1.merge(Li6400_sheet_Li6400_2, how='inner', left_on='Tree-#_1', right_on='Tree-#_2')
#     Joint_data_2 = Joint_data_1.merge(Li6400_sheet_Li6400_3, how='inner', left_on='Tree-#_1', right_on='Tree-#_3')
#     Joint_data_3 = Joint_data_2.merge(Li6400_sheet_Li6400_4, how='inner', left_on='Tree-#_2', right_on='Tree-#_4')

#     Joint_data_3.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Joint_data_Li6400' + '_' + str(uniqedate) + '_' + str(0)  +'.xlsx', index=False, header=True)
#     cnt = cnt +1


# for root, dirs, files in os.walk('/mnt/4TBHDD/100_Tree_Ref_Data/refined'):
#     finalldf = pd.DataFrame()
#     for name in files:
#         if("#" not in name):
#             print(os.path.join(root, name))
#             tmpdf = pd.read_excel(os.path.join(root, name), 'Sheet1')
#             finalldf = finalldf.append(tmpdf)
#             # tmpdf  = pd.read_excel(Li6400Data,sheet_name='Sheet1')
#             # finalldf = finalldf.merge(tmpdf,left_on='Tree-#', right_on='Tree-#')

#     print(finalldf.head()) 
#     finalldf.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Joint_data_Li640t0_ALL_ALL.xlsx', index=False, header=True)

#############################################

## Li 6400 Data Refining

            # PigmentsData = '/mnt/4TBHDD/100_Tree_Ref_Data/Pigments.xlsx'
            # PigmentsDt2018 = pd.read_excel(PigmentsData,sheet_name='Pigments-2018')
            # PigmentsDt2018['Sample'].replace('_','-',regex=True,inplace=True)
            # PigmentsDt2018["Sample"] = PigmentsDt2018["Sample"].str.split("-").str[0] + '-' + PigmentsDt2018["Sample"].str.split("-").str[2] + '-' + PigmentsDt2018["Sample"].str.split("-").str[1] + '-' + PigmentsDt2018["Sample"].str.split("-").str[3] 
            # # PigmentsDt2018 = PigmentsDt2018.rename(columns=dict(zip(PigmentsDt2018.columns, 'a_' + str(2018) + '_' +PigmentsDt2018.columns)))
            # # print(PigmentsDt2018["a_2018_Sample"].head())
            # PigmentData2018Columns = pd.DataFrame(PigmentsDt2018.columns)
            # print(PigmentData2018Columns.head(10))
            # PigmentData2018Columns.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Pigments/individual/2018.xlsx', index=False, header=True)


            # PigmentsDt2017 = pd.read_excel(PigmentsData,sheet_name='Pigments-2017')
            # PigmentsDt2017['Genotype'].replace('_','-',regex=True,inplace=True)
            # PigmentsDt2017["Genotype"] = 'SCA-' + PigmentsDt2017["Genotype"].str.split("-").str[1] + '-' + PigmentsDt2017["Genotype"].str.split("-").str[0] + '-' + PigmentsDt2017["Genotype"].str.split("-").str[2]
            # # PigmentsDt2017 = PigmentsDt2017.rename(columns=dict(zip(PigmentsDt2017.columns,  'b_' + str(2017) + '_' +PigmentsDt2017.columns)))
            # # print(PigmentsDt2017["b_2017_Genotype"].head())
            # PigmentData2017Columns = pd.DataFrame(PigmentsDt2017.columns)
            # print(PigmentData2017Columns.head(10))
            # PigmentData2017Columns.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Pigments/individual/2017.xlsx', index=False, header=True)

            # # outdf = pd.concat([PigmentData2018Columns, PigmentData2017Columns], ignore_index=True, sort=False)
# print(outdf.head())



# cnt = 1
# UniqueDates = PigmentsDt2018['a_2018_Sampling_date'].unique()
# print(UniqueDates)

# for uniqedate in UniqueDates:
#     PiigmentData_sheet_Date2018 = PigmentsDt2018[PigmentsDt2018['a_2018_Sampling_date'] ==  uniqedate]

#     PiigmentData_sheet_Date2017 = PigmentsDt2017[PigmentsDt2017['b_2017_Sampling_date'] ==  uniqedate]

#     finalldf = PiigmentData_sheet_Date2018.merge(PiigmentData_sheet_Date2017,left_on='a_2018_Sample', right_on='b_2017_Genotype')
#     finalldf.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Pigments/individual/igments' + '_' + str(uniqedate) + '_' + str(0)  +'.xlsx', index=False, header=True)
    
    # cnt = cnt +1
    # for freq in UniqueFreq:
    # #     # Li6400_sheet_DateXAndUFreq = Li6400_sheet_DateX[Li6400_sheet_DateX['Day'] ==  uqdate]
    # Li6400_sheet_Li6400_1 = PiigmentData_sheet_DateX[np.round(PiigmentData_sheet_DateX['PARi'],-1).isin([UniqueFreq[0]])]
    # Li6400_sheet_Li6400_1 = Li6400_sheet_Li6400_1.rename(columns=dict(zip(Li6400_sheet_Li6400_1.columns, Li6400_sheet_Li6400_1.columns+ '_'+ str(1)))

# finalldf = PigmentsDt2018.merge(PigmentsDt2017,left_on='a_2018_Sample', right_on='b_2017_Genotype')
# finalldf.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Pigments/Pigments_ALL_ALL.xlsx', index=False, header=True)

#############################################

# ## Water potential Data Refining
# WaterpotentialData = '/mnt/4TBHDD/100_Tree_Ref_Data/Water_potential_SCA_2017_2018.xlsx'
# WaterpotentialData = pd.read_excel(WaterpotentialData,sheet_name='Sheet1')
# WaterpotentialData["Individual"] = 'SCA-' + WaterpotentialData["Individual"].str.split(".").str[1] + '-' + WaterpotentialData["Individual"].str.split(".").str[0] + '-' + WaterpotentialData["Individual"].str.split(".").str[2]
# WaterpotentialData.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/WaterPotential/WaterPotential.xlsx', index=False, header=True)

############################################
# Li64002018Path = '/home/ensmingerlabgpu/Desktop/TEmp_Fld'
# # files = os.listdir(Li6400201Path)

# MRG_DFd = pd.DataFrame(None)
# for file in os.listdir(Li64002018Path):
#     if("2_del_10_2018" not in file and "2_del_05_2018" not in file and "2_del_07_2018" not in file ):
#         print(file)
#         temdataframe = pd.read_excel(os.path.join(Li64002018Path,file))
#         temdataframe = temdataframe.loc[temdataframe.index>6]
#         temdataframe.dropna(axis=0, how='all',inplace=True)
#         temdataframe = pd.DataFrame(temdataframe)
#         temdataframe.columns = temdataframe.iloc[0] 
#         MRG_DFd = pd.concat([MRG_DFd,temdataframe],ignore_index=False, sort=False)
#         MRG_DFd = MRG_DFd.append(temdataframe)
#         MRG_DFd.drop_duplicates(inplace=True)
# MRG_DFd['Year'] = '2018'
# MRG_DFd['Month'] = 'May'
# MRG_DFd.drop_duplicates(inplace=True)
#         # print(temdataframe.head())
#         # exit(0)
#     # break
# MRG_DFd = MRG_DFd.loc[MRG_DFd["Obs"]!='Remark=']
# MRG_DFd.reset_index()
# MRG_DFd.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Li6400/2018/Li64002018.xlsx', index=False, header=True)

# MRG_DFd = pd.DataFrame(None)
# Li64002018Path = '/mnt/4TBHDD/100_Tree_Ref_Data/refined/Li6400/2018'
# for file in os.listdir(Li64002018Path):
#     if("#" not in file):
#         print(os.path.join(Li64002018Path,file))
#         temdataframe = pd.read_excel(os.path.join(Li64002018Path,file))
#         MRG_DFd = MRG_DFd.append(temdataframe)
# MRG_DFd.reset_index()
# MRG_DFd.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Li6400/2018/ALL.xlsx', index=False, header=True)

# MRG_DFd = MRG_DFd.append(temdataframe)
#         MRG_DFd.drop_duplicates(inplace=True)
##############################################


#############################################
# Li 6400 Data Refining 2018

# Li6400Data = '/mnt/4TBHDD/100_Tree_Ref_Data/refined/Li6400/2018/ALL.xlsx'
# Li6400_sheet_Li6400 = pd.read_excel(Li6400Data,sheet_name='Li6400')
# # Li6400_sheet_Li6400['Tree-#'].replace('_','-',regex=True,inplace=True)

# UniqueDates = Li6400_sheet_Li6400['Month'].unique()
# print(UniqueDates)

# UniqueFreq = np.round(Li6400_sheet_Li6400['PARi'],-1).unique()
# print(UniqueFreq)

# print(Li6400_sheet_Li6400['Tree-#'].isna().sum(axis=0))
# cnt = 1

# for uniqedate in UniqueDates:
#     Li6400_sheet_DateX = Li6400_sheet_Li6400[Li6400_sheet_Li6400['Month'] ==  uniqedate]
    
#     # for freq in UniqueFreq:
#     #     # Li6400_sheet_DateXAndUFreq = Li6400_sheet_DateX[Li6400_sheet_DateX['Day'] ==  uqdate]
#     Li6400_sheet_Li6400_1 = Li6400_sheet_DateX[np.round(Li6400_sheet_DateX['PARi'],-1).isin([UniqueFreq[0]])]
#     Li6400_sheet_Li6400_1 = Li6400_sheet_Li6400_1.rename(columns=dict(zip(Li6400_sheet_Li6400_1.columns, Li6400_sheet_Li6400_1.columns+ '_'+ str(1))))

#     # print(Li6400_sheet_Li6400_1.head())

#     # print(Li6400_sheet_Li6400_1.head())
#     Li6400_sheet_Li6400_2 = Li6400_sheet_DateX[np.round(Li6400_sheet_DateX['PARi'],-1).isin([UniqueFreq[1]])]
#     Li6400_sheet_Li6400_2 = Li6400_sheet_Li6400_2.rename(columns=dict(zip(Li6400_sheet_Li6400_2.columns, Li6400_sheet_Li6400_2.columns+ '_'+ str(2))))

#     # print(Li6400_sheet_Li6400_2.head())

#     Li6400_sheet_Li6400_3 = Li6400_sheet_DateX[np.round(Li6400_sheet_DateX['PARi'],-1).isin([UniqueFreq[2]])]
#     Li6400_sheet_Li6400_3 = Li6400_sheet_Li6400_3.rename(columns=dict(zip(Li6400_sheet_Li6400_3.columns, Li6400_sheet_Li6400_3.columns+ '_'+ str(3))))

#     Li6400_sheet_Li6400_4 = Li6400_sheet_DateX[np.round(Li6400_sheet_DateX['PARi'],-1).isin([UniqueFreq[3]])]
#     Li6400_sheet_Li6400_4 = Li6400_sheet_Li6400_4.rename(columns=dict(zip(Li6400_sheet_Li6400_4.columns, Li6400_sheet_Li6400_4.columns+ '_'+ str(4))))

#     Joint_data_1 = Li6400_sheet_Li6400_1.merge(Li6400_sheet_Li6400_2, how='inner', left_on='Tree-#_1', right_on='Tree-#_2')

#     Joint_data_2 = Joint_data_1.merge(Li6400_sheet_Li6400_3, how='inner', left_on='Tree-#_1', right_on='Tree-#_3')
#     Joint_data_3 = Joint_data_2.merge(Li6400_sheet_Li6400_4, how='inner', left_on='Tree-#_2', right_on='Tree-#_4')
#     # print(Joint_data_3.head())

#     # exit(0)
#     Joint_data_3.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Li6400/2018/tmp/' + '_' + str(uniqedate) + '_' + str(0)  +'.xlsx', index=False, header=True)
#     cnt = cnt +1


# for root, dirs, files in os.walk('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Li6400/2018/tmp'):
#     finalldf = pd.DataFrame()
#     for name in files:
#         if("#" not in name):
#             print(os.path.join(root, name))
#             tmpdf = pd.read_excel(os.path.join(root, name), 'Sheet1')
#             finalldf = finalldf.append(tmpdf)
#             # tmpdf  = pd.read_excel(Li6400Data,sheet_name='Sheet1')
#             # finalldf = finalldf.merge(tmpdf,left_on='Tree-#', right_on='Tree-#')

#     print(finalldf.head()) 
#     finalldf.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Li6400/2018/Joint_data_2018_Li640t0_ALL.xlsx', index=False, header=True)

#############################################

# Li64002017Data = '/mnt/4TBHDD/100_Tree_Ref_Data/refined/Li6400/Joint_data_Li640t0_ALL_ALL.xlsx'
# Li640017_sheet_Li6400 = pd.read_excel(Li64002017Data,sheet_name='Li6400')

# Li64002018Data = '/mnt/4TBHDD/100_Tree_Ref_Data/refined/Li6400/Joint_data_2018_Li640t0_ALL.xlsx'
# Li6400_sheet_Li6400 = pd.read_excel(Li64002018Data,sheet_name='Li6400')

# # finalldf = Li64002017Data.merge(Li64002018Data,left_on='Tree-#', right_on='Tree-#')
# finalldf = Li640017_sheet_Li6400.append(Li6400_sheet_Li6400)
# finalldf.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Li6400/Li640t0_ALL.xlsx', index=False, header=True)

#############################################

Pigments2017Data = '/mnt/4TBHDD/100_Tree_Ref_Data/refined/Pigments/Pigments_ALL.xlsx'
PigmentsDt2017 = pd.read_excel(Pigments2017Data,sheet_name='Pigments-2017')

Pigments2018Data = '/mnt/4TBHDD/100_Tree_Ref_Data/refined/Pigments/Pigments_ALL.xlsx'
PigmentsDt2018 = pd.read_excel(Pigments2018Data,sheet_name='from_nicolas')

# finalldf = PigmentsDt2017.merge(PigmentsDt2018,left_on='Tree-#', right_on='Tree-#')
finalldf = PigmentsDt2017.append(PigmentsDt2018)
finalldf.to_excel('/mnt/4TBHDD/100_Tree_Ref_Data/refined/Pigments/ALL_2018_2017_PIGMENTS111.xlsx', index=False, header=True)