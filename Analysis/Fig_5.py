# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 12:59:32 2024

@author: vbrus
"""

import pandas as pd
from datetime import datetime
import progressbar as pb
import re
import os
from os import listdir
from os.path import isfile, join
from yaml import safe_load
import time
import sqlite3
from sqlite3 import OperationalError
        
from functools import partial
import numpy as np

import pandas as pd
import re
import matplotlib
import matplotlib.font_manager
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import matplotlib.ticker as mtick

plt.style.use("default")
matplotlib.rcParams['font.family'] = ['DengXian']
matplotlib.rcParams['figure.figsize'] = [8, 10]

files = [".//Date datasets//State Council.xlsx", ".//Date datasets//Hainan Provincial Government.xlsx", 
         ".//Date datasets//Shanghai Municipal Government.xlsx", ".//Date datasets//Sichuan Provincial Government.xlsx", 
         ".//Date datasets//Henan Provincial Government.xlsx", ".//Date datasets//Guangdong Provincial Government.xlsx",
         ".//Date datasets//Yunnan Provincial Government.xlsx"]
num_rows = math.ceil(len(files)/2)
fig, axs = plt.subplots(num_rows, 2)
fig.tight_layout(pad=3.0)
fig.supxlabel("Original issuing date of document")
fig.supylabel("Mean days from issuance until publication")

for i in range(len(files)):
    doc = files[i]
    data = pd.read_excel(doc)
    
    data['iss']= pd.to_datetime(data['iss'])
    data['pub']= pd.to_datetime(data['pub'])
    data["diff"] = data['pub'] - data['iss']
    data['year'] = data['iss'].dt.year
    #data.to_excel(doc, index=False)
    data.set_index("year", inplace=True)
    #print(len(data))
    
    
    data.dropna(subset=['diff'], inplace=True)
    data['diff'] = data["diff"].dt.days.astype(int)
    data = data[['diff']]
    data = data.loc[data['diff'] >= 0]
    #print(data)
        
    data_grouped = data.groupby("year").mean()
    data_grouped = data_grouped.loc[data_grouped.index >= 2008]
    data_grouped = data_grouped.loc[data_grouped.index <= 2022]
    #print(data_grouped)
    
    if i % 2 == 0:
        column_no = 0
    else:
        column_no = 1
        
    row_no = math.floor(i/2)

    axs[row_no, column_no].plot(data_grouped)
    #axs[row_no, column_no].plot(result)
    #axs.plot(data_grouped)
    
    try:
        axs[row_no, column_no].set_title(data["database"][0])
    except:
        axs[row_no, column_no].set_title(doc[18:-5])
    #axs[row_no, column_no].set_yscale('log')
    axs[row_no, column_no].grid(linestyle="dashed")
    axs[row_no, column_no].xaxis.set_major_locator(MaxNLocator(integer=True))

plt.savefig('Fig_5.png', dpi=600)
        
        
        