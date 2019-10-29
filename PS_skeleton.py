#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pandorable problem set 3 for PSY 1210 - Fall 2019

@author: katherineduncan

In this problem set, you'll practice your new pandas data management skills, 
continuing to work with the 2018 IAT data used in class

Note that this is a group assignment. Please work in groups of ~4. You can divvy
up the questions between you, or better yet, work together on the questions to 
overcome potential hurdles 
"""

#%% import packages 
import os as os
import numpy as np
import pandas as pd

#%%
# As edited by Corey
# Question 1: reading and cleaning

# read in the included IAT_2018.csv file
#IAT = pd.read_csv('/Users/Corey/Documents/Github/ps3-3s1bb/IAT_2018.csv')
IAT = pd.read_csv('/Users/nicholebouffard/Documents/GitHub/ps3-3s1bb/IAT_2018.csv')

# rename and reorder the variables to the following (original name->new name):
# session_id->id
# genderidentity->gender
# raceomb_002->race
# edu->edu
# politicalid_7->politic
# STATE -> state
# att_7->attitude 
# tblacks_0to10-> tblack
# twhites_0to10-> twhite
# labels->labels
# D_biep.White_Good_all->D_white_bias
# Mn_RT_all_3467->rt

IAT = IAT.rename(columns={'session_id': 'id','genderidentity' : 'gender', 'raceomb_002' : 'race', 'edu':'edu','politicalid_7':'politic', 'STATE':'state', 'att_7':'attitude', 'tblacks_0to10':'tblack', 'twhites_0to10': 'twhite','labels':'labels', 'D_biep.White_Good_all':'D_white_bias', 'Mn_RT_all_3467':'rt'})
IAT = IAT[['id','gender','race','edu','politic','state','attitude','tblack','twhite','labels','D_white_bias', 'rt']]

# remove all participants that have at least one missing value
IAT_clean = IAT.dropna(axis=0,how='any')


# check out the replace method: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.replace.html
# use this to recode gender so that 1=men and 2=women (instead of '[1]' and '[2]')
IAT_clean = IAT_clean.replace({'gender': {'[1]': 'men', '[2]': 'women'}})

# use this cleaned dataframe to answer the following questions

#%%
# Edited by Nichole
# Question 2: sorting and indexing

# use sorting and indexing to print out the following information:

# the ids of the 5 participants with the fastest reaction times
IATsortedFast=IAT_clean.sort_values(by='rt')
fastestIDs=list(IATsortedFast.id[0:5])
print('Subjects with fastest rts:', str(fastestIDs))

# the ids of the 5 men with the strongest white-good bias
IATmen=IAT_clean[IAT_clean.gender == 'men']
IATmensortedWB=IATmen.sort_values(by='D_white_bias', ascending= False)
menIDs=list(IATmensortedWB.id[0:5])
print('Men with strongest white bias:', str(menIDs))


# the ids of the 5 women in new york with the strongest white-good bias
IATwomen=IAT_clean.query('gender == "women" & state == "NY" ')
IATwomensortedWB=IATwomen.sort_values(by='D_white_bias', ascending= False)
womenIDs=list(IATwomensortedWB.id[0:5])
print('Women in New York with strongest white bias:', str(menIDs))



#%%
# Edited by Nick
# Question 3: loops and pivots

# check out the unique method: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.unique.html
# use it to get a list of states
states = list(IAT_clean['state'].unique())

# write a loop that iterates over states to calculate the median white-good
# bias per state
# store the results in a dataframe with 2 columns: state & bias
newdf=pd.DataFrame(columns={'state','med_wg_bias'})
for st in states:
    onestate=IAT_clean[IAT_clean.state == st]
    median=onestate.median(axis=0)
    wgb=median['D_white_bias']
    tempdf=pd.DataFrame({'state' : st,
                         'med_wg_bias' : wgb},index=[0])
    newdf=pd.concat([newdf,tempdf],axis=0,sort= False)
    
newdf

# now use the pivot_table function to calculate the same statistics
state_bias= pd.pivot_table(IAT_clean, values = 'D_white_bias', 
                            index = ['state'], 
                            aggfunc=np.median)
state_bias

# make another pivot_table that calculates median bias per state, separately 
# for each race (organized by columns)
state_race_bias= pd.pivot_table(IAT_clean, values = 'D_white_bias', 
                            index = ['state'], 
                            columns = ['race'],
                            aggfunc=np.median)

state_race_bias

#%%
# Question 4: merging and more merging

# add a new variable that codes for whether or not a participant identifies as 
# black/African American
IAT_clean['is_black'] = 1*(IAT_clean.race==5)

# use your new variable along with the crosstab function to calculate the 
# proportion of each state's population that is black 
# *hint check out the normalization options
prop_black = pd.crosstab(IAT_clean.state,IAT_clean.is_black,normalize='index')
prop_black = prop_black.rename(columns={1:'is_black',0:'is_otherrace'})
prop_black = prop_black[['is_otherrace','is_black']]
prop_black = prop_black.reset_index()

# state_pop.xlsx contains census data from 2000 taken from http://www.censusscope.org/us/rank_race_blackafricanamerican.html
# the last column contains the proportion of residents who identify as 
# black/African American 
# read in this file and merge its contents with your prop_black table
census = pd.read_excel('/Users/arianagiuliano/Desktop/programming_hwk/ps3/state_pop.xlsx')
census = census.rename(columns={'State':'state'})
merged = pd.merge(census,prop_black,on='state')
merged.describe()

# use the corr method to correlate the census proportions to the sample proportions
merged.corr(method = 'pearson') #r = 0.88

# now merge the census data with your state_race_bias pivot table
new_merged = pd.merge(census,state_race_bias,on='state')
new_merged.describe()

# use the corr method again to determine whether white_good biases is correlated 
# with the proportion of the population which is black across states
# calculate and print this correlation for white and black participants
correlations = new_merged.corr(method = 'pearson')
print(correlations.loc['per_black',5])
print(correlations.loc['per_black',6])
#correlation b/t black_whitegood and per_black is r = -0.14
#correlation b/t white_whitegood and per_black is r = 0.095



