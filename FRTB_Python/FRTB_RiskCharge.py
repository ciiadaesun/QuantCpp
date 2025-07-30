#%%
"""
Created By Daesun Lim (CIIA(R), FRM(R))
Bank Risk Quant
My FRTB Module 
v1.1.8
"""
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
# JIT은 쓰지말자
#from numba import jit
import warnings
import os
from scipy.sparse import diags
PrevTreeFlag = 0
tree = None
currdir = os.getcwd()
warnings.filterwarnings('ignore')
vers = "1.1.8"
recentupdate = '20250730'
print("######################################\nCreated By Daesun Lim (CIIA(R), FRM(R))\nRisk Validation Quant\nMy FRTB Module \n"+vers+" (RecentUpdated :" +recentupdate + ")" + "\n######################################\n")
GlobalFlag = 0
GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
GIRR_VegaRiskFactor1 = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
GIRR_VegaRiskFactor2 = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
GIRR_DeltaRfCorr = np.array([[1.000,0.970,0.914,0.811,0.719,0.566,0.400,0.400,0.400,0.400 ],
                             [0.970,1.000,0.970,0.914,0.861,0.763,0.566,0.419,0.400,0.400 ],
                             [0.914,0.970,1.000,0.970,0.942,0.887,0.763,0.657,0.566,0.419 ],
                             [0.811,0.914,0.970,1.000,0.985,0.956,0.887,0.823,0.763,0.657 ],
                             [0.719,0.861,0.942,0.985,1.000,0.980,0.932,0.887,0.844,0.763 ],
                             [0.566,0.763,0.887,0.956,0.980,1.000,0.970,0.942,0.914,0.861 ],
                             [0.400,0.566,0.763,0.887,0.932,0.970,1.000,0.985,0.970,0.942 ],
                             [0.400,0.419,0.657,0.823,0.887,0.942,0.985,1.000,0.990,0.970 ],
                             [0.400,0.400,0.566,0.763,0.844,0.914,0.970,0.990,1.000,0.985 ],
                             [0.400,0.400,0.419,0.657,0.763,0.861,0.942,0.970,0.985,1.000 ]])
CSR_RiskFactorRate = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
CSR_DeltaNonSecuritizedBucketCorr = np.array([[1.000,0.750,0.100,0.200,0.250,0.200,0.150,0.100,0.000,0.450,0.450],
                                        [0.750,1.000,0.050,0.150,0.200,0.150,0.100,0.100,0.000,0.450,0.450 ],
                                        [0.100,0.050,1.000,0.050,0.150,0.200,0.050,0.200,0.000,0.450,0.450 ],
                                        [0.200,0.150,0.050,1.000,0.200,0.250,0.050,0.050,0.000,0.450,0.450 ],
                                        [0.250,0.200,0.150,0.200,1.000,0.250,0.050,0.150,0.000,0.450,0.450 ],
                                        [0.200,0.150,0.200,0.250,0.250,1.000,0.050,0.200,0.000,0.450,0.450 ],
                                        [0.150,0.100,0.050,0.050,0.050,0.050,1.000,0.050,0.000,0.450,0.450 ],
                                        [0.100,0.100,0.200,0.050,0.150,0.200,0.050,1.000,0.000,0.450,0.450 ],
                                        [0.000,0.000,0.000,0.000,0.000,0.000,0.000,0.000,1.000,0.000,0.000 ],
                                        [0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.000,1.000,0.750 ],
                                        [0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.000,0.750,1.000 ]])
CSR_DeltaNonSecurCorrDf = pd.DataFrame(CSR_DeltaNonSecuritizedBucketCorr, 
                                       index = pd.Index([(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15),8,16,17,18]), 
                                       columns = pd.Index([(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15),8,16,17,18]))
CSR_SecuritizedNonCTPDelta_RiskFactor = [0.5, 1, 3, 5, 10]
CSR_SecuritizedNonCTPDelta_RW = pd.Series([0.009,0.015,0.02,0.02,0.008,0.012,0.012,0.014,
                                           0.01125,0.01875,0.025,0.025,0.01,0.015,0.015,0.0175,
                                           0.01575,0.02625,0.035,0.035,0.014,0.021,0.021,0.0245,0.035 ], 
                                              [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25])
CSR_CTP_RW = pd.Series([0.040,0.040,0.080,0.050,0.040,0.030,0.020,0.060,0.130,0.130,
                            0.160,0.100,0.120,0.120,0.120,0.130 ],[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
CSR_SecuritizedCTPDelta_RiskFactor = [0.5, 1, 3, 5, 10]
EQ_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
FX_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
HighLiquidCurrency = ["USD","EUR","JPY","GBP","AUD",
                      "CAD","CHF","MXN","CNY","NZD",
                      "RUB","HKD","SGD","TRY","KRW",
                      "SEK","ZAR","INR","NOK","BRL"]
COMM_DeltaRiskFactor = pd.Series([0, 0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
COMM_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
EQBucketIndex = [1,2,3,4,5,6,7,8,9,10,11,12,13]
EQSpotRW = [0.5500 ,0.6000 ,0.4500 ,0.5500 ,0.3000 ,0.3500 ,0.4000 ,0.5000 ,0.7000 ,0.5000 ,0.7000 ,0.1500 ,0.2500 ]
EQRepoRW = [0.0055 ,0.0060 ,0.0045 ,0.0055 ,0.0030 ,0.0035 ,0.0040 ,0.0050 ,0.0070 ,0.0050 ,0.0070 ,0.0015 ,0.0025]
EQDeltaRWMappingDF = pd.DataFrame([EQSpotRW,EQRepoRW], columns = EQBucketIndex, index = ["SpotRW","RepoRW"]).T
COMM_Delta_RWMapping = pd.Series([0.3,0.35,0.6,0.8,0.4,0.45,0.2,0.35,0.25,0.35,0.5],index = np.arange(1,12))

GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
GIRR_VegaRiskFactor1 = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
GIRR_VegaRiskFactor2 = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
GIRR_DeltaRfCorr = np.array([[1.000,0.970,0.914,0.811,0.719,0.566,0.400,0.400,0.400,0.400 ],
                             [0.970,1.000,0.970,0.914,0.861,0.763,0.566,0.419,0.400,0.400 ],
                             [0.914,0.970,1.000,0.970,0.942,0.887,0.763,0.657,0.566,0.419 ],
                             [0.811,0.914,0.970,1.000,0.985,0.956,0.887,0.823,0.763,0.657 ],
                             [0.719,0.861,0.942,0.985,1.000,0.980,0.932,0.887,0.844,0.763 ],
                             [0.566,0.763,0.887,0.956,0.980,1.000,0.970,0.942,0.914,0.861 ],
                             [0.400,0.566,0.763,0.887,0.932,0.970,1.000,0.985,0.970,0.942 ],
                             [0.400,0.419,0.657,0.823,0.887,0.942,0.985,1.000,0.990,0.970 ],
                             [0.400,0.400,0.566,0.763,0.844,0.914,0.970,0.990,1.000,0.985 ],
                             [0.400,0.400,0.419,0.657,0.763,0.861,0.942,0.970,0.985,1.000 ]])
CSR_RiskFactorRate = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
CSR_DeltaNonSecuritizedBucketCorr = np.array([[1.000,0.750,0.100,0.200,0.250,0.200,0.150,0.100,0.000,0.450,0.450],
                                        [0.750,1.000,0.050,0.150,0.200,0.150,0.100,0.100,0.000,0.450,0.450 ],
                                        [0.100,0.050,1.000,0.050,0.150,0.200,0.050,0.200,0.000,0.450,0.450 ],
                                        [0.200,0.150,0.050,1.000,0.200,0.250,0.050,0.050,0.000,0.450,0.450 ],
                                        [0.250,0.200,0.150,0.200,1.000,0.250,0.050,0.150,0.000,0.450,0.450 ],
                                        [0.200,0.150,0.200,0.250,0.250,1.000,0.050,0.200,0.000,0.450,0.450 ],
                                        [0.150,0.100,0.050,0.050,0.050,0.050,1.000,0.050,0.000,0.450,0.450 ],
                                        [0.100,0.100,0.200,0.050,0.150,0.200,0.050,1.000,0.000,0.450,0.450 ],
                                        [0.000,0.000,0.000,0.000,0.000,0.000,0.000,0.000,1.000,0.000,0.000 ],
                                        [0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.000,1.000,0.750 ],
                                        [0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.000,0.750,1.000 ]])
CSR_DeltaNonSecurCorrDf = pd.DataFrame(CSR_DeltaNonSecuritizedBucketCorr, 
                                       index = pd.Index([(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15),8,16,17,18]), 
                                       columns = pd.Index([(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15),8,16,17,18]))
CSR_SecuritizedNonCTPDelta_RiskFactor = [0.5, 1, 3, 5, 10]
CSR_SecuritizedNonCTPDelta_RW = pd.Series([0.009,0.015,0.02,0.02,0.008,0.012,0.012,0.014,
                                           0.01125,0.01875,0.025,0.025,0.01,0.015,0.015,0.0175,
                                           0.01575,0.02625,0.035,0.035,0.014,0.021,0.021,0.0245,0.035 ], 
                                              [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25])
CSR_CTP_RW = pd.Series([0.040,0.040,0.080,0.050,0.040,0.030,0.020,0.060,0.130,0.130,
                            0.160,0.100,0.120,0.120,0.120,0.130 ],[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
CSR_SecuritizedCTPDelta_RiskFactor = [0.5, 1, 3, 5, 10]
EQ_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
FX_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
HighLiquidCurrency = ["USD","EUR","JPY","GBP","AUD",
                      "CAD","CHF","MXN","CNY","NZD",
                      "RUB","HKD","SGD","TRY","KRW",
                      "SEK","ZAR","INR","NOK","BRL"]
COMM_DeltaRiskFactor = pd.Series([0, 0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
COMM_VegaRiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
EQBucketIndex = [1,2,3,4,5,6,7,8,9,10,11,12,13]
EQSpotRW = [0.5500 ,0.6000 ,0.4500 ,0.5500 ,0.3000 ,0.3500 ,0.4000 ,0.5000 ,0.7000 ,0.5000 ,0.7000 ,0.1500 ,0.2500 ]
EQRepoRW = [0.0055 ,0.0060 ,0.0045 ,0.0055 ,0.0030 ,0.0035 ,0.0040 ,0.0050 ,0.0070 ,0.0050 ,0.0070 ,0.0015 ,0.0025]
EQDeltaRWMappingDF = pd.DataFrame([EQSpotRW,EQRepoRW], columns = EQBucketIndex, index = ["SpotRW","RepoRW"]).T
COMM_Delta_RWMapping = pd.Series([0.3,0.35,0.6,0.8,0.4,0.45,0.2,0.35,0.25,0.35,0.5],index = np.arange(1,12))

##############################################################################################################
########################################### 여기까지 FRTB StaticData ##########################################
########################################### 여기부터 Pricing Lib ##############################################  
##############################################################################################################

N_Info_Array  = 203
N_Info_array_raw = 203 * 12
Info_array_raw = [
    # 한국 음력 관련 하드코딩
    # 1: 평달29
    # 2: 평달30
    # 3: 평달29 윤달29
    # 4: 평달29 윤달30
    # 5: 평달30 윤달29
    # 6: 평달30 윤달30
    
    # 1841
    1, 2, 4, 1, 1, 2,   1, 2, 1, 2, 2, 1,    2, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 1,
    2, 2, 2, 1, 2, 1,   4, 1, 2, 1, 2, 1,    2, 2, 1, 2, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 2, 1,   2, 1, 2, 1, 2, 1,    2, 1, 2, 1, 5, 2,   1, 2, 2, 1, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 3, 2, 1,   2, 1, 2, 1, 2, 2,    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 1, 2,

    # 1851
    2, 2, 1, 2, 1, 1,   2, 1, 2, 1, 5, 2,    2, 1, 2, 2, 1, 1,   2, 1, 2, 1, 1, 2,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,    1, 2, 1, 2, 1, 2,   5, 2, 1, 2, 1, 2,
    1, 1, 2, 1, 2, 2,   1, 2, 2, 1, 2, 1,    2, 1, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 5, 2,   1, 2, 1, 2, 2, 2,    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,    2, 1, 6, 1, 1, 2,   1, 1, 2, 1, 2, 2,

    # 1861
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 1, 2,    2, 1, 2, 1, 2, 2,   1, 2, 2, 3, 1, 2,
    1, 2, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 1, 2, 4, 1,   2, 2, 1, 2, 2, 1,    2, 1, 1, 2, 1, 1,   2, 2, 1, 2, 2, 2,
    1, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 2,    1, 2, 2, 3, 2, 1,   1, 2, 1, 2, 2, 1,
    2, 2, 2, 1, 1, 2,   1, 1, 2, 1, 2, 1,    2, 2, 2, 1, 2, 1,   2, 1, 1, 5, 2, 1,

    # 1871
    2, 2, 1, 2, 2, 1,   2, 1, 2, 1, 1, 2,    1, 2, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,
    1, 1, 2, 1, 2, 4,   2, 1, 2, 2, 1, 2,    1, 1, 2, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 2, 1,    2, 2, 1, 1, 5, 1,   2, 1, 2, 2, 1, 2,
    2, 2, 1, 1, 2, 1,   1, 2, 1, 2, 1, 2,    2, 2, 1, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 2, 4, 2, 1, 2,   1, 1, 2, 1, 2, 1,    2, 1, 2, 2, 1, 2,   2, 1, 2, 1, 1, 2,

    # 1881
    1, 2, 1, 2, 1, 2,   5, 2, 2, 1, 2, 1,    1, 2, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 2, 2, 1, 2,    2, 1, 1, 2, 3, 2,   1, 2, 2, 1, 2, 2,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    2, 2, 1, 5, 2, 1,   1, 2, 1, 2, 1, 2,    2, 1, 2, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,    1, 5, 2, 1, 2, 2,   1, 2, 1, 2, 1, 2,

    # 1891
    1, 2, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,    1, 1, 2, 1, 1, 5,   2, 2, 1, 2, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,    1, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 5, 1,   2, 1, 2, 1, 2, 1,    2, 2, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 2, 1,    2, 1, 5, 2, 2, 1,   2, 1, 2, 1, 2, 1,
    2, 1, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 5, 2, 2, 1, 2,

    # 1901
    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,    2, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 3, 2,   1, 1, 2, 2, 1, 2,    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 2, 1,
    2, 2, 1, 2, 2, 1,   1, 2, 1, 2, 1, 2,    1, 2, 2, 4, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,    2, 1, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,
    1, 5, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,

    #1911
    2, 1, 2, 1, 1, 5,   1, 2, 2, 1, 2, 2,    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 1, 2,
    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 1, 2,    2, 2, 1, 2, 5, 1,   2, 1, 2, 1, 1, 2,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,    1, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,
    2, 3, 2, 1, 2, 2,   1, 2, 2, 1, 2, 1,    2, 1, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   5, 2, 2, 1, 2, 2,    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2,

    #1921
    2, 1, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,    2, 1, 2, 2, 3, 2,   1, 1, 2, 1, 2, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 1, 2,    2, 1, 2, 1, 2, 2,   1, 2, 1, 2, 1, 1,
    2, 1, 2, 5, 2, 1,   2, 2, 1, 2, 1, 2,    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,    1, 5, 1, 2, 1, 1,   2, 2, 1, 2, 2, 2,
    1, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 2,    1, 2, 2, 1, 1, 5,   1, 2, 1, 2, 2, 1,

    #1931
    2, 2, 2, 1, 1, 2,   1, 1, 2, 1, 2, 1,    2, 2, 2, 1, 2, 1,   2, 1, 1, 2, 1, 2,
    1, 2, 2, 1, 6, 1,   2, 1, 2, 1, 1, 2,    1, 2, 1, 2, 2, 1,   2, 2, 1, 2, 1, 2,
    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,    2, 1, 4, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 2, 1,    2, 2, 1, 1, 2, 1,   4, 1, 2, 2, 1, 2,
    2, 2, 1, 1, 2, 1,   1, 2, 1, 2, 1, 2,    2, 2, 1, 2, 1, 2,   1, 1, 2, 1, 2, 1,

    #1941
    2, 2, 1, 2, 2, 4,   1, 1, 2, 1, 2, 1,    2, 1, 2, 2, 1, 2,   2, 1, 2, 1, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 2, 1, 2,    1, 1, 2, 4, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 2, 2, 1, 2,    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 1, 2,
    2, 5, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    2, 2, 1, 2, 1, 2,   3, 2, 1, 2, 1, 2,    2, 1, 2, 2, 1, 2,   1, 1, 2, 1, 2, 1,

    #1951
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,    1, 2, 1, 2, 4, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 1, 2, 2,   1, 2, 2, 1, 2, 2,    1, 1, 2, 1, 1, 2,   1, 2, 2, 1, 2, 2,
    2, 1, 4, 1, 1, 2,   1, 2, 1, 2, 2, 2,    1, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 2, 1,   1, 5, 2, 1, 2, 2,    1, 2, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 2, 1,    2, 1, 2, 1, 2, 5,   2, 1, 2, 1, 2, 1,

    #1961
    2, 1, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 2, 3, 2, 1,   2, 1, 2, 2, 2, 1,    2, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 1, 1,   2, 1, 1, 2, 2, 1,    2, 2, 5, 2, 1, 1,   2, 1, 1, 2, 2, 1,
    2, 2, 1, 2, 2, 1,   1, 2, 1, 2, 1, 2,    1, 2, 2, 1, 2, 1,   5, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,    2, 1, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,

    #1971
    1, 2, 1, 1, 5, 2,   1, 2, 2, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 2, 1,    2, 2, 1, 5, 1, 2,   1, 1, 2, 2, 1, 2,
    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 1, 2,    2, 2, 1, 2, 1, 2,   1, 5, 2, 1, 1, 2,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 1,    2, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,
    2, 1, 1, 2, 1, 6,   1, 2, 2, 1, 2, 1,    2, 1, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,

    #1981
    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2,    2, 1, 2, 3, 2, 1,   1, 2, 2, 1, 2, 2,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,    2, 1, 2, 2, 1, 1,   2, 1, 1, 5, 2, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 1, 2, 1, 2,    1, 2, 2, 1, 2, 2,   1, 2, 1, 2, 1, 1,
    2, 1, 2, 2, 1, 5,   2, 2, 1, 2, 1, 2,    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,    1, 2, 1, 1, 5, 1,   2, 1, 2, 2, 2, 2,

    #1991
    1, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 2,    1, 2, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,
    1, 2, 5, 2, 1, 2,   1, 1, 2, 1, 2, 1,    2, 2, 2, 1, 2, 1,   2, 1, 1, 2, 1, 2,
    1, 2, 2, 1, 2, 2,   1, 5, 2, 1, 1, 2,    1, 2, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,
    
    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,    2, 1, 1, 2, 3, 2,   2, 1, 2, 2, 2, 1,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 2, 1,    2, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 1,

    #2001
    2, 2, 2, 3, 2, 1,   1, 2, 1, 2, 1, 2,    2, 2, 1, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 2, 1, 2, 2, 1,   2, 1, 1, 2, 1, 2,    1, 5, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 2, 1, 1,    2, 1, 2, 1, 2, 1,   5, 2, 2, 1, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 2, 2, 1, 2,    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 1, 2,
    2, 2, 1, 1, 5, 1,   2, 1, 2, 1, 2, 2,    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,

    #2011
    2, 1, 2, 2, 1, 2,   1, 1, 2, 1, 2, 1,    2, 1, 6, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,    1, 2, 1, 2, 1, 2,   1, 2, 5, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 2, 2, 1, 2, 1,    2, 1, 2, 1, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 2, 1, 2, 3, 2,   1, 2, 1, 2, 2, 2,    1, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,    2, 1, 2, 5, 2, 1,   1, 2, 1, 2, 1, 2,

    # 2021
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 2, 1,    2, 1, 2, 1, 2, 2,   1, 2, 1, 2, 1, 2,
    1, 5, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 2, 1, 1, 5,   2, 1, 2, 2, 2, 1,    2, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 1, 1,   2, 1, 1, 2, 2, 2,    1, 2, 2, 1, 5, 1,   2, 1, 1, 2, 2, 1,
    2, 2, 1, 2, 2, 1,   1, 2, 1, 1, 2, 2,    1, 2, 1, 2, 2, 1,   2, 1, 2, 1, 2, 1,

    # 2031
    2, 1, 5, 2, 1, 2,   2, 1, 2, 1, 2, 1,    2, 1, 1, 2, 1, 2,   2, 1, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 5, 2,    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 1, 2,    2, 2, 1, 2, 1, 4,   1, 1, 2, 1, 2, 2,
    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 1, 2,    2, 2, 1, 2, 1, 2,   1, 2, 1, 1, 2, 1,
    2, 2, 1, 2, 5, 2,   1, 2, 1, 2, 1, 1,    2, 1, 2, 2, 1, 2,   2, 1, 2, 1, 2, 1,

    #2041
    2, 1, 1, 2, 1, 2,   2, 1, 2, 2, 1, 2,    1, 5, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2]

KoreaTempHolidayList = [20020701, 20150814, 20171002, 20200817, 20220309,
                        20220601, 20231002, 20240410, 20241001, 20250127,
                        20250603]

def CalcKoreaTempHolidayList(YYYY, KoreaTempHolidayList) : 
    n = 0
    for i in range(len(KoreaTempHolidayList)) : 
        if (YYYY == int(KoreaTempHolidayList[i] // 10000)) :
            n += 1
    
    ResultKoreaTempHolidayList = [0] * n
    
    n = 0
    for i in range(len(KoreaTempHolidayList)) : 
        if (YYYY == int(KoreaTempHolidayList[i] // 10000)) :
            ResultKoreaTempHolidayList[n] = KoreaTempHolidayList[i]
            n += 1
            
    return ResultKoreaTempHolidayList                

def CalcLunarToSolar(YYYYMMDD, Leaf, ResultArray2, _info_array_raw) : 

    Year = YYYYMMDD // 10000
    Month = (YYYYMMDD - Year * 10000) // 100
    Day = (YYYYMMDD - Year * 10000 - Month * 100)
    if (Year < 1841 or 2043 < Year) :
        return -99999999
    if (Month < 1 or 12 < Month) :
        return -99999999

    info_array = np.array(Info_array_raw).reshape(N_Info_Array, 12)

    info_month = [ 31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]

    lyear = Year
    lmonth = Month
    y1 = lyear - 1841
    m1 = lmonth - 1
    leapyes = 0
    mm = 0
    if (info_array[y1][m1] > 2) :
        leapyes = Leaf

    if (leapyes == 1) : 
        if (info_array[y1][m1] == 3 or info_array[y1][m1] == 5) :
            mm = 29
        elif (info_array[y1][m1] == 4 or info_array[y1][m1] == 6) :
            mm = 30
        else :
            return -99999999
    else :
        if (info_array[y1][m1] == 1 or info_array[y1][m1] == 3 or info_array[y1][m1] == 4) :
            mm = 29
        elif (info_array[y1][m1] == 2 or info_array[y1][m1] == 5 or info_array[y1][m1] == 6) :
            mm = 30
        else :
            return -99999999

    if (Day < 1 or mm < Day) :
        return -99999999

    lday = Day
    td = 0
    for i in range(y1) : 
        for j in range(12) : 
            if (info_array[i][j] == 1) :
                td += 29
            elif (info_array[i][j] == 2) : 
                td += 30
            elif (info_array[i][j] == 3) :
                td += 58            
            elif (info_array[i][j] == 4) :
                td += 59            
            elif (info_array[i][j] == 5) :
                td += 59            
            elif (info_array[i][j] == 6) :
                td += 60
            else :
                return -99999999

    for j in range(m1) : 
        if (info_array[y1][j] == 1) :
            td += 29
        elif (info_array[y1][j] == 2) :
            td += 30
        elif (info_array[y1][j] == 3) :  
            td += 58
        elif (info_array[y1][j] == 4) :
            td += 59
        elif (info_array[y1][j] == 5) :
            td += 59
        elif (info_array[y1][j] == 6) :
            td += 60
        else :
            return -99999999

    if (leapyes == 1) : 
        if (info_array[y1][m1] == 3 or info_array[y1][m1] == 4) :
            td += 29
        elif (info_array[y1][m1] == 5 or info_array[y1][m1] == 6) :
            td += 30
        else :
            return -99999999
        
    td += lday + 22
    y1 = 1840
    leap = 0
    y2 = 0
    while True : 
        y1 += 1
        leap = ((y1 % 4 == 0 and y1 % 100 != 0) or y1 % 400 == 0)

        if (leap) :
            y2 = 366
        else :
            y2 = 365

        if (td <= y2) :
            break
        td -= y2

    syear = y1
    info_month[1] = y2 - 337
    m1 = 0

    while True : 
        m1 += 1
        if (td <= info_month[m1 - 1]) :
            break
        td -= info_month[m1 - 1]

    smonth = m1
    sday = td
    y = syear - 1
    td = y * 365 + y // 4 - y // 100 + y // 400
    for i in range(smonth - 1) : 
        td += info_month[i]

    td += sday
    w = td % 7
    YYYYMMDD = syear * 10000 + smonth * 100 + sday
    ResultArray2[0] = YYYYMMDD
    ResultArray2[1] = w
    return 1

def LunarToSolar(YYYYMMDD_Lunar, Leap = 0) :
    ResultArray2 = [0,0]
    ResultCode = CalcLunarToSolar(YYYYMMDD_Lunar, Leap, ResultArray2, Info_array_raw)
    if (ResultCode < 0) :
        return ResultCode
    else :
        return ResultArray2[0]

def LeapCheck(Year) : 
    Year = int(Year)
    return 1 if ((Year % 4 == 0 and Year % 100 != 0 ) or Year % 400 == 0) else 0

def Linterp(x, y, targetx, extrapolateflag = 0) : 
    if extrapolateflag == 0 or len(x) == 1: 
        return np.interp(targetx, np.array(x), np.array(y))
    else : 
        if targetx < x[0] : 
            return (y[1] - y[0]) / (x[1] - x[0]) * (targetx - x[0]) + y[0]
        elif targetx > x[len(x) - 1] : 
            return (y[len(x) - 1] - y[len(x) - 2]) / (x[len(x) - 1] - x[len(x) - 2]) * (targetx - x[len(x) - 1]) + y[len(x) - 1]
        else : 
            return np.interp(targetx, np.array(x), np.array(y))

def Linterp2D(XCol, YInd, Values2D, TargetX, TargetY) : 
    XCol = np.array(XCol)
    YInd = np.array(YInd)    
    try : 
        if len(TargetX) == 1 and len(TargetY) == 1 : 
            TargetX, TargetY = TargetX[0], TargetY[0]
            if TargetX <= XCol[0] and TargetY <= YInd[0] : 
                return Values2D[0][0]
            elif TargetX >= XCol[-1] and TargetY >= YInd[-1] : 
                return Values2D[-1][-1]
            idxX2 = np.where(XCol - TargetX > 0)[0][0] if TargetX < XCol[-1] else len(XCol) - 1
            idxX1 = max(0, idxX2 - 1)
            idxY2 = np.where(YInd - TargetY > 0)[0][0] if TargetY < YInd[-1] else len(YInd) - 1
            idxY1 = max(0, idxY2 - 1)
            SlopeX = (Values2D[idxY1, idxX2] - Values2D[idxY1, idxX1])/(XCol[idxX2]-XCol[idxX1]) if idxX2 != idxX1 else 0
            SlopeY = (Values2D[idxY2, idxX1] - Values2D[idxY1, idxX1])/(YInd[idxY2]-YInd[idxY1]) if idxY2 != idxY1 else 0
            return Values2D[idxY1, idxX1] + SlopeX * (TargetX - XCol[idxX1]) + SlopeY * (TargetY - YInd[idxY1])
        else :
            def TempFunction(TargetX, TargetY) : 
                if TargetX <= XCol[0] and TargetY <= YInd[0] : 
                    return Values2D[0][0]
                elif TargetX >= XCol[-1] and TargetY >= YInd[-1] : 
                    return Values2D[-1][-1]
                idxX2 = np.where(XCol - TargetX > 0)[0][0] if TargetX < XCol[-1] else len(XCol) - 1
                idxX1 = max(0, idxX2 - 1)
                idxY2 = np.where(YInd - TargetY > 0)[0][0] if TargetY < YInd[-1] else len(YInd) - 1
                idxY1 = max(0, idxY2 - 1)
                SlopeX = (Values2D[idxY1, idxX2] - Values2D[idxY1, idxX1])/(XCol[idxX2]-XCol[idxX1]) if idxX2 != idxX1 else 0
                SlopeY = (Values2D[idxY2, idxX1] - Values2D[idxY1, idxX1])/(YInd[idxY2]-YInd[idxY1]) if idxY2 != idxY1 else 0
                return Values2D[idxY1, idxX1] + SlopeX * (TargetX - XCol[idxX1]) + SlopeY * (TargetY - YInd[idxY1])
            return np.vectorize(TempFunction)(TargetX, TargetY)        
    except TypeError : 
        if TargetX <= XCol[0] and TargetY <= YInd[0] : 
            return Values2D[0][0]
        elif TargetX >= XCol[-1] and TargetY >= YInd[-1] : 
            return Values2D[-1][-1]
        idxX2 = np.where(XCol - TargetX > 0)[0][0] if TargetX < XCol[-1] else len(XCol) - 1
        idxX1 = max(0, idxX2 - 1)        
        idxY2 = np.where(YInd - TargetY > 0)[0][0] if TargetY < YInd[-1] else len(YInd) - 1
        idxY1 = max(0, idxY2 - 1)
        SlopeX = (Values2D[idxY1, idxX2] - Values2D[idxY1, idxX1])/(XCol[idxX2]-XCol[idxX1]) if idxX2 != idxX1 else 0
        SlopeY = (Values2D[idxY2, idxX1] - Values2D[idxY1, idxX1])/(YInd[idxY2]-YInd[idxY1]) if idxY2 != idxY1 else 0
        return Values2D[idxY1, idxX1] + SlopeX * (TargetX - XCol[idxX1]) + SlopeY * (TargetY - YInd[idxY1])        

def DaysOfMonth(n) : 
    M = int(n) + 1
    if M in [1, 3, 5, 7, 8, 10, 12] : 
        return 31
    elif M in [4, 6, 9, 11] : 
        return 30
    elif M == 2 : 
        return 28
    elif M == 13 :
        return 31
    elif M == 0 : 
        return 31
    else : 
        raise ValueError("Check The Month (Whether less then 13) Month is " + str(M)) 

def DaysOfMonthLeap(n) : 
    M = int(n) + 1
    if M in [1, 3, 5, 7, 8, 10, 12] : 
        return 31
    elif M in [4, 6, 9, 11] : 
        return 30
    elif M == 2 : 
        return 29
    elif M == 13 :
        return 31
    elif M == 0 : 
        return 31
    else : 
        raise ValueError("Check The Month (Whether less then 13)Month is " + str(M)) 

def CummulativeDays(n) : 
    n = int(n) 
    return [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365][n]

def CummulativeDays_Leap(n) : 
    n = int(n) 
    return [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366][n]

def YYYYMMDDToExcelDate(YYYYMMDD) : 
    YYYYMMDD = int(YYYYMMDD)
    Leap = 0
    Year = int(YYYYMMDD / 10000)
    Month = int((YYYYMMDD - Year * 10000) / 100)
    Day = int((YYYYMMDD - Year * 10000 - Month * 100))
    Leap = LeapCheck(Year) 
    
    #엑셀에서는 1900년도를 윤년 처리함
    if (Year == 1900) :
        Leap = 1     
    
    N4 = int(Year // 4)
    N100 = int(Year // 100)
    N400 = int(Year // 400)
    
    N4_To_1900 = int(1900//4)
    N100_To_1900 = int(1900//100)
    N400_To_1900 = int(1900//400)
    Result = 0
    if (Leap == 1) : 
        if (Month > 2) : 
            Result = (Year - 1900) * 365 + (N4 - N4_To_1900) - (N100 - N100_To_1900) + (N400 - N400_To_1900) + CummulativeDays(Month - 1) + 1 + Day
        else : 
            Result = (Year - 1900) * 365 + (N4 - N4_To_1900) - (N100 - N100_To_1900) + (N400 - N400_To_1900) + CummulativeDays(Month - 1) + Day
    else : 
        Result = (Year - 1900) * 365 + (N4 - N4_To_1900) - (N100 - N100_To_1900) + (N400 - N400_To_1900) + CummulativeDays(Month - 1) + 1 + Day
    return Result        

def ExcelDateToYYYYMMDD(ExcelDate) : 
    
    #
    LeapDaysFor4Year = [0,    366,  731,  1096, 1461, 1827, 2192, 2557, 2922, 3288, 
                        3653, 4018, 4383, 4749, 5114, 5479, 5844, 6210, 6575, 6940, 
                        7305, 7671, 8036, 8401, 8766, 9132, 9497, 9862, 10227, 10593,
                        10958, 11323, 11688, 12054, 12419, 12784, 13149, 13515, 13880, 
                        14245, 14610, 14976, 15341, 15706, 16071, 16437, 16802, 17167,
                        17532, 17898, 18263, 18628, 18993, 19359, 19724, 20089, 20454, 
                        20820, 21185, 21550, 21915, 22281, 22646, 23011, 23376, 23742,
                        24107, 24472, 24837, 25203, 25568, 25933, 26298, 26664, 27029,
                        27394, 27759, 28125, 28490, 28855, 29220, 29586, 29951, 30316,
                        30681, 31047, 31412, 31777, 32142, 32508, 32873, 33238, 33603, 
                        33969, 34334, 34699, 35064, 35430, 35795, 36160, 36525]
    LeapDaysFor4YearNot400 = [0, 365, 730, 1095, 1460, 1826, 2191, 2556, 2921, 3287,
                              3652, 4017, 4382, 4748, 5113, 5478, 5843, 6209, 6574, 6939,
                              7304, 7670, 8035, 8400, 8765, 9131, 9496, 9861, 10226, 10592,
                              10957, 11322, 11687, 12053, 12418, 12783, 13148, 13514, 13879, 14244,
                              14609, 14975, 15340, 15705, 16070, 16436, 16801, 17166, 17531, 17897,
                              18262, 18627, 18992, 19358, 19723, 20088, 20453, 20819, 21184, 21549,
                              21914, 22280, 22645, 23010, 23375, 23741, 24106, 24471, 24836, 25202,
                              25567, 25932, 26297, 26663, 27028, 27393, 27758, 28124, 28489, 28854,
                              29219, 29585, 29950, 30315, 30680, 31046, 31411, 31776, 32141, 32507,
                              32872, 33237, 33602, 33968, 34333, 34698, 35063, 35429, 35794, 36159,
                              36524]
    
    if ExcelDate - 36525 > 0 : 
        ExcelDate = ExcelDate - 36525
        Year = 2000
    else : 
        Year = 1900
    
    nDay_for_400 = 146097
    for i in range(1000) : 
        if (ExcelDate - nDay_for_400 <= 0) : 
            break
        else :
            ExcelDate -= nDay_for_400
            Year += 400
    
    nDay_for_100_400x = 36525
    nDay_for_100 = 36524
    for i in range(5) : 
        if (i % 4 == 0) : 
            if (ExcelDate - nDay_for_100_400x <= 0) : 
                break
            else :
                ExcelDate -= nDay_for_100_400x
                Year += 100
        else : 
            if (ExcelDate - nDay_for_100 <= 0) : 
                break
            else :
                ExcelDate -= nDay_for_100
                Year += 100

    Leap = 0
    
    if (ExcelDate == 0) : 
        Year -= 1
        return Year * 10000 + 1231
    else : 
        Flag_400 = 1 if (i % 4 == 0) else 0
        
        if (Flag_400 == 1) : 
            for i in range(101) : 
                if (ExcelDate - LeapDaysFor4Year[i+1] <= 0) : 
                    ExcelDate = ExcelDate - LeapDaysFor4Year[i]
                    Year += i
                    break
        else : 
            for i in range(101) : 
                if (ExcelDate - LeapDaysFor4YearNot400[i+1] <= 0) : 
                    ExcelDate = ExcelDate - LeapDaysFor4YearNot400[i]
                    Year += i
                    break
        if (ExcelDate == 0) : 
            Year -= 1
            return Year * 10000 + 1231

        Leap = 0
        Leap = LeapCheck(Year)
    
        if (Year == 1900) : 
            Leap = 1
        
        if (Leap == 1) : 
            for m in range(12) : 
                if (CummulativeDays_Leap(m+1) >= ExcelDate and CummulativeDays_Leap(m) < ExcelDate) : 
                    break
            if (m < 12) : 
                Month = m + 1
            else :
                Month = 12
            Day = ExcelDate - CummulativeDays_Leap(m)
        else :
            for m in range(12) : 
                if (CummulativeDays(m+1) >= ExcelDate and CummulativeDays(m) < ExcelDate) :
                    break
            if (m < 12) : 
                Month = m + 1
            else : 
                Month = 12
            Day = ExcelDate - CummulativeDays(m)
        return Year * 10000 + Month * 100 + Day

def EDate_YYYYMMDD(YYYYMMDD, NMonths) : 
    YYYYMMDD = int(YYYYMMDD)
    NMonths = int(NMonths)

    Leap = 0
    
    Year = int(YYYYMMDD / 10000)
    Month = int((YYYYMMDD - Year * 10000) / 100)
    Day = int((YYYYMMDD - Year * 10000 - Month * 100))
    
    TargetMonth = Month + NMonths
    PlusYear = 0
    ResultMonth = 0
    ResultDay = 0
    if (TargetMonth > 12) : 
        PlusYear = int(TargetMonth // 12)
        ResultMonth = TargetMonth % 12
        Leap = LeapCheck(Year + PlusYear)
        if (Leap == 1) : 
            ResultDay = min(Day, DaysOfMonthLeap(ResultMonth - 1))
        else : 
            ResultDay = min(Day, DaysOfMonth(ResultMonth - 1))
        
        if (TargetMonth % 12 != 0) : 
            return (Year + PlusYear) * 10000 + ResultMonth * 100 + ResultDay
        else : 
            return (Year + PlusYear - 1) * 10000 + 12 * 100 + ResultDay
    elif (TargetMonth > 0) : 
        ResultMonth = TargetMonth
        Leap = LeapCheck(Year)
        if (Leap == 1) : 
            ResultDay = min(Day, DaysOfMonthLeap(ResultMonth - 1))
        else : 
            ResultDay = min(Day, DaysOfMonth(ResultMonth - 1))
        return Year * 10000 + ResultMonth * 100 + ResultDay
    else : 
        if (TargetMonth >= -12) : 
            PlusYear = -1
            ResultMonth = (12 + TargetMonth)
            Leap = LeapCheck(Year + PlusYear)
        else : 
            PlusYear = int(TargetMonth // 12)
            ResultMonth = (TargetMonth % 12)
            Leap = LeapCheck(Year + PlusYear)
        
        if (ResultMonth == 0) : 
            ResultMonth = 12
            PlusYear -= 1
            Leap = LeapCheck(Year + PlusYear)
        if (Leap == 1) : 
            ResultDay = min(Day, DaysOfMonthLeap(ResultMonth - 1))
        else : 
            ResultDay = min(Day, DaysOfMonth(ResultMonth - 1))
        return (Year + PlusYear) * 10000 + ResultMonth * 100 + ResultDay

def DayCountAtoB(Day1, Day2) : 
    return YYYYMMDDToExcelDate(Day2) - YYYYMMDDToExcelDate(Day1)

def MonthCountAtoB(YYYYMMDD1, YYYYMMDD2) : 
    Y1, Y2 = (YYYYMMDD1 // 10000) , (YYYYMMDD2 // 10000)
    M1, M2 = YYYYMMDD1//100 - Y1*100, YYYYMMDD2//100 - Y2*100
    diffY = Y2 - Y1
    diffM = M2 - M1
    return diffY * 12 + diffM

def DayPlus(cdate: int, ndays: int) -> int:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    year = cdate // 10000
    month = (cdate % 10000) // 100
    day = cdate % 100
    
    while ndays > 0:
        leap = LeapCheck(year)
        days_in_month[1] = 29 if leap else 28
        
        days_remaining = days_in_month[month - 1] - day
        
        if ndays <= days_remaining:
            day += ndays
            ndays = 0
        else:
            ndays -= (days_remaining + 1)
            day = 1
            month += 1
            
            if month > 12:
                month = 1
                year += 1
    
    if ndays < 0 : 
        return ExcelDateToYYYYMMDD(YYYYMMDDToExcelDate(cdate) + ndays)
    
    return year * 10000 + month * 100 + day

def BusinessDateArrayFromAtoB(StartY, EndY, HolidayList) : 
    StartYYYYMMDD = StartY *10000 +  101
    EndYYYYMMDD = EndY *10000 + 101
    n = DayCountAtoB(StartYYYYMMDD, EndYYYYMMDD) + 1
    BD = []
    BDExcel = []
    for d in range(n) : 
        TempDate = StartYYYYMMDD if d == 0 else DayPlus(TempDate, 1)
        ExcelDate = YYYYMMDDToExcelDate(TempDate)
        MOD7 = ExcelDate % 7
        if (MOD7 not in [0,1]) and (TempDate not in HolidayList) :         
            BD.append(TempDate)
            BDExcel.append(ExcelDate)
    return BD, BDExcel

def Calc_ChildrensDay_Korea(YYYY) :
    '''
    3.1절
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 505
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)

def Calc_31Day_Korea(YYYY) :
    '''
    어린이날
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 301
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)


def Calc_Gwangbok_Korea(YYYY) :
    '''
    광복절
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 815
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)

def Calc_GaechunJeol_Korea(YYYY) :
    '''
    개천절
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 1003
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)

def Calc_Hangul_Korea(YYYY) :
    '''
    한글날
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 1009
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)

def Calc_Christmas_Korea(YYYY) :
    '''
    크리스마스
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 1225
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)

def Calc_Budda_Korea(YYYY) :
    # 4월 8일
    YYYYMMDD_Lunar = YYYY * 10000 + 408
    ResultArray2 = [0, 0]
    ResultCode = CalcLunarToSolar(YYYYMMDD_Lunar, 0, ResultArray2, Info_array_raw)
    YYYYMMDD_Solar = ResultArray2[0]
    
    # 부처님오신날이 어린이날이랑 같은 말도안되는 때가 있음 
    ChildDay = Calc_ChildrensDay_Korea(YYYY)
    if (ResultCode < 0) :
        return YYYY * 10000 + 101
    elif (ChildDay == YYYYMMDD_Solar) :
        if (ResultArray2[1] == 5) :           
            #어린이날 또는 어린이날의 대체휴일과 부처님오신날이 같고 금요일
            return DayPlus(YYYYMMDD_Solar, 3)
        else :                                
        # 그 외의 경우
            return DayPlus(ChildDay, 1)
    else :
        if (ResultArray2[1] == 0) :
            # 일요일
            return DayPlus(YYYYMMDD_Solar, 1)
        elif (ResultArray2[1] == 6) :
        # 토요일
            return DayPlus(YYYYMMDD_Solar, 2)
        else :
            return YYYYMMDD_Solar

def Calc3_newyear(YYYY):
    '''
    구정 3일
    '''
    YYYYMMDD_Lunar = YYYY * 10000 + 101
    ResultArray2 = [0, 0]
    Result = CalcLunarToSolar(YYYYMMDD_Lunar, 0, ResultArray2, Info_array_raw)
    YYYYMMDD_Solar = ResultArray2[0]
    ResultCode = Result
    
    if ResultCode >= 0:
        b = ResultArray2[1]
        ResultDay3 = [
            DayPlus(YYYYMMDD_Solar, -1),
            YYYYMMDD_Solar,
            DayPlus(YYYYMMDD_Solar, 1)
        ]
        
        if b == 6:
            # 구정이 토요일인 경우 세번째 날짜가 일요일인데 그걸 월요일로 변경
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)
        elif b == 0:
            # 구정이 일요일인 경우
            ResultDay3[1] = ResultDay3[2]  # 월요일
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)  # 화요일
        elif b == 1:
            # 구정이 월요일인 경우 첫번째 날짜가 일요일인데 그걸 화요일로 변경
            ResultDay3[0] = ResultDay3[1]  # 월요일
            ResultDay3[1] = ResultDay3[2]  # 화요일
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)  # 수요일
        return ResultDay3
    else : 
        return [YYYY * 10000 + 101] * 3

def Calc3_chuseok(YYYY):
    '''
    추석 3일
    '''
    YYYYMMDD_Lunar = YYYY * 10000 + 815
    ResultArray2 = [0, 0]
    Result = CalcLunarToSolar(YYYYMMDD_Lunar, 0, ResultArray2, Info_array_raw)
    YYYYMMDD_Solar = ResultArray2[0]
    ResultCode = Result
    
    if ResultCode >= 0:
        b = ResultArray2[1]
        ResultDay3 = [
            DayPlus(YYYYMMDD_Solar, -1),
            YYYYMMDD_Solar,
            DayPlus(YYYYMMDD_Solar, 1)
        ]
        
        if b == 6:
            # 추석이 토요일인 경우 세번째 날짜가 일요일인데 그걸 월요일로 변경
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)
        elif b == 0:
            # 추석이 일요일인 경우
            ResultDay3[1] = ResultDay3[2]  # 월요일
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)  # 화요일
        elif b == 1:
            # 추석이 월요일인 경우 첫번째 날짜가 일요일인데 그걸 화요일로 변경
            ResultDay3[0] = ResultDay3[1]  # 월요일
            ResultDay3[1] = ResultDay3[2]  # 화요일
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)  # 수요일
        return ResultDay3
    else : 
        return [YYYY * 10000 + 101] * 3

def FixedHoliday_YYYYMMDD(YYYYMMDD) : 
    '''
    공휴일이 토요일이면 금요일, 일요일이면 월요일 대체공휴일
    '''
    ExcelDate = YYYYMMDDToExcelDate(YYYYMMDD)
    MOD07 = ExcelDate % 7
    return DayPlus(YYYYMMDD, -1) if MOD07 == 0 else (DayPlus(YYYYMMDD, 1) if MOD07 == 1 else YYYYMMDD)

def Nth_Date(YYYY, MM, Nth, Date) : 
    '''
    # YYYY = 년
    # MM = 월
    # Nth = n번째
    # Date = x요일 0:토 1:일 2:월 3:화 4:수 5:목 6:금    
    '''
    YYYYMMDD = YYYY * 10000 + MM * 100 + 1
    YYYYMM = YYYY * 100 + MM
    ExcelDate = YYYYMMDDToExcelDate(YYYYMMDD)
    
    n = 0
    for i in range(31) : 
        TempDate = ExcelDate + i
        MOD7 = TempDate % 7
        if (MOD7 == Date) : 
            n += 1
            nthdate = ExcelDateToYYYYMMDD(TempDate)
            if (n == Nth) : 
                nthdateYYYYMM = nthdate // 100
                if YYYYMM == nthdateYYYYMM : 
                    return nthdate
                elif (YYYYMM < nthdateYYYYMM) : 
                    return ExcelDateToYYYYMMDD(TempDate - 7)
    return nthdate                
            
def Mapping_KoreaHoliday16(YYYY) :
    '''
    공휴일 16개 매핑하기
    '''
    Array16 = []

    Jan01 = YYYY * 10000 + 101                            
    Array16.append(Jan01)
        
    Seol = Calc3_newyear(YYYY)
    Array16 += list(Seol)

    Samil = Calc_31Day_Korea(YYYY)
    Array16.append(Samil)

    Labor = YYYY * 10000 + 501
    Array16.append(Labor)

    Budda = Calc_Budda_Korea(YYYY)
    Array16.append(Budda)

    ChildrenDay = Calc_ChildrensDay_Korea(YYYY)
    Array16.append(ChildrenDay)
    Array16.append(YYYY * 10000 + 606)
    Gwangbok = Calc_Gwangbok_Korea(YYYY)
    Array16.append(Gwangbok)

    Chuseok = Calc3_chuseok(YYYY)
    Array16 += Chuseok

    GaeChun = Calc_GaechunJeol_Korea(YYYY)
    if (GaeChun == Chuseok[0] or GaeChun == Chuseok[1] or GaeChun == Chuseok[2]) : 
        # 개천절이 추석에 껴있을 경우 하루 더 대체휴일
        GaeChun = DayPlus(Chuseok[2], 1)
        if (YYYYMMDDToExcelDate(GaeChun) % 7 == 0) :
            GaeChun = DayPlus(GaeChun, 2)
        elif (YYYYMMDDToExcelDate(GaeChun) % 7 == 1) :
            GaeChun == DayPlus(GaeChun, 1)

    Array16.append(GaeChun)
    HanGul = Calc_Hangul_Korea(YYYY)
    Array16.append(HanGul)

    Christmas = Calc_Christmas_Korea(YYYY)
    Array16.append(Christmas)
    return Array16

def Mapping_USHoliday(YYYY) : 
    
    Jan01 = (YYYY * 10000 + 101)
    Jan01Excel = YYYYMMDDToExcelDate(Jan01)
    if (Jan01Excel % 7 == 1) :
        Jan01 = DayPlus(Jan01, 1)
        
    President = FixedHoliday_YYYYMMDD(YYYY * 10000 + 120)    
    Juneteenth = FixedHoliday_YYYYMMDD(YYYY * 10000 + 619)
    Independence = FixedHoliday_YYYYMMDD(YYYY * 10000 + 704)
    Veterans = FixedHoliday_YYYYMMDD(YYYY * 10000 + 1111)
    Christmas = FixedHoliday_YYYYMMDD(YYYY * 10000 + 1225)
    MartinLuther = Nth_Date(YYYY, 1, 3, 2)
    PresidentsDay = Nth_Date(YYYY, 2, 3, 2)
    MemorialDay = Nth_Date(YYYY, 5, 5, 2)
    LaborDay = Nth_Date(YYYY, 9, 1, 2)
    ColumBus = Nth_Date(YYYY, 10, 2, 2)
    Thanks = Nth_Date(YYYY, 11, 4, 5)
    Array11 = [Jan01, Juneteenth, Independence, Veterans, Christmas, 
               MartinLuther, PresidentsDay, MemorialDay, LaborDay, ColumBus, 
               Thanks]
    return Array11
        
def KoreaHolidaysFromStartToEnd(StartY : int, EndY : int) : 
    ResultList = []
    for y in range(StartY, EndY + 1) : 
        templist = Mapping_KoreaHoliday16(y)
        ResultList += templist
    return sorted(list(set(ResultList)))

def USHolidaysFromStartToEnd(StartY : int, EndY : int) : 
    ResultList = []
    for y in range(StartY, EndY + 1) : 
        templist = Mapping_USHoliday(y)
        ResultList += templist
    return sorted(list(set(ResultList)))

def LastBusinessDate(YYYYMM, HolidayArray) : 
    YYYY = int(YYYYMM // 100)
    MM = int(YYYYMM - YYYY * 100)
    Leap = LeapCheck(YYYY)
    
    LastYYYYMMDD = YYYY * 10000 + MM * 100 + 1
    if MM in [1,3,5,7,8,10,12] : 
        LastYYYYMMDD = YYYY * 10000 + MM * 100 + 31
    elif MM in [4,6,9,11] :
        LastYYYYMMDD = YYYY * 10000 + MM * 100 + 30
    else : 
        if (Leap == 1) : 
            LastYYYYMMDD = YYYY * 10000 + MM * 100 + 29
        else : 
            LastYYYYMMDD = YYYY * 10000 + MM * 100 + 28
    
    LastExcelDate = YYYYMMDDToExcelDate(LastYYYYMMDD)
    MOD07 = LastExcelDate % 7
    SaturSundayFlag = 0
    HolidayFlag = 0
    TempExcelDate = LastExcelDate
    TempYYYYMMDD = LastYYYYMMDD
    if (MOD07 == 1 or MOD07 == 0) :
        SaturSundayFlag = 1
    
    if (LastYYYYMMDD in HolidayArray) : 
        HolidayFlag = 1
    
    if (SaturSundayFlag == 0 and HolidayFlag == 0) : 
        return LastYYYYMMDD
    else : 
        for i in range(31) : 
            TempExcelDate = LastExcelDate - i
            TempYYYYMMDD = ExcelDateToYYYYMMDD(TempExcelDate)
            MOD07 = TempExcelDate % 7
            
            if (MOD07 == 1 or MOD07 == 0) : 
                SaturSundayFlag = 1
            else : 
                SaturSundayFlag = 0
            HolidayFlag = 0 
            if TempYYYYMMDD in HolidayArray : 
                HolidayFlag = 1
            
            if (SaturSundayFlag == 0 and HolidayFlag == 0) : 
                break
        return TempYYYYMMDD

def DayCountFractionAtoB(day1, day2, flag, holidays = []) : 
    holidaysarray = np.array(holidays)

    if day1 < 19000101:
        day1 = ExcelDateToYYYYMMDD(day1)
    if day2 < 19000101:
        day2 = ExcelDateToYYYYMMDD(day2)
    
    if flag == 0:
        return DayCountAtoB(day1, day2) / 365.0
    elif flag == 1:
        return DayCountAtoB(day1, day2) / 360.0
    elif flag == 2:
        year_a, month_a, day_a = day1 // 10000, (day1 % 10000) // 100, day1 % 100
        year_b, month_b, day_b = day2 // 10000, (day2 % 10000) // 100, day2 % 100
        
        next_y = day1 + 10000
        if day1 < day2 < next_y:
            div = DayCountAtoB(day1, next_y)
            return DayCountAtoB(day1, day2) / div
        else:
            tau = 0.0
            for i in range(year_b - year_a + 1):
                current_y = day1 + i * 10000
                next_y = day1 + (i + 1) * 10000
                if current_y < day2 <= next_y:
                    div = DayCountAtoB(current_y, next_y)
                    tau += DayCountAtoB(current_y, day2) / div
                    break
                else:
                    tau += 1.0
            return tau
    elif flag == 3:
        year_a, month_a = day1 // 10000, (day1 % 10000) // 100
        year_b, month_b = day2 // 10000, (day2 % 10000) // 100
        n_month = (year_b - year_a) * 12 + (month_b - month_a)
        return (30.0 * n_month) / 360.0
    else:
        day1_excel = YYYYMMDDToExcelDate(day1)
        day2_excel = YYYYMMDDToExcelDate(day2)
        for i in range(len(holidaysarray)):
            if holidaysarray[i] < 19000101:
                holidaysarray[i] = ExcelDateToYYYYMMDD(holidaysarray[i])
        
        nbd = 0
        for temp_date_excel in range(day1_excel, day2_excel):
            temp_c_date = ExcelDateToYYYYMMDD(temp_date_excel)
            mod7 = temp_date_excel % 7
            if (mod7 not in (0, 1)) and (temp_c_date not in holidaysarray):
                nbd += 1
        
        return nbd / 252.0    

def malloc_cpn_date_holiday(price_date_yyyymmdd, swap_mat_yyyymmdd, ann_cpn_one_year, holiday_yyyymmdd = [], modified_following=1):
    price_yyyy = price_date_yyyymmdd // 10000
    price_mm = (price_date_yyyymmdd % 10000) // 100
    
    swap_mat_yyyy = swap_mat_yyyymmdd // 10000
    swap_mat_mm = (swap_mat_yyyymmdd % 10000) // 100
    
    n = ((swap_mat_yyyymmdd // 10000 - price_date_yyyymmdd // 10000) + 2) * ann_cpn_one_year
    narray = 0
    first_cpn_date = None
    
    if ann_cpn_one_year == 0:
        narray = 1
        n = 1
    else:
        m = max(1, 12 // ann_cpn_one_year)
        for i in range(n):
            cpn_date = swap_mat_yyyymmdd if i == 0 else EDate_YYYYMMDD(swap_mat_yyyymmdd, -i * m)
            if DayCountAtoB(price_date_yyyymmdd, cpn_date) < 7:
                first_cpn_date = cpn_date
                break
            if cpn_date <= price_date_yyyymmdd:
                break
            narray += 1
    
    result_cpn_date = [0] * narray
    
    for i in range(n):
        cpn_date = swap_mat_yyyymmdd if i == 0 else EDate_YYYYMMDD(swap_mat_yyyymmdd, -i * m)
        
        if cpn_date <= price_date_yyyymmdd or DayCountAtoB(price_date_yyyymmdd, cpn_date) < 7:
            break
        
        cpn_date_excel = YYYYMMDDToExcelDate(cpn_date)
        mod7 = cpn_date_excel % 7
        satur_sunday_flag = 1 if (mod7 in [0, 1] or cpn_date in holiday_yyyymmdd) else 0
        
        if not satur_sunday_flag:
            result_cpn_date[narray - 1 - i] = cpn_date
        else:
            if modified_following == 1:
                for j in range(1, 15):
                    cpn_date_excel += 1
                    mod7 = cpn_date_excel % 7
                    cpn_date_temp = ExcelDateToYYYYMMDD(cpn_date_excel)
                    if (mod7 not in [0, 1]) and (cpn_date_temp not in holiday_yyyymmdd):
                        prev_date = ExcelDateToYYYYMMDD(cpn_date_excel)
                        break
                result_cpn_date[narray - 1 - i] = min(LastBusinessDate(cpn_date // 100, holiday_yyyymmdd), prev_date)
            else:
                for j in range(1, 15):
                    cpn_date_excel += 1
                    mod7 = cpn_date_excel % 7
                    cpn_date_temp = ExcelDateToYYYYMMDD(cpn_date_excel)
                    if (mod7 not in [0, 1]) and (cpn_date_temp not in holiday_yyyymmdd) :
                        cpn_date = ExcelDateToYYYYMMDD(cpn_date_excel)
                        break
                result_cpn_date[narray - 1 - i] = cpn_date
    
    if ann_cpn_one_year == 1 and price_mm != swap_mat_mm:
        target_date_yyyymmdd = result_cpn_date[0]
        for i in range(1, 13):
            target_date_yyyymmdd = EDate_YYYYMMDD(target_date_yyyymmdd, -1)
            target_date_yyyy = target_date_yyyymmdd // 10000
            target_date_mm = (target_date_yyyymmdd % 10000) // 100
            if target_date_yyyy == price_yyyy and target_date_mm == price_mm:
                first_cpn_date = target_date_yyyymmdd
                break
    
    return result_cpn_date, first_cpn_date

def ParseBusinessDateIfHoliday(YYYYMMDD, Holidays) :
    NHolidays = len(Holidays)
    if YYYYMMDD < 19000101:
        YYYYMMDD = ExcelDateToYYYYMMDD(YYYYMMDD)
    
    for i in range(NHolidays):
        if Holidays[i] < 19000101:
            Holidays[i] = ExcelDateToYYYYMMDD(Holidays[i])
    
    ResultYYYYMMDD = 0
    ExcelDate = YYYYMMDDToExcelDate(YYYYMMDD)
    IsHolidayFlag = 0
    IsSaturSundayFlag = 0
    MOD7 = ExcelDate % 7
    
    if MOD7 == 0 or MOD7 == 1:
        IsSaturSundayFlag = 1
    
    if (YYYYMMDD in Holidays):
        IsHolidayFlag = 1
    
    if IsSaturSundayFlag == 0 and IsHolidayFlag == 0:
        ResultYYYYMMDD = YYYYMMDD
    else:
        for i in range(100):
            TempExcelDate = ExcelDate + 1 + i
            TempYYYYMMDD = ExcelDateToYYYYMMDD(TempExcelDate)
            MOD7 = TempExcelDate % 7
            
            if MOD7 == 0 or MOD7 == 1:
                IsSaturSundayFlag = 1
            else:
                IsSaturSundayFlag = 0
            
            if (TempYYYYMMDD in Holidays):
                IsHolidayFlag = 1
            else:
                IsHolidayFlag = 0
            
            if IsSaturSundayFlag == 0 and IsHolidayFlag == 0:
                ResultYYYYMMDD = TempYYYYMMDD
                break
    
    return ResultYYYYMMDD

def NextNthBusinessDate(YYYYMMDD, NBDate, Holidays) : 
    if YYYYMMDD < 19000101 : 
        YYYYMMDD = ExcelDateToYYYYMMDD(YYYYMMDD)
    StartDate = ParseBusinessDateIfHoliday(YYYYMMDD, Holidays)
    StartDateExcel = YYYYMMDDToExcelDate(StartDate)
    for i in range(len(Holidays)) : 
        if (Holidays[i] < 19000101) : 
            Holidays[i] = ExcelDateToYYYYMMDD(Holidays[i])

    ResultYYYYMMDD = YYYYMMDD
    if (NBDate > 0) : 
        n = 0 
        for i in range(100) : 
            TempExcelDate = StartDateExcel + 1 + i
            TempYYYYMMDD = ExcelDateToYYYYMMDD(TempExcelDate)
            MOD7 = TempExcelDate % 7
            IsSaturSundayFlag = 1 if (MOD7 in [0, 1]) else 0
            IsHolidayFlag = 1 if TempYYYYMMDD in Holidays else 0
            if IsSaturSundayFlag == 0 and IsHolidayFlag == 0: 
                n += 1
            
            if n >= NBDate : 
                ResultYYYYMMDD = TempYYYYMMDD
                break
    elif (NBDate < 0) : 
        n = 0 
        for i in range(100) : 
            TempExcelDate = StartDateExcel - 1 - i
            TempYYYYMMDD = ExcelDateToYYYYMMDD(TempExcelDate)
            MOD7 = TempExcelDate % 7
            IsSaturSundayFlag = 1 if (MOD7 in [0, 1]) else 0
            IsHolidayFlag = 1 if TempYYYYMMDD in Holidays else 0
            if IsSaturSundayFlag == 0 and IsHolidayFlag == 0: 
                n += 1
            
            if n >= abs(NBDate) : 
                ResultYYYYMMDD = TempYYYYMMDD
                break
    return ResultYYYYMMDD                            

def NBusinessCountFromEndToPay(EndYYYYMMDD, PayYYYYMMDD, Holidays, ModifiedFollowing, ResultEndDate):
    NHolidays = len(Holidays)
    if EndYYYYMMDD < 19000101:
        EndYYYYMMDD = ExcelDateToYYYYMMDD(EndYYYYMMDD)
    if PayYYYYMMDD < 19000101:
        PayYYYYMMDD = ExcelDateToYYYYMMDD(PayYYYYMMDD)
    
    if EndYYYYMMDD > PayYYYYMMDD:
        return -NBusinessCountFromEndToPay(PayYYYYMMDD, EndYYYYMMDD, Holidays, ModifiedFollowing, ResultEndDate)
    elif EndYYYYMMDD == PayYYYYMMDD:
        ResultEndDate[0] = EndYYYYMMDD
        return 0
    
    for i in range(NHolidays):
        if Holidays[i] < 19000101:
            Holidays[i] = ExcelDateToYYYYMMDD(Holidays[i])
    
    nbd = 0
    
    EndYYYY = EndYYYYMMDD // 10000
    EndMM = (EndYYYYMMDD - EndYYYY * 10000) // 100
    EndDD = EndYYYYMMDD % 100
    EndExcelDate = YYYYMMDDToExcelDate(EndYYYYMMDD)
    
    PayYYYY = PayYYYYMMDD // 10000
    PayMM = (PayYYYYMMDD - PayYYYY * 10000) // 100
    PayDD = PayYYYYMMDD % 100
    PayExcelDate = YYYYMMDDToExcelDate(PayYYYYMMDD)
    
    if EndDD == PayDD:
        ResultEndDate[0] = PayYYYYMMDD
        return 0
    else:
        PrevTempMM, PrevTempDD = None, None
        for i in range(30):
            TempExcelDate = PayExcelDate - 1 - i
            TempDate = ExcelDateToYYYYMMDD(TempExcelDate)
            
            TempYYYY = TempDate // 10000
            TempMM = (TempDate - TempYYYY * 10000) // 100
            TempDD = TempDate % 100
            
            MOD7 = TempExcelDate % 7
            IsSaturSundayFlag = 1 if MOD7 in (0, 1) else 0
            IsHolidayFlag = 1 if TempDate in Holidays else 0
            
            if IsSaturSundayFlag == 0 and IsHolidayFlag == 0:
                nbd += 1
            
            if i > 0 and (PrevTempMM > TempMM or (PrevTempMM == 1 and TempMM == 12)):
                if ModifiedFollowing == 1:
                    LastBD = LastBusinessDate(TempYYYY * 100 + TempMM, Holidays)
                    if EndDD > LastBD % 100:
                        EndDD = LastBD % 100
            
            if TempDD == EndDD:
                break
            
            PrevTempMM = TempMM
        
        ResultEndDate[0] = ParseBusinessDateIfHoliday(TempYYYY * 10000 + TempMM * 100 + EndDD, Holidays)
    
    return nbd

def Generate_OptionDate(FirstOptionPayDate, SwapMaturity, NYearBetweenOptionPay, NBDateBetweenOptionFixToPay = 20, MaxNumberOption = -1, ModifiedFollow = 0) :
    OptionPayDateList = [FirstOptionPayDate]
    OptionFixDateList = []
    Holidays = KoreaHolidaysFromStartToEnd(2020, 2070)
    for i in range(1, 100) : 
        NextDate = EDate_YYYYMMDD(OptionPayDateList[0], i*NYearBetweenOptionPay*12)
        AdjDate = ParseBusinessDateIfHoliday(NextDate, Holidays)
        if ModifiedFollow >= 1 : 
            TargetDate = min(AdjDate, LastBusinessDate(NextDate//100, Holidays))
        else : 
            TargetDate = AdjDate
        if NextDate >= SwapMaturity or (i >= MaxNumberOption and MaxNumberOption > 0): 
            break
        else : 
            OptionPayDateList.append(TargetDate)

    if NBDateBetweenOptionFixToPay == 0 : 
        OptionFixDateList = OptionPayDateList
    else : 
        for i in range(len(OptionPayDateList)) : 
            OptionFixDateList.append(NextNthBusinessDate(OptionPayDateList[i], -NBDateBetweenOptionFixToPay,Holidays))
    OptionFixDateList = list(np.array(OptionFixDateList)[np.array(OptionFixDateList) < SwapMaturity])
    OptionPayDateList = list(np.array(OptionPayDateList)[np.array(OptionPayDateList) < SwapMaturity])
    
    return OptionFixDateList, OptionPayDateList

def Number_of_Coupons(
    ProductType,              # 상품종류 0이면 Futures, 1이면 Swap
    PriceDate,                # 평가일
    SwapMat,                  # 스왑 만기
    NumCpnOneYear,            # 연 스왑쿠폰지급수
    HolidayUseFlag,           # 공휴일 입력 사용 Flag
    Holidays,                 # 공휴일 리스트
    ModifiedFollowingFlag
):
    NHolidays = len(Holidays)
    if PriceDate < 19000000:
        PriceDateYYYYMMDD = ExcelDateToYYYYMMDD(PriceDate)
    else:
        PriceDateYYYYMMDD = PriceDate

    if SwapMat < 19000000:
        SwapMat_YYYYMMDD = ExcelDateToYYYYMMDD(SwapMat)
    else:
        SwapMat_YYYYMMDD = SwapMat

    if DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) > 366 * 2:
        ProductType = 1
    if ProductType == 0:
        return 1

    if not (19000101 <= PriceDateYYYYMMDD <= 999990101):
        return -1
    if not (19000101 <= SwapMat_YYYYMMDD <= 999990101):
        return -1
    if NumCpnOneYear > 6:
        return -1

    HolidayYYYYMMDD = [ExcelDateToYYYYMMDD(h) if 0 <= h < 19000000 else h for h in Holidays]

    PriceYYYY = PriceDateYYYYMMDD // 10000
    PriceMM = (PriceDateYYYYMMDD % 10000) // 100
    PriceDD = PriceDateYYYYMMDD % 100

    SwapMatYYYY = SwapMat_YYYYMMDD // 10000
    SwapMatMM = (SwapMat_YYYYMMDD % 10000) // 100
    SwapMatDD = SwapMat_YYYYMMDD % 100

    if DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) <= 62 and NumCpnOneYear < 6:
        return 1
    elif SwapMatYYYY - PriceYYYY <= 1:
        n = 0
        for i in range(24):
            TempYYYYMMDD = EDate_YYYYMMDD(PriceDateYYYYMMDD, i + 1)
            TempYYYY = TempYYYYMMDD // 10000
            TempMM = (TempYYYYMMDD % 10000) // 100
            n = i + 1
            if TempYYYY == SwapMatYYYY and TempMM == SwapMatMM:
                break
        
        if n < 6:
            return 1
        else:
            TempEndList = [0]
            if PriceDD >= 24 and SwapMatDD < 7:
                nbd = NBusinessCountFromEndToPay(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDD, ModifiedFollowingFlag, TempEndList)
                SwapMat_YYYYMMDD = TempEndList[0]

            CpnDate, firstcpndate = malloc_cpn_date_holiday(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, NumCpnOneYear, HolidayYYYYMMDD if HolidayUseFlag > 0 else [], ModifiedFollowingFlag)
            return len(CpnDate)
    else:
        StartDateYYYYMMDD = PriceDateYYYYMMDD
        StartYYYYMM = StartDateYYYYMMDD // 100
        StartDD = StartDateYYYYMMDD % 100
        EndYYYYMM = SwapMat_YYYYMMDD // 100
        EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD
        TempEndList = [0]
        if PriceDD >= 24 and SwapMatDD < 7:
            nbd = NBusinessCountFromEndToPay(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDD, ModifiedFollowingFlag, TempEndList)
            EndDateYYYYMMDD = TempEndList[0]
        
        CpnDate, firstcpndate = malloc_cpn_date_holiday(PriceDateYYYYMMDD, EndDateYYYYMMDD, NumCpnOneYear, HolidayYYYYMMDD if HolidayUseFlag > 0 else [], ModifiedFollowingFlag)

        return len(CpnDate)

def MappingCouponDates(
    ProductType,               # 상품종류 0이면 Futures, 1이면 Swap
    StartDate,                 # 시작일
    SwapMat,                   # 스왑 만기
    NBDayFromEndDate,          # N영업일 뒤 지급(만약 -1일 경우 EndDate To PayDate 자동 계산)
    NumCpnOneYear,             # 연 스왑쿠폰지급수
    HolidayUseFlag,            # 공휴일 입력 사용 Flag    
    Holidays,                  # Fixing 공휴일
    HolidaysPayDate,           # Payment 공휴일
    ModifiedFollowingFlag) : 
    
    StartDateYYYYMMDD = ExcelDateToYYYYMMDD(StartDate) if (StartDate < 19000000) else StartDate
    SwapMat_YYYYMMDD = ExcelDateToYYYYMMDD(SwapMat) if (SwapMat < 19000000) else SwapMat

    ResultIsExcelType = 0
    if (StartDate < 19000000 and SwapMat < 19000000) :
        ResultIsExcelType = 1

    StartYYYYMM = int(StartDateYYYYMMDD) // 100
    StartDD = StartDateYYYYMMDD - StartYYYYMM * 100
    SwapMat_DD = SwapMat_YYYYMMDD - (int(SwapMat_YYYYMMDD // 100)) * 100

    HolidayYYYYMMDD = [0] * max(1, len(Holidays))
    for i in range(len(Holidays)) : 
        HolidayYYYYMMDD[i] = ExcelDateToYYYYMMDD(Holidays[i]) if (Holidays[i] < 19000000) else Holidays[i]
    
    HolidayYYYYMMDDPayDate = [0] * max(1, len(HolidaysPayDate))
    for i in range(len(Holidays)) : 
        HolidayYYYYMMDDPayDate[i] = ExcelDateToYYYYMMDD(HolidaysPayDate[i]) if (HolidaysPayDate[i] < 19000000) else HolidaysPayDate[i]
    
    NumberCoupon = Number_of_Coupons(ProductType, StartDate, SwapMat, NumCpnOneYear, HolidayUseFlag, Holidays, ModifiedFollowingFlag)
    ResultForwardStart = [-1] * max(1, NumberCoupon)
    ResultForwardEnd = [-1] * max(1, NumberCoupon)
    ResultPayDate = [-1] * max(1, NumberCoupon)
    ResultNBD = [-1] * max(1, NumberCoupon)
    
    if (NumberCoupon < 0) :
        return ResultForwardStart, ResultForwardEnd, ResultPayDate, ResultNBD
    elif (NumberCoupon <= 1) : 
        if (NBDayFromEndDate == 0) :
            if (ResultIsExcelType == 1) : 
                ResultForwardStart[0] = YYYYMMDDToExcelDate(StartDateYYYYMMDD)
                ResultForwardEnd[0] = YYYYMMDDToExcelDate(SwapMat_YYYYMMDD)
                ResultPayDate[0] = ResultForwardEnd[0]
            else :
                ResultForwardStart[0] = StartDateYYYYMMDD
                ResultForwardEnd[0] = SwapMat_YYYYMMDD
                ResultPayDate[0] = ResultForwardEnd[0]
            ResultNBD[0] = NBDayFromEndDate
        elif (NBDayFromEndDate < 0) :
            # NBD Auto계산
            TempEndList = [0]
            NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDDPayDate, ModifiedFollowingFlag, TempEndList)
            EndDateYYYYMMDD = TempEndList[0]
            if (ResultIsExcelType == 1) : 
                ResultForwardStart[0] = YYYYMMDDToExcelDate(StartDateYYYYMMDD)
                ResultForwardEnd[0] = YYYYMMDDToExcelDate(EndDateYYYYMMDD)
                ResultPayDate[0] = YYYYMMDDToExcelDate(SwapMat_YYYYMMDD)
            else : 
                ResultForwardStart[0] = StartDateYYYYMMDD
                ResultForwardEnd[0] = EndDateYYYYMMDD
                ResultPayDate[0] = SwapMat_YYYYMMDD      
            ResultNBD[0] = NBDayFromEndDate  
        else :
            if ((SwapMat_DD < 7 and StartDD >= 24) or NBDayFromEndDate < 0 ):
                ##########################################
                ## If PayDate is next month of EndDate  ##
                ##########################################
                TempEndList = [0]
                NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDDPayDate, ModifiedFollowingFlag, TempEndList)
                EndDateYYYYMMDD = TempEndList[0]
                if (ResultIsExcelType == 1) :
                    ResultForwardStart[0] = YYYYMMDDToExcelDate(StartDateYYYYMMDD)
                    ResultForwardEnd[0] = YYYYMMDDToExcelDate(EndDateYYYYMMDD)
                    ResultPayDate[0] = YYYYMMDDToExcelDate(SwapMat_YYYYMMDD)
                else :
                    ResultForwardStart[0] = StartDateYYYYMMDD
                    ResultForwardEnd[0] = EndDateYYYYMMDD
                    ResultPayDate[0] = SwapMat_YYYYMMDD
                ResultNBD[0] = NBDayFromEndDate
            else : 
                n = 0
                ResultForwardStart[0] = StartDate if (ResultIsExcelType == 1) else StartDateYYYYMMDD
                ResultNBD[0] = NBDayFromEndDate
                # PayDate결정
                PayDateYYYYMMDD = SwapMat_YYYYMMDD
                PayDateExcelType = YYYYMMDDToExcelDate(PayDateYYYYMMDD)
                MOD7 = PayDateExcelType % 7
                for i in range(1, 35) : 
                    if (MOD7 in [0,1]) or (PayDateYYYYMMDD in HolidayYYYYMMDDPayDate) : 
                        # 휴일이면 n+=1
                        PayDateExcelType += 1
                        PayDateYYYYMMDD = ExcelDateToYYYYMMDD(PayDateExcelType)
                    else :
                        break

                ResultPayDate[0] = PayDateExcelType if (ResultIsExcelType == 1) else PayDateYYYYMMDD

                EndDateYYYYMMDD = PayDateYYYYMMDD
                EndDateExcel = PayDateExcelType
                for i in range(1, 35) : 
                    EndDateExcel = EndDateExcel - 1
                    EndDateYYYYMMDD = ExcelDateToYYYYMMDD(EndDateExcel)
                    MOD7 = EndDateExcel % 7
                    if ((MOD7 not in [0, 1]) and (EndDateYYYYMMDD not in HolidayYYYYMMDDPayDate)) : 
                        # 영업일이면 n+=1
                        n += 1

                    if (n == NBDayFromEndDate) :
                        ResultForwardEnd[0] = EndDateExcel if (ResultIsExcelType == 1) else EndDateYYYYMMDD
                        break
    else :
        TempYYYYMMDD = StartDateYYYYMMDD
        EndYYYYMM = (int)(SwapMat_YYYYMMDD // 100)
        TempEndList = [0]
        if ( (SwapMat_DD < 7 and StartDD >= 24) or NBDayFromEndDate < 0 ): 
            ##########################################
            ## If PayDate is next month of EndDate  ##
            ##########################################
            NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDDPayDate, ModifiedFollowingFlag, TempEndList)
            EndDateYYYYMMDD = TempEndList[0]                
        else :
            EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD

        CpnDate, firstcpndate = malloc_cpn_date_holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, NumCpnOneYear, HolidayYYYYMMDD if HolidayUseFlag > 0 else [], ModifiedFollowingFlag)
        for i in range(min(NumberCoupon, len(CpnDate))) :
            if (i == 0) : 
                if (ResultIsExcelType == 1) :
                    ResultForwardStart[0] = YYYYMMDDToExcelDate(StartDateYYYYMMDD)
                    TempDateExcelType = YYYYMMDDToExcelDate(CpnDate[0])
                    ResultForwardEnd[0] = TempDateExcelType
                else :
                    ResultForwardStart[0] = StartDateYYYYMMDD
                    ResultForwardEnd[0] = CpnDate[0]
            else :
                if (ResultIsExcelType == 1) :
                    ResultForwardStart[i] = YYYYMMDDToExcelDate(CpnDate[i - 1])
                    TempDateExcelType = YYYYMMDDToExcelDate(CpnDate[i])
                    ResultForwardEnd[i] = TempDateExcelType
                else :
                    ResultForwardStart[i] = CpnDate[i - 1]
                    ResultForwardEnd[i] = CpnDate[i]
            ResultNBD[i] = NBDayFromEndDate
            if (NBDayFromEndDate == 0) : 
                ResultPayDate[i] = ResultForwardEnd[i]
            else : 
                n = 0
                for j in range(1, 35) : 
                    PayDateYYYYMMDD = DayPlus(CpnDate[i], j)
                    PayDateExcelType = YYYYMMDDToExcelDate(PayDateYYYYMMDD)
                    MOD7 = PayDateExcelType % 7
                    if ((MOD7 not in [0, 1]) and (PayDateYYYYMMDD not in HolidayYYYYMMDDPayDate)) : 
                        # 영업일이면 n+=1
                        n += 1

                    if (n == NBDayFromEndDate) :
                        ResultPayDate[i] = PayDateExcelType if (ResultIsExcelType == 1) else PayDateYYYYMMDD                        
                        break
    return ResultForwardStart, ResultForwardEnd, ResultPayDate, ResultNBD                    

def Calc_Forward_Rate_ForSOFR(TermArray, RateArray, T1, T2, DeltaT):
    LengthArray = min(len(TermArray), len(RateArray))
    EXP_APPROX = 2.718281828459045
    # Linear Interpolation
    if TermArray[0] < T1 < TermArray[LengthArray - 1]:
        DFT1 = np.exp(-Linterp(TermArray, RateArray, T1) * T1)
        DFT2 = np.exp(-Linterp(TermArray, RateArray, T2) * T2)
        FRate = (1.0 / DeltaT) * (DFT1 / DFT2 - 1.0)
    elif T1 <= TermArray[0]:
        DFT1 = np.exp(-RateArray[0] * T1)
        DFT2 = np.exp(-Linterp(TermArray, RateArray, T2) * T2)
        FRate = (1.0 / DeltaT) * (DFT1 / DFT2 - 1.0)
    else:
        DFT1 = np.exp(-RateArray[LengthArray - 1] * T1)
        DFT2 = np.exp(-RateArray[LengthArray - 1] * T2)
        FRate = (1.0 / DeltaT) * (DFT1 / DFT2 - 1.0)    
    return FRate

def SOFR_ForwardRate_Compound(
    PriceDate,
    RefCrvTerm,
    RefCrvRate, 
    ForwardStartYYYYMMDD,
    ForwardEndYYYYMMDD,
    LockOutDays,
    LookBackDays,
    ObservShift,
    HolidayFlag,
    NotHoliday,
    DayCountNotHoliday,
    RefHistoryDate,
    RefHistory,
    denominator,
    SOFRUseFlag
):
    
    nday = DayCountAtoB(ForwardStartYYYYMMDD, ForwardEndYYYYMMDD)
    N_NotHoliday = len(NotHoliday)
    AverageFlag = 1 if SOFRUseFlag == 3 else 0
    dt = 1.0 / 365.0
    deltat = 1.0 / denominator
    PrevForwardRate = Calc_Forward_Rate_ForSOFR(RefCrvTerm, RefCrvRate, 0.0, dt, deltat)
    ForwardRate = PrevForwardRate
    PI_0 = 1.0
    
    EstStart = ForwardStartYYYYMMDD
    if ((ForwardStartYYYYMMDD in NotHoliday)) :
        EstStart = ForwardStartYYYYMMDD
    else : 
        for i in range(N_NotHoliday - 1) : 
            if (NotHoliday[i] < ForwardStartYYYYMMDD and NotHoliday[i + 1] > ForwardStartYYYYMMDD) :
                EstStart = NotHoliday[i + 1]
                break
    
    EstEnd = ForwardEndYYYYMMDD
    if ((ForwardEndYYYYMMDD in NotHoliday)) :
        EstEnd = ForwardEndYYYYMMDD
    else : 
        for i in range(N_NotHoliday - 1) : 
            if (NotHoliday[i] < ForwardEndYYYYMMDD and NotHoliday[i + 1] > ForwardEndYYYYMMDD) :
                EstEnd = NotHoliday[i + 1]
                break
    
    if EstStart in NotHoliday : 
        EstStartIdx = list(NotHoliday).index(EstStart)
    else : 
        EstStartIdx = 0
        for i in range(N_NotHoliday - 1) : 
            if (NotHoliday[i] < EstStart and NotHoliday[i + 1] > EstStart) :
                EstStartIdx = i
                break

    if EstEnd in NotHoliday : 
        EstEndIdx = list(NotHoliday).index(EstEnd)
    else : 
        EstEndIdx = 0
        for i in range(N_NotHoliday - 1) : 
            if (NotHoliday[i] < EstEnd and NotHoliday[i + 1] > EstEnd) :
                EstEndIdx = i
                break
    
    T = DayCountAtoB(EstStart, EstEnd) / denominator    
    ObservShiftFlag = 1 if LookBackDays > 0 and ObservShift > 0 else 0    
    NCumpound = 0
    AverageRate = 0.0    
    LockOutDay = NotHoliday[max(0, EstEndIdx - LockOutDays)] if LockOutDays > 0 else EstEnd
    
    for i in range(EstStartIdx, EstEndIdx):
        DayYYYYMMDD = NotHoliday[i]
        T1Est = DayCountAtoB(PriceDate, NotHoliday[max(0, i - LookBackDays)]) / 365.0
        T2Est = DayCountAtoB(PriceDate, NotHoliday[max(0, i - LookBackDays + 1)]) / 365.0
        
        if (ObservShiftFlag == 0) :
            Delta_T1_T2 = (float(DayCountNotHoliday[i])) / denominator
        else :
            Delta_T1_T2 = (float(DayCountNotHoliday[max(0, i - LookBackDays)])) / denominator
        
        if T1Est < 0.0:
            HistDayIdx = -1
            if NotHoliday[max(0, i - LookBackDays)] in RefHistoryDate : 
                HistDayIdx = list(RefHistoryDate).index(NotHoliday[max(0, i - LookBackDays)])
            ForwardRate = RefHistory[HistDayIdx] if HistDayIdx >= 0 else PrevForwardRate
        else:
            if DayYYYYMMDD < LockOutDay:
                if HolidayFlag == 0:
                    ForwardRate = Calc_Forward_Rate_ForSOFR(RefCrvTerm, RefCrvRate, T1Est, T2Est, Delta_T1_T2)
                else:
                    T3Est = DayCountAtoB(PriceDate, NotHoliday[max(0, min(N_NotHoliday - 1, i - LookBackDays + 2))]) / 365.0
                    ForwardRate = Calc_Forward_Rate_ForSOFR(RefCrvTerm, RefCrvRate, T2Est, T3Est, Delta_T1_T2)
            else:
                ForwardRate = PrevForwardRate
        
        PI_0 *= 1.0 + ForwardRate * Delta_T1_T2
        AverageRate += ForwardRate
        PrevForwardRate = ForwardRate
        NCumpound += 1
    
    if AverageFlag == 1:
        AverageRate /= NCumpound
        PI_0 = (1.0 + AverageRate / denominator) ** nday
    
    AnnualizedOISRate = (PI_0 - 1.0) / T
    return PI_0 - 1.0, AnnualizedOISRate, EstStartIdx, EstEndIdx

def istermtype(termlist) : 
    term = np.array(termlist, dtype = np.float64)
    if term.min() >= 19000101 : 
        return "YYYYMMDD"
    elif term.min() > 30.0 : 
        return "ExcelDate"
    else : 
        return "Term"

def Preprocessing_Term(Term, PriceDate) : 
    if len(Term) > 0 : 
        istermtype_ZeroTerm = istermtype(Term)
        if istermtype_ZeroTerm == "YYYYMMDD" : 
            for i in range(len(Term)) : 
                Term[i] = (DayCountAtoB(PriceDate, Term[i])/365)
        elif istermtype_ZeroTerm == "ExcelDate" :
            ExcelPriceDate = YYYYMMDDToExcelDate(PriceDate) if int(PriceDate) >= 19000101 else PriceDate
            for i in range(len(Term)) : 
                Term[i] = ((Term[i] - ExcelPriceDate)/365)

def Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate, CompareNumber = 0.6) : 
    if len(ZeroTerm) > 0 : 
        istermtype_ZeroTerm = istermtype(ZeroTerm)
        if istermtype_ZeroTerm == "YYYYMMDD" : 
            for i in range(len(ZeroTerm)) : 
                ZeroTerm[i] = (DayCountAtoB(PriceDate, ZeroTerm[i])/365)
        elif istermtype_ZeroTerm == "ExcelDate" :
            ExcelPriceDate = YYYYMMDDToExcelDate(PriceDate) if int(PriceDate) >= 19000101 else PriceDate
            for i in range(len(ZeroTerm)) : 
                ZeroTerm[i] = ((ZeroTerm[i] - ExcelPriceDate)/365)
        
        if np.abs(np.array(ZeroRate)).mean() > CompareNumber : 
            for i in range(len(ZeroRate)) : 
                ZeroRate[i] = ZeroRate[i]/100

def Preprocessing_EQVol(ParityArray, TermArray, Vols2D, PriceDate, StockPrice) : 
    if len(TermArray) > 0 : 
        istermtype_ZeroTerm = istermtype(TermArray)
        if istermtype_ZeroTerm == "YYYYMMDD" : 
            for i in range(len(TermArray)) : 
                TermArray[i] = (DayCountAtoB(PriceDate, TermArray[i])/365)
        elif istermtype_ZeroTerm == "ExcelDate" :
            ExcelPriceDate = YYYYMMDDToExcelDate(PriceDate) if int(PriceDate) >= 19000101 else PriceDate
            for i in range(len(TermArray)) : 
                TermArray[i] = ((TermArray[i] - ExcelPriceDate)/365)
        
    if np.array(Vols2D).max() > 2.0 :
        for i in range(Vols2D.shape[0]) : 
            for j in range(Vols2D.shape[1]) : 
                Vols2D[i][j] /= 100
                
    if np.array(ParityArray).max() > 5.0 : 
        for i in range(len(ParityArray)) : 
            ParityArray[i] = ParityArray[i]/StockPrice

def MapGIRRDeltaGreeks(Greeks, RiskFactor) : 
    ResultSensi = pd.Series(index = RiskFactor).fillna(0.0)
    for i in range(len(Greeks)) : 
        if float(Greeks.index[i]) < 0.251 :     
            ResultSensi.loc[0.25] += Greeks.iloc[i]
        elif float(Greeks.index[i]) >= 0.251 and float(Greeks.index[i]) < 0.51:
            ResultSensi.loc[0.5] += Greeks.iloc[i]
        elif float(Greeks.index[i]) >= 0.51 and float(Greeks.index[i]) < 1.01:
            ResultSensi.loc[1.00] += Greeks.iloc[i]
        elif float(Greeks.index[i]) >= 1.01 and float(Greeks.index[i]) < 2.01:
            ResultSensi.loc[2.00] += Greeks.iloc[i]
        elif float(Greeks.index[i]) >= 2.01 and float(Greeks.index[i]) < 3.01:
            ResultSensi.loc[3.00] += Greeks.iloc[i]
        elif float(Greeks.index[i]) >= 3.01 and float(Greeks.index[i]) < 5.01:
            ResultSensi.loc[5.00] += Greeks.iloc[i]
        elif float(Greeks.index[i]) >= 5.01 and float(Greeks.index[i]) < 10.01:
            ResultSensi.loc[10.00] += Greeks.iloc[i]                 
        elif float(Greeks.index[i]) >= 10.01 and float(Greeks.index[i]) < 15.01:
            ResultSensi.loc[15.00] += Greeks.iloc[i]                 
        elif float(Greeks.index[i]) >= 15.01 and float(Greeks.index[i]) < 20.01:
            ResultSensi.loc[20.00] += Greeks.iloc[i]                 
        else : 
            ResultSensi.loc[30.00] += Greeks.iloc[i]                 
    return ResultSensi            

def MapCSRDeltaGreeks(Greeks, RiskFactor) : 
    ResultSensi = pd.Series(index = RiskFactor).fillna(0.0)
    for i in range(len(Greeks)) : 
        if float(Greeks.index[i]) < 0.51 :     
            ResultSensi.loc[0.5] += Greeks.iloc[i]
        elif float(Greeks.index[i]) >= 0.51 and float(Greeks.index[i]) < 1.01:
            ResultSensi.loc[1.00] += Greeks.iloc[i]
        elif float(Greeks.index[i]) >= 1.01 and float(Greeks.index[i]) < 3.01:
            ResultSensi.loc[3.00] += Greeks.iloc[i]
        elif float(Greeks.index[i]) >= 3.01 and float(Greeks.index[i]) < 5.01:
            ResultSensi.loc[5.00] += Greeks.iloc[i]
        else : 
            ResultSensi.loc[10.00] += Greeks.iloc[i]                 
    return ResultSensi 

def Calc_Discount_Factor(Term, Rate, T) : 
    r = Linterp(Term, Rate, T)
    return np.exp(-r * T)

def Calc_ForwardDiscount_Factor(Term, Rate, t, T) : 
    r1 = np.interp(t, Term, Rate)
    r2 = np.interp(T, Term, Rate)
    return np.exp(-r2 * T)/np.exp(-r1 * t)

def FSR(PricingDate, SwapStartDate, SwapMaturity, NCPN_Ann, DayCountFlag,
        Holiday, Term, Rate, TermDisc, RateDisc) :
    if PricingDate < 19000101 : 
        PricingDate = ExcelDateToYYYYMMDD(PricingDate)
    if SwapStartDate < 19000101 : 
        SwapStartDate = ExcelDateToYYYYMMDD(SwapStartDate)
    if SwapMaturity < 19000101 : 
        SwapMaturity = ExcelDateToYYYYMMDD(SwapMaturity)
    if NCPN_Ann == 0 : 
        T1 = DayCountAtoB(PricingDate, SwapStartDate)/365
        T2 = DayCountAtoB(PricingDate, SwapMaturity)/365
        DeltaT = DayCountFractionAtoB(SwapStartDate, SwapMaturity, DayCountFlag)
        return Calc_Forward_Rate_ForSOFR(Term, Rate, T1, T2, DeltaT)
    Preprocessing_ZeroTermAndRate(Term, Rate, PricingDate)
    Preprocessing_ZeroTermAndRate(TermDisc, RateDisc, PricingDate)
    NHoliday = len(Holiday)
    NTerm = len(Term)
    NTermDisc = len(TermDisc)
    FixingDate, CpnDate, PayDate, NBD = MappingCouponDates(1,SwapStartDate,SwapMaturity, 0, NCPN_Ann,1,Holiday,Holiday,1)
    NCpnDate = len(CpnDate)
    t = DayCountAtoB(PricingDate, SwapStartDate) / 365.0
    P0T = [0] * (NCpnDate + 1)
    P0T[0] = Calc_Discount_Factor(Term, Rate, t)
    
    for i in range(1, NCpnDate + 1):
        t = DayCountAtoB(PricingDate, CpnDate[i - 1]) / 365.0
        P0T[i] = Calc_Discount_Factor(Term, Rate,  t)
    
    a = P0T[0] - P0T[NCpnDate]
    b = 0.0
    
    for i in range(NCpnDate):
        t = DayCountAtoB(PricingDate, CpnDate[i]) / 365.0
        
        if i == 0:
            dt = DayCountFractionAtoB(SwapStartDate, CpnDate[i], DayCountFlag)
        else:
            dt = DayCountFractionAtoB(CpnDate[i - 1], CpnDate[i], DayCountFlag)
        
        b += dt * Calc_Discount_Factor(TermDisc, RateDisc, t)
    
    Swap_Rate = a / b
    return Swap_Rate

def Calc_CMS_Maturity(StartingDate, RefSwap_Maturity_T_Year = 0.25) : 
    MatDate = EDate_YYYYMMDD(StartingDate, int(RefSwap_Maturity_T_Year * 12 + 1e-9))
    return MatDate

def GPrimePrime_Over_GPrime(CpnRate, YTM, PriceDate, SwapMaturityT, NumCpnOneYear):
    if SwapMaturityT < 19000101 : 
        SwapEndDate = Calc_CMS_Maturity(PriceDate, SwapMaturityT)
    else : 
        SwapEndDate = SwapMaturityT        
    CpnDates, FirstCpnDate = malloc_cpn_date_holiday(PriceDate, SwapEndDate, NumCpnOneYear)
    Gp = 0.0
    Gpp = 0.0
    
    for i in range(len(CpnDates)):
        T = DayCountFractionAtoB(PriceDate, CpnDates[i], 3)
        if i == 0:
            Deltat = DayCountFractionAtoB(PriceDate, CpnDates[i], 3)
        else:
            Deltat = DayCountFractionAtoB(CpnDates[i - 1], CpnDates[i], 3)
        
        Gp -= CpnRate * Deltat * T * (1.0 + YTM)**(-T)
        Gpp += CpnRate * Deltat * T * T * (1.0 + YTM)**(-T)
        
        if i == len(CpnDates) - 1:
            Gp -= T * (1.0 + YTM)**(-T)
            Gpp += T * T * (1.0 + YTM)**(-T)
    
    return (Gpp / 100.0) / Gp

def CDF_N(x) : 
    y = abs(x)
    if (y > 37.0) : 
        value = 0.
    else :
        Exponential = np.exp(-y * y / 2)
        if (y < 7.07106781186547) :
            S = 3.52624965998911E-02 * y + 0.700383064443688
            S = S * y + 6.37396220353165
            S = S * y + 33.912866078383
            S = S * y + 112.079291497871
            S = S * y + 221.213596169931
            S = S * y + 220.206867912376
            S2 = 8.83883476483184E-02 * y + 1.75566716318264
            S2 = S2 * y + 16.064177579207
            S2 = S2 * y + 86.7807322029461
            S2 = S2 * y + 296.564248779674
            S2 = S2 * y + 637.333633378831
            S2 = S2 * y + 793.826512519948
            S2 = S2 * y + 440.413735824752
            value = Exponential * S / S2
        else :
            S = y + 0.65
            S = y + 4.0 / S
            S = y + 3.0 / S
            S = y + 2.0 / S
            S = y + 1.0 / S
            value = Exponential / (S * 2.506628274631)

    if (x > 0.0) :
        value = 1.0 - value

    return value

def BS_Option(PriceDate, MaturityDate, S0, X, TermDisc, 
              RateDisc, DivTerm, DivRate, Volatility, QuantoCorr = 0, 
              FXVolTerm = [], FXVol = [], DivFlag = 0, EstTerm = [], EstRate = [], 
              ForwardPrice = 0, LoggingFlag = 0, LoggingDir = "", VolTerm = [0], VolParity = [0],TypeFlag = 'c', ATMVolFlag = False, ATMVol = []) :
    
    if len(EstTerm) == 0 and ForwardPrice == 0 : 
        EstTerm = TermDisc
        EstRate = RateDisc
    elif ForwardPrice > 0 :
        EstTerm = [0]
        EstRate = [0]
    
    if PriceDate < 19000101 : 
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
    if MaturityDate < 19000101 : 
        MaturityDate = ExcelDateToYYYYMMDD(MaturityDate)
        
    Preprocessing_ZeroTermAndRate(TermDisc, RateDisc, PriceDate)
    Preprocessing_ZeroTermAndRate(EstTerm, EstRate, PriceDate)
    TimeToMaturity = DayCountAtoB(PriceDate, MaturityDate)/365
    StockLevel = X/S0 if np.array(VolParity).max() < 3.0 else X
    v = 0.001
    try : 
        if isinstance(Volatility, float) : 
            v = Volatility
        elif ATMVolFlag == False : 
            v = Linterp2D(VolTerm, VolParity, Volatility, TimeToMaturity, StockLevel)
        else : 
            v = np.interp(TimeToMaturity, VolTerm, ATMVol)
    except TypeError : 
        if isinstance(Volatility, float) : 
            v = Volatility
        elif ATMVolFlag == False : 
            v = Volatility
        else : 
            v = np.interp(TimeToMaturity, VolTerm, ATMVol)
                
    d1, d2 = 0, 0
    fxvol = Linterp(FXVolTerm, FXVol, TimeToMaturity) if len(FXVolTerm) > 0 else 0
    r_est = Linterp(EstTerm, EstRate, TimeToMaturity) - fxvol * v * QuantoCorr 
    r_disc = Linterp(TermDisc, RateDisc, TimeToMaturity)
    DivPV, F = 0, S0
    if DivFlag < 2 : 
        Preprocessing_ZeroTermAndRate(DivTerm, DivRate, PriceDate)
        Dv = Linterp(DivTerm, DivRate, TimeToMaturity) if len(DivTerm) > 0 else 0
        F = S0 * np.exp((r_est - Dv) * TimeToMaturity) if ForwardPrice == 0 else ForwardPrice
    else : 
        for i in range(len(DivTerm)) : 
            if DivTerm[i] < 30 : 
                DivTerm[i] = DayPlus(PriceDate, int(DivTerm[i] * 365.0 + 0.00001)) 
            elif DivTerm[i] < 19000101 : 
                DivTerm[i] = ExcelDateToYYYYMMDD(int(DivTerm[i]))
            
            if DivTerm[i] < MaturityDate and DivTerm[i] > PriceDate : 
                t = DayCountAtoB(PriceDate, DivTerm[i])/365
                r = Linterp(TermDisc, RateDisc, t)
                DivPV += DivRate[i] * np.exp(-r * t)
        S0 = S0 - DivPV
        F = S0 * np.exp((r_est) * TimeToMaturity) if ForwardPrice == 0 else ForwardPrice
    DiscountFactor = np.exp(-r_disc * TimeToMaturity)
    Price, Delta, Gamma, Vega, Theta, Rho = 0, 0, 0, 0, 0, 0
    if TimeToMaturity < 0.0000001 or PriceDate == MaturityDate : 
        if TypeFlag in [1,'1','c','C'] : 
            Price = max(S0 - X, 0)
            Delta = 1 if S0 - X > 0 else 0
        else : 
            Price = max(-S0 + X, 0)
            Delta = 1 if -S0+X < 0 else 0
        Gamma = Vega = Theta = Rho = 0
    else : 
        d1 = (np.log(F/X) + (0.5 * v * v) * TimeToMaturity)/(v * np.sqrt(TimeToMaturity))       
        d2 = d1 - v * np.sqrt(TimeToMaturity)
        if TypeFlag in [1,'1','c','C'] : 
            Price = (F * CDF_N(d1) - X * CDF_N(d2)) * DiscountFactor
            exp_minusdivt = F / S0 * np.exp(-r_est * TimeToMaturity)
            Delta = exp_minusdivt * CDF_N(d1)
            PDF_Nd1 = np.exp(-d1 * d1/2.0) / np.sqrt(2.0 * np.pi)
            Gamma = exp_minusdivt * PDF_Nd1/(S0 * v * np.sqrt(TimeToMaturity))
            Vega = exp_minusdivt * PDF_Nd1 * S0 * np.sqrt(TimeToMaturity)
            Theta = -exp_minusdivt * 0.5 * S0 * PDF_Nd1 * v / np.sqrt(TimeToMaturity) - r_disc * X * np.exp(-r_disc * TimeToMaturity) * CDF_N(d2)
            Rho = X * TimeToMaturity * np.exp(-r_disc * TimeToMaturity) * CDF_N(d2)
        else : 
            Price = (-F * CDF_N(-d1) + X * CDF_N(-d2)) * DiscountFactor
            exp_minusdivt = F / S0 * np.exp(-r_est * TimeToMaturity)
            Delta = exp_minusdivt * (CDF_N(d1)-1)
            PDF_Nd1 = np.exp(-d1 * d1/2.0) / np.sqrt(2.0 * np.pi)
            Gamma = exp_minusdivt * PDF_Nd1/(S0 * v * np.sqrt(TimeToMaturity))
            Vega = exp_minusdivt * PDF_Nd1 * S0 * np.sqrt(TimeToMaturity)
            Theta = exp_minusdivt * 0.5 * S0 * PDF_Nd1 * v / np.sqrt(TimeToMaturity) + r_disc * X * np.exp(-r_disc * TimeToMaturity) * CDF_N(d2)
            Rho = -X * TimeToMaturity * np.exp(-r_disc * TimeToMaturity) * CDF_N(d2)
    
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[TimeToMaturity, S0, X, r_disc, r_est,ForwardPrice, v, d1, d2, Price, Delta, Gamma, Vega, Theta, Rho]], 
                               columns = ["TimeToMaturity", "S0", "X", "r_disc","r_est","ForwardPrice", "Volatility", "d1", "d2", "Price", "Delta", "Gamma", "Vega", "Theta", "Rho"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)
    return Price, Delta, Gamma, Vega, Theta, Rho, v

def BSDigitalOption(TypeFlag, PriceDate, Maturity, PayDate, S0, X, DiscTerm, DiscRate, RefTerm, RefRate, DivTerm, DivRate, VolTerm, VolParity, Vols2D, QuantoCorr, FXVolTerm, FXVol, DivType, ForwardPrice = 0, LoggingFlag = 0, LoggingDir = os.getcwd()) : 
    T = max(0.00001, DayCountAtoB(PriceDate, Maturity)/365)
    TEnd = T
    TPay = DayCountAtoB(PriceDate, PayDate)/365
    TPay = max(T, TPay)
    Preprocessing_ZeroTermAndRate(DiscTerm, DiscRate, PriceDate)
    Preprocessing_ZeroTermAndRate(RefTerm, RefRate, PriceDate)
    Preprocessing_Term(DivTerm, PriceDate)
    df_tmat_to_pay = Calc_ForwardDiscount_Factor(DiscTerm,DiscRate, T, TPay) if T != TPay else 1
    if (DivType == 0) : 
        dvd = DivRate[0] if ForwardPrice <= 0 else 0
    elif (DivType == 1) : 
        dvd = np.interp(TEnd, DivTerm, DivRate) if ForwardPrice <= 0 else 0
    else : 
        td = np.array(DivTerm)
        dr = np.array(DivRate)
        idx = td <= TEnd
        dvd = 1/TEnd * dr[idx].sum() / S0 if ForwardPrice <= 0 else 0
        
    if isinstance(Vols2D, float) : 
        vol = Vols2D
    else : 
        vol = Linterp2D(VolTerm, VolParity, Vols2D, TEnd, X/S0 if np.array(VolParity).max() < 2.0 else S0)
    
    fxv = np.interp(TEnd, FXVolTerm, FXVol) if len(FXVolTerm) > 0 else 0
    rd = np.interp(TEnd, DiscTerm, DiscRate)
    if ForwardPrice > 0 : 
        rf = 1/TEnd * np.log(ForwardPrice/S0)
    else : 
        if len(RefTerm) > 0 :
            rf = np.interp(TEnd, RefTerm, RefRate)
        else : 
            rf = rd

    DiscreteDivFlag = 0 if DivType != 2 else 1  
    if DiscreteDivFlag == 1 : 
        S0 = S0 - dvd * np.exp(-rd * T)
        dvd = 0

    Rf_Quanto = rf - fxv * vol * QuantoCorr  
    d1 = (np.log(S0 / X) + (Rf_Quanto - dvd + 0.5 * vol * vol) * T) / (vol * np.sqrt(T)) 
    d2 = d1 - vol * np.sqrt(T)
    theta_d2 = -(Rf_Quanto - dvd - 0.5 * vol * vol) / (vol * np.sqrt(T)) + 0.5 * d2 / T
    PDF_ND2 = np.exp(-d2 * d2/2.0) / np.sqrt(2.0 * np.pi)
    if (TypeFlag == 1) : 
        if (X <= 0.0) : 
            Price = np.exp(-rd * T)
            Delta = 0.0
            Gamma = 0.0
            Vega = 0.0
            Theta = dvd * S0 * np.exp(-dvd * T) - rd * X * np.exp(-rd * T)
            Rho = X * T * np.exp(-r * T)
        else : 
            Price = np.exp(-rd * T) * CDF_N(d2) 
            Delta = np.exp(-rd * T) * PDF_ND2 / (vol * np.sqrt(T) * S0)
            Gamma = -np.exp(-rd * T) * PDF_ND2 / (vol * vol * (T)*S0 * S0) * (d2 + (vol * np.sqrt(T)))
            Vega = -np.exp(-rd * T) * PDF_ND2 * (np.sqrt(T) + d2 / vol)
            Theta = np.exp(-rd * T) * (Rf_Quanto * CDF_N(d2) + PDF_ND2 * theta_d2)
            Rho = -np.exp(-rd * T) * (T * CDF_N(d2) - PDF_ND2 * np.sqrt(T) / vol)
    else : 
        if X <= 0.0 : 
            Price = 0.0
            Delta = 0.0
            Gamma = 0.0
            Vega = 0.0
            Theta = 0.0
            Rho = 0.0         
        else :
            Price = np.exp(-rd * T) * CDF_N(-d2)
            Delta = -np.exp(-rd * T) * PDF_ND2 / (vol * np.sqrt(T) * S0)
            Gamma = np.exp(-rd * T) * PDF_ND2 / (vol * vol * (T)*S0 * S0) * (d2 + (vol * np.sqrt(T)))
            Vega = np.exp(-rd * T)* PDF_ND2* (np.sqrt(T) + d2 / vol)
            Theta = np.exp(-rd * T) * (Rf_Quanto * CDF_N(-d2) - PDF_ND2 * theta_d2)
            Rho = -((np.exp(-rd * T) * (PDF_ND2 * np.sqrt(T) / vol - T * CDF_N(-1.0 * d2))))
    Price *= df_tmat_to_pay
    Delta *= df_tmat_to_pay
    Gamma *= df_tmat_to_pay
    Vega *= df_tmat_to_pay
    Theta *= df_tmat_to_pay
    Rho *= df_tmat_to_pay
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[T, S0, X, rd, Rf_Quanto,ForwardPrice, vol, d1, d2, Price, Delta, Gamma, Vega, Theta, Rho]], 
                               columns = ["TimeToMaturity", "S0", "X", "r_disc","r_est","ForwardPrice", "Volatility", "d1", "d2", "Price", "Delta", "Gamma", "Vega", "Theta", "Rho"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)

    return Price, Delta, Gamma, Vega, Theta, Rho, vol

def Sumation_Beta(StartIDX, EndIDX, ForwardArray, WeightArray) : 
    return (ForwardArray[StartIDX:EndIDX+1] * WeightArray[StartIDX:EndIDX+1]).sum()

def Arithmetic_Asian_Opt_m1(N, WeightArray, ForwardArray) : 
    return Sumation_Beta(0, N-1, ForwardArray, WeightArray)

def Arithmetic_Asian_Opt_m2(n, Forward, Weight, T, TermVol, Vol):
    TauAry = T[:n]
    SigAry = np.interp(TauAry, TermVol, Vol)
    eAry = np.exp(SigAry * SigAry * TauAry)
    BetaAry = Forward[:n] * Weight[:n]
    SumBetaFunc = np.vectorize(lambda i : Sumation_Beta(i, n - 1, Forward[:n], Weight[:n]))
    SumBetaAry = SumBetaFunc(np.arange(0,n))
    value1 = 2.0 * (BetaAry * eAry * SumBetaAry).sum()
    value2 = (BetaAry * BetaAry * eAry).sum()
    m2 = value1 - value2
    return m2

def Arithmetic_Asian_Opt_m3(n, Forward, Weight, T, TermVol, Vol):
    m3 = 0.0
    TauAry = T[:n]
    SigAry = np.interp(TauAry, TermVol, Vol)
    eAry = np.exp(SigAry * SigAry * TauAry)
    BetaAry = Forward[:n] * Weight[:n]
    SumBetaFunc = np.vectorize(lambda i : Sumation_Beta(i, n - 1, Forward[:n], Weight[:n]))
    SumBetaAry = SumBetaFunc(np.arange(0,n))
    V1Ary = (BetaAry * BetaAry * eAry)
    V2Ary = 3.0 * (BetaAry * eAry * SumBetaAry)
    for i in range(n):
        e_i = eAry[i]
        b_i = BetaAry[i]
        V1 = V1Ary[i]
        V2 = V2Ary[i]
        j_ary = np.arange(i, n)
        V3 = 3.0 * (BetaAry[j_ary] * BetaAry[j_ary] * eAry[j_ary]).sum()
        SumBetaAry2 = SumBetaFunc(j_ary)
        V4 = 6.0 * (BetaAry[j_ary] * eAry[j_ary] * SumBetaAry2).sum()        
        m3 += 2.0 * b_i * e_i * e_i * (V1 - V2 - V3 + V4)

    return m3

def Arithmetic_Asian_Option_Delta(n, Forward, Weight, T, TermVol, Vol, r, y1, y11, d1):
    delta = 0.0
    PDF_ND1 = np.exp(-d1 * d1/2.0) / np.sqrt(2.0 * np.pi)
    for i in range(n):
        sumaFe = 0.0
        for k in range(i) :
            v = np.interp(T[k], TermVol, Vol)
            sumaFe += Weight[k] * Forward[k] * np.exp(v * v * T[k])

        v = np.interp(T[i], TermVol, Vol)
        sumaF = 0.0
        for k in range(i, n):
            sumaF += Weight[k] * Forward[k] * np.exp(v * v * T[i])

        sqrt_log_term = np.sqrt(np.log(y11 / (y1 * y1)))
        delta_i = Weight[i] * np.exp(-r * T[n - 1]) * (CDF_N(d1) + y1 * PDF_ND1 * y1 * y1 / (sqrt_log_term * y11) * ((sumaFe + sumaF) / y11 - 1.0 / y1))
        delta += delta_i
    return delta

def Arithmetic_Asian_Option_Vega(n, Forward, Weight, T, TermVol, Vol, r, y1, y11, d1):
    vega = 0.0
    PDF_ND1 = np.exp(-d1 * d1/2.0) / np.sqrt(2.0 * np.pi)
    for i in range(n):
        sumaF = 0.0
        for j in range(i + 1, n):
            sumaF += 2.0 * Weight[j] * Forward[j]

        aF_i = Weight[i] * Forward[i]
        v = np.interp(T[i], TermVol, Vol) 
        sqrt_log_term = np.sqrt(np.log(y11 / (y1 * y1)))
        vega_i = ((sumaF + aF_i) * Weight[i] * Forward[i] * np.exp(v * v * T[i]) * v * T[i]* np.exp(-r * T[n - 1]) * (PDF_ND1 / ((y11 / y1) * sqrt_log_term)))
        vega += vega_i
    return vega

def Arithmetic_Asian_Opt_Pricing(
    n, Forward, Weight, T, TermVol, Vol,
    PrevCummulative_Weight, Strike, PrevAverage,
    Call0Put1, T_Option, TermRate, Rate
):
    m1 = Arithmetic_Asian_Opt_m1(n, Weight, Forward)
    m2 = Arithmetic_Asian_Opt_m2(n, Forward, Weight, T, TermVol, Vol)
    m3 = Arithmetic_Asian_Opt_m3(n, Forward, Weight, T, TermVol, Vol)

    mu1 = m1
    mu2 = m2 - mu1 * mu1
    mu3 = m3 - 3.0 * mu1 * mu2 - mu1 ** 3

    z = (0.5 * mu3 + 0.5 * np.sqrt(mu3 * mu3 + 4.0 * mu2 ** 3)) ** (1.0 / 3.0)
    y1 = mu1  # original comment: mu2 / (z - mu2 / z)
    y11 = mu2 + y1 * y1
    E = mu1 - y1

    r_disc = np.interp(T_Option, TermRate, Rate)
    intrinsic = Strike - PrevCummulative_Weight * PrevAverage - E

    if intrinsic <= 0:
        if Call0Put1 == 0:  # Call
            value = np.exp(-r_disc * T_Option) * (y1 - intrinsic)
        else:  # Put
            value = 0.0
    else:
        d1 = np.log(np.sqrt(y11) / intrinsic) / np.sqrt(np.log(y11 / (y1 * y1)))
        d2 = d1 - np.sqrt(np.log(y11 / (y1 * y1)))

        if Call0Put1 == 0:  # Call
            value = np.exp(-r_disc * T_Option) * (y1 * CDF_N(d1) - intrinsic * CDF_N(d2))
        else:  # Put
            value = np.exp(-r_disc * T_Option) * (intrinsic * CDF_N(-d2) - y1 * CDF_N(-d1))

    delta = Arithmetic_Asian_Option_Delta(n, Forward, Weight, T, TermVol, Vol, r_disc, y1, y11, d1)
    vega = Arithmetic_Asian_Option_Vega(n, Forward, Weight, T, TermVol, Vol, r_disc, y1, y11, d1)
    return value, delta, vega

def Arithmetic_Asian_Opt_Pricing_Preprocessing(Long0Short1, Call0Put1, PriceDate, AverageStartDate, AverageEndDate, OptionMaturityDate, S, K, PrevAverage, DiscTerm, DiscRate, DivTerm, DivRate, QuantoCorr, FXVolTerm, FXVol, VolTerm, VolParity, Vols2D, DivTypeFlag, Holidays, ForwardTerm = [], ForwardPrice = []) : 
    T_Opt = DayCountAtoB(PriceDate, OptionMaturityDate)/365
    PrevCummulativeWeight = 0
    NDays = DayCountAtoB(AverageStartDate, AverageEndDate) + 1
    StartDateExcel = YYYYMMDDToExcelDate(AverageStartDate)
    N_BD_Avg = 0
    for i in range(NDays) : 
        MOD7 = (StartDateExcel + i) % 7
        YYYYMMDD = ExcelDateToYYYYMMDD(StartDateExcel + i)
        isHolidayFlag = YYYYMMDD in Holidays
        if ((MOD7 == 1 or MOD7 == 0) or isHolidayFlag == 1) :
            SaturSundayFlag = 1
        else : 
            SaturSundayFlag = 0
        
        if SaturSundayFlag != 1 : 
            N_BD_Avg += 1
    
    AvgDate = np.zeros(max(1, NDays))
    j = 0
    for i in range(NDays) : 
        MOD7 = (StartDateExcel + i) % 7
        YYYYMMDD = ExcelDateToYYYYMMDD(StartDateExcel + i)
        isHolidayFlag = YYYYMMDD in Holidays
        if ((MOD7 == 1 or MOD7 == 0) or isHolidayFlag == 1) :
            SaturSundayFlag = 1
        else : 
            SaturSundayFlag = 0
        
        if SaturSundayFlag != 1 : 
            AvgDate[j] = YYYYMMDD
            j += 1
            
    NPrev, NForward = 0, 0
    for i in range(N_BD_Avg) : 
        if AvgDate[i] <= PriceDate : 
            NPrev += 1
        else : 
            NForward += 1
    
    ForwardDate = np.zeros(max(1, NForward))
    j = 0
    for i in range(N_BD_Avg) : 
        if AvgDate[i] > PriceDate : 
            ForwardDate[j] = AvgDate[i]
            j += 1    
    
    w = 1/NForward
    Weight = np.array([w] * NForward)
    PrevCummulativeWeight = NPrev/N_BD_Avg
    TimeAry = np.vectorize(DayCountAtoB)([PriceDate],ForwardDate)/365
    if len(ForwardTerm) == 0 : 
        R_Ref = np.interp(TimeAry, DiscTerm, DiscRate)
    else : 
        Preprocessing_Term(ForwardTerm, PriceDate)
        RefTerm = ForwardTerm
        RefRate = (TimeAry[i] > 0) * np.log(np.array(ForwardPrice)/S)/ForwardTerm 
        R_Ref = np.interp(TimeAry, RefTerm, RefRate)       
         
    DivAry = np.interp(TimeAry, DivTerm, DivRate)
    FXVolAry = np.interp(TimeAry, FXVolTerm, FXVol) if len(FXVolTerm) > 0 else 0

    if isinstance(Vols2D, float) :
        Vol = np.array([Vols2D] * NForward)
    else : 
        TempFunc = np.vectorize(lambda Times : Linterp2D(VolTerm, VolParity, Vols2D, Times, K/S))
        Vol = TempFunc(TimeAry)
    Forward = S * np.exp((R_Ref - DivAry - (abs(QuantoCorr) > 0.0001) * QuantoCorr * FXVolAry * Vol) * TimeAry)
    price, delta, vega = Arithmetic_Asian_Opt_Pricing(NForward, Forward, Weight, TimeAry, TimeAry, Vol, PrevCummulativeWeight, K, PrevAverage, Call0Put1, T_Opt, DiscTerm, DiscRate)
    priceu, deltau, vegau = Arithmetic_Asian_Opt_Pricing(NForward, Forward * 1.01, Weight, TimeAry, TimeAry, Vol, PrevCummulativeWeight, K, PrevAverage, Call0Put1, T_Opt, DiscTerm, DiscRate)
    gamma = (deltau - delta) / (S * 0.01)
    if Long0Short1 == 0 : 
        return price, delta, gamma, vega, 0, 0, Vol.mean()        
    else : 
        return -price, -delta, -gamma, -vega, 0, 0, Vol.mean()        
        
def BS_Swaption(PriceDate, StartDate, SwapTenorT, NCpnOneYear, Notional, Vol, StrikePrice, Term, Rate, DayCountFracFlag = 0, VolFlag = 0, HolidaysFixing = [], HolidaysPay = [], NBDayFromEndDateToPay = 0, FixedPayer0Receiver1 = 0) : 
    FixedPayerFlag = FixedPayer0Receiver1
    if StrikePrice > 1.0 : 
        StrikePrice /= 100
    
    if (PriceDate < 19000101) :
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
    
    if (StartDate < 19000101) : 
        StartDate = ExcelDateToYYYYMMDD(StartDate)

    Preprocessing_ZeroTermAndRate(Term, Rate, PriceDate)

    T_Option = float(DayCountAtoB(PriceDate, StartDate))/365
    if (SwapTenorT < 10000) : 
        SwapMaturity = EDate_YYYYMMDD(StartDate, int(SwapTenorT * 12 + 0.00001))
    elif (SwapTenorT < 19000101) : 
        SwapMaturity = ExcelDateToYYYYMMDD(SwapTenorT)
    else : 
        SwapMaturity = SwapTenorT
     
    Start, End, Pay, NBD = MappingCouponDates(1,StartDate,SwapMaturity,NBDayFromEndDateToPay, NCpnOneYear,1,HolidaysFixing,HolidaysPay,1) 
    T_Option = max(0.0000285388, T_Option)
    ForwardSwapRate = FSR(PriceDate, StartDate,SwapMaturity, NCpnOneYear, DayCountFracFlag, HolidaysFixing, Term, Rate, Term, Rate)        
    annuity = 0
    for i in range(len(End)) : 
        if i == 0 : 
            dt = DayCountFractionAtoB(StartDate, End[i], DayCountFracFlag, HolidaysPay)
        else : 
            dt = DayCountFractionAtoB(End[i-1], End[i], DayCountFracFlag, HolidaysPay)
        t_pay = (float(DayCountAtoB(PriceDate, Pay[i] if NBDayFromEndDateToPay > 0 else End[i]))) / 365.0
        annuity += dt * Calc_Discount_Factor(Term, Rate, t_pay)
    
    value, value_atm = 0,0
    if (VolFlag == 0) : 
        d1 = (np.log(ForwardSwapRate / StrikePrice) + 0.5 * Vol * Vol * T_Option) / (Vol * np.sqrt(T_Option))
        d2 = d1 - Vol * np.sqrt(T_Option)

        d1_atm = 0.5 * Vol * np.sqrt(T_Option)
        d2_atm = -0.5 * Vol * np.sqrt(T_Option)
        if (PriceDate != StartDate) :
            if (FixedPayerFlag == 0) : 
                value = max(annuity * (ForwardSwapRate * CDF_N(d1) - StrikePrice * CDF_N(d2)), 0.0)
                value_atm = annuity * (ForwardSwapRate * CDF_N(d1_atm) - ForwardSwapRate * CDF_N(d2_atm))
            else :                 
                value = max(annuity * (-ForwardSwapRate * CDF_N(-d1) + StrikePrice * CDF_N(-d2)), 0.0)
                value_atm = annuity * (-ForwardSwapRate * CDF_N(-d1_atm) + ForwardSwapRate * CDF_N(-d2_atm))
        else : 
            if (FixedPayerFlag == 0) : 
                value = annuity * max(ForwardSwapRate - StrikePrice, 0.0)
                value_atm = 0.0
            else :
                value = annuity * max(-ForwardSwapRate + StrikePrice, 0.0)
                value_atm = 0.0
    else : 
        d1 = (ForwardSwapRate - StrikePrice) / (Vol * np.sqrt(T_Option))
        d1_atm = 0.0
        if (PriceDate != StartDate) :
            if (FixedPayerFlag == 0) : 
                value = max(annuity * ((ForwardSwapRate - StrikePrice) * CDF_N(d1) + Vol * np.sqrt(T_Option) * (np.exp(-d1 * d1 / 2.0) / 2.506628274631)), 0.0)
                value_atm = annuity * Vol * np.sqrt(T_Option) * (np.exp(-d1_atm * d1_atm / 2.0) / 2.506628274631)
            else :                 
                c_value = max(annuity * ((ForwardSwapRate - StrikePrice) * CDF_N(d1) + Vol * np.sqrt(T_Option) * (np.exp(-d1 * d1 / 2.0) / 2.506628274631)), 0.0)
                value_atm = annuity * Vol * np.sqrt(T_Option) * (np.exp(-d1_atm * d1_atm / 2.0) / 2.506628274631)
                value = max(0.0 , annuity * (StrikePrice - ForwardSwapRate) + c_value)
        else : 
            if (FixedPayerFlag == 0) : 
                value = annuity * max(ForwardSwapRate - StrikePrice, 0.0)
            else :             
                value = annuity * max(-ForwardSwapRate + StrikePrice, 0.0)
            value_atm = 0

    ExerciseValue = (ForwardSwapRate - StrikePrice) * annuity
    MyDict = {"Price":Notional * value,"Value":Notional*(value - value_atm), "ForwardSwapRate":ForwardSwapRate,"ExerciseValue":ExerciseValue}
    return MyDict

def calc_mu(b, sigma):
    return (b - 0.5 * sigma ** 2) / (sigma ** 2)

def calc_lambda(mu, r, sigma):
    return np.sqrt(mu ** 2 + 2.0 * r / (sigma ** 2))

def calc_z(H, K, sigma, T, Lambda):
    return np.log(H / K) / (sigma * np.sqrt(T)) + Lambda * sigma * np.sqrt(T)

def calc_x1(S, K, sigma, T, mu):
    return np.log(S / K) / (sigma * np.sqrt(T)) + (1.0 + mu) * sigma * np.sqrt(T)

def calc_x2(S, H, sigma, T, mu):
    return np.log(S / H) / (sigma * np.sqrt(T)) + (1.0 + mu) * sigma * np.sqrt(T)

def calc_y1(S, H, K, sigma, T, mu):
    return np.log(H * H / (S * K)) / (sigma * np.sqrt(T)) + (1.0 + mu) * sigma * np.sqrt(T)

def calc_y2(S, H, sigma, T, mu):
    return np.log(H / S) / (sigma * np.sqrt(T)) + (1.0 + mu) * sigma * np.sqrt(T)

def calc_A(phi, S, b, T, x1, X, r, sigma):
    return phi * S * np.exp((b - r) * T) * CDF_N(phi * x1) - phi * X * np.exp(-r * T) * CDF_N(phi * x1 - phi * sigma * np.sqrt(T))

def calc_B(phi, S, b, T, x2, K, r, sigma):
    return phi * S * np.exp((b - r) * T) * CDF_N(phi * x2) - phi * K * np.exp(-r * T) * CDF_N(phi * x2 - phi * sigma * np.sqrt(T))

def calc_C(phi, S, b, T, H, mu, n, y1, K, r, sigma):
    return phi * S * np.exp((b - r) * T) * (H / S) ** (2 * (mu + 1.0)) * CDF_N(n * y1) - phi * K * np.exp(-r * T) * (H / S) ** (2 * mu) * CDF_N(n * y1 - n * sigma * np.sqrt(T))

def calc_D(phi, S, b, T, H, mu, n, y2, K, r, sigma):
    return phi * S * np.exp((b - r) * T) * (H / S) ** (2 * (mu + 1.0)) * CDF_N(n * y2) - phi * K * np.exp(-r * T) * (H / S) ** (2 * mu) * CDF_N(n * y2 - n * sigma * np.sqrt(T))

def calc_E(Reb, r, T, n, x2, sigma, H, S, mu, y2):
    return Reb * np.exp(-r * T) * (CDF_N(n * x2 - n * sigma * np.sqrt(T)) - (H / S) ** (2.0 * mu) * CDF_N(n * y2 - n * np.sqrt(T)))

def calc_F(Reb, H, S, mu, Lambda, n, z, sigma, T):
    return Reb * ((H / S) ** (mu + Lambda) * CDF_N(n * z) + (H / S) ** (mu - Lambda) * CDF_N(n * z - 2.0 * n * Lambda * sigma * np.sqrt(T)))

def C_out(n, x1, x2, y1, y2, A, B, C, D, S, X, H):
    if n == 1:
        return A - C if X > H else B - D
    else:
        return 0.0 if X > H else A - B + C - D

def P_out(n, x1, x2, y1, y2, A, B, C, D, S, X, H):
    if n == 1:
        return A - B + C - D if X > H else 0.0
    else:
        return B - D if X > H else A - C

def SimpleBSCall(S, K, b, T, q, r, sigma):
    d1 = (np.log(S / K) + (b + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * np.exp((b - r - q) * T) * CDF_N(d1) - K * np.exp(-r * T) * CDF_N(d2)

def SimpleBSPut(S, K, b, T, q, r, sigma):
    d1 = (np.log(S / K) + (b + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * CDF_N(-d2) - S * np.exp((b - r - q) * T) * CDF_N(-d1)

def Call_Down(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb = 0, LoggingFlag = 0, LoggingDir = ''):
    Sigma, r, phi, n = sig, r_disc, 1, 1
    b = r_ref - rho_fx * fxvol * sig - (0 if DiscreteDivFlag == 1 else div)
    if DiscreteDivFlag == 1:
        S -= div

    mu = calc_mu(b, Sigma)
    lambda_ = calc_lambda(mu, r, Sigma)
    z = calc_z(H, X, Sigma, T, lambda_)
    x1, x2 = calc_x1(S, X, Sigma, T, mu), calc_x2(S, H, Sigma, T, mu)
    y1, y2 = calc_y1(S, H, X, Sigma, T, mu), calc_y2(S, H, Sigma, T, mu)

    A = calc_A(phi, S, b, T, x1, X, r, Sigma)
    B = calc_B(phi, S, b, T, x2, X, r, Sigma)
    C = calc_C(phi, S, b, T, H, mu, n, y1, X, r, Sigma)
    D = calc_D(phi, S, b, T, H, mu, n, y2, X, r, Sigma)
    E = calc_E(Reb, r, T, n, x2, Sigma, H, S, mu, y2) if Reb != 0 else 0
    F = calc_F(Reb, H, S, mu, lambda_, n, z, Sigma, T) if Reb != 0 else 0

    c_do = A - C + F if X > H else B - D + F
    c_di = SimpleBSCall(S, X, b, T, div if DiscreteDivFlag == 0 else 0, r, Sigma) - c_do
    Price = c_di if in0out1flag == 0 else c_do 
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[Price, T, S, X, b, sig, A,B,C,D,E,F]], 
                               columns = ["Price","T", "S", "X", "b", "sig", "A","B","C","D","E","F"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)

    return c_di if in0out1flag == 0 else c_do

def Put_Down(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb = 0, LoggingFlag = 0, LoggingDir = ''):
    Sigma, r, phi, n = sig, r_disc, -1, 1
    b = r_ref - rho_fx * fxvol * sig - (0 if DiscreteDivFlag == 1 else div)
    if DiscreteDivFlag == 1:
        S -= div

    mu = calc_mu(b, Sigma)
    lambda_ = calc_lambda(mu, r, Sigma)
    z = calc_z(H, X, Sigma, T, lambda_)
    x1, x2 = calc_x1(S, X, Sigma, T, mu), calc_x2(S, H, Sigma, T, mu)
    y1, y2 = calc_y1(S, H, X, Sigma, T, mu), calc_y2(S, H, Sigma, T, mu)

    A = calc_A(phi, S, b, T, x1, X, r, Sigma)
    B = calc_B(phi, S, b, T, x2, X, r, Sigma)
    C = calc_C(phi, S, b, T, H, mu, n, y1, X, r, Sigma)
    D = calc_D(phi, S, b, T, H, mu, n, y2, X, r, Sigma)
    E = calc_E(Reb, r, T, n, x2, Sigma, H, S, mu, y2) if Reb != 0 else 0
    F = calc_F(Reb, H, S, mu, lambda_, n, z, Sigma, T) if Reb != 0 else 0

    p_do = A - B + C - D + F if X > H else F
    p_di = SimpleBSPut(S, X, b, T, div if DiscreteDivFlag == 0 else 0, r, Sigma) - p_do
    Price = p_di if in0out1flag == 0 else p_do
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[Price, T, S, X, b, sig, A,B,C,D,E,F]], 
                               columns = ["Price","T", "S", "X", "b", "sig", "A","B","C","D","E","F"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)

    return p_di if in0out1flag == 0 else p_do

def Call_Up(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb = 0, LoggingFlag = 0, LoggingDir = ''):
    Sigma, r, phi, n = sig, r_disc, 1, -1
    b = r_ref - rho_fx * fxvol * sig - (0 if DiscreteDivFlag == 1 else div)
    if DiscreteDivFlag == 1:
        S -= div

    mu = calc_mu(b, Sigma)
    lambda_ = calc_lambda(mu, r, Sigma)
    z = calc_z(H, X, Sigma, T, lambda_)
    x1, x2 = calc_x1(S, X, Sigma, T, mu), calc_x2(S, H, Sigma, T, mu)
    y1, y2 = calc_y1(S, H, X, Sigma, T, mu), calc_y2(S, H, Sigma, T, mu)

    A = calc_A(phi, S, b, T, x1, X, r, Sigma)
    B = calc_B(phi, S, b, T, x2, X, r, Sigma)
    C = calc_C(phi, S, b, T, H, mu, n, y1, X, r, Sigma)
    D = calc_D(phi, S, b, T, H, mu, n, y2, X, r, Sigma)
    E = calc_E(Reb, r, T, n, x2, Sigma, H, S, mu, y2) if Reb != 0 else 0
    F = calc_F(Reb, H, S, mu, lambda_, n, z, Sigma, T) if Reb != 0 else 0

    c_uo = F if X > H else A - B + C - D + F
    c_ui = SimpleBSCall(S, X, b, T, div if DiscreteDivFlag == 0 else 0, r, Sigma) - c_uo
    Price = c_ui if in0out1flag == 0 else c_uo
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[Price, T, S, X, b, sig, A,B,C,D,E,F]], 
                               columns = ["Price","T", "S", "X", "b", "sig", "A","B","C","D","E","F"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)
    
    return c_ui if in0out1flag == 0 else c_uo

def Put_Up(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb = 0, LoggingFlag = 0, LoggingDir = ''):
    Sigma, r, phi, n = sig, r_disc, -1, -1
    b = r_ref - rho_fx * fxvol * sig - (0 if DiscreteDivFlag == 1 else div)
    if DiscreteDivFlag == 1:
        S -= div

    mu = calc_mu(b, Sigma)
    lambda_ = calc_lambda(mu, r, Sigma)
    z = calc_z(H, X, Sigma, T, lambda_)
    x1, x2 = calc_x1(S, X, Sigma, T, mu), calc_x2(S, H, Sigma, T, mu)
    y1, y2 = calc_y1(S, H, X, Sigma, T, mu), calc_y2(S, H, Sigma, T, mu)

    A = calc_A(phi, S, b, T, x1, X, r, Sigma)
    B = calc_B(phi, S, b, T, x2, X, r, Sigma)
    C = calc_C(phi, S, b, T, H, mu, n, y1, X, r, Sigma)
    D = calc_D(phi, S, b, T, H, mu, n, y2, X, r, Sigma)
    E = calc_E(Reb, r, T, n, x2, Sigma, H, S, mu, y2) if Reb != 0 else 0
    F = calc_F(Reb, H, S, mu, lambda_, n, z, Sigma, T) if Reb != 0 else 0

    p_uo = B - D + F if X > H else A - C + F
    p_ui = SimpleBSPut(S, X, b, T, div if DiscreteDivFlag == 0 else 0, r, Sigma) - p_uo
    Price = p_ui if in0out1flag == 0 else p_uo
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[Price, T, S, X, b, sig, A,B,C,D,E,F]], 
                               columns = ["Price","T", "S", "X", "b", "sig", "A","B","C","D","E","F"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)
    
    return p_ui if in0out1flag == 0 else p_uo

def BarrierOptionGreek(
    in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol,
    DiscreteDivFlag, div, sig, Reb, pricing_function
):
    Su = S * 1.01
    Sd = S * 0.99
    dS = S * 0.01

    Pu = pricing_function(in0out1flag, Su, X, H, T, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    Pd = pricing_function(in0out1flag, Sd, X, H, T, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    P = pricing_function(in0out1flag, S, X, H, T, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    sigu = sig + 0.01
    sigd = max(sig - 0.01,0.00001)
    Delta = (Pu - Pd) / (2.0 * dS) 
    Gamma = (Pu + Pd -2.0 * P) / (dS * dS)
    Pvu = pricing_function(in0out1flag, S, X, H, T, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sigu, Reb)
    Pvd = pricing_function(in0out1flag, S, X, H, T, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sigd, Reb)
    Vega = (Pvu - Pvd) / ((sigu-sigd))
    Pru = pricing_function(in0out1flag, S, X, H, T, r_disc+0.0001, r_ref+0.0001,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    Prd = pricing_function(in0out1flag, S, X, H, T, r_disc-0.0001, r_ref-0.0001,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    Rho = (Pru - Prd) / (0.0001 * 2)
    T_u = T + 1.0 / 365.0
    T_d = max(T - 1.0 / 365.0,0.00001)
    Ptu = pricing_function(in0out1flag, S, X, H, T_u, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    Ptd = pricing_function(in0out1flag, S, X, H, T_d, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    Theta = (Ptu - Ptd) / (T_u-T_d)
    return Delta, Gamma, Vega, Theta, Rho

def BSBarrierOption(PriceDate, Call1Put2, S0, X, H, ZeroDiscTerm, 
                    ZeroDiscRate, ZeroRefTerm, ZeroRefRate, DivTerm, DivRate, 
                    QuantoCorr, FXVolTerm, FXVol, VolTerm, VolParity, 
                    Vols2D, DivType, Maturity, PayDate, Down0Up1Flag, In0Out1Flag, Reb = 0, ForwardPrice = 0, LoggingFlag = 0, LoggingDir = os.getcwd()) : 
    Preprocessing_ZeroTermAndRate(ZeroDiscTerm, ZeroDiscRate, PriceDate)
    if isinstance(Vols2D, float) == False : 
        if len(np.array(Vols2D).shape) == 2 : 
            Preprocessing_EQVol(VolParity, VolTerm, Vols2D, PriceDate, S0)
        else : 
            Vols1D = np.array(Vols2D).reshape(-1)
            Preprocessing_ZeroTermAndRate(VolTerm, Vols1D, PriceDate, 6)
            Vols2D = Vols1D.reshape(1,-1)
            VolParity = [1]
    TEnd = DayCountAtoB(PriceDate, Maturity)/365
    TPay = max(TEnd, DayCountAtoB(PriceDate, PayDate)/365)
    
    TEnd = max(0.00001, TEnd)
    TPay = max(0.00001, TPay)
    fdf = Calc_ForwardDiscount_Factor(ZeroDiscTerm, ZeroDiscRate, TEnd, TPay) if TEnd != TPay else 1
    if (DivType == 0) : 
        dvd = DivRate[0] if ForwardPrice <= 0 else 0
    elif (DivType == 1) : 
        dvd = np.interp(TEnd, DivTerm, DivRate) if ForwardPrice <= 0 else 0
    else : 
        td = np.array(DivTerm)
        dr = np.array(DivRate)
        idx = td <= TEnd
        dvd = 1/TEnd * dr[idx].sum() / S0 if ForwardPrice <= 0 else 0
        
    if isinstance(Vols2D, float) : 
        vol = Vols2D
    else : 
        vol = Linterp2D(VolTerm, VolParity, Vols2D, TEnd, X/S0 if np.array(VolParity).max() < 2.0 else S0)
    
    fxv = np.interp(TEnd, FXVolTerm, FXVol) if len(FXVolTerm) > 0 else 0
    rd = np.interp(TEnd, ZeroDiscTerm, ZeroDiscRate)
    if ForwardPrice > 0 : 
        rf = 1/TEnd * np.log(ForwardPrice/S0)
    else : 
        if len(ZeroRefTerm) > 0 :
            rf = np.interp(TEnd, ZeroRefTerm, ZeroRefRate)
        else : 
            rf = rd

    DiscreteDivFlag = 0 if DivType != 2 else 1
    if Call1Put2 == 1 : 
        if Down0Up1Flag == 0 : 
            PricingFunction = Call_Down
        else : 
            PricingFunction = Call_Up                        
    else : 
        if Down0Up1Flag == 0 : 
            PricingFunction = Put_Down            
        else : 
            PricingFunction = Put_Up            
    P = PricingFunction(In0Out1Flag, S0, X, H, TEnd, rd, rf, QuantoCorr, fxv, DiscreteDivFlag, dvd, vol, Reb,LoggingFlag, LoggingDir)                        
    Delta, Gamma, Vega, Theta, Rho = BarrierOptionGreek(In0Out1Flag, S0, X, H, TEnd, rd, rf, QuantoCorr, fxv, DiscreteDivFlag, dvd, vol, Reb, PricingFunction)

    return P*fdf, Delta*fdf, Gamma*fdf, Vega*fdf, Theta*fdf, Rho*fdf, vol

def HW_Integral_ShortRate_Vol(t, A, kappa, tVol, Vol) : 
    '''
    Calculate Volatility of Integral ShortRate from 0 to t
    I(t) = Int_0^t sigma(s)^2 A exp(ks) ds
    '''
    NodeNumber = 10.0
    ds = t/NodeNumber
    value = 0.0
    nVol = len(tVol)
    if nVol == 1 :
        value = A * Vol[0] * Vol[0] / (kappa) * (np.exp(kappa * t) - 1.0)
    else : 
        #for i in range(nVol) : 
        #    s = float(i+1) * ds
        #    v = np.interp(s, tVol, Vol)
        #    print(v)
        #    value += v * v * A * np.exp(kappa * s) * ds
        NodeNumber = 10
        Node = np.linspace(0, t, NodeNumber+1)
        u = (Node[1:] + Node[:-1])/2
        du = Node[1:] - Node[:-1]
        MyFunc = np.vectorize(lambda t : Linterp(tVol, Vol, t, 1))
        v = MyFunc(u)
        value = (v * v * A * np.exp(kappa * u) * du).sum()        
    return value 

def B_s_to_t(s, t, kappa) : 
    return (1.0 - np.exp(-kappa * (t-s)))/kappa if kappa != 0 else 1

def V_t_T(k1, k2, t, T, v1, v2) : 
    return v1 * v2 / (k1 * k2) * (T - t + (np.exp(-k1 * (T-t)) - 1.0)/k1 + (np.exp(-k2 * (T-t)) - 1.0)/k2 - (np.exp(-(k1+k2)*(T-t))-1.0)/(k1+k2))

#def V_t_T2(k1, k2, t, T, tVol1, Vol1, tVol2, Vol2) : 
#    NInteg = 10
#    MySpace = np.linspace(0, t, NInteg + 1)
#    u = (MySpace[:-1] + MySpace[1:])/2
#    v1 = np.interp(u, tVol1, Vol1)
#    v2 = np.interp(u, tVol2, Vol2)
#    du = MySpace[1:] - MySpace[:-1]
#    Bst1 = B_s_to_t(u, t, k1)
#    Bst2 = B_s_to_t(u, t, k2)
#    BsT1 = B_s_to_t(u, T, k1)
#    BsT2 = B_s_to_t(u, T, k2)
#    RHS = (v1 * v2 * (Bst1 * Bst2 - BsT1 * BsT2) * du).sum()
#    #RHS = (v1 * v2 * (1-np.exp(-k1 * (T-u)))/k1 * (1-np.exp(-k2 * (T-u)))/k2 * du).sum()
#    return RHS

def V_t_T2(k1, k2, t, T, tVol1, Vol1, tVol2, Vol2) : 
    NInteg = 10
    MySpace = np.linspace(t, T, NInteg + 1)
    u = (MySpace[:-1] + MySpace[1:])/2
    v1 = np.interp(u, tVol1, Vol1)
    v2 = np.interp(u, tVol2, Vol2)
    du = MySpace[1:] - MySpace[:-1]
    RHS = (v1 * v2 * (1-np.exp(-k1 * (T-u)))/k1 * (1-np.exp(-k2 * (T-u)))/k2 * du).sum()
    return RHS

def hw_variance_closed_form(alpha, sigma, t, T):
    if alpha <= 0:
        raise ValueError("Alpha must be positive")

    term1 = (1 - np.exp(-alpha * t)) / alpha
    term2 = (np.exp(-alpha * (T - t)) - np.exp(-alpha * T)) / alpha
    term3 = (1 - np.exp(-2 * alpha * t)) / (2 * alpha)
    term4 = (np.exp(-2 * alpha * (T - t)) - np.exp(-2 * alpha * T)) / (2 * alpha)

    result = (sigma ** 2 / alpha ** 2) * (-2 * (term1 - term2) + (term3 - term4))
    return result

#def HWQVTerm(t, T, kappa, HWVolTerm, HWVol) : 
#    RHS = 0
#    if len(HWVol) == 1 or kappa > 0.25 : 
#        v = np.interp(t, HWVolTerm, HWVol)
#        RHS = 0.5 * (hw_variance_closed_form(kappa, VegaRiskWeight, t, T))
#    else : 
#        RHS = 0.5 * V_t_T2(kappa, kappa, t, T, HWVolTerm, HWVol, HWVolTerm, HWVol)
#    return RHS        

def HWQVTerm(t, T, kappa, HWVolTerm, HWVol) : 
    RHS = 0
    if len(HWVol) == 1 or kappa > 0.25 : 
        v = np.interp((t+T)/2, HWVolTerm, HWVol)
        V_1 = V_t_T(kappa, kappa, t, T, v, v)
        V_2 = V_t_T(kappa, kappa, 0, T, v, v)
        V_3 = V_t_T(kappa, kappa, 0, t, v, v)
        RHS = 0.5 * (V_1)
    else : 
        V_1 = V_t_T2(kappa, kappa, t, T, HWVolTerm, HWVol, HWVolTerm, HWVol)
        V_2 = V_t_T2(kappa, kappa, 0, T, HWVolTerm, HWVol, HWVolTerm, HWVol)
        V_3 = V_t_T2(kappa, kappa, 0, t, HWVolTerm, HWVol, HWVolTerm, HWVol)
        RHS = 0.5 * (V_1)
    return RHS 

def HWCrossTerm(t, T, kappa1, kappa2, HWVolTerm1, HWVol1, HWVolTerm2, HWVol2, rho) : 
    RHS = 0
    if (len(HWVol1) == 1 and len(HWVol1) == 1) or kappa1 > 0.25 : 
        v1 = np.interp((t+T)/2, HWVolTerm1, HWVol1)
        v2 = np.interp((t+T)/2, HWVolTerm2, HWVol2)
        V_1 = V_t_T(kappa1, kappa2, t, T, v1, v2)
        V_2 = V_t_T(kappa1, kappa2, 0, T, v1, v2)
        V_3 = V_t_T(kappa1, kappa2, 0, t, v1, v2)
        RHS = 2.0 * rho * 0.5 * (V_1)
    else : 
        V_1 = V_t_T2(kappa1, kappa2, t, T, HWVolTerm1, HWVol1, HWVolTerm2, HWVol2)
        V_2 = V_t_T2(kappa1, kappa2, 0, T, HWVolTerm1, HWVol1, HWVolTerm2, HWVol2)
        V_3 = V_t_T2(kappa1, kappa2, 0, t, HWVolTerm1, HWVol1, HWVolTerm2, HWVol2)
        RHS = 2.0 * rho * 0.5 * (V_1)
    return RHS     

def HullWhite_A_t_T_1F(DF_0_t_T, t, T, kappa, HWVolTerm, HWVol) : 
    return DF_0_t_T * np.exp(HWQVTerm(t, T, kappa, HWVolTerm, HWVol))        

def HullWhite1F_DiscFactor_t_T(BtT, xt, A_t_T_1F) : 
    return np.exp(-xt * BtT) * A_t_T_1F

def HullWhite2F_DiscFactor_t_T_2F(BtTxt, BtTyt, xt, yt, A_t_T_xt, A_t_T_yt, hwcross) : 
    return np.exp(-xt * BtTxt - yt * BtTyt + hwcross) *  A_t_T_xt *  A_t_T_yt

def XV(kappa, tVol, Vol, t, T) : 
    if len(tVol) == 1 : 
        time = (t+T)/2
        v = np.interp(time, tVol, Vol)
        return np.sqrt(v * v * 0.5 / kappa * (1.0 - np.exp(-2.0 * kappa * (T - t))))
    else : 
        NInteg = 10
        MySpace = np.linspace(t, T, NInteg + 1)
        u = (MySpace[:-1] + MySpace[1:])/2
        v = np.interp(u, tVol, Vol)
        du = MySpace[1:] - MySpace[:-1]
        return np.sqrt((v * v * np.exp(-2.0 * kappa * (T - u)) * du).sum(0))                

def XA(kappa, t, T) : 
    return np.exp(-kappa * (T-t))

def SimulateXt(xt, xa, xv, eps) : 
    return xt * xa + eps * xv

def HW_Swaption(NA, kappa, tVol, Vol, Term, Rate, StrikePrice, T_SwapStartDate, TArray_of_CpnDate) : 
    tVol = np.array(tVol, dtype = np.float64)
    Vol = np.array(Vol, dtype = np.float64)
    TempInterpFunc = np.vectorize(lambda x : Linterp(Term, Rate, x))
    t = np.array([T_SwapStartDate] + list(TArray_of_CpnDate), dtype = np.float64)
    r = TempInterpFunc(t)
    DF = np.exp(-r * t)

    Vol = np.maximum(0.000001, Vol)
    VT0 = np.exp(-2.0 * kappa * T_SwapStartDate) * HW_Integral_ShortRate_Vol(T_SwapStartDate, 1, 2.0 * kappa, tVol, Vol)
    deltaT = t[1:] - t[:-1]
    G = (DF[-1] + (DF[1:] * deltaT * StrikePrice).sum())/DF[0]

    TempFunction2 = np.vectorize(lambda x : B_s_to_t(T_SwapStartDate, x, kappa))
    H = (DF[-1] * B_s_to_t(T_SwapStartDate, TArray_of_CpnDate[-1], kappa) + (StrikePrice * deltaT * DF[1:] * TempFunction2(TArray_of_CpnDate)).sum())/(G * DF[0])
    d1 = -np.log(G) / (H * np.sqrt(VT0)) + 0.5 * H * np.sqrt(VT0)
    d2 = -np.log(G) / (H * np.sqrt(VT0)) - 0.5 * H * np.sqrt(VT0)

    value = DF[0] * (CDF_N(d1) - G * CDF_N(d2))
    return NA * value

def SimulateShortRateMC(NSimul, SimulationDateList, PriceDate, kappa, HWVolTerm, HWVol) : 
    np.random.seed(1)
    Rndn = np.random.normal(0,1,size = (len(SimulationDateList),NSimul))
    t1 = np.vectorize(DayCountAtoB)(PriceDate, SimulationDateList)/365
    X_A0 = XA(kappa, 0, t1[0])
    X_V0 = XV(kappa, HWVolTerm, HWVol, 0, t1[0])
    X_A = XA(kappa, t1[:-1], t1[1:])
    X_V = XV(kappa, HWVolTerm, HWVol, t1[:-1], t1[1:])
    SimulatedXt = SimulateXt(0, X_A0, X_V0, Rndn[0]).reshape(1,-1)
    for i in range(len(SimulationDateList) - 1) :
        prevx = SimulatedXt[i]
        SimulatedXt = np.concatenate([SimulatedXt, SimulateXt(prevx, X_A[i], X_V[i], Rndn[i+1]).reshape(1,-1)],axis = 0)
    return SimulatedXt

def SimulateParRateMC(PriceDate, SimulatedXt2D, SimulationDateList, RefSwapMaturity_T, RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, ZeroTerm, ZeroRate) :
    EachSwapMaturityInSimulation = np.vectorize(EDate_YYYYMMDD)(SimulationDateList, int(RefSwapMaturity_T * 12 + 0.0001))
    CpnDateListInSimul = []
    for i in range(len(SimulationDateList)) : 
        CpnDateListInSimul.append(np.array(malloc_cpn_date_holiday(SimulationDateList[i], EachSwapMaturityInSimulation[i], RefSwapNCPNOneYear)[0]).reshape(1,-1))
    CpnDateArrayForEachSimulDate = np.concatenate(CpnDateListInSimul, axis = 0)

    t1 = np.vectorize(DayCountAtoB)(PriceDate, SimulationDateList)/365
    t2 = np.vectorize(DayCountAtoB)(PriceDate, CpnDateArrayForEachSimulDate)/365
    r1 = np.interp(t1, ZeroTerm, ZeroRate)
    r2 = np.interp(t2, ZeroTerm, ZeroRate)
    df1 = np.exp(-r1 * t1)
    df2 = np.exp(-r2 * t2)
    df_t_T = df2/df1.reshape(-1,1)
    MyFunc = np.vectorize(lambda DF_0_t_T, t, T: HullWhite_A_t_T_1F(DF_0_t_T, t, T, kappa, HWVolTerm, HWVol))
    A_t_T = MyFunc(df_t_T, t1.reshape(-1,1), t2) 
    B_t_T = B_s_to_t(t1.reshape(-1,1), t2, kappa)

    deltat = np.concatenate([(t2[:,0] - t1).reshape(-1,1), (t2[:,1:] - t2[:,:-1])], axis = 1)
    
    deltat3D = deltat.reshape(deltat.shape[0], deltat.shape[1], 1)
    B_t_T3D = B_t_T.reshape(B_t_T.shape[0], B_t_T.shape[1], 1)
    A_t_T3D = A_t_T.reshape(A_t_T.shape[0], A_t_T.shape[1], 1)

    SimulatedXt3D = SimulatedXt2D.reshape(len(SimulationDateList), 1, -1)
    Disc = HullWhite1F_DiscFactor_t_T(B_t_T3D, SimulatedXt3D, A_t_T3D)

    SwapRate = (1-Disc[:,-1,:])/(Disc * deltat3D).sum(1)    
    SwapRateForwardMeasure = (1-df_t_T[:,-1])/(df_t_T * deltat).sum(1)
    
    if df_t_T.shape[1] > 1 : 
        MyFuncTemp = np.vectorize(lambda CpnRateList, YTMList, StartDateList, EndDateList : GPrimePrime_Over_GPrime(CpnRateList, YTMList, StartDateList, EndDateList, RefSwapNCPNOneYear))
        GppOvGp = MyFuncTemp(SwapRateForwardMeasure, SwapRateForwardMeasure, np.array(SimulationDateList), EachSwapMaturityInSimulation)
        v = np.interp(t1, HWVolTerm, HWVol)
        ConvAdjAmt = GppOvGp * v * v * 100. * t1 * 0.5    
    else : 
        ConvAdjAmt = t1 * 0
    return SwapRate, SwapRateForwardMeasure, ConvAdjAmt

def ParRateForFDMGreed(PriceDate, xt_greed, yt_greed, SimulationDateList, RefSwapMaturity_T, RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, kappa2, HWVolTerm2, HWVol2, ZeroTerm, ZeroRate, HW2FFlag = 0, HWRho12Factor = 0) :
    EachSwapMaturityInSimulation = np.vectorize(EDate_YYYYMMDD)(SimulationDateList, int(RefSwapMaturity_T * 12 + 0.0001))
    CpnDateListInSimul = []
    for i in range(len(SimulationDateList)) : 
        CpnDateListInSimul.append(np.array(malloc_cpn_date_holiday(SimulationDateList[i], EachSwapMaturityInSimulation[i], RefSwapNCPNOneYear)[0]).reshape(1,-1))
    CpnDateArrayForEachSimulDate = np.concatenate(CpnDateListInSimul, axis = 0)

    t1 = np.vectorize(DayCountAtoB)(PriceDate, SimulationDateList)/365
    t2 = np.vectorize(DayCountAtoB)(PriceDate, CpnDateArrayForEachSimulDate)/365
    r1 = np.interp(t1, ZeroTerm, ZeroRate)
    r2 = np.interp(t2, ZeroTerm, ZeroRate)
    df1 = np.exp(-r1 * t1)
    df2 = np.exp(-r2 * t2)
    df_t_T = df2/df1.reshape(-1,1)
    MyFunc = np.vectorize(lambda DF_0_t_T, t, T: HullWhite_A_t_T_1F(DF_0_t_T, t, T, kappa, HWVolTerm, HWVol))
    if HW2FFlag == 0 : 
        A_t_T = MyFunc(df_t_T, t1.reshape(-1,1), t2) 
        B_t_T = B_s_to_t(t1.reshape(-1,1), t2, kappa)
        deltat = np.concatenate([(t2[:,0] - t1).reshape(-1,1), (t2[:,1:] - t2[:,:-1])], axis = 1)
        deltat3D = deltat.reshape(deltat.shape[0], deltat.shape[1], 1)
        B_t_T3D = B_t_T.reshape(B_t_T.shape[0], B_t_T.shape[1], 1)
        A_t_T3D = A_t_T.reshape(A_t_T.shape[0], A_t_T.shape[1], 1)

        Xt3D = xt_greed.reshape(len(SimulationDateList), 1, -1)
        Disc = HullWhite1F_DiscFactor_t_T(B_t_T3D, Xt3D, A_t_T3D)
        SwapRate = (1-Disc[:,-1,:])/(Disc * deltat3D).sum(1)    
    else : 
        MyFunc2F = np.vectorize(lambda DF_0_t_T, t, T: HullWhite_A_t_T_1F(1, t, T, kappa2, HWVolTerm2, HWVol2))
        MyFuncCrossTerm = np.vectorize(lambda t, T: HWCrossTerm(t, T, kappa, kappa2, HWVolTerm, HWVol, HWVolTerm2, HWVol2, HWRho12Factor))
        deltat = np.concatenate([(t2[:,0] - t1).reshape(-1,1), (t2[:,1:] - t2[:,:-1])], axis = 1)
        deltat3D = deltat.reshape(deltat.shape[0], deltat.shape[1], 1)

        A_t_T_Xt = MyFunc(df_t_T, t1.reshape(-1,1), t2) 
        B_t_T_Xt = B_s_to_t(t1.reshape(-1,1), t2, kappa)
        B_t_T_Xt3D = B_t_T_Xt.reshape(B_t_T_Xt.shape[0], B_t_T_Xt.shape[1], 1)
        A_t_T_Xt3D = A_t_T_Xt.reshape(A_t_T_Xt.shape[0], A_t_T_Xt.shape[1], 1)
        
        A_t_T_Yt = MyFunc2F(df_t_T, t1.reshape(-1,1), t2) 
        B_t_T_Yt = B_s_to_t(t1.reshape(-1,1), t2, kappa)
        B_t_T_Yt3D = B_t_T_Yt.reshape(B_t_T_Yt.shape[0], B_t_T_Yt.shape[1], 1)
        A_t_T_Yt3D = A_t_T_Yt.reshape(A_t_T_Yt.shape[0], A_t_T_Yt.shape[1], 1)
        
        HWCross = np.exp(MyFuncCrossTerm(t1.reshape(-1,1), t2)) 
        HWCross_4D = HWCross.reshape(HWCross.shape[0], HWCross.shape[1], 1, 1)
        Xt3D = xt_greed.reshape(len(SimulationDateList), 1, -1)
        Yt3D = yt_greed.reshape(len(SimulationDateList), 1, -1)
        Disc1 = HullWhite1F_DiscFactor_t_T(B_t_T_Xt3D, Xt3D, A_t_T_Xt3D)
        Disc2 = HullWhite1F_DiscFactor_t_T(B_t_T_Yt3D, Yt3D, A_t_T_Yt3D)
        Disc1_4D = Disc1.reshape(Disc1.shape[0], Disc1.shape[1], Disc1.shape[2], 1)
        Disc2_4D = Disc2.reshape(Disc2.shape[0], Disc2.shape[1], 1, Disc2.shape[2])
        deltat4D = deltat3D.reshape(deltat3D.shape[0], deltat3D.shape[1], 1, 1)
        Disc = Disc1_4D * Disc2_4D * HWCross_4D
        SwapRate = (1-Disc[:,-1,:,:])/(Disc * deltat4D).sum(1)    

    SwapRateForwardMeasure = (1-df_t_T[:,-1])/(df_t_T * deltat).sum(1)
    if df_t_T.shape[1] > 1 : 
        MyFuncTemp = np.vectorize(lambda CpnRateList, YTMList, StartDateList, EndDateList : GPrimePrime_Over_GPrime(CpnRateList, YTMList, StartDateList, EndDateList, RefSwapNCPNOneYear))
        GppOvGp = MyFuncTemp(SwapRateForwardMeasure, SwapRateForwardMeasure, np.array(SimulationDateList), EachSwapMaturityInSimulation)
        v = np.interp(t1, HWVolTerm, HWVol)
        ConvAdjAmt = GppOvGp * v * v * 100. * t1 * 0.5    
    else : 
        ConvAdjAmt = t1 * 0
    return SwapRate, SwapRateForwardMeasure, ConvAdjAmt

def Calc_RefRateOnFixingDate_And_ForwardDisc_FixingToPay(PriceDate, FixingDate, FixingDate2, PayDate, kappa, HWVolTerm, HWVol, ZeroTerm, ZeroRate, SimulationDateList, OptionFixDate, OptionPayDate, Leg_RefRate_Simul2DArray, SimulatedXt2D, RefRateForwardMeasure, Conv) :
    MyFunc = np.vectorize(lambda DF_0_t_T, t, T: HullWhite_A_t_T_1F(DF_0_t_T, t, T, kappa, HWVolTerm, HWVol))
    FixingIdx = np.array([list(FixingDate).index(SimulationDateList[i]) for i in range(len(SimulationDateList)) if SimulationDateList[i] in FixingDate])
    IdxSimul = np.array([i for i in range(len(SimulationDateList)) if SimulationDateList[i] in FixingDate])
    IdxSimul2 = np.array([i for i in range(len(SimulationDateList)) if SimulationDateList[i] in FixingDate2])
    RefRateOnFixingDate = Leg_RefRate_Simul2DArray[IdxSimul]
    RefRateOnFixingDate2 = Leg_RefRate_Simul2DArray[IdxSimul2]  
    RefRateOnFixingDateForwardMeasure = RefRateForwardMeasure[IdxSimul] - Conv[IdxSimul]
    RefRateOnFixingDateForwardMeasure2 = RefRateForwardMeasure[IdxSimul2] - Conv[IdxSimul2]
    tfix_ = np.vectorize(DayCountAtoB)(PriceDate, np.array(FixingDate)[FixingIdx])/365
    tpay_ = np.vectorize(DayCountAtoB)(PriceDate, np.array(PayDate)[FixingIdx])/365
    df_tfix = np.exp(-np.interp(tfix_, ZeroTerm, ZeroRate) * tfix_)
    DiscountFactorToPriceDatetoFixing = df_tfix
    df_tpay = np.exp(-np.interp(tpay_, ZeroTerm, ZeroRate) * tpay_)
    df_fix_to_pay = df_tpay/df_tfix
    A_t_T_FixedToPay = MyFunc(df_fix_to_pay,tfix_, tpay_).reshape(-1,1)    
    B_t_T_FixedToPay = B_s_to_t(tfix_,tpay_, kappa).reshape(-1,1)
    
    HWDF_tfix_tpay = HullWhite1F_DiscFactor_t_T(B_t_T_FixedToPay, SimulatedXt2D[IdxSimul], A_t_T_FixedToPay)

    OptFixingIdx = np.array([list(OptionFixDate).index(SimulationDateList[i]) for i in range(len(SimulationDateList)) if SimulationDateList[i] in OptionFixDate])
    Opttfix_ = np.vectorize(DayCountAtoB)(PriceDate, np.array(OptionFixDate)[OptFixingIdx])/365
    Opttpay_ = np.vectorize(DayCountAtoB)(PriceDate, np.array(OptionPayDate)[OptFixingIdx])/365
    Xt_Opt = SimulatedXt2D[OptFixingIdx]
    Optdf_tfix = np.exp(-np.interp(Opttfix_, ZeroTerm, ZeroRate) * Opttfix_)
    Optdf_tpay = np.exp(-np.interp(Opttpay_, ZeroTerm, ZeroRate) * Opttpay_)
    Optdf_fix_to_pay = Optdf_tpay/Optdf_tfix
    OptA_t_T_FixedToPay = MyFunc(Optdf_fix_to_pay,Optdf_tfix, Optdf_tpay).reshape(-1,1)    
    OptB_t_T_FixedToPay = B_s_to_t(Optdf_tfix,Optdf_tpay, kappa).reshape(-1,1)
    OptHWDF_tfix_tpay = HullWhite1F_DiscFactor_t_T(OptB_t_T_FixedToPay, Xt_Opt, OptA_t_T_FixedToPay)    

    return RefRateOnFixingDate, RefRateOnFixingDate2, HWDF_tfix_tpay, DiscountFactorToPriceDatetoFixing, RefRateOnFixingDateForwardMeasure, RefRateOnFixingDateForwardMeasure2, df_tpay.reshape(-1,1), SimulatedXt2D[IdxSimul], Xt_Opt, Optdf_tfix.reshape(-1,1), OptHWDF_tfix_tpay

def Calc_Payoff_Sim_and_NotSim(PriceDate, EffectiveDate, SimulatedRefRate, Nominal, Phase2StartDate, ForwardStart, ForwardEnd, PayDate, DayCount,RefSwapRate_Multiple_Phase1, RefSwapRate_Multiple_Phase2, FixedCpnRate_Phase1, FixedCpnRate_Phase2, FixingHistoryDate, FixingHistoryRate, ZeroCouponFlag, CompoundCouponFlag, RefRateForwardMeasure,ZeroTerm, ZeroRate, rounding = 11) : 
    D1 = np.array(ForwardStart)
    D2 = np.array(ForwardEnd)
    SimIdx = np.array(ForwardStart) > PriceDate
    NotSimIdx = (np.array(ForwardStart) <= PriceDate ) & (np.array(PayDate) > PriceDate)
    FixingDate_Sim = np.array(ForwardStart)[SimIdx]
    FixingDate2_Sim = np.array(ForwardEnd)[SimIdx]
    PayDate_Sim = np.array(PayDate)[SimIdx]
    
    IdxCummulativeCpn = -1
    for i in range(len(PayDate)-1) : 
        if (PriceDate >= PayDate[i] and PriceDate < PayDate[i+1]) : 
            IdxCummulativeCpn = i 
            break        
    
    if ZeroCouponFlag == True : 
        DeltaT = np.vectorize(DayCountFractionAtoB)(np.array([EffectiveDate]), D2, np.array([DayCount])).reshape(-1,1)
    else : 
        DeltaT = np.vectorize(DayCountFractionAtoB)(D1, D2, np.array([DayCount])).reshape(-1,1)
    DeltaT_NotSim = DeltaT[NotSimIdx]
    DeltaT_Sim = DeltaT[SimIdx]
    RefRateMultiple = ((np.array(PayDate) < Phase2StartDate) * RefSwapRate_Multiple_Phase1 + (np.array(PayDate) >= Phase2StartDate) * RefSwapRate_Multiple_Phase2).reshape(-1,1)
    RefRateMultiple_NotSim = RefRateMultiple[NotSimIdx]
    RefRateMultiple_Sim = RefRateMultiple[SimIdx]
    CpnRate = ((np.array(PayDate) < Phase2StartDate) * FixedCpnRate_Phase1 + (np.array(PayDate) >= Phase2StartDate) * FixedCpnRate_Phase2).reshape(-1,1)
    CpnRate_NotSim = CpnRate[NotSimIdx]
    CpnRate_Sim = CpnRate[SimIdx]
    
    if CompoundCouponFlag == False : 
        Payoff_Sim = ((SimulatedRefRate* RefRateMultiple_Sim) + CpnRate_Sim) * DeltaT_Sim * Nominal
        Payoff_ForwardMeasure = ((RefRateForwardMeasure.reshape(-1,1)* RefRateMultiple_Sim) + CpnRate_Sim) * DeltaT_Sim * Nominal
        if ZeroCouponFlag == True : 
            CummulativePrevCpn = (CpnRate[IdxCummulativeCpn]) * DeltaT[IdxCummulativeCpn] * Nominal if IdxCummulativeCpn >= 0 else [0]
        else : 
            CummulativePrevCpn = [0]
    else : 
        div = 10 ** rounding
        Payoff_Sim = np.ceil(((1+(SimulatedRefRate*RefRateMultiple_Sim) + CpnRate_Sim)**DeltaT_Sim - 1) * div)/div * Nominal
        Payoff_ForwardMeasure = np.ceil(((1+(RefRateForwardMeasure.reshape(-1,1)*RefRateMultiple_Sim) + CpnRate_Sim)**DeltaT_Sim - 1) * div)/div * Nominal
        if ZeroCouponFlag == True : 
            CummulativePrevCpn = np.ceil(((1+ CpnRate[IdxCummulativeCpn]) ** DeltaT[IdxCummulativeCpn]-1) * div)/div * Nominal if IdxCummulativeCpn >= 0 else [0]
        else : 
            CummulativePrevCpn = [0]

    PrevDate = np.array(ForwardStart)[NotSimIdx]
    PrevDate2 = np.array(ForwardEnd)[NotSimIdx]
    PrevPayDate = np.array(PayDate)[NotSimIdx]
    if len(PrevPayDate) > 0 : 
        PrevT = np.vectorize(DayCountFractionAtoB)(PriceDate, PrevPayDate, np.array([0])).reshape(-1,1)
        PrevR = np.interp(PrevT, ZeroTerm, ZeroRate)
        PrevDF = np.exp(-PrevR * PrevT)
        FixedRate1 = pd.Series(PrevDate, PrevDate).map(pd.Series(FixingHistoryRate, FixingHistoryDate)).fillna(0).values.reshape(-1,1)
        FixedRate2 = pd.Series(PrevDate2, PrevDate).map(pd.Series(FixingHistoryRate, FixingHistoryDate)).fillna(0).values.reshape(-1,1)
        Payoff_NotSim = ((FixedRate1 * RefRateMultiple_NotSim) + CpnRate_NotSim) * DeltaT_NotSim * Nominal
    else : 
        PrevPayDate = np.array([0])
        PrevDF = np.array([[1.0]])
        FixedRate1 = pd.Series([0.0])
        FixedRate2 = pd.Series([0.0])
        Payoff_NotSim = np.array([[0.0]])
    return {"FixingDate_Simul":FixingDate_Sim, "FixingDate2_Simul" :FixingDate2_Sim, "PayDate_Simul" : PayDate_Sim, "PrevFixDate" : PrevDate,"PrevFixDate2" : PrevDate2, "Payoff_Simul" : Payoff_Sim, "Payoff_Prev" : Payoff_NotSim,"FixedRate1_Prev" : FixedRate1,"FixedRate2_Prev" : FixedRate2, "PrevPayDate":PrevPayDate, "PrevDF" : PrevDF, "PrevCummulativeCpn" : CummulativePrevCpn, "Payoff_ForwardMeasure" : Payoff_ForwardMeasure}

def Calc_Payoff_FDM_ForTimeGreed(ZeroTerm, ZeroRate, PriceDate, EffectiveDate, RefRateOnFixingDate, RefRateOnFixingDate_PowerSpread, Nominal, 
                                 Phase2StartDate, ForwardStart, ForwardEnd, PayDate, DayCount,
                                 RefSwapRate_Multiple_Phase1, RefSwapRate_Multiple_Phase2, FixedCpnRate_Phase1, FixedCpnRate_Phase2, FixingHistoryDate, 
                                 FixingHistoryRate, ZeroCouponFlag, CompoundCouponFlag, RefRateForwardMeasure,RefRateForwardMeasure_PowerSpread, PowerSpreadFlag, rounding = 11, HW2FFlag = 0, MaxReturn = 1000, MaxLoss = -1000) : 
    maxi, mini = np.maximum, np.minimum
    D1 = np.array(ForwardStart)
    D2 = np.array(ForwardEnd)
    SimIdx = np.array(ForwardStart) > PriceDate
    NotSimIdx = (np.array(ForwardStart) <= PriceDate ) & (np.array(PayDate) > PriceDate)
    FixingDate_Sim = np.array(ForwardStart)[SimIdx]
    FixingDate2_Sim = np.array(ForwardEnd)[SimIdx]
    PayDate_Sim = np.array(PayDate)[SimIdx]

    IdxCummulativeCpn = -1
    for i in range(len(PayDate)-1) : 
        if (PriceDate >= PayDate[i] and PriceDate < PayDate[i+1]) : 
            IdxCummulativeCpn = i 
            break        

    if ZeroCouponFlag == True : 
        DeltaT = np.vectorize(DayCountFractionAtoB)(np.array([EffectiveDate]), D2, np.array([DayCount])).reshape(-1,1)
    else : 
        DeltaT = np.vectorize(DayCountFractionAtoB)(D1, D2, np.array([DayCount])).reshape(-1,1)
    DeltaT_NotSim = DeltaT[NotSimIdx]
    DeltaT_Sim = DeltaT[SimIdx]
    RefRateMultiple = ((np.array(PayDate) < Phase2StartDate) * RefSwapRate_Multiple_Phase1 + (np.array(PayDate) >= Phase2StartDate) * RefSwapRate_Multiple_Phase2).reshape(-1,1)
    RefRateMultiple_NotSim = RefRateMultiple[NotSimIdx]
    RefRateMultiple_Sim = RefRateMultiple[SimIdx]
    CpnRate = ((np.array(PayDate) < Phase2StartDate) * FixedCpnRate_Phase1 + (np.array(PayDate) >= Phase2StartDate) * FixedCpnRate_Phase2).reshape(-1,1)
    CpnRate_NotSim = CpnRate[NotSimIdx]
    CpnRate_Sim = CpnRate[SimIdx]

    if CompoundCouponFlag == False : 
        if PowerSpreadFlag == 0 : 
            if HW2FFlag == 0 : 
                Payoff_Sim = mini(MaxReturn, maxi((RefRateOnFixingDate* RefRateMultiple_Sim) + CpnRate_Sim, MaxLoss)) * DeltaT_Sim * Nominal
            else : 
                Multiple = RefRateMultiple_Sim[:,:,np.newaxis]
                Cpn = CpnRate_Sim[:,:,np.newaxis]
                dT = DeltaT_Sim[:,:,np.newaxis]
                Payoff_Sim = mini(MaxReturn, maxi((RefRateOnFixingDate* Multiple) + Cpn, MaxLoss)) * dT * Nominal
            Payoff_ForwardMeasure = mini(MaxReturn, maxi((RefRateForwardMeasure.reshape(-1,1)* RefRateMultiple_Sim) + CpnRate_Sim, MaxLoss)) * DeltaT_Sim * Nominal
        else : 
            if HW2FFlag == 0 : 
                Payoff_Sim = mini(MaxReturn, maxi(((RefRateOnFixingDate - RefRateOnFixingDate_PowerSpread)* RefRateMultiple_Sim) + CpnRate_Sim, MaxLoss)) * DeltaT_Sim * Nominal
            else : 
                Multiple = RefRateMultiple_Sim[:,:,np.newaxis]
                Cpn = CpnRate_Sim[:,:,np.newaxis]
                dT = DeltaT_Sim[:,:,np.newaxis]
                Payoff_Sim = mini(MaxReturn, maxi(((RefRateOnFixingDate - RefRateOnFixingDate_PowerSpread)* Multiple) + Cpn, MaxLoss)) * dT * Nominal
                
            Payoff_ForwardMeasure = mini(MaxReturn, maxi(((RefRateForwardMeasure.reshape(-1,1) - RefRateForwardMeasure_PowerSpread.reshape(-1,1))* RefRateMultiple_Sim) + CpnRate_Sim, MaxLoss)) * DeltaT_Sim * Nominal
            
        if ZeroCouponFlag == True : 
            CummulativePrevCpn = (CpnRate[IdxCummulativeCpn]) * DeltaT[IdxCummulativeCpn] * Nominal if IdxCummulativeCpn >= 0 else [0]
        else : 
            CummulativePrevCpn = [0]
    else : 
        div = 10 ** rounding
        if PowerSpreadFlag == 0 : 
            if HW2FFlag == 0 : 
                Payoff_Sim = np.ceil(((1+(RefRateOnFixingDate*RefRateMultiple_Sim) + CpnRate_Sim)**DeltaT_Sim - 1) * div)/div * Nominal
            else : 
                Multiple = RefRateMultiple_Sim[:,:,np.newaxis]
                Cpn = CpnRate_Sim[:,:,np.newaxis]
                dT = DeltaT_Sim[:,:,np.newaxis]
                Payoff_Sim = np.ceil(((1+(RefRateOnFixingDate*Multiple) + Cpn)**dT - 1) * div)/div * Nominal
                
            Payoff_ForwardMeasure = np.ceil(((1+(RefRateForwardMeasure.reshape(-1,1)*RefRateMultiple_Sim) + CpnRate_Sim)**DeltaT_Sim - 1) * div)/div * Nominal
        else : 
            if HW2FFlag == 0 :
                Payoff_Sim = np.ceil(((1+((RefRateOnFixingDate - RefRateOnFixingDate_PowerSpread)*RefRateMultiple_Sim) + CpnRate_Sim)**DeltaT_Sim - 1) * div)/div * Nominal        
            else : 
                Multiple = RefRateMultiple_Sim[:,:,np.newaxis]
                Cpn = CpnRate_Sim[:,:,np.newaxis]
                dT = DeltaT_Sim[:,:,np.newaxis]
                Payoff_Sim = np.ceil(((1+((RefRateOnFixingDate - RefRateOnFixingDate_PowerSpread)*Multiple) + Cpn)**dT - 1) * div)/div * Nominal        
                
            Payoff_ForwardMeasure = (((RefRateForwardMeasure.reshape(-1,1) - RefRateForwardMeasure_PowerSpread.reshape(-1,1))* RefRateMultiple_Sim) + CpnRate_Sim) * DeltaT_Sim * Nominal

        if ZeroCouponFlag == True : 
            CummulativePrevCpn = np.ceil(((1+ CpnRate[IdxCummulativeCpn]) ** DeltaT[IdxCummulativeCpn]-1) * div)/div * Nominal if IdxCummulativeCpn >= 0 else [0]
        else : 
            CummulativePrevCpn = [0]
        
    PrevDate = np.array(ForwardStart)[NotSimIdx]
    PrevDate2 = np.array(ForwardEnd)[NotSimIdx]
    PrevPayDate = np.array(PayDate)[NotSimIdx]
    if len(PrevPayDate) > 0 : 
        PrevT = np.vectorize(DayCountFractionAtoB)(PriceDate, PrevPayDate, np.array([0])).reshape(-1,1)
        PrevR = np.interp(PrevT, ZeroTerm, ZeroRate)
        PrevDF = np.exp(-PrevR * PrevT)
        FixedRate1 = pd.Series(PrevDate, PrevDate).map(pd.Series(FixingHistoryRate, FixingHistoryDate)).fillna(0).values.reshape(-1,1)
        FixedRate2 = pd.Series(PrevDate2, PrevDate).map(pd.Series(FixingHistoryRate, FixingHistoryDate)).fillna(0).values.reshape(-1,1)
        Payoff_NotSim = ((FixedRate1 * RefRateMultiple_NotSim) + CpnRate_NotSim) * DeltaT_NotSim * Nominal
    else : 
        PrevPayDate = np.array([0])
        PrevDF = np.array([[1.0]])
        FixedRate1 = pd.Series([0.0])
        FixedRate2 = pd.Series([0.0])
        Payoff_NotSim = np.array([[0.0]])
            
    return {"FixingDate_Simul":FixingDate_Sim, "FixingDate2_Simul" :FixingDate2_Sim, "PayDate_Simul" : PayDate_Sim, "PrevFixDate" : PrevDate,"PrevFixDate2" : PrevDate2, "Payoff_Simul" : Payoff_Sim, "Payoff_Prev" : Payoff_NotSim,"FixedRate1_Prev" : FixedRate1,"FixedRate2_Prev" : FixedRate2, "PrevPayDate":PrevPayDate, "PrevDF" : PrevDF, "PrevCummulativeCpn" : CummulativePrevCpn, "Payoff_ForwardMeasure" : Payoff_ForwardMeasure}


def HullWhiteCalibration1Factor(PriceDate, OptionTenor_ByMonth, SwapTenor_ByMonth, OptionVol, SwapFreqByMonth, BSVol0NormalVol1, Term, Rate, FixedKappa = 0, DayCountFlag = 0, KoreanHolidayFlag = True, AdditionalHolidays = [], initialkappa = 0.01, initialvol = 0.01, PrintMRSPE = False) :
    if PriceDate < 19000101 : 
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
        
    if len(OptionTenor_ByMonth) == len(SwapTenor_ByMonth) : 
        for i in range(len(OptionTenor_ByMonth)) : 
            if OptionTenor_ByMonth[i] > 2400 : 
                MC = MonthCountAtoB(PriceDate, OptionTenor_ByMonth[i])
                OptionTenor_ByMonth[i] = 3 * (MC // 3)
        
        for i in range(len(SwapTenor_ByMonth)) : 
            if SwapTenor_ByMonth[i] > 2400 :
                Start = EDate_YYYYMMDD(PriceDate, OptionTenor_ByMonth[i]) 
                MC = MonthCountAtoB(Start, SwapTenor_ByMonth[i])
                SwapTenor_ByMonth[i] = 3 * (MC // 3)
        
    Holidays = KoreaHolidaysFromStartToEnd(PriceDate//10000, PriceDate//10000 + 50) if KoreanHolidayFlag == True else AdditionalHolidays
    NCpnAnn = int(12/SwapFreqByMonth)
    OptionTenor_ByMonth = np.array(OptionTenor_ByMonth)
    SwapTenor_ByMonth = np.array(SwapTenor_ByMonth)
    FSRList, SwapStartDateList, SwapEndDateList,CpnDateArrayList,BlackPriceList = [], [], [], [],[]
    T_StartDate, T_CpnDate = [], []
    Notional = 100
    TempDayCount = np.vectorize(DayCountAtoB)
    Preprocessing_ZeroTermAndRate(Term, Rate, PriceDate)
    try : 
        Number_Of_Swaption = len(OptionVol.shape[0]) * len(OptionVol.shape[1])
        for i in range(len(SwapTenor_ByMonth)) : 
            for j in range(len(OptionTenor_ByMonth)) : 
                StartDate = EDate_YYYYMMDD(PriceDate, int(OptionTenor_ByMonth[j]))
                SwapEndDate = EDate_YYYYMMDD(StartDate, int(SwapTenor_ByMonth[i]))
                f = FSR(PriceDate, StartDate, SwapEndDate,NCpnAnn,DayCountFlag,Holidays, Term, Rate, Term, Rate)
                FSRList.append(f)
                SwapStartDateList.append(StartDate)
                SwapEndDateList.append(SwapEndDate)
                Start, End, Pay, NBD = MappingCouponDates(1,StartDate,SwapEndDate,0,int(NCpnAnn),1, Holidays, Holidays,1)
                CpnDateArrayList.append(End)
                T_StartDate.append(DayCountAtoB(PriceDate, StartDate)/365)
                T_CpnDate.append(TempDayCount([PriceDate], End)/365)
                
                P = BS_Swaption(PriceDate, StartDate, SwapEndDate, NCpnAnn, Notional, OptionVol[i][j], f, Term, Rate, DayCountFlag, BSVol0NormalVol1, Holidays, Holidays, 0, 0)
                BlackPriceList.append(P["Price"])
    except IndexError : 
        Number_Of_Swaption = min(len(OptionTenor_ByMonth), len(SwapTenor_ByMonth)) 
        for i in range(Number_Of_Swaption) : 
            StartDate = EDate_YYYYMMDD(PriceDate, int(OptionTenor_ByMonth[i]))
            SwapEndDate = EDate_YYYYMMDD(StartDate, int(SwapTenor_ByMonth[i]))
            f = FSR(PriceDate, StartDate, SwapEndDate,NCpnAnn,DayCountFlag,Holidays, Term, Rate, Term, Rate)
            FSRList.append(f)
            SwapStartDateList.append(StartDate)
            SwapEndDateList.append(SwapEndDate)
            Start, End, Pay, NBD = MappingCouponDates(1,StartDate,SwapEndDate,0,int(NCpnAnn),1, Holidays, Holidays,1)
            CpnDateArrayList.append(End)
            T_StartDate.append(DayCountAtoB(PriceDate, StartDate)/365)
            T_CpnDate.append(TempDayCount([PriceDate], End)/365)            
            P = BS_Swaption(PriceDate, StartDate, SwapEndDate, NCpnAnn, Notional, OptionVol[i], f, Term, Rate, DayCountFlag, BSVol0NormalVol1, Holidays, Holidays, 0, 0)
            BlackPriceList.append(P["Price"])                    
    except AttributeError : 
        Number_Of_Swaption = min(len(OptionTenor_ByMonth), len(SwapTenor_ByMonth)) 
        for i in range(Number_Of_Swaption) : 
            StartDate = EDate_YYYYMMDD(PriceDate, int(OptionTenor_ByMonth[i]))
            SwapEndDate = EDate_YYYYMMDD(StartDate, int(SwapTenor_ByMonth[i]))
            f = FSR(PriceDate, StartDate, SwapEndDate,NCpnAnn,DayCountFlag,Holidays, Term, Rate, Term, Rate)
            FSRList.append(f)
            SwapStartDateList.append(StartDate)
            SwapEndDateList.append(SwapEndDate)
            Start, End, Pay, NBD = MappingCouponDates(1,StartDate,SwapEndDate,0,int(NCpnAnn),1, Holidays, Holidays,1)
            CpnDateArrayList.append(End)
            T_StartDate.append(DayCountAtoB(PriceDate, StartDate)/365)
            T_CpnDate.append(TempDayCount([PriceDate], End)/365)            
            P = BS_Swaption(PriceDate, StartDate, SwapEndDate, NCpnAnn, Notional, OptionVol[i], f, Term, Rate, DayCountFlag, BSVol0NormalVol1, Holidays, Holidays, 0, 0)
            BlackPriceList.append(P["Price"])                    

    HWTenor = [1/30] + list(pd.Series(OptionTenor_ByMonth).unique())            
    Parameters = [initialkappa] + [initialvol] * (len(HWTenor)) if FixedKappa == 0 else [initialvol] * (len(HWTenor))
    Parameters = np.array(Parameters)
    TermHWVol = np.array(HWTenor,dtype = np.float64)/12
    JacovMatrix = np.zeros(shape = (Number_Of_Swaption, len(Parameters)))
    firstmu, PrevErrorSquare = 1.0, 100000
    MinErr = 100000
    dkappa, dhwvol = 0.005, 0.001
    MinVol, MaxVol = 0.0001, 0.10
    MinKap, MaxKap = 0.001, 1.5
    ArgMinParams = Parameters.copy()
    ArgMinPrice = np.array(BlackPriceList)
    ArgMinErrArray = np.array([-1] * len(BlackPriceList))
    for n in range(10) : 
        ErrorList = []
        HWPList = []
        MRSPE, errsquaresum = 0, 0
        kap = Parameters[0] if FixedKappa == 0 else FixedKappa
        usingvol = Parameters[1:] if FixedKappa == 0 else Parameters
        for i in range(Number_Of_Swaption) : 
            HWP = HW_Swaption(Notional, kap, TermHWVol, usingvol, Term, Rate, FSRList[i], T_StartDate[i], T_CpnDate[i])
            BSP = BlackPriceList[i]    
            Err = BSP - HWP
            HWPList.append(HWP)
            RSPercent = (Err * Err)/(BSP * BSP)
            ErrorList.append(Err)
            errsquaresum += (Err * Err)
            MRSPE += RSPercent/Number_Of_Swaption
        ErrorArray = np.array(ErrorList)    
        if PrintMRSPE == True : 
            print('###   iters = ' + str(n))
            print('###   RMSPE = ' + str(np.round(MRSPE*100,7)) + "%")
            print('###   HWPar = ' + str(Parameters.round(3)))
        
        if n <= 2 : 
            mu = firstmu
        elif (PrevErrorSquare > errsquaresum) : 
            mu = max(0.0001, mu * 0.5) if ((PrevErrorSquare - errsquaresum)/PrevErrorSquare > 0.1) else mu
            if errsquaresum < MinErr : 
                MinErr = errsquaresum
                ArgMinParams = Parameters.copy()
                ArgMinPrice = np.array(HWPList)
                ArgMinErrArray = ErrorArray
        else : 
            mu = min(firstmu, 10 * mu)
                
        mu = firstmu
        Iden = np.identity(len(Parameters))    
        BaseKappa = Parameters[0] if FixedKappa == 0 else FixedKappa
        BaseVol = np.array(Parameters[1:]) if FixedKappa == 0 else np.array(Parameters)
        for i in range(Number_Of_Swaption) : 
            for j in range(len(Parameters)) :    
                KappaUp, KappaDn = BaseKappa, BaseKappa
                VolUp = BaseVol.copy()
                VolDn = BaseVol.copy()
                HWT = 0
                if FixedKappa == 0 : 
                    if j == 0 :
                        KappaUp = min(MaxKap, kap + dkappa)
                        KappaDn = max(MinKap, kap - dkappa)
                        dParams = KappaUp - KappaDn
                    else : 
                        VolUp[j-1] = min(MaxVol, Parameters[j] + dhwvol)
                        VolDn[j-1] = max(MinVol, Parameters[j] - dhwvol)
                        dParams = VolUp[j-1] - VolDn[j-1]
                        HWT = TermHWVol[j-1]
                else : 
                    VolUp[j] = min(MaxVol, Parameters[j] + dhwvol)
                    VolDn[j] = max(MinVol, Parameters[j] - dhwvol)
                    dParams = VolUp[j] - VolDn[j]
                    HWT = TermHWVol[j]
                TMAX = T_CpnDate[i][-1] + 1
                #if TMAX >+ HWT : 
                HWPUP = HW_Swaption(Notional, KappaUp, TermHWVol, VolUp, Term, Rate, FSRList[i], T_StartDate[i], T_CpnDate[i])
                HWPDN = HW_Swaption(Notional, KappaDn, TermHWVol, VolDn, Term, Rate, FSRList[i], T_StartDate[i], T_CpnDate[i])
                ErrUp = BlackPriceList[i] - HWPUP
                ErrDn = BlackPriceList[i] - HWPDN        
                JacovMatrix[i][j] = (ErrUp - ErrDn) / (dParams)
                #else : 
                #    JacovMatrix[i][j] = 0                    

        JtJ = JacovMatrix.T.dot(JacovMatrix)
        NextdParams = np.linalg.inv(JtJ + mu * Iden).dot(JacovMatrix.T.dot(ErrorArray))                 
        
        Parameters = Parameters - NextdParams
        if FixedKappa == 0 : 
            k = np.minimum(np.maximum(MinKap, Parameters[:1]), MaxKap)
            v = np.minimum(np.maximum(MinVol, Parameters[1:]), MaxVol)
            Parameters = np.r_[k, v]
        else : 
            Parameters = np.minimum(np.maximum(MinVol, Parameters), MaxVol)
        PrevErrorSquare = errsquaresum
        
    BlackPriceList = np.array(BlackPriceList)
    SwapEndDateList = np.array(SwapEndDateList)
    SwapStartDateList = np.array(SwapStartDateList)
    return {"kappa" : ArgMinParams[0] if FixedKappa == 0 else FixedKappa, "HWVolTerm" : TermHWVol, "HWVol" : ArgMinParams[1:] if FixedKappa == 0 else ArgMinParams, "HWPrice": ArgMinPrice, "Error" : ArgMinErrArray, "BlackPrice": BlackPriceList, "SwapStartDate":SwapStartDateList,"SwapEndDate" : SwapEndDateList}

def FindSwaptionImpliedVolatility(PriceDate, SwapStartDate, SwapEndDate, NCpnAnn, Term, Rate, TargetPrice, DayCountFracFlag, VolFlag, Nominal = 1, HolidayFlag = "kr", SelfHolidays = [], FixedPayer0Receiver1 = 0) : 
    if 'kr' in str(HolidayFlag).lower() or str(HolidayFlag) == '0' :
        Holidays = KoreaHolidaysFromStartToEnd(SwapStartDate//10000, SwapStartDate//10000 + 40)
    elif 'us' in  str(HolidayFlag).lower() or str(HolidayFlag) == '1' :
        Holidays = USHolidaysFromStartToEnd(SwapStartDate//10000, SwapStartDate//10000 + 40)
    else : 
        Holidays = SelfHolidays
    
    if PriceDate < 19000101 : 
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
    
    if SwapStartDate < 19000101 : 
        SwapStartDate = ExcelDateToYYYYMMDD(SwapStartDate)

    if SwapEndDate < 19000101 : 
        SwapEndDate = ExcelDateToYYYYMMDD(SwapEndDate)
        
    Preprocessing_ZeroTermAndRate(Term, Rate, PriceDate)
    
    StartDate, EndDate, Price = SwapStartDate, SwapEndDate, TargetPrice
    TempValue = BS_Swaption(PriceDate, StartDate, EndDate, NCpnAnn, Nominal, 0.01, 0.02, Term, Rate, DayCountFracFlag, VolFlag = VolFlag, HolidaysFixing = Holidays, HolidaysPay= Holidays, NBDayFromEndDateToPay=0, FixedPayer0Receiver1=FixedPayer0Receiver1)
    StrikePrice = TempValue["ForwardSwapRate"]
    MaxVol = 1.5
    MinVol = 0.000001
    if VolFlag == 1 : 
        MaxVol = 0.25
    TargetVol = MaxVol
    for j in range(200) : 
        v = BS_Swaption(PriceDate, StartDate, EndDate, NCpnAnn, Nominal, TargetVol, StrikePrice, Term, Rate, DayCountFracFlag, VolFlag, Holidays, Holidays, 0, FixedPayer0Receiver1 )
        Err = v["Price"] - TargetPrice
        if abs(Err) < 0.000001 : 
            break
        elif Err > 0 : 
            MaxVol = TargetVol
            TargetVol = (MaxVol + MinVol)/2
        else : 
            MinVol = TargetVol
            TargetVol = (MaxVol + MinVol)/2
        
    if j == 200 : 
        raise ValueError("Check The Price")
    return {"ImpliedVol" : TargetVol, "ForwardSwapRate" : StrikePrice}
        
def Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
              PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
              NumCpnOneYear, DayCountFlag, KoreanHoliday = True, MaturityToPayDate = 0, EstZeroCurveTerm = [],
              EstZeroCurveRate = [], FixingHolidayList = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False,
              LoggingFlag = 0, LoggingDir = '', ModifiedFollow = 1, OverNightRateDateHistory = [], OverNightRateHistory = [], 
              LookBackDays = 0, ObservShift = False, DiscCurveName = "", EstCurveName = "", CMSFlag = 0, RefSwapMaturity_T = 0.25, RefSwapNCPNAnn = 4, TermVol = [], Vol = [], YTMPricing = False, AIList = [0]) :
    
    LoggingStart = []
    LoggingEnd = []
    LoggingEstStart = []
    LoggingEstEnd = []
    LoggingPayDate = []
    LoggingFraction = []
    LoggingForwardRate = []
    LoggingCpnFix = []
    LoggingCpnRate = []
    LoggingAdj = []
    LoggingRawCpn = []
    LoggingDF = []
    rawcpn = 0
    BondFlag = 0 
    if DayCountFlag >= 5 : 
        BondFlag = 1
        DayCountFlag = DayCountFlag - 5
        
    ModifiedFollow = 1
    PriceDateYYYY, MaturityYYYY = int(PriceDateYYYYMMDD // 10000), int(MaturityYYYYMMDD // 10000)
    if len(AdditionalPayHolidayList) == 0 : 
        if KoreanHoliday == True : 
            HolidayYYYYMMDD = np.array(KoreaHolidaysFromStartToEnd(PriceDateYYYY, MaturityYYYY + 1), dtype = np.int64)
        else : 
            HolidayYYYYMMDD = np.array(AdditionalPayHolidayList, dtype = np.int64)            
    else : 
        HolidayYYYYMMDD = np.array(AdditionalPayHolidayList, dtype = np.int64)
    
    FixingHolidayYYYYMMDD = HolidayYYYYMMDD if len(FixingHolidayList) == 0 else np.array(FixingHolidayList, dtype = np.int64)
    if (NumCpnOneYear >= 4 and DayCountAtoB(EffectiveDateYYYYMMDD, MaturityYYYYMMDD) < 70) or (DayCountAtoB(EffectiveDateYYYYMMDD, MaturityYYYYMMDD) < 10) : 
        Generated_CpnDate = np.array([MaturityYYYYMMDD], dtype = np.int64)
    else : 
        if EffectiveDateYYYYMMDD % 100 == MaturityYYYYMMDD % 100 : 
            # 만기 Day가 같을 때
            Generated_CpnDate, firstcpndate = malloc_cpn_date_holiday(EffectiveDateYYYYMMDD, MaturityYYYYMMDD, NumCpnOneYear, FixingHolidayYYYYMMDD, ModifiedFollow)
        else : 
            Generated_Fixing, Generated_CpnDate, Generated_Pay, NBD = MappingCouponDates(1,EffectiveDateYYYYMMDD,MaturityYYYYMMDD,0,NumCpnOneYear,1,FixingHolidayYYYYMMDD,HolidayYYYYMMDD,1)

    AccruedT, AI = 0, 0
    BondCompStart = EffectiveDateYYYYMMDD
    if PriceDateYYYYMMDD == EffectiveDateYYYYMMDD or PriceDateYYYYMMDD in Generated_CpnDate : 
        AccruedT = 0
    else : 
        if BondFlag == 1 : 
            if PriceDateYYYYMMDD > EffectiveDateYYYYMMDD and PriceDateYYYYMMDD < Generated_CpnDate[0] : 
                AccruedT = DayCountAtoB(BondCompStart, PriceDateYYYYMMDD)/DayCountAtoB(BondCompStart, Generated_CpnDate[0])/NumCpnOneYear
                AI = AccruedT * CpnRate * Nominal
            else : 
                for i in range(len(Generated_CpnDate) - 1) : 
                    if PriceDateYYYYMMDD >= Generated_CpnDate[i] and PriceDateYYYYMMDD < Generated_CpnDate[i+1] : 
                        BondCompStart = Generated_CpnDate[i]
                        AccruedT = DayCountAtoB(BondCompStart, PriceDateYYYYMMDD)/DayCountAtoB(BondCompStart, Generated_CpnDate[i+1])/NumCpnOneYear
                        AI = AccruedT * CpnRate * Nominal
                        break
    YTMRate = 0
    if YTMPricing == True :     
        t = DayCountAtoB(PriceDateYYYYMMDD, MaturityYYYYMMDD)/365
        YTMRate = np.interp(t, ZeroCurveTerm, ZeroCurveRate)
        
    BDate = []  
    DayCountBDate = []
    if FloatFlag == 2 : 
        # SOFR의 경우 BusinessDate를 Generate
        BDate, BDExcel = BusinessDateArrayFromAtoB(PriceDateYYYY - 1, MaturityYYYY + 1, FixingHolidayYYYYMMDD)
        BDate = np.array(BDate[:-1])
        BDExcel = np.array(BDExcel)
        DayCountBDate = BDExcel[1:] - BDExcel[:-1]
            
    s = 0
    for i in range(len(Generated_CpnDate)) : 
        YYYYMMDDofNextDate = Generated_CpnDate[i]
        tpay = DayCountAtoB(PriceDateYYYYMMDD, Generated_CpnDate[i])/365
        r1 = 0.
        r2 = 0.
        if MaturityToPayDate > 0 : 
            ExcelDate = YYYYMMDDToExcelDate(Generated_CpnDate[i])
            n = 0
            for k in range(20) : 
                NextExcelDate = ExcelDate + (k + 1)
                SaturSundayFlag = 1 if NextExcelDate % 7 in [0,1] else 0
                YYYYMMDDofNextDate = ExcelDateToYYYYMMDD(NextExcelDate)
                HolidayFlag = YYYYMMDDofNextDate in HolidayYYYYMMDD
                if (HolidayFlag == 0) and (SaturSundayFlag == 0) : 
                    n += 1
                
                if (n >= MaturityToPayDate) : 
                    tpay = DayCountAtoB(PriceDateYYYYMMDD, YYYYMMDDofNextDate) / 365
                    break
        if (i > 0) : 
            tstart = DayCountAtoB(PriceDateYYYYMMDD, Generated_CpnDate[i-1])/365
            tend = DayCountAtoB(PriceDateYYYYMMDD, Generated_CpnDate[i])/365            
            deltat = DayCountFractionAtoB(Generated_CpnDate[i-1], Generated_CpnDate[i], DayCountFlag, HolidayYYYYMMDD)
        else : 
            tstart = DayCountAtoB(PriceDateYYYYMMDD, EffectiveDateYYYYMMDD)/365
            tend = DayCountAtoB(PriceDateYYYYMMDD, Generated_CpnDate[i])/365            
            deltat = DayCountFractionAtoB(EffectiveDateYYYYMMDD, Generated_CpnDate[i], DayCountFlag, HolidayYYYYMMDD)
            
        LastFixingDate = EffectiveDateYYYYMMDD if i == 0 else Generated_CpnDate[i-1]
        EstStartDate = LastFixingDate
        EstEndDate = Generated_CpnDate[i]
        f = 0
        ConvAdjAmt = 0
        if LastFixingDate < PriceDateYYYYMMDD : 
            f = FirstFloatFixRate
        elif LastFixingDate >= PriceDateYYYYMMDD : 
            if len(EstZeroCurveRate) == 0 and len(EstZeroCurveTerm) == 0 :
                if FloatFlag == 2 : 
                    Start = EDate_YYYYMMDD(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, -1)
                    End = Generated_CpnDate[i]
                    BusinessDate = BDate[(BDate >= Start) & (BDate <= End)]
                    NBDCount = DayCountBDate[(BDate >= Start) & (BDate <= End)]
                    
                    CompValue, f, EstStartIdx, EstEndIdx = SOFR_ForwardRate_Compound(PriceDateYYYYMMDD,    ZeroCurveTerm,    ZeroCurveRate,     Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD,    Generated_CpnDate[i],
                                                            0,    LookBackDays,    ObservShift,    0,    BusinessDate,    NBDCount,
                                                            OverNightRateDateHistory,    OverNightRateHistory,    365 if DayCountFlag == 0 else 360,    1)
                    EstStartDate = BusinessDate[max(0, EstStartIdx - LookBackDays)]
                    EstEndDate = BusinessDate[max(0, EstEndIdx - LookBackDays)]                    
                elif CMSFlag == 1 : 
                    SwapMaturity = Calc_CMS_Maturity(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, RefSwap_Maturity_T_Year = RefSwapMaturity_T)
                    f = FSR(PriceDateYYYYMMDD, Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, SwapMaturity, RefSwapNCPNAnn,DayCountFlag, FixingHolidayYYYYMMDD, ZeroCurveTerm, ZeroCurveRate, ZeroCurveTerm, ZeroCurveRate)
                    v = Linterp(TermVol, Vol, tstart)
                    GppOvGp = GPrimePrime_Over_GPrime(f, f, Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, RefSwapMaturity_T, RefSwapNCPNAnn)
                    ConvAdjAmt = GppOvGp * v * v * 100. * tstart * 0.5
                    f = f - ConvAdjAmt;                                        
                else : 
                    r1 = Linterp(ZeroCurveTerm, ZeroCurveRate, tstart)
                    r2 = Linterp(ZeroCurveTerm, ZeroCurveRate, tend)
                    f = 1.0 / deltat * (np.exp(-r1 * tstart)/np.exp(-r2 * tend) - 1.0)
            else : 
                if FloatFlag == 2 : 
                    Start = EDate_YYYYMMDD(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, -1)
                    End = Generated_CpnDate[i]
                    BusinessDate = BDate[(BDate >= Start) & (BDate <= End)]
                    NBDCount = DayCountBDate[(BDate >= Start) & (BDate <= End)]
                    CompValue, f, EstStartIdx, EstEndIdx = SOFR_ForwardRate_Compound(PriceDateYYYYMMDD,    EstZeroCurveTerm,    EstZeroCurveRate,     Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD,    Generated_CpnDate[i],
                                                            0,    LookBackDays,    ObservShift,    0,    BusinessDate,    NBDCount,
                                                            OverNightRateDateHistory,    OverNightRateHistory,    365 if DayCountFlag == 0 else 360,    1)
                    EstStartDate = BusinessDate[max(0, EstStartIdx - LookBackDays)]
                    EstEndDate = BusinessDate[max(0, EstEndIdx - LookBackDays)]                        
                elif CMSFlag == 1 : 
                    SwapMaturity = Calc_CMS_Maturity(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, RefSwap_Maturity_T_Year = RefSwapMaturity_T)
                    f = FSR(PriceDateYYYYMMDD, Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, SwapMaturity, RefSwapNCPNAnn,DayCountFlag, FixingHolidayYYYYMMDD, EstZeroCurveTerm, EstZeroCurveRate, ZeroCurveTerm, ZeroCurveRate)
                    v = Linterp(TermVol, Vol, tstart)
                    GppOvGp = GPrimePrime_Over_GPrime(f, f, Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, RefSwapMaturity_T, RefSwapNCPNAnn)
                    ConvAdjAmt = GppOvGp * v * v * 100. * tstart * 0.5
                    f = f - ConvAdjAmt;                                                            
                else : 
                    r1 = Linterp(EstZeroCurveTerm, EstZeroCurveRate, tstart)
                    r2 = Linterp(EstZeroCurveTerm, EstZeroCurveRate, tend)
                    f = 1.0 / deltat * (np.exp(-r1 * tstart)/np.exp(-r2 * tend) - 1.0)                    
            
        r = Linterp(ZeroCurveTerm, ZeroCurveRate, tpay)
        DF = np.exp(-r * tpay)
        if tpay > 0 : 
            if DayCountFlag != 3 and BondFlag == 0 : 
                rawcpn = (f * (FloatFlag > 0) + CpnRate) * Nominal * deltat
                cpn = rawcpn * DF
            elif BondFlag == 0 : 
                if (NumCpnOneYear == 1) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * Nominal
                    cpn = rawcpn * DF 
                elif (NumCpnOneYear == 2) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.5 * Nominal
                    cpn = rawcpn * DF 
                elif (NumCpnOneYear == 3) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.3333333333 * Nominal
                    cpn = rawcpn * DF 
                elif (NumCpnOneYear == 4) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.25 * Nominal
                    cpn = rawcpn * DF 
                elif (NumCpnOneYear == 6) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.166666666667 * Nominal
                    cpn = rawcpn * DF 
                elif (NumCpnOneYear == 12) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.083333333333 * Nominal
                    cpn = rawcpn * DF 
                else : 
                    raise ValueError("Check AnnCpnNum")
            else : 
                if YTMPricing == True : 
                    DF = 1/((1.0+YTMRate/NumCpnOneYear)**(NumCpnOneYear * DayCountFractionAtoB(BondCompStart, YYYYMMDDofNextDate,DayCountFlag) - AccruedT ))
                
                if (NumCpnOneYear == 1) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * Nominal
                    cpn = rawcpn * DF
                elif (NumCpnOneYear == 2) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.5 * Nominal
                    cpn = rawcpn * DF
                elif (NumCpnOneYear == 3) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.3333333333 * Nominal
                    cpn = rawcpn * DF
                elif (NumCpnOneYear == 4) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.25 * Nominal
                    cpn = rawcpn * DF
                elif (NumCpnOneYear == 6) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.166666666667 * Nominal
                    cpn = rawcpn * DF
                elif (NumCpnOneYear == 12) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.083333333333 * Nominal
                    cpn = rawcpn * DF
                else : 
                    raise ValueError("Check AnnCpnNum")                
        else : 
            cpn = 0
            rawcpn = 0
        
        s += cpn
        if LoggingFlag > 0 : 
            LoggingStart.append(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD)
            LoggingEnd.append(Generated_CpnDate[i])
            LoggingEstStart.append(EstStartDate)
            LoggingEstEnd.append(EstEndDate)
            LoggingPayDate.append(YYYYMMDDofNextDate)
            LoggingFraction.append(deltat)
            LoggingAdj.append(ConvAdjAmt)
            if tpay > 0 : 
                LoggingForwardRate.append(f if FloatFlag > 0 else 0)
                LoggingCpnFix.append(CpnRate)
                LoggingCpnRate.append(cpn)
                LoggingRawCpn.append(rawcpn)
                LoggingDF.append(DF)                    
            else : 
                LoggingForwardRate.append(0)
                LoggingCpnFix.append(0)
                LoggingCpnRate.append(0)
                LoggingRawCpn.append(0)
                LoggingDF.append(1.0)                
                    
    if NominalFlag == 1 : 
        if NominalDateIsNominalPayDate == True : 
            tpay = DayCountAtoB(PriceDateYYYYMMDD, Generated_CpnDate[-1])/365
            r = Linterp(ZeroCurveTerm, ZeroCurveRate, tpay)
        s += Nominal * DF
        if (LoggingFlag > 0) : 
            LoggingAdj.append(0)
            LoggingStart.append(EffectiveDateYYYYMMDD)
            LoggingEnd.append(Generated_CpnDate[-1])
            LoggingEstStart.append(EffectiveDateYYYYMMDD)
            LoggingEstEnd.append(Generated_CpnDate[-1])            
            LoggingPayDate.append(YYYYMMDDofNextDate if NominalDateIsNominalPayDate == False else Generated_CpnDate[-1])
            LoggingFraction.append(tpay)
            LoggingForwardRate.append(r)
            LoggingCpnFix.append(CpnRate)
            LoggingCpnRate.append(Nominal* DF)
            LoggingRawCpn.append(Nominal)
            LoggingDF.append(DF)             
    
    if LoggingFlag == 1 : 
        LoggingDF = pd.DataFrame([LoggingStart,LoggingEnd,LoggingEstStart,LoggingEstEnd,LoggingPayDate,LoggingFraction, LoggingForwardRate, LoggingAdj, LoggingCpnFix, LoggingCpnRate, LoggingRawCpn, LoggingDF], index = ["Start","End","EstStart","EstEnd","Pay","Frac","ForwardRate","ConvAdj","CpnFixed","Cpn","RawCpn","DF"]).T               
        if (len(DiscCurveName) > 0) : 
            LoggingDF["DiscCurve"] = DiscCurveName
            LoggingDF["EstCurve"] = DiscCurveName if len(EstZeroCurveTerm) == 0 else EstCurveName
        LoggingDF["AccruedT"] = AccruedT
        LoggingDF["AI"] = AI
            
        LoggingDF["Price"] = s
        LoggingDF.to_csv(LoggingDir + "\\LoggingFilesBond.csv", index = False, encoding = "cp949")
    elif LoggingFlag == 2 : 
        df = ReadCSV(LoggingDir + "\\LoggingFilesBond.csv")
        ColList = ["Leg1_" + str(s) for s in df.columns]
        df.columns = ColList
        LoggingDF = pd.DataFrame([LoggingStart,LoggingEnd,LoggingEstStart, LoggingEstEnd, LoggingPayDate,LoggingFraction, LoggingForwardRate, LoggingAdj, LoggingCpnFix, LoggingCpnRate, LoggingRawCpn, LoggingDF], index = ["Start","End","EstStart","EstEnd","Pay","Frac","ForwardRate","ConvAdj","CpnFixed","Cpn","RawCpn","DF"]).T               
        if (len(DiscCurveName) > 0) : 
            LoggingDF["DiscCurve"] = DiscCurveName
            LoggingDF["EstCurve"] = DiscCurveName if len(EstZeroCurveTerm) == 0 else EstCurveName
        LoggingDF["AccruedT"] = AccruedT
        LoggingDF["AI"] = AI

        LoggingDF["Price"] = s
        ColList2 = ["Leg2_" + str(s) for s in LoggingDF.columns]
        LoggingDF.columns = ColList2
        pd.concat([df, LoggingDF],axis = 1).to_csv(LoggingDir + "\\LoggingFilesIRS.csv", index = False, encoding = "cp949")
    AIList[0] = AI
    return s                               

def Calc_Bond_PV01(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
                    PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
                    NumCpnOneYear, DayCountFlag, KoreanHoliday = True, MaturityToPayDate = 0, EstZeroCurveTerm = [],
                    EstZeroCurveRate = [], FixingHolidayList = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False,
                    LoggingFlag = 0, LoggingDir = '', ModifiedFollow = 1, OverNightRateDateHistory = [], OverNightRateHistory = [], 
                    LookBackDays = 0, ObservShift = False, DiscCurveName= "", EstCurveName = "", YTMPricing = False, AIList = [0]) :
    MaturityToPayDate = max(0, MaturityToPayDate)    
    Preprocessing_ZeroTermAndRate(ZeroCurveTerm, ZeroCurveRate, int(PriceDateYYYYMMDD))
    P = Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
            PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
            NumCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm ,
            EstZeroCurveRate , FixingHolidayList , AdditionalPayHolidayList , NominalDateIsNominalPayDate ,
            LoggingFlag, LoggingDir, ModifiedFollow , OverNightRateDateHistory, OverNightRateHistory , LookBackDays , ObservShift, DiscCurveName, EstCurveName, YTMPricing = YTMPricing, AIList = AIList)

    ResultArray = np.zeros(len(ZeroCurveRate))
    for i in range(len(ZeroCurveTerm)) : 
        ZeroUp = np.array(ZeroCurveRate).copy()
        ZeroUp[i] += 0.0001
        Pu = Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
                PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroUp, 
                NumCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm ,
                EstZeroCurveRate , FixingHolidayList , AdditionalPayHolidayList , NominalDateIsNominalPayDate ,
                0, '', ModifiedFollow , OverNightRateDateHistory, OverNightRateHistory , LookBackDays , ObservShift , YTMPricing = YTMPricing)

        ResultArray[i] = Pu - P
        
    if (len(EstZeroCurveRate) > 0 and len(EstZeroCurveTerm) > 0 and len(EstZeroCurveRate) == len(EstZeroCurveTerm)) : 
        Preprocessing_ZeroTermAndRate(EstZeroCurveTerm, EstZeroCurveRate, int(PriceDateYYYYMMDD))
        ResultArray2 = np.zeros(len(EstZeroCurveTerm))
        for i in range(len(EstZeroCurveRate)) : 
            ZeroUp = np.array(EstZeroCurveRate).copy()
            ZeroUp[i] += 0.0001            
            Pu = Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
                    PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
                    NumCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm ,
                    ZeroUp , FixingHolidayList , AdditionalPayHolidayList , NominalDateIsNominalPayDate ,
                    0, '', ModifiedFollow , OverNightRateDateHistory, OverNightRateHistory , LookBackDays , ObservShift , YTMPricing = YTMPricing)
            ResultArray2[i] = Pu - P

        df2 = pd.Series(ResultArray, index = ZeroCurveTerm).reset_index()
        df2.columns = ["PV01Term","PV01"]
        df3 = pd.Series(ResultArray2, index = EstZeroCurveTerm).reset_index()
        df3.columns = ["PV01TermEst","PVEst01"]
        if LoggingFlag > 0 : 
            df = ReadCSV(LoggingDir + "\\LoggingFilesBond.csv")
            GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
            CSR_RiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)   
            DataGIRR = MapGIRRDeltaGreeks(df2.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
            DataGIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
            DataGIRR2 = MapGIRRDeltaGreeks(df3.set_index("PV01TermEst")["PVEst01"], GIRR_DeltaRiskFactor).reset_index()
            DataGIRR2.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
            DataCSR = MapCSRDeltaGreeks(df2.set_index("PV01Term")["PV01"], CSR_RiskFactor).reset_index()
            DataCSR.columns = ["CSR_Tenor","CSR_Delta_Sensi"]       
            DataCSR2 = MapCSRDeltaGreeks(df3.set_index("PV01TermEst")["PVEst01"], CSR_RiskFactor).reset_index()
            DataCSR2.columns = ["CSR_Tenor","CSR_Delta_Sensi"]                   
            pd.concat([df, df2, df3, DataGIRR, DataGIRR2, DataCSR, DataCSR2],axis = 1).to_csv(LoggingDir + "\\LoggingFilesBond.csv", index = False, encoding = "cp949")
        return P, df2, df3

    df2 = pd.Series(ResultArray, index = ZeroCurveTerm).reset_index()
    df2.columns = ["PV01Term","PV01"]
    if LoggingFlag > 0 : 
        df = ReadCSV(LoggingDir + "\\LoggingFilesBond.csv")
        GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
        DataGIRR = MapGIRRDeltaGreeks(df2.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
        DataGIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
        CSR_RiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)   
        DataCSR = MapCSRDeltaGreeks(df2.set_index("PV01Term")["PV01"], CSR_RiskFactor).reset_index()
        DataCSR.columns = ["CSR_Tenor","CSR_Delta_Sensi"]       
        pd.concat([df, df2, DataGIRR, DataCSR],axis = 1).to_csv(LoggingDir + "\\LoggingFilesBond.csv", index = False, encoding = "cp949")
    return P, df2, df2           
    
def Calc_Schedule_ErrorCheck(Nominal, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, ZeroCurveTerm, 
                              ZeroCurveRate, NumCpnOneYear, DayCountFlag) : 
    ErrorFlag = 0
    ErrorString = ""
    if (Nominal < 0) :
        ErrorString += "\nCheck Nominal < 0"
        ErrorFlag = 1
        
    if (PriceDateYYYYMMDD > MaturityYYYYMMDD) :
        ErrorString += "\nCheck PriceDate > Maturity"
        ErrorFlag = 1
        
    if (EffectiveDateYYYYMMDD > MaturityYYYYMMDD) : 
        ErrorString += "\nCheck EffectiveDate > Maturity"
        ErrorFlag = 1
        
    if (len(ZeroCurveTerm) == 0 and len(ZeroCurveRate) == 0) : 
        ErrorString += "\nCheck ZeroCurveTerm Length = 0"
        ErrorFlag = 1
        
    if (PriceDateYYYYMMDD < 19000000) : 
        ErrorString += "\nPriceDate < 19000101"
        ErrorFlag = 1

    if (EffectiveDateYYYYMMDD < 19000000) : 
        ErrorString += "\nEffectiveDate < 19000101"
        ErrorFlag = 1

    if (MaturityYYYYMMDD < 19000000) : 
        ErrorString += "\nMaturity < 19000101"
        ErrorFlag = 1

    if (NumCpnOneYear < 0 ) : 
        ErrorString += "\nNumCpnOneYear < 0"
        ErrorFlag = 1

    if (DayCountFlag < 0 ) : 
        ErrorString += "\nDayCountFlag < 0"
        ErrorFlag = 1
        
    return ErrorFlag, ErrorString
    
def Calc_IRS(Nominal, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTerm, ZeroCurveRate, NumCpnOneYear, DayCountFlag, 
             KoreanHoliday = True, MaturityToPayDate = 0, EstZeroCurveTerm = [], EstZeroCurveRate = [], FixingHolidayList = [], 
             AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False, LoggingFlag = 0, LoggingDir = '', 
             ModifiedFollow = 1, OverNightRateDateHistory = [], OverNightRateHistory = [], LookBackDays = 0, ObservShift = False, 
             FixedPayerFlag = 0, DiscCurveNameLeg1 = "", EstCurveNameLeg1 = "", DiscCurveNameLeg2 = "", EstCurveNameLeg2 = "", 
             CMSFlag = 0, RefSwapMaturity_T = 0.25, RefSwapNCPNAnn = 4, TermVol = [], Vol = [] ) :
    
    LoggingFlag1, LoggingFlag2 = 0,0
    if LoggingFlag > 0 : 
        LoggingFlag1, LoggingFlag2 = 1, 2 

    Preprocessing_ZeroTermAndRate(ZeroCurveTerm, ZeroCurveRate, PriceDateYYYYMMDD)
    
    FixedLeg = Calc_Bond(Nominal, 0, 0, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
              PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
              NumCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm = EstZeroCurveTerm,
              EstZeroCurveRate = EstZeroCurveTerm, FixingHolidayList = FixingHolidayList, AdditionalPayHolidayList  = AdditionalPayHolidayList, NominalDateIsNominalPayDate = NominalDateIsNominalPayDate,
              LoggingFlag = LoggingFlag1, LoggingDir = LoggingDir, ModifiedFollow = ModifiedFollow, OverNightRateDateHistory = OverNightRateDateHistory, OverNightRateHistory = OverNightRateHistory, LookBackDays = LookBackDays, ObservShift = ObservShift, DiscCurveName = DiscCurveNameLeg1, EstCurveName = EstCurveNameLeg1)

    if len(EstZeroCurveTerm) > 0 and len(EstZeroCurveRate) > 0 : 
        Preprocessing_ZeroTermAndRate(EstZeroCurveTerm, EstZeroCurveRate, PriceDateYYYYMMDD)

    FloatLeg = Calc_Bond(Nominal, 0, 1 if LookBackDays== 0 else 2, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
            PriceDateYYYYMMDD, MaturityYYYYMMDD, 0.0, ZeroCurveTerm, ZeroCurveRate, 
            NumCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm = EstZeroCurveTerm,
            EstZeroCurveRate = EstZeroCurveRate, FixingHolidayList = FixingHolidayList, AdditionalPayHolidayList  = AdditionalPayHolidayList, NominalDateIsNominalPayDate = NominalDateIsNominalPayDate,
            LoggingFlag = LoggingFlag2, LoggingDir = LoggingDir, ModifiedFollow = ModifiedFollow, OverNightRateDateHistory = OverNightRateDateHistory, OverNightRateHistory = OverNightRateHistory, LookBackDays = LookBackDays, ObservShift = ObservShift, DiscCurveName= DiscCurveNameLeg2, EstCurveName = EstCurveNameLeg2,
            CMSFlag = CMSFlag, RefSwapMaturity_T = RefSwapMaturity_T, RefSwapNCPNAnn = RefSwapNCPNAnn, TermVol = TermVol, Vol = Vol)
    
    return FixedLeg - FloatLeg if FixedPayerFlag == 0 else FloatLeg - FixedLeg    
    
def Calc_IRS_PV01(Nominal, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTerm, ZeroCurveRate, NumCpnOneYear, DayCountFlag, 
             KoreanHoliday = True, MaturityToPayDate = 0, EstZeroCurveTerm = [], EstZeroCurveRate = [], FixingHolidayList = [], 
             AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False, LoggingFlag = 0, LoggingDir = '', 
             ModifiedFollow = 1, OverNightRateDateHistory = [], OverNightRateHistory = [], LookBackDays = 0, ObservShift = False, 
             FixedPayerFlag = 0, DiscCurveNameLeg1 = "", EstCurveNameLeg1 = "", DiscCurveNameLeg2 = "", EstCurveNameLeg2 = "",
             CMSFlag = 0, RefSwapMaturity_T = 0.25, RefSwapNCPNAnn = 4, TermVol = [], Vol = []) : 
    LookBackDays = max(0, LookBackDays)
    
    P = Calc_IRS(Nominal, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTerm, ZeroCurveRate, NumCpnOneYear, DayCountFlag, 
             KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm , EstZeroCurveRate , FixingHolidayList , 
             AdditionalPayHolidayList , NominalDateIsNominalPayDate , LoggingFlag , LoggingDir , 
             ModifiedFollow , OverNightRateDateHistory , OverNightRateHistory , LookBackDays , ObservShift, 
             FixedPayerFlag, DiscCurveNameLeg1 = DiscCurveNameLeg1, EstCurveNameLeg1 = EstCurveNameLeg1, DiscCurveNameLeg2 = DiscCurveNameLeg2, EstCurveNameLeg2 = EstCurveNameLeg2,
             CMSFlag = CMSFlag, RefSwapMaturity_T = RefSwapMaturity_T, RefSwapNCPNAnn = RefSwapNCPNAnn, TermVol = TermVol, Vol = Vol)

    ResultArray = np.zeros(len(ZeroCurveRate))
    for i in range(len(ZeroCurveTerm)) : 
        ZeroUp = np.array(ZeroCurveRate).copy()
        ZeroUp[i] += 0.0001
        Pu = Calc_IRS(Nominal, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTerm, ZeroUp, NumCpnOneYear, DayCountFlag, 
             KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm , EstZeroCurveRate , FixingHolidayList , 
             AdditionalPayHolidayList , NominalDateIsNominalPayDate , LoggingFlag , LoggingDir , 
             ModifiedFollow , OverNightRateDateHistory , OverNightRateHistory , LookBackDays , ObservShift, 
             FixedPayerFlag, DiscCurveNameLeg1 = DiscCurveNameLeg1, EstCurveNameLeg1 = EstCurveNameLeg1, DiscCurveNameLeg2 = DiscCurveNameLeg2, EstCurveNameLeg2 = EstCurveNameLeg2,
             CMSFlag = CMSFlag, RefSwapMaturity_T = RefSwapMaturity_T, RefSwapNCPNAnn = RefSwapNCPNAnn, TermVol = TermVol, Vol = Vol)

        ResultArray[i] = Pu - P
        
    if (len(EstZeroCurveRate) > 0 and len(EstZeroCurveTerm) > 0 and len(EstZeroCurveRate) == len(EstZeroCurveTerm)) : 
        ResultArray2 = np.zeros(len(EstZeroCurveTerm))
        for i in range(len(EstZeroCurveRate)) : 
            ZeroUp = np.array(EstZeroCurveRate).copy()
            ZeroUp[i] += 0.0001            
            Pu = Calc_IRS(Nominal, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTerm, ZeroCurveRate, NumCpnOneYear, DayCountFlag, 
             KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm , ZeroUp , FixingHolidayList , 
             AdditionalPayHolidayList , NominalDateIsNominalPayDate , LoggingFlag , LoggingDir , 
             ModifiedFollow , OverNightRateDateHistory , OverNightRateHistory , LookBackDays , ObservShift, 
             FixedPayerFlag, DiscCurveNameLeg1 = DiscCurveNameLeg1, EstCurveNameLeg1 = EstCurveNameLeg1, DiscCurveNameLeg2 = DiscCurveNameLeg2, EstCurveNameLeg2 = EstCurveNameLeg2,
             CMSFlag = CMSFlag, RefSwapMaturity_T = RefSwapMaturity_T, RefSwapNCPNAnn = RefSwapNCPNAnn, TermVol = TermVol, Vol = Vol)
            ResultArray2[i] = Pu - P

        df2 = pd.Series(ResultArray, index = ZeroCurveTerm).reset_index()
        df2.columns = ["PV01Term","PV01"]
        df3 = pd.Series(ResultArray2, index = EstZeroCurveTerm).reset_index()
        df3.columns = ["PV01TermEst","PVEst01"]
        if LoggingFlag > 0 : 
            df = ReadCSV(LoggingDir + "\\LoggingFilesIRS.csv")
            GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
            DataGIRR = MapGIRRDeltaGreeks(df2.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
            DataGIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
            DataGIRR2 = MapGIRRDeltaGreeks(df3.set_index("PV01TermEst")["PVEst01"], GIRR_DeltaRiskFactor).reset_index()
            DataGIRR2.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
            pd.concat([df, df2, df3, DataGIRR, DataGIRR2],axis = 1).to_csv(LoggingDir + "\\LoggingFilesIRS.csv", index = False, encoding = "cp949")
        return P, df2, df3

    df2 = pd.Series(ResultArray, index = ZeroCurveTerm).reset_index()
    df2.columns = ["PV01Term","PV01"]
    df3 = pd.DataFrame([], columns = ["PV01TermEst","PVEst01"], index = [0.0]).fillna(0)
    if LoggingFlag > 0 : 
        df = ReadCSV(LoggingDir + "\\LoggingFilesIRS.csv")
        GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
        DataGIRR = MapGIRRDeltaGreeks(df2.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
        DataGIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
        pd.concat([df, df2, DataGIRR],axis = 1).to_csv(LoggingDir + "\\LoggingFilesIRS.csv", index = False, encoding = "cp949")
    return P, df2, df3          
    
def Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
             DayCountFlagForeign, KoreanHoliday = False, MaturityToPayDate = 0, EstZeroCurveTermDomestic = [], EstZeroCurveRateDomestic = [], 
             EstZeroCurveTermForeign = [], EstZeroCurveRateForeign = [], ZeroCurveTermForeign = [], ZeroCurveRateForeign = [], FixingHolidayListDomestic = [], 
             FixingHolidayListForeign = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = True, LoggingFlag = 0, LoggingDir = '', 
             ModifiedFollow = 1,LookBackDaysDomestic = 0, LookBackDaysForeign = 0, ObservShift = False, DomesticPayerFlag = 0, 
             DiscCurveName = "", EstCurveName = "", ValuationDomesticFX = 1.0, ValuationForeignFX = 1.0, SOFRFlag = False, FixFixFlag = False, FirstFloatFixRateForeign = 0, DiscCurveNameForeign = "", EstCurveNameForeign = "") :
    
    FirstFloatFixRateForeign = FirstFloatFixRate if FirstFloatFixRateForeign == 0 else FirstFloatFixRateForeign
    ValuationFlag = 1 if int(PriceDateYYYYMMDD) > int(EffectiveDateYYYYMMDD) else 0
    LoggingFlag1, LoggingFlag2 = 0,0
    if LoggingFlag > 0 : 
        LoggingFlag1, LoggingFlag2 = 1, 2 

    Preprocessing_ZeroTermAndRate(ZeroCurveTermDomestic, ZeroCurveRateDomestic, PriceDateYYYYMMDD)
    if len(EstZeroCurveTermDomestic) > 0 and len(EstZeroCurveRateDomestic) > 0 : 
        Preprocessing_ZeroTermAndRate(EstZeroCurveTermDomestic, EstZeroCurveRateDomestic, PriceDateYYYYMMDD)
        
    if len(ZeroCurveTermForeign) > 0 and len(ZeroCurveRateForeign)  : 
        Preprocessing_ZeroTermAndRate(ZeroCurveTermForeign, ZeroCurveRateForeign, PriceDateYYYYMMDD)
        
    if len(ZeroCurveTermForeign) > 0 and len(ZeroCurveRateForeign)  : 
        Preprocessing_ZeroTermAndRate(ZeroCurveTermForeign, ZeroCurveRateForeign, PriceDateYYYYMMDD)
    
    FloatFlagDomestic = 0
    FloatFlagForeign = 1 if SOFRFlag == False else 2
    if len(EstZeroCurveRateDomestic) > 0 : 
        FloatFlagDomestic = 1 if SOFRFlag == False else 2
    if FixFixFlag == True : 
        FloatFlagDomestic, FloatFlagForeign = 0, 0
                 
    FixedLeg = Calc_Bond(NominalDomestic, 1, FloatFlagDomestic, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
              PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, 
              NumCpnOneYear, DayCountFlagDomestic, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm = EstZeroCurveTermDomestic,
              EstZeroCurveRate = EstZeroCurveRateDomestic, FixingHolidayList = FixingHolidayListDomestic, AdditionalPayHolidayList  = AdditionalPayHolidayList, NominalDateIsNominalPayDate = NominalDateIsNominalPayDate,
              LoggingFlag = LoggingFlag1, LoggingDir = LoggingDir, ModifiedFollow = ModifiedFollow, LookBackDays = LookBackDaysDomestic, ObservShift = ObservShift, DiscCurveName = DiscCurveName, EstCurveName = EstCurveName)

    FloatLeg = Calc_Bond(NominalForeign, 1, FloatFlagForeign, FirstFloatFixRateForeign, EffectiveDateYYYYMMDD, 
            PriceDateYYYYMMDD, MaturityYYYYMMDD, 0.0, ZeroCurveTermForeign, ZeroCurveRateForeign, 
            NumCpnOneYear, DayCountFlagForeign, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm = EstZeroCurveTermForeign,
            EstZeroCurveRate = EstZeroCurveRateForeign, FixingHolidayList = FixingHolidayListForeign, AdditionalPayHolidayList  = AdditionalPayHolidayList, NominalDateIsNominalPayDate = NominalDateIsNominalPayDate,
            LoggingFlag = LoggingFlag2, LoggingDir = LoggingDir, ModifiedFollow = ModifiedFollow, LookBackDays = LookBackDaysForeign, ObservShift = ObservShift, DiscCurveName = DiscCurveNameForeign, EstCurveName = EstCurveNameForeign)
    if ValuationFlag == 0 : 
        return FixedLeg - FloatLeg if DomesticPayerFlag == 0 else FloatLeg - FixedLeg    
    else : 
        return FixedLeg *ValuationDomesticFX - FloatLeg *ValuationForeignFX if DomesticPayerFlag == 0 else FloatLeg *ValuationForeignFX - FixedLeg *ValuationDomesticFX    

def CalC_CRS_PV01(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
             DayCountFlagForeign, KoreanHoliday = False, MaturityToPayDate = 0, EstZeroCurveTermDomestic = [], EstZeroCurveRateDomestic = [], 
             EstZeroCurveTermForeign = [], EstZeroCurveRateForeign = [], ZeroCurveTermForeign = [], ZeroCurveRateForeign = [], FixingHolidayListDomestic = [], 
             FixingHolidayListForeign = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = True, LoggingFlag = 0, LoggingDir = '', 
             ModifiedFollow = 1,LookBackDaysDomestic = 0, LookBackDaysForeign = 0, ObservShift = False, DomesticPayerFlag = 0, 
             DiscCurveName = "", EstCurveName = "", ValuationDomesticFX = 1.0, ValuationForeignFX = 1.0, SOFRFlag = False, FixFixFlag = False, FirstFloatFixRateForeign = 0, DiscCurveNameForeign = "", EstCurveNameForeign = "") : 
    
    P = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
                DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , EstZeroCurveRateDomestic, 
                EstZeroCurveTermForeign, EstZeroCurveRateForeign, ZeroCurveTermForeign, ZeroCurveRateForeign, FixingHolidayListDomestic, 
                FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign )

    ResultArray = np.zeros(len(ZeroCurveTermDomestic))
    for i in range(len(ZeroCurveTermDomestic)) : 
        ZeroUp = np.array(ZeroCurveRateDomestic).copy()
        ZeroUp[i] += 0.0001
        Pu = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                CpnRate, ZeroCurveTermDomestic, ZeroUp, NumCpnOneYear, DayCountFlagDomestic, 
                DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , EstZeroCurveRateDomestic, 
                EstZeroCurveTermForeign, EstZeroCurveRateForeign, ZeroCurveTermForeign, ZeroCurveRateForeign, FixingHolidayListDomestic, 
                FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign)

        ResultArray[i] = Pu - P

    ResultArray2 = np.zeros(len(ZeroCurveTermForeign))
    for i in range(len(ZeroCurveTermForeign)) : 
        ZeroUp = np.array(ZeroCurveRateForeign).copy()
        ZeroUp[i] += 0.0001
        Pu = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
                DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , EstZeroCurveRateDomestic, 
                EstZeroCurveTermForeign, EstZeroCurveRateForeign, ZeroCurveTermForeign, ZeroUp, FixingHolidayListDomestic, 
                FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign)

        ResultArray2[i] = Pu - P
    
    ResultArray3 = np.zeros(len(EstZeroCurveTermDomestic))
    if len(EstZeroCurveTermDomestic) > 0 :
        for i in range(len(EstZeroCurveTermDomestic)) : 
            ZeroUp = np.array(EstZeroCurveRateDomestic).copy()
            ZeroUp[i] += 0.0001
            Pu = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                    CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
                    DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , ZeroUp, 
                    EstZeroCurveTermForeign, EstZeroCurveRateForeign, ZeroCurveTermForeign, ZeroCurveRateForeign, FixingHolidayListDomestic, 
                    FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                    ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                    DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign)

            ResultArray3[i] = Pu - P        

    ResultArray4 = np.zeros(len(EstZeroCurveTermForeign))
    if len(EstZeroCurveTermForeign) > 0 : 
        for i in range(len(EstZeroCurveTermForeign)) : 
            ZeroUp = np.array(EstZeroCurveRateForeign).copy()
            ZeroUp[i] += 0.0001
            Pu = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                    CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
                    DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , EstZeroCurveRateDomestic, 
                    EstZeroCurveTermForeign, ZeroUp, ZeroCurveTermForeign, ZeroCurveRateForeign, FixingHolidayListDomestic, 
                    FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                    ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                    DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign)

            ResultArray4[i] = Pu - P        
            
    df = pd.Series(ResultArray, index = ZeroCurveTermDomestic).reset_index()
    df.columns = ["PV01TermDomesticDisc","PV01DomesticDisc"]
    df2 = pd.Series(ResultArray2, index = ZeroCurveTermForeign).reset_index()
    df2.columns = ["PV01TermForeignDisc","PV01ForeignDisc"]    
    df3 = pd.Series(ResultArray3, index = EstZeroCurveTermDomestic).reset_index()
    df3.columns = ["PV01TermDomesticEst","PV01DomesticEst"]
    df4 = pd.Series(ResultArray4, index = EstZeroCurveTermForeign).reset_index()
    df4.columns = ["PV01TermForeignEst","PV01ForeignEst"]
    if LoggingFlag > 0 : 
        MyData = ReadCSV(LoggingDir + "\\LoggingFilesIRS.csv")
        GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
        Data_GIRR1 = MapGIRRDeltaGreeks(df.set_index("PV01TermDomesticDisc")["PV01DomesticDisc"], GIRR_DeltaRiskFactor).reset_index()
        Data_GIRR1.columns = ["Leg1Disc_GIRR_Tenor","Leg1Disc_GIRR_Delta_Sensi"]
        Data_GIRR2 = MapGIRRDeltaGreeks(df2.set_index("PV01TermForeignDisc")["PV01ForeignDisc"], GIRR_DeltaRiskFactor).reset_index()
        Data_GIRR2.columns = ["Leg2Disc_GIRR_Tenor","Leg2Disc_GIRR_Delta_Sensi"]
        Data_GIRR3 = MapGIRRDeltaGreeks(df3.set_index("PV01TermDomesticEst")["PV01DomesticEst"], GIRR_DeltaRiskFactor).reset_index()
        Data_GIRR3.columns = ["Leg1Est_GIRR_Tenor","Leg1Est_GIRR_Delta_Sensi"]
        Data_GIRR4 = MapGIRRDeltaGreeks(df4.set_index("PV01TermForeignEst")["PV01ForeignEst"], GIRR_DeltaRiskFactor).reset_index()
        Data_GIRR4.columns = ["Leg2Est_GIRR_Tenor","Leg2Est_GIRR_Delta_Sensi"]
        pd.concat([MyData, df, df2, df3, df4, Data_GIRR1, Data_GIRR2, Data_GIRR3, Data_GIRR4],axis = 1).to_csv(LoggingDir + "\\LoggingFilesIRS.csv", index = False, encoding = "cp949")
        
    return P, df, df2, df3, df4

def Calc_Current_FXForward(Spot, T, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, SpotT = 0) : 
    if SpotT == 0 :         
        rd = Linterp(DomesticTerm, DomesticRate, T)
        rf = Linterp(ForeignTerm, ForeignRate, T)
        DF_d = np.exp(-rd * T)
        DF_f = np.exp(-rf * T)
    else : 
        DF_d = Calc_ForwardDiscount_Factor(DomesticTerm, DomesticRate, SpotT, T)
        DF_f = Calc_ForwardDiscount_Factor(ForeignTerm, ForeignRate, SpotT, T)        
    return Spot * DF_f/DF_d
    
def Calc_Value_FXSwap(Spot, T1, T2, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, long0short1, SpotT = 0, NominalForeign = 100, ForwardPrice1 = 0, ForwardPrice2 = 0) : 
    if (T1 >= 0.0) : 
        F1 = NominalForeign * Calc_ForwardDiscount_Factor(ForeignTerm, ForeignRate, SpotT, T1)
        if ForwardPrice1 == 0 : 
            D1 = NominalForeign * Calc_Current_FXForward(Spot, T1, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, SpotT) * Calc_ForwardDiscount_Factor(DomesticTerm, DomesticRate, SpotT, T1)
        else : 
            D1 = NominalForeign * ForwardPrice1 * Calc_ForwardDiscount_Factor(DomesticTerm, DomesticRate, SpotT, T1)
    else :
        D1, F1 = 0, 0
    F2 = NominalForeign * Calc_ForwardDiscount_Factor(ForeignTerm, ForeignRate, SpotT, T2)
    if ForwardPrice2 == 0 : 
        D2 = NominalForeign * Calc_Current_FXForward(Spot, T2, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, SpotT) * Calc_ForwardDiscount_Factor(DomesticTerm, DomesticRate, SpotT, T2)
    else : 
        D2 = NominalForeign * ForwardPrice2 * Calc_ForwardDiscount_Factor(DomesticTerm, DomesticRate, SpotT, T2)
        
    VF = F1 - F2 if long0short1 == 0 else F2 - F1
    VD = - D1 + D2 if long0short1 == 0 else D1 - D2
    P = VF * Spot - VD if long0short1 == 0 else VF * Spot - VD
    return P, VD, VF

def BS_Cap(
    NA,                # 액면금액
    VolFlag,           # 0: Black Vol, 1: Normal Vol
    Vol,               # 변동성
    DF,                # 할인계수 리스트 (길이: nDates + 1)
    StrikeRate,        # 행사금리
    Dates,             # 각 지급일까지의 일수 리스트 (길이: nDates)
    FirstStartDay,     # 첫 시작일
    FirstFixingRate,   # 첫 추정금리
    AverageFlag,       # 평균 계산 여부
    deltat,            # 각 기간에 대한 델타 리스트
    AllStrikeATMFlag,  # 1: F를 행사금리로 사용, 2: swaprate 사용
    swaprate           # 스왑레이트
):
    PrevT = FirstStartDay / 365.0
    value = 0.0
    nDates = len(Dates)
    
    if AverageFlag == 0:
        if VolFlag == 0:  # Black vol
            
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                F = (PrevDisc / Disc - 1.0) / delta
                if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                    F = FirstFixingRate

                if i == 0:
                    if PrevT <= 0.0:
                        if F > StrikeRate:
                            value = deltat[i] * Disc * (F - StrikeRate)
                    else:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (np.log(F / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (F * CDF_N(d1) - StrikeRate * CDF_N(d2))
                else:
                    if F > 0.0:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (np.log(F / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (F * CDF_N(d1) - StrikeRate * CDF_N(d2))
                    else:
                        value += 1e-13
                PrevT = T
        else:  # Normal vol
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                F = (PrevDisc / Disc - 1.0) / delta
                if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                    F = FirstFixingRate

                if i == 0:
                    if PrevT <= 0.0:
                        if F > StrikeRate:
                            value = deltat[i] * Disc * (F - StrikeRate)
                    else:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (F - StrikeRate) / (Vol * np.sqrt(PrevT))
                        value += deltat[i] * Disc * (
                            (F - StrikeRate) * CDF_N(d1) + Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                        )
                else:
                    if AllStrikeATMFlag == 1:
                        StrikeRate = F
                    elif AllStrikeATMFlag == 2:
                        StrikeRate = swaprate
                    d1 = (F - StrikeRate) / (Vol * np.sqrt(PrevT))
                    value += deltat[i] * Disc * (
                        (F - StrikeRate) * CDF_N(d1) + Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                    )

                PrevT = T
    else:
        F_Avg = 0.0
        for i in range(nDates):
            T = Dates[i] / 365.0
            delta = T - PrevT

            PrevDisc = DF[i]
            Disc = DF[i + 1]

            F = (PrevDisc / Disc - 1.0) / delta
            if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                F = FirstFixingRate

            F_Avg += F / nDates
            PrevT = T

        PrevT = FirstStartDay / 365.0
        for i in range(nDates):
            T = Dates[i] / 365.0
            delta = T - PrevT

            PrevDisc = DF[i]
            Disc = DF[i + 1]

            if VolFlag == 0:
                if i == 0:
                    if PrevT <= 0.0 and F_Avg > StrikeRate:
                        value = deltat[i] * Disc * (F_Avg - StrikeRate)
                    else:
                        d1 = (np.log(F_Avg / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (F_Avg * CDF_N(d1) - StrikeRate * CDF_N(d2))
                else:
                    if F_Avg > 0.0:
                        d1 = (np.log(F_Avg / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (F_Avg * CDF_N(d1) - StrikeRate * CDF_N(d2))
                    else:
                        value += 1e-13
            else:
                if i == 0:
                    if PrevT <= 0.0 and F_Avg > StrikeRate:
                        value = deltat[i] * Disc * (F_Avg - StrikeRate)
                    else:
                        d1 = (F_Avg - StrikeRate) / (Vol * np.sqrt(PrevT))
                        value += deltat[i] * Disc * (
                            (F_Avg - StrikeRate) * CDF_N(d1) + Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                        )
                else:
                    d1 = (F_Avg - StrikeRate) / (Vol * np.sqrt(PrevT))
                    value += deltat[i] * Disc * (
                        (F_Avg - StrikeRate) * CDF_N(d1) + Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                    )
            PrevT = T
    
    return NA * value    
    
def BS_Floor(
    NA,                  # 액면금액
    VolFlag,             # 0: Black Vol, 1: Normal Vol
    Vol,                 # 변동성
    DF,                  # 할인계수 리스트 (nDates + 1)
    StrikeRate,          # 행사금리
    Dates,               # 각 지급일까지의 일수 리스트 (길이: nDates)
    FirstStartDay,
    FirstFixingRate,
    AverageFlag,
    deltat,              # 기간별 델타 리스트 (길이: nDates)
    AllStrikeATMFlag,
    swaprate
):
    PrevT = FirstStartDay / 365.0
    value = 0.0
    nDates = len(Dates)

    if AverageFlag == 0:
        if VolFlag == 0:  # Black vol
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                F = (PrevDisc / Disc - 1.0) / delta
                if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                    F = FirstFixingRate

                if i == 0:
                    if PrevT <= 0.0:
                        if F < StrikeRate:
                            value = deltat[i] * Disc * (StrikeRate - F)
                    else:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (np.log(F / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (-F * CDF_N(-d1) + StrikeRate * CDF_N(-d2))
                else:
                    if F > 0.0:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (np.log(F / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (-F * CDF_N(-d1) + StrikeRate * CDF_N(-d2))
                    else:
                        value += 1e-13

                PrevT = T
        else:  # Normal vol
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                F = (PrevDisc / Disc - 1.0) / delta
                if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                    F = FirstFixingRate

                if i == 0:
                    if PrevT <= 0.0:
                        if F < StrikeRate:
                            value = deltat[i] * Disc * (StrikeRate - F)
                    else:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (F - StrikeRate) / (Vol * np.sqrt(PrevT))
                        value += deltat[i] * Disc * (
                            (StrikeRate - F) * CDF_N(-d1) +
                            Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                        )
                else:
                    if AllStrikeATMFlag == 1:
                        StrikeRate = F
                    elif AllStrikeATMFlag == 2:
                        StrikeRate = swaprate
                    d1 = (F - StrikeRate) / (Vol * np.sqrt(PrevT))
                    value += deltat[i] * Disc * (
                        (StrikeRate - F) * CDF_N(-d1) +
                        Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                    )

                PrevT = T
    else:
        F_Avg = 0.0
        for i in range(nDates):
            T = Dates[i] / 365.0
            delta = T - PrevT

            PrevDisc = DF[i]
            Disc = DF[i + 1]

            F = (PrevDisc / Disc - 1.0) / delta
            if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                F = FirstFixingRate

            F_Avg += F / nDates
            PrevT = T

        PrevT = FirstStartDay / 365.0
        if VolFlag == 0:
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                if i == 0:
                    if PrevT <= 0.0:
                        if F_Avg < StrikeRate:
                            value = deltat[i] * Disc * (StrikeRate - F_Avg)
                    else:
                        d1 = (np.log(F_Avg / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (-F_Avg * CDF_N(-d1) + StrikeRate * CDF_N(-d2))
                else:
                    if F_Avg > 0.0:
                        d1 = (np.log(F_Avg / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (-F_Avg * CDF_N(-d1) + StrikeRate * CDF_N(-d2))
                    else:
                        value += 1e-13

                PrevT = T
        else:  # Normal vol
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                if i == 0:
                    if PrevT <= 0.0:
                        if F_Avg < StrikeRate:
                            value = deltat[i] * Disc * (StrikeRate - F_Avg)
                    else:
                        d1 = (F_Avg - StrikeRate) / (Vol * np.sqrt(PrevT))
                        value += deltat[i] * Disc * (
                            (StrikeRate - F_Avg) * CDF_N(-d1) +
                            Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                        )
                else:
                    d1 = (F_Avg - StrikeRate) / (Vol * np.sqrt(PrevT))
                    value += deltat[i] * Disc * (
                        (StrikeRate - F_Avg) * CDF_N(-d1) +
                        Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                    )

                PrevT = T

    return NA * value    

def Pricing_CapFloor(
    CapFloorFlag,            # 0: Cap, 1: Floor
    PriceDate,
    StartDate,
    SwapMaturityDate,
    AnnCpnOneYear,
    NA,
    Vol,
    StrikePrice,
    UseStrikeAsAverage,
    Term,
    Rate,
    DayCountFracFlag,
    VolFlag,
    HolidayYYYYMMDD,
    FirstFixingRate,
    AverageFlag,
    AllStrikeATMFlag,
    ResultValue             # Output: length = 4 + NTerm (but only 2 values used)
):
    ResultCode = 0
    NHoliday = len(HolidayYYYYMMDD)
    if StrikePrice > 1 : 
        StrikePrice = StrikePrice /100
    if PriceDate < 19000000:
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
    if StartDate < 19000000:
        StartDate = ExcelDateToYYYYMMDD(StartDate)
    if SwapMaturityDate < 19000000:
        SwapMaturityDate = ExcelDateToYYYYMMDD(SwapMaturityDate)
    Temp = [20000101]
    NBDayFromEndDate = NBusinessCountFromEndToPay(StartDate, SwapMaturityDate, HolidayYYYYMMDD,1, Temp)    
    StartDate = ParseBusinessDateIfHoliday(StartDate, HolidayYYYYMMDD)
    Preprocessing_ZeroTermAndRate(Term, Rate, PriceDate)
    
    EndYYYYMM = SwapMaturityDate // 100
    EndDD = StartDate % 100
    SwapMaturityDate = EndYYYYMM * 100 + EndDD

    TempDate = StartDate
    FixingDate, CpnDate, ResultPayDate, ResultNBD = MappingCouponDates(1,StartDate,SwapMaturityDate,NBDayFromEndDate,AnnCpnOneYear,1,HolidayYYYYMMDD,HolidayYYYYMMDD,1)
    NCpnDate = len(CpnDate)
    DaysCpnDate = [DayCountAtoB(PriceDate, d) for d in CpnDate]
    FirstStartDay = DayCountAtoB(PriceDate, StartDate)

    DF = [0.0] * (len(CpnDate) + 1)
    deltat = [0.0] * len(CpnDate)
    for i in range(len(CpnDate)):
        if i == 0:
            deltat[i] = DayCountFractionAtoB(StartDate, CpnDate[i], DayCountFracFlag)
        else:
            deltat[i] = DayCountFractionAtoB(CpnDate[i - 1], CpnDate[i], DayCountFracFlag)

    t = DayCountAtoB(PriceDate, StartDate) / 365.0
    r = Linterp(Term, Rate, t)
    DF[0] = np.exp(-r * t)

    for i in range(len(CpnDate)):
        t = DayCountAtoB(PriceDate, CpnDate[i]) / 365.0
        r = Linterp(Term, Rate, t)
        DF[i + 1] = np.exp(-r * t)

    if UseStrikeAsAverage > 0:
        F_Avg = 0.0
        PrevT = FirstStartDay / 365.0
        for i in range(len(CpnDate)):
            T = DaysCpnDate[i] / 365.0
            delta = T - PrevT
            PrevDisc = DF[i]
            Disc = DF[i + 1]
            F = (PrevDisc / Disc - 1.0) / delta
            if abs(FirstFixingRate) > 1e-6:
                F = FirstFixingRate
            F_Avg += F / len(CpnDate)
            PrevT = T
        StrikePrice = F_Avg

    swprate = FSR(PriceDate, StartDate, SwapMaturityDate, AnnCpnOneYear,DayCountFracFlag, HolidayYYYYMMDD, Term, Rate, Term, Rate )

    if CapFloorFlag == 0:
        swv = BS_Cap(NA, VolFlag, Vol, DF, StrikePrice,
                     DaysCpnDate, FirstStartDay,
                     FirstFixingRate, AverageFlag, deltat,
                     AllStrikeATMFlag, swprate)
    else:
        swv = BS_Floor(NA, VolFlag, Vol, DF, StrikePrice,
                       DaysCpnDate, FirstStartDay,
                       FirstFixingRate, AverageFlag, deltat,
                       AllStrikeATMFlag, swprate)

    ResultValue[0] = swv
    ResultValue[1] = swprate
    ResultValue[2] = StrikePrice if AllStrikeATMFlag != 2 else swprate

    return ResultValue


    
def Pricing_IRCallableSwap_HWFDM(
    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
    Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
    NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
    Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
    ZeroRate, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
    kappa = 0.01, kappa2 = 0.01, HWVolTerm = [0.0001], HWVol = [0.006323], HWVolTerm2 = [0.0001], 
    HWVol2 = [0.003323], HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = 0, 
    LoggingDir = os.getcwd(), Leg1_DiscCurveName = "TempCurve", Leg1_EstCurveName = "TempCurve", Leg2_DiscCurveName = "TempCurve",
    Leg2_EstCurveName = "TempCurve", KoreanAutoHolidayFlag = True, FixHolidays = [], PayHolidays = [],
    Leg1_Phase2UseFlag = 0, NumCpnOneYear_Leg1_Phase2 = 0, Leg1_Phase2StartDate = 20280929, Leg1_RefSwapRate_Multiple_Phase2 = 0.0, Leg1_FixedCpnRate_Phase2 = 0.0237,   
    Leg2_Phase2UseFlag = 0, NumCpnOneYear_Leg2_Phase2 = 4, Leg2_Phase2StartDate = 20280929, Leg2_RefSwapRate_Multiple_Phase2 = 1.0, Leg2_FixedCpnRate_Phase2 = -0.0012,
    Leg1_PowerSpreadFlag = 0, Leg1_RefSwapMaturity_T_PowerSpread = 0.25, Leg2_PowerSpreadFlag = 0, Leg2_RefSwapMaturity_T_PowerSpread = 0.25,
    MaxReturn = 1000, MaxLoss = -1000
    ) : 
        
    '''
    Description : Pricing IRCallable Swap Using Hull White 1, 2Factor Model
    
    Variables : 
        Nominal -> Nominal Amount | <float or int>
        SwapEffectiveDate -> Swap Effective Date (YYYYMMDD) | <int>
        PriceDate -> Pricing Date (YYYYMMDD) | <int>
        SwapMaturity -> Swap Maturity (YYYYMMDD) | <int>
        NumCpnOneYear_Leg1_Phase1 -> Leg1) Number of Cpn for One Year(if ZeroCouponCallable Then input 0) | <int>
        Leg1_RefSwapMaturity_T -> Leg1) Reference Rate Maturity to Convert T (ex 0.25, 0.5, 1, ...) | <float>
        Leg1_RefSwapNCPNOneYear -> Leg1) Reference Rate Number of Swap Cpn for One Year | <int>
        Leg1_FixedCpnRate_Phase1 -> Leg1) Fixed Cpn Rate Phase1 | <float>
        Leg1_DayCount -> Leg1) DayCountFlag <int> [0: Act365 1: Act360 2: ActAct 3:30/360, ZeroCompoundCoupon = {5: Act365, 6:Act360, 7: ActAct, 8:30/360}]
        NumCpnOneYear_Leg2_Phase1 -> Leg2) Number of Cpn for One Year <int> (if ZeroCouponCallable Then input 0)
        Leg2_RefSwapMaturity_T -> Leg2) Reference Rate Maturity to Convert T (ex 0.25, 0.5, 1, ...) <float>
        Leg2_RefSwapNCPNOneYear -> Leg2) Reference Rate Number of Swap Cpn for One Year <int>
        Leg2_FixedCpnRate_Phase1 -> Leg2) Fixed Cpn Rate Phase1 <float>
        Leg2_DayCount -> Leg2) DayCountFlag <int> [0: Act365 1: Act360 2: ActAct 3:30/360, ZeroCompoundCoupon = {5: Act365, 6:Act360, 7: ActAct, 8:30/360}]
        OptionFixDate -> Option Fix Date (YYYYMMDD <int Array>)
        OptionPayDate -> Option Pay Date (YYYYMMDD <int Array>)
        OptionHolder_0Recever1Payer -> 0 if Receiver have option else 1(Payer have)
        ZeroTerm -> Zero Discount Term Array <float Array>
        ZeroRate -> Zero Discount Rate Array <float Array>
        Leg1_FixingHistoryDate -> Leg1) Fixing Rate Date History Array <int Array>
        Leg1_FixingHistoryRate -> Leg1) Fixing Rate History Array <float Array>
        Leg2_FixingHistoryDate -> Leg2) Fixing Rate Date History Array <int Array>
        Leg2_FixingHistoryRate -> Leg2) Fixing Rate History Array <float Array>
        kappa -> Mean Revert Param <float>
        kappa2 -> Mean Revert Param2 <float>
        HWVolTerm -> Hull White 1F Vol Term <float Array>
        HWVol -> Hull White 1F Vol Term <float Array> 
        HWVolTerm2 -> Hull White 2F Vol Term <float Array>
        HWVol2 -> Hull White 2F Vol Term <float Array> 
        HWRho12Factor -> Corr between 1, 2 OS Process Randomness <float>
        CpnRounding -> Coupon Rounding <int>
        HW2FFlag -> 0 if HW1F else 1
        LoggingDir -> Logging Directory <String>
        KoreanAutoHolidayFlag -> True if Korean Schedule else False
        FixHolidays -> Fixing Holiday Using Calculating Fixing Rate <int Array>
        PayHolidays -> Holiday Using FixingEndDate to Payment <int Array>
        
    SampleVariable : 
    
        Nominal = 20000
        SwapEffectiveDate, PriceDate, SwapMaturity = 20160929, 20250304, 20460929
        NumCpnOneYear_Leg1_Phase1, Leg1_RefSwapRate_Multiple_Phase1, Leg1_FixedCpnRate_Phase1, Leg1_DayCount = 0, 0.0, 0.0237,  3
        NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_FixedCpnRate_Phase1, Leg2_DayCount = 4, 1.0, -0.0012, 0
        OptionFixDate = [20190902,20200903,20210831,20220901,20230904,20240830,20250903,20260901,20270831,20280905,20290903,20300830,20310903,20320901,20330831,20340831,20350903,20360903,20370903,20380903,20390905,20400905,20410904,20420903,20430904,20440905,20450905]
        OptionPayDate = [20190930,20200929,20210929,20220929,20231004,20240930,20250929,20260929,20270929,20280929,20291001,20300930,20310929,20320929,20330929,20340929,20351001,20360929,20370929,20380929,20390929,20401001,20410930,20421001,20430929,20440929,20450929]
        OptionHolder = 1
        Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear = 0.25, 4
        Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear = 0.25, 4

        ZeroTerm = [0.00274, 0.00548, 0.25479, 0.506849, 0.756164, 1.00274, 1.512329, 2.00274, 3.00822, 4.00548, 5.00548, 6.00548, 7.008219, 8.013699, 9.010959, 10.00822, 12.01096, 15.0137, 20.01918, 25.02466, 30.02192]
        ZeroRate = [0.027989, 0.027992, 0.028394, 0.027554, 0.026807, 0.02633, 0.025806, 0.025455, 0.025154, 0.025235, 0.025264, 0.025397, 0.025531, 0.025638, 0.025719, 0.025856, 0.026049, 0.025598, 0.024243, 0.022474, 0.021085]
        kappa = -0.0133
        kappa2 = 0.01
        HWVolTerm = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52]
        HWVol = [0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368]
        HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52]
        HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2
        HWRho12Factor = -0.3
        CpnRounding = 15
        HW2FFlag = 0

        Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2 = 0, 0
        Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2= 20280929, 0.0, 0.0237
        Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2 = 0, 4
        Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2 = 20280929, 1.0, -0.0012
        Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = 0, 0.25
        Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = 0, 0.25

        LoggingFlag = 1
        LoggingDir = currdir
        Leg1_DiscCurveName = "TempCurve"
        Leg1_EstCurveName = "TempCurve"
        Leg2_DiscCurveName = "TempCurve"
        Leg2_EstCurveName = "TempCurve"

        Leg1_FixingHistoryDate = [DayPlus(20240102, i) for i in range(365)]
        Leg1_FixingHistoryRate = [0.0344]*len(Leg1_FixingHistoryDate)
        Leg2_FixingHistoryDate = [DayPlus(20240102, i) for i in range(365)]
        Leg2_FixingHistoryRate = [0.0344]*len(Leg2_FixingHistoryDate)
        KoreanAutoHolidayFlag = True
        
        Pricing_IRCallableSwap_HWFDM(
            20000, 20160929, 20250304, 20460929, 0,         
            0.0, 0.25, 4, 0.0237, 3, 
            4, 1.0, 0.25, 4, -0.0012, 
            0, 
            [20190902,20200903,20210831,20220901,20230904,20240830,20250903,20260901,20270831,20280905,20290903,20300830,20310903,20320901,20330831,20340831,20350903,20360903,20370903,20380903,20390905,20400905,20410904,20420903,20430904,20440905,20450905], 
            [20190930,20200929,20210929,20220929,20231004,20240930,20250929,20260929,20270929,20280929,20291001,20300930,20310929,20320929,20330929,20340929,20351001,20360929,20370929,20380929,20390929,20401001,20410930,20421001,20430929,20440929,20450929], 
            1,
            [0.00274, 0.00548, 0.25479, 0.506849, 0.756164, 1.00274, 1.512329, 2.00274, 3.00822, 4.00548, 5.00548, 6.00548, 7.008219, 8.013699, 9.010959, 10.00822, 12.01096, 15.0137, 20.01918, 25.02466, 30.02192],
            [0.027989, 0.027992, 0.028394, 0.027554, 0.026807, 0.02633, 0.025806, 0.025455, 0.025154, 0.025235, 0.025264, 0.025397, 0.025531, 0.025638, 0.025719, 0.025856, 0.026049, 0.025598, 0.024243, 0.022474, 0.021085],
            [DayPlus(20240102, i) for i in range(365)], 
            [0.0344]*365, 
            [DayPlus(20240102, i) for i in range(365)], 
            [0.0344]*365, 
            kappa = -0.0133,
            kappa2 = 0.01,
            HWVolTerm = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
            HWVol = [0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368],
            HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
            HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2)
                
    '''
    OptionHolder = OptionHolder_0Recever1Payer

    # Error Processing
    if SwapMaturity < PriceDate : 
        raise ValueError("PriceDate > SwapMaturity")
    if SwapMaturity < SwapEffectiveDate : 
        raise ValueError("SwapMaturity < SwapEffectiveDate")        

    # Preprocessing
    if PriceDate < 19000101 : 
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
    
    if SwapEffectiveDate < 19000101 : 
        SwapEffectiveDate = ExcelDateToYYYYMMDD(SwapEffectiveDate)
        
    if SwapMaturity < 19000101 : 
        SwapMaturity = ExcelDateToYYYYMMDD(SwapMaturity)
    
    if NumCpnOneYear_Leg1_Phase2 < 0 : 
        NumCpnOneYear_Leg1_Phase2 = NumCpnOneYear_Leg1_Phase1

    if NumCpnOneYear_Leg2_Phase2 < 0 : 
        NumCpnOneYear_Leg2_Phase2 = NumCpnOneYear_Leg2_Phase1

    if KoreanAutoHolidayFlag == True : 
        FixHolidays = KoreaHolidaysFromStartToEnd(PriceDate//10000-1,SwapMaturity//10000 + 1)
        PayHolidays = FixHolidays
        
    for i in range(len(FixHolidays)) : 
        if FixHolidays[i] < 19000101 : 
            FixHolidays[i] = ExcelDateToYYYYMMDD(FixHolidays[i])
    
    for i in range(len(PayHolidays)) : 
        if PayHolidays[i] < 19000101 : 
            PayHolidays[i] = ExcelDateToYYYYMMDD(PayHolidays[i])
    
    for i in range(len(Leg1_FixingHistoryDate)) :
        if Leg1_FixingHistoryDate[i] < 19000101 : 
            Leg1_FixingHistoryDate[i] = ExcelDateToYYYYMMDD(Leg1_FixingHistoryDate[i])

    for i in range(len(Leg2_FixingHistoryDate)) :
        if Leg2_FixingHistoryDate[i] < 19000101 : 
            Leg2_FixingHistoryDate[i] = ExcelDateToYYYYMMDD(Leg2_FixingHistoryDate[i])
        
    if abs(kappa) > 1.5 : 
        kappa = kappa / 100
    if abs(kappa2) > 1.5 : 
        kappa2 = kappa2 / 100

    if (Leg1_Phase2UseFlag == 0) : 
        NumCpnOneYear_Leg1_Phase2 = NumCpnOneYear_Leg1_Phase1
        Leg1_RefSwapRate_Multiple_Phase2 = Leg1_RefSwapRate_Multiple_Phase1
        Leg1_FixedCpnRate_Phase2 = Leg1_FixedCpnRate_Phase1

    if (Leg2_Phase2UseFlag == 0) : 
        NumCpnOneYear_Leg2_Phase2 = NumCpnOneYear_Leg2_Phase1
        Leg2_RefSwapRate_Multiple_Phase2 = Leg2_RefSwapRate_Multiple_Phase1
        Leg2_FixedCpnRate_Phase2 = Leg2_FixedCpnRate_Phase1

    # Function Start
    NGreed = 100
    Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)
    Preprocessing_ZeroTermAndRate(HWVolTerm, HWVol, PriceDate, CompareNumber = 0.3)
    Preprocessing_ZeroTermAndRate(HWVolTerm2, HWVol2, PriceDate, CompareNumber = 0.3)

    IdxOpt = np.array(OptionFixDate) > PriceDate
    OptionFixDate = list(np.array(OptionFixDate)[IdxOpt])
    OptionPayDate = list(np.array(OptionPayDate)[IdxOpt])
    Leg1CompoundCouponFlag = False
    Leg2CompoundCouponFlag = False
    if Leg1_DayCount >= 5 : 
        # 복리 제로쿠폰의 경우 5번 넘는 Flag를 넣으면 됨
        Leg1_DayCount = Leg1_DayCount % 5
        Leg1CompoundCouponFlag = True

    if Leg2_DayCount >= 5 : 
        # 복리 제로쿠폰의 경우 5번 넘는 Flag를 넣으면 됨
        Leg2_DayCount = Leg2_DayCount % 5
        Leg2CompoundCouponFlag = True

    Leg1ZeroCouponFlag = (NumCpnOneYear_Leg1_Phase1 == 0) or (NumCpnOneYear_Leg1_Phase2 == 0) if Leg1_Phase2UseFlag == True else (NumCpnOneYear_Leg1_Phase1 == 0)
    Leg2ZeroCouponFlag = (NumCpnOneYear_Leg2_Phase1 == 0) or (NumCpnOneYear_Leg2_Phase2 == 0) if Leg2_Phase2UseFlag == True else (NumCpnOneYear_Leg2_Phase1 == 0)
    if Leg1ZeroCouponFlag == True : 
        NumCpnOneYear_Leg1_Phase1 = max(1, NumCpnOneYear_Leg1_Phase2)    
        NumCpnOneYear_Leg1_Phase2 = max(1, NumCpnOneYear_Leg1_Phase2)    

    if Leg2ZeroCouponFlag == True : 
        NumCpnOneYear_Leg2_Phase1 = max(1, NumCpnOneYear_Leg2_Phase2)    
        NumCpnOneYear_Leg2_Phase2 = max(1, NumCpnOneYear_Leg2_Phase2)    

    if Leg1_Phase2UseFlag > 0 : 
        #print("L1PhaseMulti",NumCpnOneYear_Leg1_Phase1,NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate)
        Leg1ForwardStart1,Leg1ForwardEnd1, Leg1PayDate1, Leg1ResultNBD1 = MappingCouponDates(1, SwapEffectiveDate, Leg1_Phase2StartDate, 0 if SwapEffectiveDate % 100 == Leg1_Phase2StartDate % 100 else -1, NumCpnOneYear_Leg1_Phase1, True, FixHolidays, PayHolidays, 1) 
        Leg1ForwardStart2,Leg1ForwardEnd2, Leg1PayDate2, Leg1ResultNBD2 = MappingCouponDates(1, Leg1ForwardEnd1[-1] if Leg1ForwardEnd1[-1] % 100 == SwapMaturity % 100 else ((Leg1ForwardEnd1[-1] // 100)*100 + SwapEffectiveDate % 100), SwapMaturity, 0 if Leg1ForwardEnd1[-1] % 100 == SwapMaturity % 100 else -1, NumCpnOneYear_Leg1_Phase2, True, FixHolidays, PayHolidays, 1) 
        Leg1ForwardStart = list(Leg1ForwardStart1) + list(Leg1ForwardStart2)
        Leg1ForwardEnd = list(Leg1ForwardEnd1) + list(Leg1ForwardEnd2)
        Leg1PayDate = list(Leg1PayDate1) + list(Leg1PayDate2)
        Leg1ResultNBD = Leg1ResultNBD1
    else : 
        Leg1ForwardStart,Leg1ForwardEnd, Leg1PayDate, Leg1ResultNBD = MappingCouponDates(1, SwapEffectiveDate, SwapMaturity, 0 if SwapEffectiveDate % 100 == SwapMaturity % 100 else -1, NumCpnOneYear_Leg1_Phase1, True, FixHolidays, PayHolidays, 1) 
    #print(Leg1ForwardEnd)

    if Leg2_Phase2UseFlag > 0 : 
        #print("L2PhaseMulti",NumCpnOneYear_Leg2_Phase1,NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate)
        Leg2ForwardStart1,Leg2ForwardEnd1, Leg2PayDate1, Leg2ResultNBD1 = MappingCouponDates(1, SwapEffectiveDate, Leg2_Phase2StartDate, 0 if SwapEffectiveDate % 100 == Leg2_Phase2StartDate % 100 else -1, NumCpnOneYear_Leg2_Phase1, True, FixHolidays, PayHolidays, 1) 
        Leg2ForwardStart2,Leg2ForwardEnd2, Leg2PayDate2, Leg2ResultNBD2 = MappingCouponDates(1, Leg2ForwardEnd1[-1] if Leg2ForwardEnd1[-1] % 100 == SwapMaturity % 100 else ((Leg2ForwardEnd1[-1] // 100)*100 + SwapEffectiveDate % 100) , SwapMaturity, 0 if Leg2ForwardEnd1[-1] % 100 == SwapMaturity % 100 else -1, NumCpnOneYear_Leg2_Phase2, True, FixHolidays, PayHolidays, 1) 
        Leg2ForwardStart = list(Leg2ForwardStart1) + list(Leg2ForwardStart2)
        Leg2ForwardEnd = list(Leg2ForwardEnd1) + list(Leg2ForwardEnd2)
        Leg2PayDate = list(Leg2PayDate1) + list(Leg2PayDate2)
        Leg2ResultNBD = Leg2ResultNBD1
    else : 
        Leg2ForwardStart,Leg2ForwardEnd, Leg2PayDate, Leg2ResultNBD = MappingCouponDates(1, SwapEffectiveDate, SwapMaturity, 0 if SwapEffectiveDate % 100 == SwapMaturity % 100 else -1, NumCpnOneYear_Leg2_Phase1, True, FixHolidays, PayHolidays, 1) 
    
    #print(Leg2ForwardEnd)
    if (PriceDate in Leg1ForwardStart) and (PriceDate not in Leg1_FixingHistoryDate):             
        Sm_Add = EDate_YYYYMMDD(PriceDate, int(Leg1_RefSwapMaturity_T * 12 + 0.000001))
        if Leg1_PowerSpreadFlag == 0 : 
            Leg1_RHistAdd = FSR(PriceDate, PriceDate, Sm_Add, Leg1_RefSwapNCPNOneYear, Leg1_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Leg1_FixingHistoryDate.append(PriceDate)
            Leg1_FixingHistoryRate.append(Leg1_RHistAdd)            
        else : 
            Leg1_RHistAdd = FSR(PriceDate, PriceDate, Sm_Add, Leg1_RefSwapNCPNOneYear, Leg1_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Sm_Add_PowerSpread = EDate_YYYYMMDD(PriceDate, int(Leg1_RefSwapMaturity_T_PowerSpread * 12 + 0.000001))
            Leg1_RHistAdd_PowerSpread = FSR(PriceDate, PriceDate, Sm_Add_PowerSpread, Leg1_RefSwapNCPNOneYear, Leg1_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Leg1_FixingHistoryDate.append(PriceDate)
            Leg1_FixingHistoryRate.append(Leg1_RHistAdd - Leg1_RHistAdd_PowerSpread)            

    if (PriceDate in Leg2ForwardStart) and (PriceDate not in Leg2_FixingHistoryDate):             
        Sm_Add = EDate_YYYYMMDD(PriceDate, int(Leg2_RefSwapMaturity_T * 12 + 0.000001))
        if Leg2_PowerSpreadFlag == 0 : 
            Leg2_RHistAdd = FSR(PriceDate, PriceDate, Sm_Add, Leg2_RefSwapNCPNOneYear, Leg2_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Leg2_FixingHistoryDate.append(PriceDate)
            Leg2_FixingHistoryRate.append(Leg2_RHistAdd)            
        else : 
            Leg2_RHistAdd = FSR(PriceDate, PriceDate, Sm_Add, Leg2_RefSwapNCPNOneYear, Leg2_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Sm_Add_PowerSpread = EDate_YYYYMMDD(PriceDate, int(Leg2_RefSwapMaturity_T_PowerSpread * 12 + 0.000001))
            Leg2_RHistAdd_PowerSpread = FSR(PriceDate, PriceDate, Sm_Add_PowerSpread, Leg2_RefSwapNCPNOneYear, Leg2_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Leg2_FixingHistoryDate.append(PriceDate)
            Leg2_FixingHistoryRate.append(Leg2_RHistAdd - Leg2_RHistAdd_PowerSpread)            
            
    TotalDateList = np.sort(np.array(pd.Series([PriceDate] + Leg1ForwardStart + Leg1ForwardEnd + Leg1PayDate + Leg2ForwardStart + Leg2ForwardEnd + Leg2PayDate + OptionFixDate + OptionPayDate).unique()))    
    SimulationDateList = TotalDateList[TotalDateList > PriceDate]

    xt_min, xt_max = -0.1, 0.4
    yt_min, yt_max = -0.1, 0.4
    dxt = (xt_max - xt_min) / float(NGreed)
    dyt = (yt_max - yt_min) / float(NGreed)
    xt = np.linspace(xt_min, xt_max, NGreed+1)[:-1]
    yt = np.linspace(yt_min, yt_max, NGreed+1)[:-1]
    xt_greed = xt.reshape(1,-1) * np.ones(len(SimulationDateList)).reshape(-1,1)
    yt_greed = yt.reshape(1,-1) * np.ones(len(SimulationDateList)).reshape(-1,1)

    Leg1SwapRate, Leg1SwapRateForwardMeasure, Leg1ConvAdj = ParRateForFDMGreed(PriceDate, xt_greed, yt_greed, SimulationDateList, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, kappa2, HWVolTerm2, HWVol2, ZeroTerm, ZeroRate, HW2FFlag, HWRho12Factor = HWRho12Factor)
    if Leg1_PowerSpreadFlag == 0 : 
        Leg1SwapRate_PowerSpread, Leg1SwapRateForwardMeasure_PowerSpread, Leg1ConvAdj_PowerSpread = Leg1SwapRate, Leg1SwapRateForwardMeasure, Leg1ConvAdj
    else : 
        Leg1SwapRate_PowerSpread, Leg1SwapRateForwardMeasure_PowerSpread, Leg1ConvAdj_PowerSpread = ParRateForFDMGreed(PriceDate, xt_greed, yt_greed, SimulationDateList, Leg1_RefSwapMaturity_T_PowerSpread, Leg1_RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, kappa2, HWVolTerm2, HWVol2, ZeroTerm, ZeroRate, HW2FFlag, HWRho12Factor = HWRho12Factor)
        
    Leg2SwapRate, Leg2SwapRateForwardMeasure, Leg2ConvAdj = ParRateForFDMGreed(PriceDate, xt_greed, yt_greed, SimulationDateList, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, kappa2, HWVolTerm2, HWVol2, ZeroTerm, ZeroRate, HW2FFlag, HWRho12Factor = HWRho12Factor)
    if Leg2_PowerSpreadFlag == 0 : 
        Leg2SwapRate_PowerSpread, Leg2SwapRateForwardMeasure_PowerSpread, Leg2ConvAdj_PowerSpread = Leg2SwapRate, Leg2SwapRateForwardMeasure, Leg2ConvAdj
    else : 
        Leg2SwapRate_PowerSpread, Leg2SwapRateForwardMeasure_PowerSpread, Leg2ConvAdj_PowerSpread = ParRateForFDMGreed(PriceDate, xt_greed, yt_greed, SimulationDateList, Leg2_RefSwapMaturity_T_PowerSpread, Leg2_RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, kappa2, HWVolTerm2, HWVol2, ZeroTerm, ZeroRate, HW2FFlag, HWRho12Factor = HWRho12Factor)

    IdxSimul = np.array([i for i in range(len(SimulationDateList)) if SimulationDateList[i] in Leg1ForwardStart])
    Leg1RefRateOnFixingDate = Leg1SwapRate[IdxSimul]
    Leg1RefRateOnFixingDate_PowerSpread = Leg1SwapRate_PowerSpread[IdxSimul]
    Leg1RefRateOnFixingDateForwardMeasure = Leg1SwapRateForwardMeasure[IdxSimul] - Leg1ConvAdj[IdxSimul]
    Leg1RefRateOnFixingDateForwardMeasure_PowerSpread = Leg1SwapRateForwardMeasure_PowerSpread[IdxSimul] - Leg1ConvAdj_PowerSpread[IdxSimul]
    IdxSimul = np.array([i for i in range(len(SimulationDateList)) if SimulationDateList[i] in Leg2ForwardStart])
    Leg2RefRateOnFixingDate = Leg2SwapRate[IdxSimul]
    Leg2RefRateOnFixingDate_PowerSpread = Leg2SwapRate_PowerSpread[IdxSimul]
    Leg2RefRateOnFixingDateForwardMeasure = Leg2SwapRateForwardMeasure[IdxSimul] - Leg2ConvAdj[IdxSimul]
    Leg2RefRateOnFixingDateForwardMeasure_PowerSpread = Leg2SwapRateForwardMeasure_PowerSpread[IdxSimul] - Leg2ConvAdj_PowerSpread[IdxSimul]

    Leg1_ResultData = Calc_Payoff_FDM_ForTimeGreed(ZeroTerm, ZeroRate, PriceDate, SwapEffectiveDate, Leg1RefRateOnFixingDate, Leg1RefRateOnFixingDate_PowerSpread, Nominal, 
                                    Leg1_Phase2StartDate, Leg1ForwardStart, Leg1ForwardEnd, Leg1PayDate, Leg1_DayCount,
                                    Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase1, Leg1_FixedCpnRate_Phase2, Leg1_FixingHistoryDate, 
                                    Leg1_FixingHistoryRate, Leg1ZeroCouponFlag, Leg1CompoundCouponFlag, Leg1RefRateOnFixingDateForwardMeasure,Leg1RefRateOnFixingDateForwardMeasure_PowerSpread, Leg1_PowerSpreadFlag, CpnRounding, HW2FFlag, MaxReturn = MaxReturn, MaxLoss = MaxLoss)
    Leg2_ResultData = Calc_Payoff_FDM_ForTimeGreed(ZeroTerm, ZeroRate, PriceDate, SwapEffectiveDate, Leg2RefRateOnFixingDate, Leg2RefRateOnFixingDate_PowerSpread, Nominal, 
                                    Leg2_Phase2StartDate, Leg2ForwardStart, Leg2ForwardEnd, Leg2PayDate, Leg2_DayCount,
                                    Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase1, Leg2_FixedCpnRate_Phase2, Leg2_FixingHistoryDate, 
                                    Leg2_FixingHistoryRate, Leg2ZeroCouponFlag, Leg2CompoundCouponFlag, Leg2RefRateOnFixingDateForwardMeasure,Leg2RefRateOnFixingDateForwardMeasure_PowerSpread, Leg2_PowerSpreadFlag, CpnRounding, HW2FFlag, MaxReturn = MaxReturn, MaxLoss = MaxLoss)
    DeltaTime = np.vectorize(DayCountAtoB)(SimulationDateList[:-1],SimulationDateList[1:])/365
    FDMTime = np.vectorize(DayCountAtoB)([PriceDate],SimulationDateList)/365
    r = np.interp(FDMTime, ZeroTerm, ZeroRate)
    DF_TimeGreed = np.exp(-r * FDMTime)
    if HW2FFlag == 0 : 
        Leg1PayoffAccum = np.r_[Leg1_ResultData["Payoff_Prev"][-1] * np.ones((1,NGreed)), Leg1_ResultData["Payoff_Simul"][:-1]]
        Leg2PayoffAccum = np.r_[Leg2_ResultData["Payoff_Prev"][-1] * np.ones((1,NGreed)), Leg2_ResultData["Payoff_Simul"][:-1]]
    else : 
        Leg1PayoffAccum = np.r_[Leg1_ResultData["Payoff_Prev"][-1] * np.ones((1,NGreed, NGreed)), Leg1_ResultData["Payoff_Simul"][:-1]]
        Leg2PayoffAccum = np.r_[Leg2_ResultData["Payoff_Prev"][-1] * np.ones((1,NGreed, NGreed)), Leg2_ResultData["Payoff_Simul"][:-1]]

    OptionExerciseOX = np.zeros(Leg1_ResultData["Payoff_Simul"][-1].shape)
    nextoptidx = len(OptionPayDate) - 1

    FDMValueAtGreedMax0Min = np.zeros((len(SimulationDateList),3))
    PayoffGreedMax0Min = np.zeros((len(SimulationDateList),2))
    Leg1SwapRateMax0Min = np.zeros((len(SimulationDateList),3))
    Leg2SwapRateMax0Min = np.zeros((len(SimulationDateList),3))
    if HW2FFlag == 0 : 
        Leg1SwapRateMax0Min[:,0] = Leg1SwapRate[:,0] if Leg1_PowerSpreadFlag == 0 else Leg1SwapRate[:,0] - Leg1SwapRate_PowerSpread[:, 0]
        Leg1SwapRateMax0Min[:,-1] = Leg1SwapRate[:,-1] if Leg1_PowerSpreadFlag == 0 else Leg1SwapRate[:,-1] - Leg1SwapRate_PowerSpread[:, -1]
        Leg2SwapRateMax0Min[:,0] = Leg2SwapRate[:,0] if Leg2_PowerSpreadFlag == 0 else Leg2SwapRate[:,0] - Leg2SwapRate_PowerSpread[:, 0]
        Leg2SwapRateMax0Min[:,-1] = Leg2SwapRate[:,-1] if Leg2_PowerSpreadFlag == 0 else Leg2SwapRate[:,-1] - Leg2SwapRate_PowerSpread[:, -1]
    else : 
        Leg1SwapRateMax0Min[:,0] = Leg1SwapRate[:,0,0] if Leg1_PowerSpreadFlag == 0 else Leg1SwapRate[:,0,0] - Leg1SwapRate_PowerSpread[:, 0, 0]
        Leg1SwapRateMax0Min[:,-1] = Leg1SwapRate[:,-1,-1] if Leg1_PowerSpreadFlag == 0 else Leg1SwapRate[:,-1,-1] - Leg1SwapRate_PowerSpread[:, -1, -1]
        Leg2SwapRateMax0Min[:,0] = Leg2SwapRate[:,0,0] if Leg2_PowerSpreadFlag == 0 else Leg2SwapRate[:,0,0] - Leg2SwapRate_PowerSpread[:, 0,0]
        Leg2SwapRateMax0Min[:,-1] = Leg2SwapRate[:,-1,-1] if Leg2_PowerSpreadFlag == 0 else Leg2SwapRate[:,-1,-1] - Leg2SwapRate_PowerSpread[:, -1, -1]
        
    for i in range(len(SimulationDateList)) : 
        FDMDate = SimulationDateList[::-1][i]
        T = FDMTime[::-1][i]
        if i == 0 : 
            FDMValue = Leg1_ResultData["Payoff_Simul"][-1] - Leg2_ResultData["Payoff_Simul"][-1]
            if HW2FFlag == 0 : 
                PayoffGreedMax0Min[-(i+1)][0] = np.interp(0, xt, Leg1_ResultData["Payoff_Simul"][-1])
                PayoffGreedMax0Min[-(i+1)][1] = np.interp(0, xt, Leg2_ResultData["Payoff_Simul"][-1])
            else : 
                PayoffGreedMax0Min[-(i+1)][0] = Linterp2D(xt, yt, Leg1_ResultData["Payoff_Simul"][-1], 0, 0)
                PayoffGreedMax0Min[-(i+1)][1] = Linterp2D(xt, yt, Leg2_ResultData["Payoff_Simul"][-1], 0, 0)
                
            if (FDMDate <= PriceDate) : 
                break
            
        else :         
            TPrev = FDMTime[::-1][i-1]
            deltat = DeltaTime[::-1][i-1]        
            df_t2 = DF_TimeGreed[::-1][i-1]
            df_t1 = DF_TimeGreed[::-1][i]
            PtT =  df_t2 / df_t1
            if HW2FFlag == 0 : 
                vol1 = np.interp((T+TPrev)/2, HWVolTerm, HWVol)
                an = -deltat * 0.5 * (kappa * xt / dxt + vol1 * vol1 / (dxt * dxt))
                bn = np.ones(len(an)) * (1.0 + deltat * vol1 * vol1 / (dxt * dxt)) + (1.0 / PtT - 1.0)
                cn = deltat * 0.5 * (kappa * xt / dxt - vol1 * vol1 / (dxt * dxt))
                a0 , b0 , c0 = an[0], bn[0], cn[0]
                aN , bN , cN = an[-1],bn[-1],cn[-1]
                bn[0] = 2*a0 + b0
                cn[0] = c0-a0
                bn[-1] = bN +2*cN
                an[-1] = aN - cN 
                k = np.array([an[1:], bn, cn[:-1]], dtype = object)
                offset = [-1,0,1]
                tdiag = diags(k,offset).toarray()
                inv_tdiag = np.linalg.inv(tdiag)
                FDMValue = inv_tdiag.dot(FDMValue)
            else : 
                vol1 = np.interp((T+TPrev)/2, HWVolTerm, HWVol)
                vol2 = np.interp((T+TPrev)/2, HWVolTerm2, HWVol2)
                s2F = 0.5 * vol1 * vol2 * HWRho12Factor * deltat / (4.0 * dxt * dyt)
                
                #################
                # x tridiagonal #
                #################

                an1F = -deltat * 0.5 * (kappa * xt / dxt + vol1 * vol1 / (dxt * dxt))
                bn1F = np.ones(len(an1F)) * (1.0 + deltat * vol1 * vol1 / (dxt * dxt)) + (1.0 / PtT - 1.0) * 0.5
                cn1F = deltat * 0.5 * (kappa * xt / dxt - vol1 * vol1 / (dxt * dxt))
                a01F , b01F , c01F = an1F[0], bn1F[0], cn1F[0]
                aN1F , bN1F, cN1F = an1F[-1],bn1F[-1],cn1F[-1]
                bn1F[0] = 2*a01F + b01F
                cn1F[0] = c01F-a01F
                bn1F[-1] = bN1F +2*cN1F
                an1F[-1] = aN1F - cN1F 
                k1F = np.array([an1F[1:], bn1F, cn1F[:-1]], dtype = object)
                offset1F = [-1,0,1]
                tdiag1F = diags(k1F,offset1F).toarray()
                inv_tdiag1F = np.linalg.inv(tdiag1F)

                ################
                # x implicited #
                ################
                
                adj1F = np.zeros((FDMValue.shape[0]+2,FDMValue.shape[1]+2))
                adj1F[1:-1,1:-1] = FDMValue
                adj1F[:,0] = adj1F[:,1] * 2 - adj1F[:,2]
                adj1F[:,-1] = adj1F[:,-2] * 2 - adj1F[:,-3]
                adj1F[0,:] = adj1F[1,:] * 2 - adj1F[2,:]
                adj1F[-1,:] = adj1F[-2,:] * 2 - adj1F[-3,:]
                RHSxt = s2F * (adj1F[2:,2:] + adj1F[:-2,:-2] - adj1F[2:,:-2] - adj1F[:-2, 2:]) + FDMValue              
                FDMValue = inv_tdiag1F.dot(RHSxt).T

                #################
                # y tridiagonal #
                #################

                an2F = -deltat * 0.5 * (kappa * yt / dyt + vol1 * vol1 / (dyt * dyt))
                bn2F = np.ones(len(an2F)) * (1.0 + deltat * vol1 * vol1 / (dyt * dyt)) + (1.0 / PtT - 1.0) * 0.5
                cn2F = deltat * 0.5 * (kappa * yt / dyt - vol1 * vol1 / (dyt * dyt))
                a02F , b02F , c02F = an2F[0], bn2F[0], cn2F[0]
                aN2F , bN2F, cN2F = an2F[-1],bn2F[-1],cn2F[-1]
                bn2F[0] = 2*a02F + b02F
                cn2F[0] = c02F-a02F
                bn2F[-1] = bN2F +2*cN2F
                an2F[-1] = aN2F - cN2F 
                k2F = np.array([an2F[1:], bn2F, cn2F[:-1]], dtype = object)
                offset2F = [-1,0,1]
                tdiag2F = diags(k2F,offset2F).toarray()
                inv_tdiag2F = np.linalg.inv(tdiag2F)

                ################
                # y implicited #
                ################

                adj2F = np.zeros((FDMValue.shape[0]+2,FDMValue.shape[1]+2))
                adj2F[1:-1,1:-1] = FDMValue
                adj2F[:,0] = adj2F[:,1] * 2 - adj2F[:,2]
                adj2F[:,-1] = adj2F[:,-2] * 2 - adj2F[:,-3]
                adj2F[0,:] = adj2F[1,:] * 2 - adj2F[2,:]
                adj2F[-1,:] = adj2F[-2,:] * 2 - adj2F[-3,:]
                RHSyt = s2F * (adj2F[2:,2:] + adj2F[:-2,:-2] - adj2F[2:,:-2] - adj2F[:-2, 2:]) + FDMValue              
                FDMValue = inv_tdiag2F.dot(RHSyt).T        
                
            if (FDMDate <= PriceDate) : 
                break
                    
            if (FDMDate in Leg1_ResultData["PayDate_Simul"]) and (Leg1ZeroCouponFlag == False) : 
                idx = list(Leg1_ResultData["PayDate_Simul"]).index(FDMDate)
                FDMValue += Leg1_ResultData["Payoff_Simul"][idx]
                PayoffGreedMax0Min[-(i+1)][0] = np.interp(0, xt, Leg1_ResultData["Payoff_Simul"][idx]) if HW2FFlag == 0 else Linterp2D(xt, yt, Leg1_ResultData["Payoff_Simul"][idx], 0, 0)            
            elif (FDMDate in Leg1_ResultData["PrevPayDate"]) and (Leg1ZeroCouponFlag == False) : 
                FDMValue += np.ones(FDMValue.shape) * Leg1_ResultData["Payoff_Prev"][-1]
                PayoffGreedMax0Min[-(i+1)][0] = float(Leg1_ResultData["Payoff_Prev"][-1])            

            if (FDMDate in Leg2_ResultData["PayDate_Simul"]) and (Leg2ZeroCouponFlag == False) : 
                idx = list(Leg2_ResultData["PayDate_Simul"]).index(FDMDate)
                FDMValue -= Leg2_ResultData["Payoff_Simul"][idx]
                PayoffGreedMax0Min[-(i+1)][1] = np.interp(0, xt, Leg2_ResultData["Payoff_Simul"][idx]) if HW2FFlag == 0 else Linterp2D(xt, yt, Leg2_ResultData["Payoff_Simul"][idx], 0, 0)            
            elif (FDMDate in Leg2_ResultData["PrevPayDate"]) and (Leg2ZeroCouponFlag == False) : 
                FDMValue -= np.ones(FDMValue.shape) * Leg2_ResultData["Payoff_Prev"][-1]
                PayoffGreedMax0Min[-(i+1)][1] = float(Leg2_ResultData["Payoff_Prev"][-1])            
        
        if i != 0 and len(OptionPayDate) > 0 and (FDMDate <= OptionPayDate[nextoptidx] and FDMDate >= OptionFixDate[nextoptidx]) : 
            if FDMDate == OptionPayDate[nextoptidx] : 
                OptionExerciseOX = OptionExerciseOX * 0
            FixDateOpt = OptionFixDate[nextoptidx]
            PayDateOpt = OptionPayDate[nextoptidx]
            t1 = DayCountAtoB(PriceDate, FDMDate)/365
            t2 = DayCountAtoB(PriceDate, PayDateOpt)/365
            tmat_Leg1 = DayCountAtoB(PriceDate, Leg1_ResultData["PayDate_Simul"][-1])/365
            tmat_Leg2 = DayCountAtoB(PriceDate, Leg2_ResultData["PayDate_Simul"][-1])/365
            df_t1 = Calc_Discount_Factor(ZeroTerm, ZeroRate, t1)
            df_t2 = Calc_Discount_Factor(ZeroTerm, ZeroRate, t2)
            df_tmat_Leg1 = Calc_Discount_Factor(ZeroTerm, ZeroRate, tmat_Leg1)
            df_tmat_Leg2 = Calc_Discount_Factor(ZeroTerm, ZeroRate, tmat_Leg2)
            
            Leg1_Idx = (FixDateOpt <= Leg1_ResultData["PayDate_Simul"]) & (PayDateOpt > Leg1_ResultData["FixingDate_Simul"])
            Leg2_Idx = (FixDateOpt <= Leg2_ResultData["PayDate_Simul"]) & (PayDateOpt > Leg2_ResultData["FixingDate_Simul"])

            if FDMDate <= Leg1_ResultData["PrevPayDate"][-1] : 
                Leg1_Acc = np.ones(FDMValue.shape) * Leg1_ResultData["PrevCummulativeCpn"][-1]
                Leg1_OptPayoff = np.ones(FDMValue.shape) *Leg1_ResultData["Payoff_Prev"][-1] - Leg1_Acc
            else : 
                Leg1_Acc = Leg1PayoffAccum[Leg1_Idx][-1] * float(Leg1ZeroCouponFlag == True)
                Leg1_OptPayoff = Leg1_ResultData["Payoff_Simul"][Leg1_Idx][-1] - Leg1_Acc
            
            if FDMDate <= Leg2_ResultData["PrevPayDate"][-1] : 
                Leg2_Acc = np.ones(FDMValue.shape) * Leg2_ResultData["PrevCummulativeCpn"][-1]
                Leg2_OptPayoff = np.ones(FDMValue.shape) *Leg2_ResultData["Payoff_Prev"][-1] - Leg2_Acc
            else : 
                Leg2_Acc = Leg2PayoffAccum[Leg2_Idx][-1] * float(Leg2ZeroCouponFlag == True)
                Leg2_OptPayoff = Leg2_ResultData["Payoff_Simul"][Leg2_Idx][-1] - Leg2_Acc
            
            NPV_ExerciseValue_Leg1 = Leg1_Acc * df_tmat_Leg1/df_t1 + Leg1_OptPayoff * df_t2/df_t1
            NPV_ExerciseValue_Leg2 = Leg2_Acc * df_tmat_Leg2/df_t1 + Leg2_OptPayoff * df_t2/df_t1
            NPV_ExerciseValue = NPV_ExerciseValue_Leg1 - NPV_ExerciseValue_Leg2
            if FDMDate == max(OptionPayDate[nextoptidx], OptionFixDate[nextoptidx]) : 
                if OptionHolder == 0 : 
                    OptionExerciseOX = NPV_ExerciseValue > FDMValue
                else : 
                    OptionExerciseOX = NPV_ExerciseValue < FDMValue
            FDMValue = (OptionExerciseOX == True) * NPV_ExerciseValue + (OptionExerciseOX == False) * FDMValue

            if FDMDate == min(OptionFixDate[nextoptidx], OptionPayDate[nextoptidx]) : 
                nextoptidx = max(0, nextoptidx - 1)
                
        if HW2FFlag == 0 : 
            ResultValue = np.interp(0, xt, FDMValue)
        else : 
            ResultValue = Linterp2D(xt, yt, FDMValue, 0, 0)

        FDMValueAtGreedMax0Min[-(i+1)][0] = np.round(FDMValue[0], 2) if HW2FFlag == 0 else FDMValue[0, 0]
        FDMValueAtGreedMax0Min[-(i+1)][1] = np.round(ResultValue, 2) 
        FDMValueAtGreedMax0Min[-(i+1)][2] = np.round(FDMValue[-1], 2) if HW2FFlag == 0 else FDMValue[-1, -1]
        if HW2FFlag == 0 : 
            Leg1SwapRateMax0Min[-(i+1)][1] = np.interp(0, xt, Leg1SwapRate[-(i+1)]) if Leg1_PowerSpreadFlag == 0 else np.interp(0, xt, Leg1SwapRate[-(i+1)]) - np.interp(0, xt, Leg1SwapRate_PowerSpread[-(i+1)])
            Leg2SwapRateMax0Min[-(i+1)][1] = np.interp(0, xt, Leg2SwapRate[-(i+1)]) if Leg2_PowerSpreadFlag == 0 else np.interp(0, xt, Leg2SwapRate[-(i+1)]) - np.interp(0, xt, Leg2SwapRate_PowerSpread[-(i+1)])
        else : 
            Leg1SwapRateMax0Min[-(i+1)][1] = Linterp2D(xt, yt, Leg1SwapRate[-(i+1)], 0, 0) if Leg1_PowerSpreadFlag == 0 else Linterp2D(xt, yt, Leg1SwapRate[-(i+1)], 0, 0) - Linterp2D(xt, yt, Leg1SwapRate_PowerSpread[-(i+1)], 0, 0)
            Leg2SwapRateMax0Min[-(i+1)][1] = Linterp2D(xt, yt, Leg2SwapRate[-(i+1)], 0, 0) if Leg2_PowerSpreadFlag == 0 else Linterp2D(xt, yt, Leg2SwapRate[-(i+1)], 0, 0) - Linterp2D(xt, yt, Leg2SwapRate_PowerSpread[-(i+1)], 0, 0)
            
    if HW2FFlag == 0 : 
        ResultPrice = np.interp(0, xt, FDMValue)
    else : 
        ResultPrice = Linterp2D(xt, yt, FDMValue, 0, 0)

    OptionExerciseDeclare = ["OptionExerciseDeclare" if i in OptionFixDate else '' for i in SimulationDateList] 
    OptionExercisePayment = ["OptionExercisePayment" if i in OptionPayDate else '' for i in SimulationDateList] 
    
    Result2 = pd.DataFrame(FDMValueAtGreedMax0Min, index = SimulationDateList, columns = ["V(xt("+str(np.round(xt[0],2))+"))","V(xt(0))","V(xt("+str(np.round(xt[-1],2))+"))"])
    Result3 = pd.DataFrame(Leg1SwapRateMax0Min, index = SimulationDateList, columns = ["Leg1Rate(xt("+str(np.round(xt[0],2))+"))","Leg1Rate(xt(0))","Leg1Rate(xt("+str(np.round(xt[-1],2))+"))"])
    Result4 = pd.DataFrame(Leg2SwapRateMax0Min, index = SimulationDateList, columns = ["Leg2Rate(xt("+str(np.round(xt[0],2))+"))","Leg2Rate(xt(0))","Leg2Rate(xt("+str(np.round(xt[-1],2))+"))"])
    Result1 = pd.DataFrame(PayoffGreedMax0Min, index = SimulationDateList, columns = ["Leg1CF","Leg2CF"])
    Result = pd.concat([Result1, Result2, Result3, Result4],axis = 1)

    Leg1FwdPayoff = [(Leg1_ResultData["Payoff_ForwardMeasure"][list(Leg1_ResultData["PayDate_Simul"]).index(i), 0]) if i in Leg1_ResultData["PayDate_Simul"] else 0 for i in SimulationDateList]
    Leg2FwdPayoff = [(Leg2_ResultData["Payoff_ForwardMeasure"][list(Leg2_ResultData["PayDate_Simul"]).index(i), 0]) if i in Leg2_ResultData["PayDate_Simul"] else 0 for i in SimulationDateList]
    if Leg1_ResultData["PrevPayDate"][-1] in SimulationDateList : 
        Leg1FwdPayoff[list(SimulationDateList).index(Leg1_ResultData["PrevPayDate"][-1])] = float(Leg1_ResultData["Payoff_Prev"][-1])
    if Leg2_ResultData["PrevPayDate"][-1] in SimulationDateList : 
        Leg2FwdPayoff[list(SimulationDateList).index(Leg2_ResultData["PrevPayDate"][-1])] = float(Leg2_ResultData["Payoff_Prev"][-1])
    Result["Leg1_Payoff_FwdMsr"] = Leg1FwdPayoff
    Result["Leg2_Payoff_FwdMsr"] = Leg2FwdPayoff
    Result["DiscountFactor"] = DF_TimeGreed
    Result["ResultPrice"] = ResultPrice
    Result["Leg1_DiscCurveName"] = Leg1_DiscCurveName
    Result["Leg1_EstCurveName"] = Leg1_EstCurveName
    Result["Leg2_DiscCurveName"] = Leg2_DiscCurveName
    Result["Leg2_EstCurveName"] = Leg2_EstCurveName
    Result["OptionDeclare"] = OptionExerciseDeclare
    Result["OptionPayment"] = OptionExercisePayment

    if LoggingFlag > 0 :                                 
        Result.to_csv(LoggingDir + "\\LoggingIRStructuredSwap.csv", index = True, encoding = "cp949")

    return Result            

def Pricing_IRCallableSwap_HWFDM_Greek(
    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
    Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
    NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
    Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
    ZeroRate, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
    kappa = 0.01, kappa2 = 0.01, HWVolTerm = [0.0001], HWVol = [0.006323], HWVolTerm2 = [0.0001], 
    HWVol2 = [0.003323], HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = 0, 
    LoggingDir = os.getcwd(), Leg1_DiscCurveName = "TempCurve", Leg1_EstCurveName = "TempCurve", Leg2_DiscCurveName = "TempCurve",
    Leg2_EstCurveName = "TempCurve", KoreanAutoHolidayFlag = True, FixHolidays = [], PayHolidays = [],
    Leg1_Phase2UseFlag = 0, NumCpnOneYear_Leg1_Phase2 = 0, Leg1_Phase2StartDate = 20280929, Leg1_RefSwapRate_Multiple_Phase2 = 0.0, Leg1_FixedCpnRate_Phase2 = 0.0237,   
    Leg2_Phase2UseFlag = 0, NumCpnOneYear_Leg2_Phase2 = 4, Leg2_Phase2StartDate = 20280929, Leg2_RefSwapRate_Multiple_Phase2 = 1.0, Leg2_FixedCpnRate_Phase2 = -0.0012,
    Leg1_PowerSpreadFlag = 0, Leg1_RefSwapMaturity_T_PowerSpread = 0.25, Leg2_PowerSpreadFlag = 0, Leg2_RefSwapMaturity_T_PowerSpread = 0.25,
    GreekFlag = 0) :
         
    ResultDict = {}
    PInfo = Pricing_IRCallableSwap_HWFDM(
            Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
            Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
            NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
            Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
            ZeroRate, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
            kappa, kappa2, HWVolTerm, HWVol, HWVolTerm2, 
            HWVol2, HWRho12Factor, CpnRounding, HW2FFlag, LoggingFlag, 
            LoggingDir, Leg1_DiscCurveName, Leg1_EstCurveName, Leg2_DiscCurveName,
            Leg2_EstCurveName, KoreanAutoHolidayFlag, FixHolidays, PayHolidays,
            Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2,   
            Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2,
            Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread)
    P = PInfo["ResultPrice"].values[0]
    ResultDict["Price"] = P
    LoggingFlag = 0
    PV01Array = np.zeros(len(ZeroTerm))
    PVGammaArray = np.zeros(len(ZeroTerm))
    for i in range(len(ZeroTerm)) : 
        ZeroUp = np.array(ZeroRate).copy()
        ZeroUp[i] = ZeroUp[i] + 0.0001
        PuInfo = Pricing_IRCallableSwap_HWFDM(
                Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
                Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
                NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
                Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
                ZeroUp, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
                kappa, kappa2, HWVolTerm, HWVol, HWVolTerm2, 
                HWVol2, HWRho12Factor, CpnRounding, HW2FFlag, LoggingFlag, 
                LoggingDir, Leg1_DiscCurveName, Leg1_EstCurveName, Leg2_DiscCurveName,
                Leg2_EstCurveName, KoreanAutoHolidayFlag, FixHolidays, PayHolidays,
                Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2,   
                Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2,
                Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread)
        Pu = PuInfo["ResultPrice"].values[0]

        ZeroDn = np.array(ZeroRate).copy()
        ZeroDn[i] = ZeroUp[i] - 0.0001
        PdInfo = Pricing_IRCallableSwap_HWFDM(
                Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
                Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
                NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
                Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
                ZeroDn, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
                kappa, kappa2, HWVolTerm, HWVol, HWVolTerm2, 
                HWVol2, HWRho12Factor, CpnRounding, HW2FFlag, LoggingFlag, 
                LoggingDir, Leg1_DiscCurveName, Leg1_EstCurveName, Leg2_DiscCurveName,
                Leg2_EstCurveName, KoreanAutoHolidayFlag, FixHolidays, PayHolidays,
                Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2,   
                Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2,
                Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread)
        Pd = PdInfo["ResultPrice"].values[0]

        PV01 = (Pu - Pd)/2
        PV01Array[i] = PV01
        PVGammaArray[i] = (Pu + Pd - 2.0 * P)
    ResultDict["PV01"] = PV01Array
    ResultDict["PVGamma"] = PVGammaArray
    
    if GreekFlag > 1 :
        VegaArray = np.zeros(len(HWVolTerm)) 
        for i in range(len(HWVolTerm)) : 
            VUp = np.array(HWVol).copy()
            VUp[i] = VUp[i] + 0.0001    
            PVuInfo = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
                    Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
                    NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
                    Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
                    ZeroRate, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
                    kappa, kappa2, HWVolTerm, VUp, HWVolTerm2, 
                    HWVol2, HWRho12Factor, CpnRounding, HW2FFlag, LoggingFlag, 
                    LoggingDir, Leg1_DiscCurveName, Leg1_EstCurveName, Leg2_DiscCurveName,
                    Leg2_EstCurveName, KoreanAutoHolidayFlag, FixHolidays, PayHolidays,
                    Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2,   
                    Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2,
                    Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread)  
            Vega = PVuInfo["ResultPrice"].values[0] - P
            VegaArray[i] = Vega
        ResultDict["Vega"] = VegaArray
        ResultDict["VegaFRTB"] = VegaArray/0.0001 * np.array(HWVol)
        ResultDict["VegaTerm"] = HWVolTerm
        if HW2FFlag > 0 : 
            VegaArray2 = np.zeros(len(HWVolTerm2)) 
            for i in range(len(HWVolTerm2)) : 
                VUp = np.array(HWVol2).copy()
                VUp[i] = VUp[i] + 0.0001    
                PVuInfo = Pricing_IRCallableSwap_HWFDM(
                        Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
                        Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
                        NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
                        Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
                        ZeroRate, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
                        kappa, kappa2, HWVolTerm, HWVol, HWVolTerm2, 
                        VUp, HWRho12Factor, CpnRounding, HW2FFlag, LoggingFlag, 
                        LoggingDir, Leg1_DiscCurveName, Leg1_EstCurveName, Leg2_DiscCurveName,
                        Leg2_EstCurveName, KoreanAutoHolidayFlag, FixHolidays, PayHolidays,
                        Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2,   
                        Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2,
                        Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread)  
                Vega = PVuInfo["ResultPrice"].values[0] - P
                VegaArray2[i] = Vega
            ResultDict["Vega2"] = VegaArray2
            ResultDict["VegaTerm2"] = HWVolTerm2
            ResultDict["VegaFRTB2"] = VegaArray2/0.0001 * np.array(HWVol2)
    return ResultDict    

def HullWhiteCalibrationProgram(CurveDirectory, PriceDate, CurveTerm, CurveRate, HolidayDate) : 
    Result = {"CalibrationFlag":False,"HWTerm":np.array([]),"HWVol":np.array([])}
    ZeroCurveName = CurveDirectory.split("\\")[-1].replace(".csv","")  
    Currency = CurveDirectory.split("\\")[-2]
    Holidays = list(HolidayDate[Currency].dropna().unique())
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namein = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    Data = Data[Data['DirectoryPrint'].apply(lambda x : ('KOSPI' in str(x).upper() or ('EQ' in str(x).upper() and 'VOL' in str(x).upper()) == False))] #Out EQ Vol 
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == str(PriceDate)]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))            
    if len(GroupbyYYYYMMDD) == 0 :
        return Result
     
    root = tk.Tk()
    root.title("Hull White Calibration")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(PriceDate))
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=int(PriceDate) + 100000)
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], titlelable = True, titleName = "Swption Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    vb_L1_DayCount = make_listvariable_interface(left_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11)
    vb_VolFlag = make_listvariable_interface(left_frame, 'VolFlag', ["0: Black Vol","1: Normal Vol"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=1)
    vb_FixedKappaFlag = make_listvariable_interface(left_frame, 'FixedKappaFlag', ["0: Kappa도 Calib","1: Kappa 고정"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0)
    v_FixedKappa = make_variable_interface(left_frame, 'FixedKappa', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 0.01)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(right_frame, ZeroCurveName, termratestr(CurveTerm, CurveRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)
    vb_SelectedCurve_P1 = make_listvariable_interface(right_frame, 'Swaption Vol 선택', list(GroupbyYYYYMMDD["ListName"]), listheight = 5, textfont = 11, titlelable = True, titleName = "Swaption Info", defaultflag = True, defaultvalue = 0, width = 50)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    PrevTreeFlag, tree, scrollbar, scrollbar2, tree2, tree3 = 0, None, None, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, Result, tree2, tree3]
    def run_function(MyArrays) :     

        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]  
        CalcResult = MyArrays[4] 
        tree2 = MyArrays[5]     
        tree3 = MyArrays[6]
        SelectedNumber = int(str(vb_SelectedCurve_P1.get(vb_SelectedCurve_P1.curselection())).split(".")[0]) if vb_SelectedCurve_P1.curselection() else 1
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(PriceDate)
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (int(PriceDate) + 100000)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        SwapFreqByMonth = 12/L1_NumCpnOneYear_P1
        DayCountFlag = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else 0    
        BSVol0NormalVol1 = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 1
        FixedKappaFlag = int(str(vb_FixedKappaFlag.get(vb_FixedKappaFlag.curselection())).split(":")[0]) if vb_FixedKappaFlag.curselection() else 0
        if FixedKappaFlag == 0 : 
            FixedKappa = 0
        else : 
            FixedKappa = float(v_FixedKappa.get()) if len(str(v_PriceDate.get())) > 0 else 0
            
        VolRawData = ReadCSV(GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == SelectedNumber]['Directory'].iloc[0])
        VolRawDataIndexSet = VolRawData.set_index(VolRawData.columns[0])
        XCol = VolRawDataIndexSet.columns.astype(np.float64)
        YInd = VolRawDataIndexSet.index.astype(np.float64)
        Values = VolRawDataIndexSet.values.astype(np.float64)
        tf = np.vectorize(lambda x, y : Linterp2D(XCol, YInd, Values, x, y))
        x = np.r_[np.array([3,6,9]) , np.arange(12,132, 12)].reshape(1,-1)
        y = np.r_[np.array([3,6,9]) , np.arange(12,132, 12)].reshape(-1,1)
        InterpolatedVols = tf(x, y)
        SwaptionVolData = pd.DataFrame(InterpolatedVols, columns = x.reshape(-1), index = y.reshape(-1))        

        OptionTenor = SwaptionVolData.columns.astype(np.float64)
        SwapTenor = SwaptionVolData.index.astype(np.float64)
        OptionVolMatrix = SwaptionVolData.values.astype(np.float64)
        if OptionVolMatrix.max() > 0.25 :
            OptionVolMatrix = OptionVolMatrix / 100 
            
        OptionTenor_ByMonth = []
        SwapTenor_ByMonth = []
        OptionVol = []
        for i in range(len(SwapTenor)) : 
            for j in range(len(OptionTenor)) : 
                StartDate = EDate_YYYYMMDD(PriceDate, OptionTenor[j]) 
                EndDate = EDate_YYYYMMDD(StartDate, SwapTenor[i])
                if EndDate < EDate_YYYYMMDD(int(SwapMaturity),3) and EndDate >= int(SwapMaturity) : 
                    OptionTenor_ByMonth.append(OptionTenor[j])
                    SwapTenor_ByMonth.append(SwapTenor[i])
                    OptionVol.append(OptionVolMatrix[i][j])                
        
        if len(OptionVol) <= 4 : 
            OptionTenor_ByMonth = []
            SwapTenor_ByMonth = []
            OptionVol = []
            if DayCountAtoB(PriceDate, SwapMaturity)/365 > (SwapTenor[-1] + OptionTenor[-1])/12 - 1: 
                for i in range(len(SwapTenor)) : 
                    for j in range(len(OptionTenor)) : 
                        if ((i == len(SwapTenor) - 1) or (j == len(OptionTenor) - 1)) : 
                            StartDate = EDate_YYYYMMDD(PriceDate, OptionTenor[j]) 
                            EndDate = EDate_YYYYMMDD(StartDate, SwapTenor[i])
                            OptionTenor_ByMonth.append(OptionTenor[j])
                            SwapTenor_ByMonth.append(SwapTenor[i])
                            OptionVol.append(OptionVolMatrix[i][j])                                    
            else :
                for i in range(len(SwapTenor)) : 
                    for j in range(len(OptionTenor)) : 
                        StartDate = EDate_YYYYMMDD(PriceDate, OptionTenor[j]) 
                        EndDate = EDate_YYYYMMDD(StartDate, SwapTenor[i])
                        OptionTenor_ByMonth.append(OptionTenor[j])
                        SwapTenor_ByMonth.append(SwapTenor[i])
                        OptionVol.append(OptionVolMatrix[i][j])                
                    
        Preprocessing_ZeroTermAndRate(CurveTerm, CurveRate, int(PriceDate))
        MyDict = HullWhiteCalibration1Factor(PriceDate, OptionTenor_ByMonth, SwapTenor_ByMonth, OptionVol, SwapFreqByMonth, BSVol0NormalVol1, CurveTerm, CurveRate, FixedKappa = FixedKappa, DayCountFlag = DayCountFlag, KoreanHolidayFlag = False, AdditionalHolidays = Holidays, initialkappa = 0.01, initialvol = 0.005 if BSVol0NormalVol1== 0 else np.array(OptionVol).mean(), PrintMRSPE=True)
        if len(MyDict["Error"]) == int(np.abs(MyDict["Error"]).sum() + 0.00001) : 
            print("Calibration 실패")
            Calibration = False
        else : 
            Calibration = True
        CalcResult["CalibrationFlag"] = Calibration
        ResultHW = pd.concat([pd.Series(MyDict["HWVolTerm"]), pd.Series(MyDict["HWVol"])],axis = 1)
        ResultHW.columns = ["HWTerm","HWVol"]
        ResultHW = ResultHW.sort_values(by = "HWTerm")
        ResultHW["HWKappa"] = MyDict["kappa"]
        CalcResult["kappa"] = MyDict["kappa"]
        CalcResult["HWTerm"] = ResultHW["HWTerm"].round(8)
        CalcResult["HWVol"] = ResultHW["HWVol"].round(8)
        A = pd.Series(MyDict["SwapStartDate"], name = "SwapStartDate")
        B = pd.Series(MyDict["SwapEndDate"], name = "SwapEndDate")
        C = pd.Series(MyDict["BlackPrice"], name = "BlackPrice").round(4)
        D = pd.Series(MyDict["HWPrice"], name = "HWPrice").round(4)
        E = pd.concat([A,B,C,D],axis = 1)

        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
            tree2 = ttk.Treeview(root)
            tree3 = ttk.Treeview(root)
        else : 
            tree.destroy()
            tree2.destroy()
            tree3.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
            tree2 = ttk.Treeview(root)
            tree3 = ttk.Treeview(root)
        ResultHW = ResultHW.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        InputVol = VolRawData.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree3.pack(padx=5, pady=5, fill="both", expand=False)
        tree.pack(padx=5, pady=5, fill="both", expand=False)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        tree2.pack(padx=5, pady=5, fill="both", expand=False)
        PrevTreeFlag = insert_dataframe_to_treeview(tree, ResultHW, width = 90)
        PrevTreeFlag2 = insert_dataframe_to_treeview(tree2, E, width = 90)
        PrevTreeFlag3 = insert_dataframe_to_treeview(tree3, InputVol, width = 90)

        MyArrays[0] = PrevTreeFlag
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2  
        MyArrays[4] = CalcResult  
        MyArrays[5] = tree2
        MyArrays[6] = tree3

    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()

    root.mainloop()
    return MyArrays[4]

def PricingIRStructuredSwapProgram(HolidayData, currdir) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                    namenotin = "vol",
                                                                    Comments = "IRS Pricing을 위한 커브 번호를 입력하시오.",
                                                                    MultiSelection = False,
                                                                    DefaultStringList=["IRS"])     
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    PriceDateDefault = int(YYYYMMDD)
    Curve = MyMarketDataList[0]
    UsedCurveName = Name[0].split("\\")[-1].split(".")[0]
    Curr = Name[0].split("\\")[-2].upper()
    CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
    CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
    CalibrationResult = HullWhiteCalibrationProgram(Name[0], int(YYYYMMDD), CurveTerm1, CurveRate1, HolidayData)
    CalibrationFlag = CalibrationResult['CalibrationFlag']
    defaultkappa = 0.01
    if CalibrationFlag == True : 
        defaultkappa = CalibrationResult['kappa']

    YYYY = int(YYYYMMDD) // 10000
    root = tk.Tk()
    root.title("Callable Swap Pricer(Single Phase)")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+21) * 10000 + 929)
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["0","1","2","4","6"], titlelable = True, titleName = "Leg1 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3)
    v_L1_FixedCpnRate_P1 = make_variable_interface(left_frame, 'Leg1 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =2.19)
    v_L1_RefSwapMaturity_T = make_variable_interface(left_frame, 'Leg1 변동금리 만기\n(3M-> 0.25, 5Y-> 5)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11)
    vb_L1_RefSwapNCPNOneYear_P1 = make_listvariable_interface(left_frame, 'Leg1 변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11)
    v_L1_RefRateMultiple_P1 = make_variable_interface(left_frame, 'Leg1 변동금리Multiple', bold = False, textfont = 11)
    vb_L1_DayCount = make_listvariable_interface(left_frame, 'Leg1 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(center_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = PriceDateDefault)
    vb_Holiday = make_listvariable_interface(center_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 4, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)

    vb_L2_NumCpnOneYear_P1 = make_listvariable_interface(center_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["0","1","2","4","6"], titlelable = True, titleName = "Leg2 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue = 3)
    v_L2_FixedCpnRate_P1 = make_variable_interface(center_frame, 'Leg2 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = -0.1)
    v_L2_RefSwapMaturity_T = make_variable_interface(center_frame, 'Leg2 변동금리 만기\n(3M-> 0.25, 5Y-> 5)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11, defaultflag = True ,defaultvalue = 0.25)
    vb_L2_RefSwapNCPNOneYear_P1 = make_listvariable_interface(center_frame, 'Leg2 변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 2)
    v_L2_RefRateMultiple_P1 = make_variable_interface(center_frame, 'Leg2 변동금리Multiple', bold = False, textfont = 11, defaultflag = True, defaultvalue = 1.0)
    vb_L2_DayCount = make_listvariable_interface(center_frame, 'Leg2 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_OptionHolder = make_listvariable_interface(right_frame, 'OptionHolder', ["0: Leg1 Hold Option","1: Leg2 Hold Option"], titleName = "Option Information", titlelable= True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue= 0)
    v_FirstOptPayDate = make_variable_interface(right_frame, '첫 옵션행사일\n(지급일기준)', bold = False, textfont = 11, defaultflag = True, defaultvalue = (YYYY-6) * 10000 + 929)
    vb_NYearBetweenOptionPay = make_listvariable_interface(right_frame, '옵션행사간격', ["6M","12M","24M","36M","60M"], listheight = 5, textfont = 11, defaultflag = True, defaultvalue = 1)
    v_NBDateBetweenOptionFixToPay = make_variable_interface(right_frame, '옵션행사선언일과\n옵션지급일사이의\n영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 20)
    v_MaxNumOpt = make_variable_interface(right_frame, '최대옵션개수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0)
    v_L1FirstFixing = make_variable_interface(right_frame, 'Leg1)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_L2FirstFixing = make_variable_interface(right_frame, 'Leg2)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_GreekFlag = make_listvariable_interface(right_frame, 'Greek산출', ["0: Pricing만","1: Delta,Gamma","2: Delta,Gamma,Vega"], listheight = 3, textfont = 11)

    rightright_frame = tk.Frame(root)
    rightright_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(rightright_frame, 'ZeroCurve(자동Load)', termratestr(CurveTerm1, CurveRate1), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)
    v_hwkappa = make_variable_interface(rightright_frame, 'HullWhite Kappa', bold = False, textfont = 11, titleName = "\nHull White Params", titlelable = True, defaultflag = True, defaultvalue = defaultkappa)
    defaulthwterm = "0.25, 0.5, 1" if CalibrationFlag == False else str(list(CalibrationResult["HWTerm"].round(5))).replace("[","").replace("]","")
    defaulthwvol = "0.87, 0.98, 0.89" if CalibrationFlag == False else str(list(CalibrationResult["HWVol"])).replace("[","").replace("]","")
    v_hwvolterm = make_variable_interface(rightright_frame, 'HullWhite Vol Tenor\n[0.25, 0.5, 1.0, ...] 등의\n포멧으로 입력', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaulthwterm)
    v_hwvol = make_variable_interface(rightright_frame, 'HullWhite Volatility(%)\n[0.87, 0.88, 0.91, ...] 등의\n포멧으로 입력', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaulthwvol)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)
    
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P1.get()) : 
                L1_FixedCpnRate_P1 = float(v_L1_FixedCpnRate_P1.get())/100
            else : 
                L1_FixedCpnRate_P1 = float(str(v_L1_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P1 = 0
        
        L1_PowerSpreadFlag = 0
        if len(str(v_L1_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L1_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L1_RefSwapMaturity_T.get()).split("-")
                if 'm' in SplitedStr[0].lower() :
                    L1_RefSwapMaturity_T = float(SplitedStr[0].lower().split("m")[0])/12
                elif 'y' in SplitedStr[0].lower() : 
                    L1_RefSwapMaturity_T = float(SplitedStr[0].lower().split("y")[0]) 
                else : 
                    L1_RefSwapMaturity_T = float(SplitedStr[0]) 

                if 'm' in SplitedStr[1].lower() :
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("m")[0])/12
                elif 'y' in SplitedStr[1].lower() : 
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("y")[0]) 
                else : 
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1]) 
                L1_PowerSpreadFlag = 1
            else : 
                if 'm' in str(v_L1_RefSwapMaturity_T.get()).lower() : 
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L1_RefSwapMaturity_T.get()).lower() :
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L1_RefSwapMaturity_T = float(v_L1_RefSwapMaturity_T.get()) 
                L1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T
        else : 
            L1_RefSwapMaturity_T = 0.25
            L1_RefSwapMaturity_T_PowerSpread = 0.25
            
        L1_RefSwapNCPNOneYear_P1 = int(vb_L1_RefSwapNCPNOneYear_P1.get(vb_L1_RefSwapNCPNOneYear_P1.curselection())) if vb_L1_RefSwapNCPNOneYear_P1.curselection() else 4
        if L1_RefSwapMaturity_T == 0.25 : 
            L1_RefSwapNCPNOneYear_P1 = 4

        L1_RefRateMultiple_P1 = float(v_L1_RefRateMultiple_P1.get()) if len(str(v_L1_RefRateMultiple_P1.get())) > 0 else 0
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L1ResultPayoff = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        
        L2_NumCpnOneYear_P1 = int(vb_L2_NumCpnOneYear_P1.get(vb_L2_NumCpnOneYear_P1.curselection())) if vb_L2_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L2_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P1.get()) : 
                L2_FixedCpnRate_P1 = float(v_L2_FixedCpnRate_P1.get())/100
            else : 
                L2_FixedCpnRate_P1 = float(str(v_L2_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P1 = 0
        
        L2_PowerSpreadFlag = 0
        if len(str(v_L2_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L2_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L2_RefSwapMaturity_T.get()).split("-")
                if 'm' in SplitedStr[0].lower() :
                    L2_RefSwapMaturity_T = float(SplitedStr[0].lower().split("m")[0])/12
                elif 'y' in SplitedStr[0].lower() : 
                    L2_RefSwapMaturity_T = float(SplitedStr[0].lower().split("y")[0]) 
                else : 
                    L2_RefSwapMaturity_T = float(SplitedStr[0]) 

                if 'm' in SplitedStr[1].lower() :
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("m")[0])/12
                elif 'y' in SplitedStr[1].lower() : 
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("y")[0]) 
                else : 
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1]) 
                L2_PowerSpreadFlag = 1
            else : 
                if 'm' in str(v_L2_RefSwapMaturity_T.get()).lower() : 
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L2_RefSwapMaturity_T.get()).lower() :
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L2_RefSwapMaturity_T = float(v_L2_RefSwapMaturity_T.get()) 
                L2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T
        else : 
            L2_RefSwapMaturity_T = 0.25
            L2_RefSwapMaturity_T_PowerSpread = 0.25
            
        L2_RefSwapNCPNOneYear_P1 = int(vb_L2_RefSwapNCPNOneYear_P1.get(vb_L2_RefSwapNCPNOneYear_P1.curselection())) if vb_L2_RefSwapNCPNOneYear_P1.curselection() else 4
        if L2_RefSwapMaturity_T == 0.25 : 
            L2_RefSwapNCPNOneYear_P1 = 4
            
        L2_RefRateMultiple_P1 = float(v_L2_RefRateMultiple_P1.get()) if len(str(v_L2_RefRateMultiple_P1.get())) > 0 else 0
        L2_DayCount = int(str(vb_L2_DayCount.get(vb_L2_DayCount.curselection())).split(":")[0]) if vb_L2_DayCount.curselection() else (0 if L2_NumCpnOneYear_P1 != 0 else 3)
        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L2ResultPayoff = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"

        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        Holiday = str(vb_Holiday.get(vb_Holiday.curselection())).upper() if vb_Holiday.curselection() else "KRW"
        if 'KRW' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif "KRW" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else : 
            if Curr in HolidayData.columns : 
                HolidaysForSwap = HolidayData[Curr].unique().astype(np.int64)
            else : 
                HolidaysForSwap = []
                            
        OptionHolder = int(str(vb_OptionHolder.get(vb_OptionHolder.curselection())).split(":")[0]) if vb_OptionHolder.curselection() else 0    
        FirstOptPayDate = int(v_FirstOptPayDate.get()) if len(str(v_FirstOptPayDate.get())) > 0 else SwapEffectiveDate + 10000
        NYearBetweenOptionPay = float(str(vb_NYearBetweenOptionPay.get(vb_NYearBetweenOptionPay.curselection())).split("M")[0])/12 if vb_NYearBetweenOptionPay.curselection() else 1    
        MaxNumOpt = int(v_MaxNumOpt.get()) if len(str(v_MaxNumOpt.get())) > 0 else -1
        NBDateBetweenOptionFixToPay = int(v_NBDateBetweenOptionFixToPay.get()) if len(str(v_NBDateBetweenOptionFixToPay.get())) > 0 else 0
        
        GreekFlag = int(str(vb_GreekFlag.get(vb_GreekFlag.curselection())).split(":")[0]) if vb_GreekFlag.curselection() else 0
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        
        hwkappa = float(v_hwkappa.get()) if len(str(v_hwkappa.get())) > 0 else 0.001
        if len(str(v_hwvolterm.get())) > 0 : 
            if '(' in str(v_hwvolterm.get()) or ')' in str(v_hwvolterm.get()) : 
                tenorstr = str(v_hwvolterm.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvolterm.get()) or ']' in str(v_hwvolterm.get()) :
                tenorstr = str(v_hwvolterm.get()).replace("[","").replace("]","").split(',')
            else : 
                tenorstr = str(v_hwvolterm.get()).split(',')
            hwvolterm = list(np.vectorize(lambda x : float(x))(tenorstr))
        else : 
            hwvolterm = [1.0]

        if len(str(v_hwvol.get())) > 0 : 
            if '(' in str(v_hwvol.get()) or ')' in str(v_hwvol.get()) : 
                volstr = str(v_hwvol.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol.get()) or ']' in str(v_hwvol.get()) :
                volstr = str(v_hwvol.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol.get()).split(',')
            hwvol = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol = [0.001]

        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0
        L2FirstFixing = float(v_L2FirstFixing.get())/100 if str(v_L2FirstFixing.get()) else 0.0
        
        L1_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(365)]
        L1_FixingHistoryRate = [L1FirstFixing] * len(L1_FixingHistoryDate)    
        L2_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(366)] 
        L2_FixingHistoryRate = [L2FirstFixing] * len(L2_FixingHistoryDate)    
        OptionFixDate, OptionPayDate = Generate_OptionDate(FirstOptPayDate, SwapMaturity, NYearBetweenOptionPay, NBDateBetweenOptionFixToPay, MaxNumOpt, ModifiedFollow = 0)
        if GreekFlag == 0 : 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag = (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            GIRRDelta = 0
            GIRRCurvature = 0
            GIRRVega = 0
            
        else : 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            Result = Pricing_IRCallableSwap_HWFDM_Greek(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = False, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread,
                    GreekFlag = GreekFlag)
            
            DeltaGreek = pd.Series(Result["PV01"], index = CurveTerm1).reset_index()
            DeltaGreek.columns = ["PV01Term","PV01"]
            GIRRDelta = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(DeltaGreek, "PV01Term","PV01"), 4)
            Cvup = list(np.array(CurveRate1) + 0.012)
            Pu = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvup, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            Cvdn = list(np.array(CurveRate1) - 0.012)
            Pd = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvdn, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            GammaGreek = DeltaGreek.copy()
            GammaGreek.columns = ["Tenor","DeltaSensi"]
            GammaGreek["DeltaSensi"] = GammaGreek["DeltaSensi"] * 10000
            GammaGreek["Bucket"] ="KRW"
            GammaGreek["RiskWeight"] = GIRR_DeltaRiskWeight(list(DeltaGreek["PV01Term"].values), ["KRW"] * len(DeltaGreek), ["IRS"] * len(DeltaGreek))
            CVR_Plus = -(Pu - Result["Price"] - (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            CVR_Minus = -(Pd - Result["Price"] + (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            GIRRCurvature = max(abs(CVR_Plus), abs(CVR_Minus))
            T = DayCountAtoB(int(YYYYMMDD), SwapMaturity)/365
            if GreekFlag > 1 : 
                V = pd.Series(Result["VegaFRTB"][1:-1], Result["VegaTerm"][1:-1]).reset_index()
                V.columns = ["Tenor1","VegaSensi"]
                V["Tenor2"] = T - V["Tenor1"]
                V["Risk_Type"] = "Vega"
                V["Curve"] = UsedCurveName
                V["Risk_Class"] = "GIRR"
                V["Bucket"] = "KRW"
                GIRRVega = Calc_GIRRVega(V, SensitivityColumnName = "VegaSensi")["KB_M"].iloc[0]
            else : 
                GIRRVega = 0
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        resultframe = resultframe.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, resultframe.reset_index(), width = 100)
        if GreekFlag > 0 : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\n\nLeg1 Payoff: \n{L1ResultPayoff}\n\nLeg2 Payoff: \n{L2ResultPayoff}\n\nGIRR Delta: {np.round(GIRRDelta,4)}\n\nGIRR Curvature: {np.round(GIRRCurvature,4)}\n\nGIRR Vega: {np.round(GIRRVega,4)} ", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\n\nLeg1 Payoff: \n{L1ResultPayoff}\n\nLeg2 Payoff: \n{L2ResultPayoff}", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop()
    MainFlag2 = 0#input("종료하시겠습니까? (Y/N)\n->")

    return MainFlag2, 1, 1, 1

def PricingIRStructuredSwapProgramDoublePhase(HolidayData, currdir) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                    namenotin = "vol",
                                                                    Comments = "IRS Pricing을 위한 커브 번호를 입력하시오.",
                                                                    MultiSelection = False,
                                                                    DefaultStringList=["IRS"])     
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    PriceDateDefault = int(YYYYMMDD)
    Curve = MyMarketDataList[0]
    UsedCurveName = Name[0].split("\\")[-1].split(".")[0]
    Curr = Name[0].split("\\")[-2].upper()
    CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
    CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
    CalibrationResult = HullWhiteCalibrationProgram(Name[0], int(YYYYMMDD), CurveTerm1, CurveRate1, HolidayData)
    CalibrationFlag = CalibrationResult['CalibrationFlag']
    defaultkappa = 0.01
    if CalibrationFlag == True : 
        defaultkappa = CalibrationResult['kappa']

    YYYY = int(YYYYMMDD) // 10000
    root = tk.Tk()
    root.title("Callable Swap Pricer(Double Phase)")
    root.geometry("1550x790+2+2")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = PriceDateDefault)
    vb_Holiday = make_listvariable_interface(left_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 4, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 929)
    v_Phase2StartDate = make_variable_interface(left_frame, 'Phase2StartDate\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 100000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+21) * 10000 + 929)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 1, pady = 3, anchor = 'n')
    vb_L1_PhaseUseFlag = make_listvariable_interface(center_frame, 'Phase2사용Flag', ["0: False","1: True"], titlelable = True, titleName = "Leg1 Information", listheight = 2, textfont = 10, defaultflag = True, defaultvalue=1)
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(center_frame, '연 쿠폰지급수(P1)', ["0","1","2","4","6"], listheight = 4, textfont = 11, pady = 1, defaultflag = True, defaultvalue=3)
    vb_L1_NumCpnOneYear_P2 = make_listvariable_interface(center_frame, '연 쿠폰지급수(P2)', ["0","1","2","4","6"], listheight = 4, textfont = 10, pady = 1, defaultflag = True, defaultvalue=3)
    v_L1_FixedCpnRate_P1 = make_variable_interface(center_frame, '고정쿠폰(%)(P1)', bold = False, textfont = 11, pady = 1, defaultflag = True, defaultvalue =2.19)
    v_L1_FixedCpnRate_P2 = make_variable_interface(center_frame, '고정쿠폰(%)(P2)', bold = False, textfont = 10, pady = 1, defaultflag = True, defaultvalue =2.19)
    v_L1_RefSwapMaturity_T = make_variable_interface(center_frame, '변동금리 만기\n(3M-> 0.25, 5Y-> 5)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11, pady = 1)
    vb_L1_RefSwapNCPNOneYear_P1 = make_listvariable_interface(center_frame, '변동금리 연쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, pady = 1)
    v_L1_RefRateMultiple_P1 = make_variable_interface(center_frame, '변동금리Multiple(P1)', bold = False, textfont = 11, pady = 1)
    v_L1_RefRateMultiple_P2 = make_variable_interface(center_frame, '변동금리Multiple(P2)', bold = False, textfont = 10, pady = 1)
    vb_L1_DayCount = make_listvariable_interface(center_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 1, pady = 3, anchor = 'n')
    vb_L2_PhaseUseFlag = make_listvariable_interface(right_frame, 'Phase2사용Flag', ["0: False","1: True"], titlelable = True, titleName = "Leg2 Information", listheight = 2, textfont = 10, defaultflag = True, defaultvalue=0)
    vb_L2_NumCpnOneYear_P1 = make_listvariable_interface(right_frame, '연 쿠폰지급수(P1)', ["0","1","2","4","6"], listheight = 4, textfont = 11, pady = 1, defaultflag = True, defaultvalue = 3)
    vb_L2_NumCpnOneYear_P2 = make_listvariable_interface(right_frame, '연 쿠폰지급수(P2)', ["0","1","2","4","6"], listheight = 4, textfont = 10, pady = 1, defaultflag = True, defaultvalue=3)
    v_L2_FixedCpnRate_P1 = make_variable_interface(right_frame, '고정쿠폰(%)(P1)', bold = False, textfont = 11, pady = 1, defaultflag = True, defaultvalue = -0.1)
    v_L2_FixedCpnRate_P2 = make_variable_interface(right_frame, '고정쿠폰(%)(P2)', bold = False, textfont = 10, pady = 1, defaultflag = True, defaultvalue = 0.15)
    v_L2_RefSwapMaturity_T = make_variable_interface(right_frame, '변동금리 만기\n(3M-> 0.25, 5Y-> 5)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11, defaultflag = True ,defaultvalue = 0.25, pady = 1)
    vb_L2_RefSwapNCPNOneYear_P1 = make_listvariable_interface(right_frame, '변동금리 연쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, pady = 1, defaultflag = True, defaultvalue = 2)
    v_L2_RefRateMultiple_P1 = make_variable_interface(right_frame, '변동금리Multiple(P1)', bold = False, textfont = 11, pady = 1, defaultflag = True, defaultvalue = 1.0)
    v_L2_RefRateMultiple_P2 = make_variable_interface(right_frame, '변동금리Multiple(P2)', bold = False, textfont = 10, pady = 1)
    vb_L2_DayCount = make_listvariable_interface(right_frame, 'Leg2 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    rightright_frame = tk.Frame(root)
    rightright_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_OptionHolder = make_listvariable_interface(rightright_frame, 'OptionHolder', ["0: Leg1 Hold Option","1: Leg2 Hold Option"], titleName = "Option Information", titlelable= True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue= 0)
    v_FirstOptPayDate = make_variable_interface(rightright_frame, '첫 옵션행사일\n(지급일기준)', bold = False, textfont = 11, defaultflag = True, defaultvalue = (YYYY-6) * 10000 + 929)
    vb_NYearBetweenOptionPay = make_listvariable_interface(rightright_frame, '옵션행사간격', ["6M","12M","24M","36M","60M"], listheight = 5, textfont = 11, defaultflag = True, defaultvalue = 1)
    v_NBDateBetweenOptionFixToPay = make_variable_interface(rightright_frame, '옵션행사선언일과\n옵션지급일사이의\n영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 20)
    v_MaxNumOpt = make_variable_interface(rightright_frame, '최대옵션개수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0)
    v_L1FirstFixing = make_variable_interface(rightright_frame, 'Leg1)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_L2FirstFixing = make_variable_interface(rightright_frame, 'Leg2)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_GreekFlag = make_listvariable_interface(rightright_frame, 'Greek산출', ["0: Pricing만","1: Delta,Gamma","2: Delta,Gamma,Vega"], listheight = 3, textfont = 11)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(Result_frame, 'ZeroCurve(자동Load)', termratestr(CurveTerm1, CurveRate1), titleName = "MARKET DATA INFO", titlelable= True, listheight = 13, textfont = 11)
    v_hwkappa = make_variable_interface(Result_frame, 'HullWhite Kappa', bold = False, textfont = 11, titleName = "\nHull White Params", titlelable = True, defaultflag = True, defaultvalue = defaultkappa)
    defaulthwterm = "0.25, 0.5, 1" if CalibrationFlag == False else str(list(CalibrationResult["HWTerm"].round(5))).replace("[","").replace("]","")
    defaulthwvol = "0.87, 0.98, 0.89" if CalibrationFlag == False else str(list(CalibrationResult["HWVol"])).replace("[","").replace("]","")
    v_hwvolterm = make_variable_interface(Result_frame, 'HullWhite Vol Tenor\n[0.25, 0.5, 1.0, ...] 등의\n포멧으로 입력', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaulthwterm)
    v_hwvol = make_variable_interface(Result_frame, 'HullWhite Volatility(%)\n[0.87, 0.88, 0.91, ...] 등의\n포멧으로 입력', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaulthwvol)
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 10, pady = 5)

    Result_frame2 = tk.Frame(root)
    Result_frame2.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        Phase2StartDate = int(v_Phase2StartDate.get()) if len(str(v_Phase2StartDate.get())) > 0 else (20200627 + 50000)
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        L1_PhaseUseFlag = int(str(vb_L1_PhaseUseFlag.get(vb_L1_PhaseUseFlag.curselection())).split(":")[0]) if vb_L1_PhaseUseFlag.curselection() else 0
        
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P1.get()) : 
                L1_FixedCpnRate_P1 = float(v_L1_FixedCpnRate_P1.get())/100
            else : 
                L1_FixedCpnRate_P1 = float(str(v_L1_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P1 = 0

        L1_NumCpnOneYear_P2 = int(vb_L1_NumCpnOneYear_P2.get(vb_L1_NumCpnOneYear_P2.curselection())) if vb_L1_NumCpnOneYear_P2.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P2.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P2.get()) : 
                L1_FixedCpnRate_P2 = float(v_L1_FixedCpnRate_P2.get())/100
            else : 
                L1_FixedCpnRate_P2 = float(str(v_L1_FixedCpnRate_P2.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P2 = 0
        
        L1_PowerSpreadFlag = 0
        if len(str(v_L1_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L1_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L1_RefSwapMaturity_T.get()).split("-")
                if 'm' in SplitedStr[0].lower() :
                    L1_RefSwapMaturity_T = float(SplitedStr[0].lower().split("m")[0])/12
                elif 'y' in SplitedStr[0].lower() : 
                    L1_RefSwapMaturity_T = float(SplitedStr[0].lower().split("y")[0]) 
                else : 
                    L1_RefSwapMaturity_T = float(SplitedStr[0]) 

                if 'm' in SplitedStr[1].lower() :
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("m")[0])/12
                elif 'y' in SplitedStr[1].lower() : 
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("y")[0]) 
                else : 
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1]) 
                L1_PowerSpreadFlag = 1
            else : 
                if 'm' in str(v_L1_RefSwapMaturity_T.get()).lower() : 
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L1_RefSwapMaturity_T.get()).lower() :
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L1_RefSwapMaturity_T = float(v_L1_RefSwapMaturity_T.get()) 
                L1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T
        else : 
            L1_RefSwapMaturity_T = 0.25
            L1_RefSwapMaturity_T_PowerSpread = 0.25
            
        L1_RefSwapNCPNOneYear_P1 = int(vb_L1_RefSwapNCPNOneYear_P1.get(vb_L1_RefSwapNCPNOneYear_P1.curselection())) if vb_L1_RefSwapNCPNOneYear_P1.curselection() else 4
        if L1_RefSwapMaturity_T == 0.25 : 
            L1_RefSwapNCPNOneYear_P1 = 4

        L1_RefRateMultiple_P1 = float(v_L1_RefRateMultiple_P1.get()) if len(str(v_L1_RefRateMultiple_P1.get())) > 0 else 0
        L1_RefRateMultiple_P2 = float(v_L1_RefRateMultiple_P2.get()) if len(str(v_L1_RefRateMultiple_P2.get())) > 0 else 0
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L1ResultPayoff = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff_P2 = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P2) + " + " +str(np.round(L1_FixedCpnRate_P2*100,4)) + "%"
        else : 
            L1ResultPayoff_P2 = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P2) + " + " +str(np.round(L1_FixedCpnRate_P2*100,4)) + "%"
        
        L2_PhaseUseFlag = int(str(vb_L2_PhaseUseFlag.get(vb_L2_PhaseUseFlag.curselection())).split(":")[0]) if vb_L2_PhaseUseFlag.curselection() else 0        
        
        L2_NumCpnOneYear_P1 = int(vb_L2_NumCpnOneYear_P1.get(vb_L2_NumCpnOneYear_P1.curselection())) if vb_L2_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L2_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P1.get()) : 
                L2_FixedCpnRate_P1 = float(v_L2_FixedCpnRate_P1.get())/100
            else : 
                L2_FixedCpnRate_P1 = float(str(v_L2_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P1 = 0
        
        L2_NumCpnOneYear_P2 = int(vb_L2_NumCpnOneYear_P2.get(vb_L2_NumCpnOneYear_P2.curselection())) if vb_L2_NumCpnOneYear_P2.curselection() else 4
        if len(str(v_L2_FixedCpnRate_P2.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P2.get()) : 
                L2_FixedCpnRate_P2 = float(v_L2_FixedCpnRate_P2.get())/100
            else : 
                L2_FixedCpnRate_P2 = float(str(v_L2_FixedCpnRate_P2.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P2 = 0        
        
        L2_PowerSpreadFlag = 0
        if len(str(v_L2_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L2_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L2_RefSwapMaturity_T.get()).split("-")
                if 'm' in SplitedStr[0].lower() :
                    L2_RefSwapMaturity_T = float(SplitedStr[0].lower().split("m")[0])/12
                elif 'y' in SplitedStr[0].lower() : 
                    L2_RefSwapMaturity_T = float(SplitedStr[0].lower().split("y")[0]) 
                else : 
                    L2_RefSwapMaturity_T = float(SplitedStr[0]) 

                if 'm' in SplitedStr[1].lower() :
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("m")[0])/12
                elif 'y' in SplitedStr[1].lower() : 
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("y")[0]) 
                else : 
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1]) 
                L2_PowerSpreadFlag = 1
            else : 
                if 'm' in str(v_L2_RefSwapMaturity_T.get()).lower() : 
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L2_RefSwapMaturity_T.get()).lower() :
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L2_RefSwapMaturity_T = float(v_L2_RefSwapMaturity_T.get()) 
                L2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T
        else : 
            L2_RefSwapMaturity_T = 0.25
            L2_RefSwapMaturity_T_PowerSpread = 0.25
            
        L2_RefSwapNCPNOneYear_P1 = int(vb_L2_RefSwapNCPNOneYear_P1.get(vb_L2_RefSwapNCPNOneYear_P1.curselection())) if vb_L2_RefSwapNCPNOneYear_P1.curselection() else 4
        if L2_RefSwapMaturity_T == 0.25 : 
            L2_RefSwapNCPNOneYear_P1 = 4
            
        L2_RefRateMultiple_P1 = float(v_L2_RefRateMultiple_P1.get()) if len(str(v_L2_RefRateMultiple_P1.get())) > 0 else 0
        L2_RefRateMultiple_P2 = float(v_L2_RefRateMultiple_P2.get()) if len(str(v_L2_RefRateMultiple_P2.get())) > 0 else 0
        L2_DayCount = int(str(vb_L2_DayCount.get(vb_L2_DayCount.curselection())).split(":")[0]) if vb_L2_DayCount.curselection() else (0 if L2_NumCpnOneYear_P1 != 0 else 3)
        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L2ResultPayoff = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"

        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff_P2 = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P2) + " + " +str(np.round(L2_FixedCpnRate_P2*100,4)) + "%"
        else : 
            L2ResultPayoff_P2 = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P2) + " + " +str(np.round(L2_FixedCpnRate_P2*100,4)) + "%"

        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        Holiday = str(vb_Holiday.get(vb_Holiday.curselection())).upper() if vb_Holiday.curselection() else "KRW"
        if 'KRW' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif "KRW" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else : 
            if Curr in HolidayData.columns : 
                HolidaysForSwap = HolidayData[Curr].unique().astype(np.int64)
            else : 
                HolidaysForSwap = []
                            
        OptionHolder = int(str(vb_OptionHolder.get(vb_OptionHolder.curselection())).split(":")[0]) if vb_OptionHolder.curselection() else 0    
        FirstOptPayDate = int(v_FirstOptPayDate.get()) if len(str(v_FirstOptPayDate.get())) > 0 else SwapEffectiveDate + 10000
        NYearBetweenOptionPay = float(str(vb_NYearBetweenOptionPay.get(vb_NYearBetweenOptionPay.curselection())).split("M")[0])/12 if vb_NYearBetweenOptionPay.curselection() else 1    
        MaxNumOpt = int(v_MaxNumOpt.get()) if len(str(v_MaxNumOpt.get())) > 0 else -1
        NBDateBetweenOptionFixToPay = int(v_NBDateBetweenOptionFixToPay.get()) if len(str(v_NBDateBetweenOptionFixToPay.get())) > 0 else 0
        
        GreekFlag = int(str(vb_GreekFlag.get(vb_GreekFlag.curselection())).split(":")[0]) if vb_GreekFlag.curselection() else 0
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        
        hwkappa = float(v_hwkappa.get()) if len(str(v_hwkappa.get())) > 0 else 0.001
        if len(str(v_hwvolterm.get())) > 0 : 
            if '(' in str(v_hwvolterm.get()) or ')' in str(v_hwvolterm.get()) : 
                tenorstr = str(v_hwvolterm.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvolterm.get()) or ']' in str(v_hwvolterm.get()) :
                tenorstr = str(v_hwvolterm.get()).replace("[","").replace("]","").split(',')
            else : 
                tenorstr = str(v_hwvolterm.get()).split(',')
            hwvolterm = list(np.vectorize(lambda x : float(x))(tenorstr))
        else : 
            hwvolterm = [1.0]

        if len(str(v_hwvol.get())) > 0 : 
            if '(' in str(v_hwvol.get()) or ')' in str(v_hwvol.get()) : 
                volstr = str(v_hwvol.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol.get()) or ']' in str(v_hwvol.get()) :
                volstr = str(v_hwvol.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol.get()).split(',')
            hwvol = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol = [0.001]

        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0
        L2FirstFixing = float(v_L2FirstFixing.get())/100 if str(v_L2FirstFixing.get()) else 0.0
        
        L1_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(365)]
        L1_FixingHistoryRate = [L1FirstFixing] * len(L1_FixingHistoryDate)    
        L2_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(366)] 
        L2_FixingHistoryRate = [L2FirstFixing] * len(L2_FixingHistoryDate)    
        OptionFixDate, OptionPayDate = Generate_OptionDate(FirstOptPayDate, SwapMaturity, NYearBetweenOptionPay, NBDateBetweenOptionFixToPay, MaxNumOpt, ModifiedFollow = 0)
        if GreekFlag == 0 : 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag = (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag= L1_PhaseUseFlag,NumCpnOneYear_Leg1_Phase2=L1_NumCpnOneYear_P2,Leg1_Phase2StartDate= Phase2StartDate,Leg1_RefSwapRate_Multiple_Phase2=L1_RefRateMultiple_P2,Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,
                    Leg2_Phase2UseFlag= L2_PhaseUseFlag,NumCpnOneYear_Leg2_Phase2=L2_NumCpnOneYear_P2,Leg2_Phase2StartDate= Phase2StartDate,Leg2_RefSwapRate_Multiple_Phase2=L2_RefRateMultiple_P2,Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            GIRRDelta = 0
            GIRRCurvature = 0
            GIRRVega = 0
            
        else : 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag= L1_PhaseUseFlag,NumCpnOneYear_Leg1_Phase2=L1_NumCpnOneYear_P2,Leg1_Phase2StartDate= Phase2StartDate,Leg1_RefSwapRate_Multiple_Phase2=L1_RefRateMultiple_P2,Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,
                    Leg2_Phase2UseFlag= L2_PhaseUseFlag,NumCpnOneYear_Leg2_Phase2=L2_NumCpnOneYear_P2,Leg2_Phase2StartDate= Phase2StartDate,Leg2_RefSwapRate_Multiple_Phase2=L2_RefRateMultiple_P2,Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            Result = Pricing_IRCallableSwap_HWFDM_Greek(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = False, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag= L1_PhaseUseFlag,NumCpnOneYear_Leg1_Phase2=L1_NumCpnOneYear_P2,Leg1_Phase2StartDate= Phase2StartDate,Leg1_RefSwapRate_Multiple_Phase2=L1_RefRateMultiple_P2,Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,
                    Leg2_Phase2UseFlag= L2_PhaseUseFlag,NumCpnOneYear_Leg2_Phase2=L2_NumCpnOneYear_P2,Leg2_Phase2StartDate= Phase2StartDate,Leg2_RefSwapRate_Multiple_Phase2=L2_RefRateMultiple_P2,Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread,
                    GreekFlag = GreekFlag)
            
            DeltaGreek = pd.Series(Result["PV01"], index = CurveTerm1).reset_index()
            DeltaGreek.columns = ["PV01Term","PV01"]
            GIRRDelta = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(DeltaGreek, "PV01Term","PV01"), 4)
            Cvup = list(np.array(CurveRate1) + 0.012)
            Pu = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvup, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag= L1_PhaseUseFlag,NumCpnOneYear_Leg1_Phase2=L1_NumCpnOneYear_P2,Leg1_Phase2StartDate= Phase2StartDate,Leg1_RefSwapRate_Multiple_Phase2=L1_RefRateMultiple_P2,Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,
                    Leg2_Phase2UseFlag= L2_PhaseUseFlag,NumCpnOneYear_Leg2_Phase2=L2_NumCpnOneYear_P2,Leg2_Phase2StartDate= Phase2StartDate,Leg2_RefSwapRate_Multiple_Phase2=L2_RefRateMultiple_P2,Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            Cvdn = list(np.array(CurveRate1) - 0.012)
            Pd = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvdn, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag= L1_PhaseUseFlag,NumCpnOneYear_Leg1_Phase2=L1_NumCpnOneYear_P2,Leg1_Phase2StartDate= Phase2StartDate,Leg1_RefSwapRate_Multiple_Phase2=L1_RefRateMultiple_P2,Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,
                    Leg2_Phase2UseFlag= L2_PhaseUseFlag,NumCpnOneYear_Leg2_Phase2=L2_NumCpnOneYear_P2,Leg2_Phase2StartDate= Phase2StartDate,Leg2_RefSwapRate_Multiple_Phase2=L2_RefRateMultiple_P2,Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            GammaGreek = DeltaGreek.copy()
            GammaGreek.columns = ["Tenor","DeltaSensi"]
            GammaGreek["DeltaSensi"] = GammaGreek["DeltaSensi"] * 10000
            GammaGreek["Bucket"] ="KRW"
            GammaGreek["RiskWeight"] = GIRR_DeltaRiskWeight(list(DeltaGreek["PV01Term"].values), ["KRW"] * len(DeltaGreek), ["IRS"] * len(DeltaGreek))
            CVR_Plus = -(Pu - Result["Price"] - (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            CVR_Minus = -(Pd - Result["Price"] + (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            GIRRCurvature = max(abs(CVR_Plus), abs(CVR_Minus))
            T = DayCountAtoB(int(YYYYMMDD), SwapMaturity)/365
            if GreekFlag > 1 : 
                V = pd.Series(Result["VegaFRTB"][1:-1], Result["VegaTerm"][1:-1]).reset_index()
                V.columns = ["Tenor1","VegaSensi"]
                V["Tenor2"] = T - V["Tenor1"]
                V["Risk_Type"] = "Vega"
                V["Curve"] = UsedCurveName
                V["Risk_Class"] = "GIRR"
                V["Bucket"] = "KRW"
                GIRRVega = Calc_GIRRVega(V, SensitivityColumnName = "VegaSensi")["KB_M"].iloc[0]
            else : 
                GIRRVega = 0
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        resultframe = resultframe.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, resultframe.reset_index(), width = 100)
        if GreekFlag > 0 : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\nLeg1 Payoff: \n{L1ResultPayoff} (Ph1)\n{L1ResultPayoff_P2} (Ph2)\nLeg2 Payoff: \n{L2ResultPayoff} (Ph1)\n{L2ResultPayoff_P2} (Ph2)\nGIRR Delta: {np.round(GIRRDelta,4)}\nGIRR Curvature: {np.round(GIRRCurvature,4)}\nGIRR Vega: {np.round(GIRRVega,4)} ", font = ("맑은 고딕", 11, 'bold'))
        else : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\nLeg1 Payoff: \n{L1ResultPayoff} (Ph1)\n{L1ResultPayoff_P2} (Ph2)\nLeg2 Payoff: \n{L2ResultPayoff} (Ph1)\n{L2ResultPayoff_P2} (Ph2)", font = ("맑은 고딕", 11, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 2, pady = 5, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 11).pack()
    output_label = tk.Label(Result_frame2, text = "", anchor = "n")
    output_label.pack(padx = 2, pady = 2)

    root.mainloop()
    MainFlag2 = 0#input("종료하시겠습니까? (Y/N)\n->")

    return MainFlag2, 1, 1, 1

def PricingIRStructuredSwapProgram2F(HolidayData, currdir) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                    namenotin = "vol",
                                                                    Comments = "IRS Pricing을 위한 커브 번호를 입력하시오.",
                                                                    MultiSelection = False,
                                                                    DefaultStringList=["IRS"])     
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    PriceDateDefault = int(YYYYMMDD)
    Curve = MyMarketDataList[0]
    UsedCurveName = Name[0].split("\\")[-1].split(".")[0]
    Curr = Name[0].split("\\")[-2].upper()
    CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
    CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
    CalibrationFlag = False
    defaultkappa = 0.01
    defaultkappa2 = 0.01        

    YYYY = int(YYYYMMDD) // 10000
    root = tk.Tk()
    root.title("Callable Swap 2F Pricer(Single Phase)")
    root.geometry("1560x780+5+5")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+21) * 10000 + 929)
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수', ["0","1","2","4","6"], titlelable = True, titleName = "Leg1 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3)
    v_L1_FixedCpnRate_P1 = make_variable_interface(left_frame, 'Leg1 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =1.69)
    v_L1_RefSwapMaturity_T = make_variable_interface(left_frame, 'Leg1 변동금리 만기\n(3M-> 0.25, 5Y-> 5, \n5Y-1Y -> 5-1)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11)
    vb_L1_RefSwapNCPNOneYear_P1 = make_listvariable_interface(left_frame, 'Leg1 변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11)
    v_L1_RefRateMultiple_P1 = make_variable_interface(left_frame, 'Leg1 변동금리Multiple', bold = False, textfont = 11)
    vb_L1_DayCount = make_listvariable_interface(left_frame, 'Leg1 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(center_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = PriceDateDefault)
    vb_Holiday = make_listvariable_interface(center_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 4, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)

    vb_L2_NumCpnOneYear_P1 = make_listvariable_interface(center_frame, '연 쿠폰지급수', ["0","1","2","4","6"], titlelable = True, titleName = "Leg2 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue = 3)
    v_L2_FixedCpnRate_P1 = make_variable_interface(center_frame, 'Leg2 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0.2)
    v_L2_RefSwapMaturity_T = make_variable_interface(center_frame, 'Leg2 변동금리 만기\n(3M-> 0.25, 5Y-> 5, \n5Y-1Y -> 5-1)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11, defaultflag = True ,defaultvalue = '5 - 1')
    vb_L2_RefSwapNCPNOneYear_P1 = make_listvariable_interface(center_frame, 'Leg2 변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 2)
    v_L2_RefRateMultiple_P1 = make_variable_interface(center_frame, 'Leg2 변동금리Multiple', bold = False, textfont = 11, defaultflag = True, defaultvalue = 5.0)
    vb_L2_DayCount = make_listvariable_interface(center_frame, 'Leg2 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')
    vb_OptionHolder = make_listvariable_interface(right_frame, 'OptionHolder', ["0: Leg1 Hold Option","1: Leg2 Hold Option"], titleName = "Option Information", titlelable= True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue= 0)
    v_FirstOptPayDate = make_variable_interface(right_frame, '첫 옵션행사일\n(지급일기준)', bold = False, textfont = 11, defaultflag = True, defaultvalue = (YYYY-6) * 10000 + 929)
    vb_NYearBetweenOptionPay = make_listvariable_interface(right_frame, '옵션행사간격', ["6M","12M","24M","36M","60M"], listheight = 5, textfont = 11, defaultflag = True, defaultvalue = 1)
    v_NBDateBetweenOptionFixToPay = make_variable_interface(right_frame, '옵션행사선언일과\n옵션지급일사이의\n영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 20)
    v_MaxNumOpt = make_variable_interface(right_frame, '최대옵션개수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0)
    v_L1FirstFixing = make_variable_interface(right_frame, 'Leg1)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_L2FirstFixing = make_variable_interface(right_frame, 'Leg2)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_GreekFlag = make_listvariable_interface(right_frame, 'Greek산출', ["0: Pricing만","1: Delta,Gamma","2: Delta,Gamma,Vega"], listheight = 3, textfont = 11)

    rightright_frame = tk.Frame(root)
    rightright_frame.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(rightright_frame, 'ZeroCurve(자동Load)', termratestr(CurveTerm1, CurveRate1), titleName = "MARKET DATA INFO", titlelable= True, listheight = 12, textfont = 10)
    v_hwkappa = make_variable_interface(rightright_frame, 'Kappa', bold = False, textfont = 11, titleName = "\nHull White Params", titlelable = True, defaultflag = True, defaultvalue = defaultkappa)
    v_hwkappa2 = make_variable_interface(rightright_frame, 'Kappa2', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaultkappa2)
    v_hwvol = make_variable_interface(rightright_frame, 'Volatility1(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0.99)
    v_hwvol2 = make_variable_interface(rightright_frame, 'Volatility2(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0.66)
    v_hwfactorcorr = make_variable_interface(rightright_frame, 'Factor Corr(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = -0.1)
    vb_Logging = make_listvariable_interface(rightright_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')
    
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P1.get()) : 
                L1_FixedCpnRate_P1 = float(v_L1_FixedCpnRate_P1.get())/100
            else : 
                L1_FixedCpnRate_P1 = float(str(v_L1_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P1 = 0
        
        L1_PowerSpreadFlag = 0
        if len(str(v_L1_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L1_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L1_RefSwapMaturity_T.get()).split("-")
                if 'm' in SplitedStr[0].lower() :
                    L1_RefSwapMaturity_T = float(SplitedStr[0].lower().split("m")[0])/12
                elif 'y' in SplitedStr[0].lower() : 
                    L1_RefSwapMaturity_T = float(SplitedStr[0].lower().split("y")[0]) 
                else : 
                    L1_RefSwapMaturity_T = float(SplitedStr[0]) 

                if 'm' in SplitedStr[1].lower() :
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("m")[0])/12
                elif 'y' in SplitedStr[1].lower() : 
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("y")[0]) 
                else : 
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1]) 
                L1_PowerSpreadFlag = 1
            else : 
                if 'm' in str(v_L1_RefSwapMaturity_T.get()).lower() : 
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L1_RefSwapMaturity_T.get()).lower() :
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L1_RefSwapMaturity_T = float(v_L1_RefSwapMaturity_T.get()) 
                L1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T
        else : 
            L1_RefSwapMaturity_T = 0.25
            L1_RefSwapMaturity_T_PowerSpread = 0.25
            
        L1_RefSwapNCPNOneYear_P1 = int(vb_L1_RefSwapNCPNOneYear_P1.get(vb_L1_RefSwapNCPNOneYear_P1.curselection())) if vb_L1_RefSwapNCPNOneYear_P1.curselection() else 4
        if L1_RefSwapMaturity_T == 0.25 : 
            L1_RefSwapNCPNOneYear_P1 = 4

        L1_RefRateMultiple_P1 = float(v_L1_RefRateMultiple_P1.get()) if len(str(v_L1_RefRateMultiple_P1.get())) > 0 else 0
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L1ResultPayoff = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        
        L2_NumCpnOneYear_P1 = int(vb_L2_NumCpnOneYear_P1.get(vb_L2_NumCpnOneYear_P1.curselection())) if vb_L2_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L2_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P1.get()) : 
                L2_FixedCpnRate_P1 = float(v_L2_FixedCpnRate_P1.get())/100
            else : 
                L2_FixedCpnRate_P1 = float(str(v_L2_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P1 = 0
        
        L2_PowerSpreadFlag = 0
        if len(str(v_L2_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L2_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L2_RefSwapMaturity_T.get()).split("-")
                if 'm' in SplitedStr[0].lower() :
                    L2_RefSwapMaturity_T = float(SplitedStr[0].lower().split("m")[0])/12
                elif 'y' in SplitedStr[0].lower() : 
                    L2_RefSwapMaturity_T = float(SplitedStr[0].lower().split("y")[0]) 
                else : 
                    L2_RefSwapMaturity_T = float(SplitedStr[0]) 

                if 'm' in SplitedStr[1].lower() :
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("m")[0])/12
                elif 'y' in SplitedStr[1].lower() : 
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("y")[0]) 
                else : 
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1]) 
                L2_PowerSpreadFlag = 1
            else : 
                if 'm' in str(v_L2_RefSwapMaturity_T.get()).lower() : 
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L2_RefSwapMaturity_T.get()).lower() :
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L2_RefSwapMaturity_T = float(v_L2_RefSwapMaturity_T.get()) 
                L2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T
        else : 
            L2_RefSwapMaturity_T = 0.25
            L2_RefSwapMaturity_T_PowerSpread = 0.25
            
        L2_RefSwapNCPNOneYear_P1 = int(vb_L2_RefSwapNCPNOneYear_P1.get(vb_L2_RefSwapNCPNOneYear_P1.curselection())) if vb_L2_RefSwapNCPNOneYear_P1.curselection() else 4
        if L2_RefSwapMaturity_T == 0.25 : 
            L2_RefSwapNCPNOneYear_P1 = 4
            
        L2_RefRateMultiple_P1 = float(v_L2_RefRateMultiple_P1.get()) if len(str(v_L2_RefRateMultiple_P1.get())) > 0 else 0
        L2_DayCount = int(str(vb_L2_DayCount.get(vb_L2_DayCount.curselection())).split(":")[0]) if vb_L2_DayCount.curselection() else (0 if L2_NumCpnOneYear_P1 != 0 else 3)
        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L2ResultPayoff = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"

        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        Holiday = str(vb_Holiday.get(vb_Holiday.curselection())).upper() if vb_Holiday.curselection() else "KRW"
        if 'KRW' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif "KRW" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else : 
            if Curr in HolidayData.columns : 
                HolidaysForSwap = HolidayData[Curr].unique().astype(np.int64)
            else : 
                HolidaysForSwap = []
                            
        OptionHolder = int(str(vb_OptionHolder.get(vb_OptionHolder.curselection())).split(":")[0]) if vb_OptionHolder.curselection() else 0    
        FirstOptPayDate = int(v_FirstOptPayDate.get()) if len(str(v_FirstOptPayDate.get())) > 0 else SwapEffectiveDate + 10000
        NYearBetweenOptionPay = float(str(vb_NYearBetweenOptionPay.get(vb_NYearBetweenOptionPay.curselection())).split("M")[0])/12 if vb_NYearBetweenOptionPay.curselection() else 1    
        MaxNumOpt = int(v_MaxNumOpt.get()) if len(str(v_MaxNumOpt.get())) > 0 else -1
        NBDateBetweenOptionFixToPay = int(v_NBDateBetweenOptionFixToPay.get()) if len(str(v_NBDateBetweenOptionFixToPay.get())) > 0 else 0
        
        GreekFlag = int(str(vb_GreekFlag.get(vb_GreekFlag.curselection())).split(":")[0]) if vb_GreekFlag.curselection() else 0
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        
        hwkappa = float(v_hwkappa.get()) if len(str(v_hwkappa.get())) > 0 else 0.001
        hwvolterm = [1.0]
        hwkappa2 = float(v_hwkappa2.get()) if len(str(v_hwkappa2.get())) > 0 else 0.001
        hwvolterm2 = [1.0]
        hwfactorcorr = float(v_hwfactorcorr.get()) if len(str(v_hwfactorcorr.get())) > 0 else -0.001
        
        if len(str(v_hwvol.get())) > 0 : 
            if '(' in str(v_hwvol.get()) or ')' in str(v_hwvol.get()) : 
                volstr = str(v_hwvol.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol.get()) or ']' in str(v_hwvol.get()) :
                volstr = str(v_hwvol.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol.get()).split(',')
            hwvol = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol = [0.001]

        if len(str(v_hwvol2.get())) > 0 : 
            if '(' in str(v_hwvol2.get()) or ')' in str(v_hwvol2.get()) : 
                volstr = str(v_hwvol2.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol2.get()) or ']' in str(v_hwvol2.get()) :
                volstr = str(v_hwvol2.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol2.get()).split(',')
            hwvol2 = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol2 = [0.001]

        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0
        L2FirstFixing = float(v_L2FirstFixing.get())/100 if str(v_L2FirstFixing.get()) else 0.0
        
        L1_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(365)]
        L1_FixingHistoryRate = [L1FirstFixing] * len(L1_FixingHistoryDate)    
        L2_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(366)] 
        L2_FixingHistoryRate = [L2FirstFixing] * len(L2_FixingHistoryDate)    
        OptionFixDate, OptionPayDate = Generate_OptionDate(FirstOptPayDate, SwapMaturity, NYearBetweenOptionPay, NBDateBetweenOptionFixToPay, MaxNumOpt, ModifiedFollow = 0)
        if GreekFlag == 0 : 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag = (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            GIRRDelta = 0
            GIRRCurvature = 0
            GIRRVega = 0
            
        else : 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag = (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            Result = Pricing_IRCallableSwap_HWFDM_Greek(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = False, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread,
                    GreekFlag = GreekFlag)
            
            DeltaGreek = pd.Series(Result["PV01"], index = CurveTerm1).reset_index()
            DeltaGreek.columns = ["PV01Term","PV01"]
            GIRRDelta = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(DeltaGreek, "PV01Term","PV01"), 4)
            Cvup = list(np.array(CurveRate1) + 0.012)
            Pu = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvup, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = False,
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            Cvdn = list(np.array(CurveRate1) - 0.012)
            Pd = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvdn, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = False,
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            GammaGreek = DeltaGreek.copy()
            GammaGreek.columns = ["Tenor","DeltaSensi"]
            GammaGreek["DeltaSensi"] = GammaGreek["DeltaSensi"] * 10000
            GammaGreek["Bucket"] ="KRW"
            GammaGreek["RiskWeight"] = GIRR_DeltaRiskWeight(list(DeltaGreek["PV01Term"].values), ["KRW"] * len(DeltaGreek), ["IRS"] * len(DeltaGreek))
            CVR_Plus = -(Pu - Result["Price"] - (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            CVR_Minus = -(Pd - Result["Price"] + (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            GIRRCurvature = max(abs(CVR_Plus), abs(CVR_Minus))
            T = DayCountAtoB(int(YYYYMMDD), SwapMaturity)/365
            if GreekFlag > 1 : 
                V = pd.Series(Result["VegaFRTB"][1:-1], Result["VegaTerm"][1:-1]).reset_index()
                V.columns = ["Tenor1","VegaSensi"]
                V["Tenor2"] = T - V["Tenor1"]
                V["Risk_Type"] = "Vega"
                V["Curve"] = UsedCurveName
                V["Risk_Class"] = "GIRR"
                V["Bucket"] = "KRW"
                GIRRVega = Calc_GIRRVega(V, SensitivityColumnName = "VegaSensi")["KB_M"].iloc[0]
            else : 
                GIRRVega = 0
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        resultframe = resultframe.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, resultframe.reset_index(), width = 100)
        if GreekFlag > 0 : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\n\nLeg1 Payoff: \n{L1ResultPayoff}\n\nLeg2 Payoff: \n{L2ResultPayoff}\n\nGIRR Delta: {np.round(GIRRDelta,4)}\n\nGIRR Curvature: {np.round(GIRRCurvature,4)}\n\nGIRR Vega: {np.round(GIRRVega,4)} ", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\n\nLeg1 Payoff: \n{L1ResultPayoff}\n\nLeg2 Payoff: \n{L2ResultPayoff}", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(rightright_frame, text = '실행', padx = 3, pady = 3, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 12).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 3, pady = 2)

    root.mainloop()
    MainFlag2 = 0#input("종료하시겠습니까? (Y/N)\n->")

    return MainFlag2, 1, 1, 1

def PricingIRStructuredSwapProgram2FDoublePhase(HolidayData, currdir) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                    namenotin = "vol",
                                                                    Comments = "IRS Pricing을 위한 커브 번호를 입력하시오.",
                                                                    MultiSelection = False,
                                                                    DefaultStringList=["IRS"])     
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    PriceDateDefault = int(YYYYMMDD)
    Curve = MyMarketDataList[0]
    UsedCurveName = Name[0].split("\\")[-1].split(".")[0]
    Curr = Name[0].split("\\")[-2].upper()
    CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
    CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
    CalibrationFlag = False
    defaultkappa = 0.01
    defaultkappa2 = 0.01        

    YYYY = int(YYYYMMDD) // 10000
    root = tk.Tk()
    root.title("Callable Swap 2F Pricer(Single Phase)")
    root.geometry("1560x787+5+5")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 929)
    vb_Phase2Flag = make_listvariable_interface(left_frame, 'Phase2UseFlag', ["0: False","1: Phase2 USE"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)
    v_Phase2StartDate = make_variable_interface(left_frame, 'Phase2StartDate\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 80000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'MaturityDate\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+21) * 10000 + 929)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = PriceDateDefault)
    vb_Holiday = make_listvariable_interface(left_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 4, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(center_frame, '연쿠폰지급수(Phase1)', ["0","1","2","4","6"], pady = 2, titlelable = True, titleName = "Leg1 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3)
    vb_L1_NumCpnOneYear_P2 = make_listvariable_interface(center_frame, '연쿠폰지급수(Phase2)', ["0","1","2","4","6"], pady = 2, listheight = 4, textfont = 10, defaultflag = True, defaultvalue=3)
    v_L1_FixedCpnRate_P1 = make_variable_interface(center_frame, '고정쿠폰(%)(Phase1)', bold = False, textfont = 11, pady = 2, defaultflag = True, defaultvalue =1.69)
    v_L1_FixedCpnRate_P2 = make_variable_interface(center_frame, '고정쿠폰(%)(Phase2)', bold = False, textfont = 10, pady = 2, defaultflag = True, defaultvalue =1.69)
    v_L1_RefSwapMaturity_T = make_variable_interface(center_frame, '변동금리 만기\n(3M-> 0.25, 5Y-> 5, \n5Y-1Y -> 5-1)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11)
    vb_L1_RefSwapNCPNOneYear_P1 = make_listvariable_interface(center_frame, '변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11)
    v_L1_RefRateMultiple_P1 = make_variable_interface(center_frame, '변동금리Multiple(Phase1)', bold = False, textfont = 11, pady = 2)
    v_L1_RefRateMultiple_P2 = make_variable_interface(center_frame, '변동금리Multiple(Phase2)', bold = False, textfont = 10, pady = 2)
    vb_L1_DayCount = make_listvariable_interface(center_frame, 'Leg1 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_L2_NumCpnOneYear_P1 = make_listvariable_interface(right_frame, '연쿠폰지급수(Phase1)', ["0","1","2","4","6"], pady = 2, titlelable = True, titleName = "Leg2 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue = 3)
    vb_L2_NumCpnOneYear_P2 = make_listvariable_interface(right_frame, '연쿠폰지급수(Phase2)', ["0","1","2","4","6"], pady = 2, listheight = 4, textfont = 10, defaultflag = True, defaultvalue = 3)
    v_L2_FixedCpnRate_P1 = make_variable_interface(right_frame, '고정쿠폰(%)(Phase1)', bold = False, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0.2)
    v_L2_FixedCpnRate_P2 = make_variable_interface(right_frame, '고정쿠폰(%)(Phase2)', bold = False, textfont = 10, pady = 2, defaultflag = True, defaultvalue = 0.2)
    v_L2_RefSwapMaturity_T = make_variable_interface(right_frame, '변동금리 만기\n(3M-> 0.25, 5Y-> 5, \n5Y-1Y -> 5-1)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11, defaultflag = True ,defaultvalue = '5 - 1')
    vb_L2_RefSwapNCPNOneYear_P1 = make_listvariable_interface(right_frame, '변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 2)
    v_L2_RefRateMultiple_P1 = make_variable_interface(right_frame, '변동금리Multiple(Phase1)', bold = False, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 5.0)
    v_L2_RefRateMultiple_P2 = make_variable_interface(right_frame, '변동금리Multiple(Phase2)', bold = False, textfont = 10, pady = 2, defaultflag = True, defaultvalue = 5.0)
    vb_L2_DayCount = make_listvariable_interface(right_frame, 'Leg2 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    rightright_frame = tk.Frame(root)
    rightright_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_OptionHolder = make_listvariable_interface(rightright_frame, 'OptionHolder', ["0: Leg1 Hold Option","1: Leg2 Hold Option"], titleName = "Option Information", titlelable= True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue= 0)
    v_FirstOptPayDate = make_variable_interface(rightright_frame, '첫 옵션행사일\n(지급일기준)', bold = False, textfont = 11, defaultflag = True, defaultvalue = (YYYY-6) * 10000 + 929)
    vb_NYearBetweenOptionPay = make_listvariable_interface(rightright_frame, '옵션행사간격', ["6M","12M","24M","36M","60M"], listheight = 5, textfont = 11, defaultflag = True, defaultvalue = 1)
    v_NBDateBetweenOptionFixToPay = make_variable_interface(rightright_frame, '옵션행사선언일과\n옵션지급일사이의\n영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 20)
    v_MaxNumOpt = make_variable_interface(rightright_frame, '최대옵션개수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0)
    v_L1FirstFixing = make_variable_interface(rightright_frame, 'Leg1)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_L2FirstFixing = make_variable_interface(rightright_frame, 'Leg2)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_GreekFlag = make_listvariable_interface(rightright_frame, 'Greek산출', ["0: Pricing만","1: Delta,Gamma","2: Delta,Gamma,Vega"], listheight = 3, textfont = 11)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(Result_frame, 'ZeroCurve(자동Load)', termratestr(CurveTerm1, CurveRate1), titleName = "MARKET DATA INFO", titlelable= True, listheight = 12, textfont = 10)
    v_hwkappa = make_variable_interface(Result_frame, 'Kappa', bold = False, textfont = 11, titleName = "\nHull White Params", titlelable = True, defaultflag = True, defaultvalue = defaultkappa)
    v_hwkappa2 = make_variable_interface(Result_frame, 'Kappa2', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaultkappa2)
    v_hwvol = make_variable_interface(Result_frame, 'Volatility1(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0.99)
    v_hwvol2 = make_variable_interface(Result_frame, 'Volatility2(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0.66)
    v_hwfactorcorr = make_variable_interface(Result_frame, 'Factor Corr(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = -0.1)
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)

    Result_frame2 = tk.Frame(root)
    Result_frame2.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]      
        Phase2Flag = int(str(vb_Phase2Flag.get(vb_Phase2Flag.curselection())).split(":")[0]) if vb_Phase2Flag.curselection() else 0            
        Phase2StartDate = int(v_Phase2StartDate.get()) if len(str(v_Phase2StartDate.get())) > 0 else (20200627 + 50000)  
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        L1_NumCpnOneYear_P2 = int(vb_L1_NumCpnOneYear_P2.get(vb_L1_NumCpnOneYear_P2.curselection())) if vb_L1_NumCpnOneYear_P2.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P1.get()) : 
                L1_FixedCpnRate_P1 = float(v_L1_FixedCpnRate_P1.get())/100
            else : 
                L1_FixedCpnRate_P1 = float(str(v_L1_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P1 = 0

        if len(str(v_L1_FixedCpnRate_P2.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P2.get()) : 
                L1_FixedCpnRate_P2 = float(v_L1_FixedCpnRate_P2.get())/100
            else : 
                L1_FixedCpnRate_P2 = float(str(v_L1_FixedCpnRate_P2.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P2 = 0
        
        L1_PowerSpreadFlag = 0
        if len(str(v_L1_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L1_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L1_RefSwapMaturity_T.get()).split("-")
                if 'm' in SplitedStr[0].lower() :
                    L1_RefSwapMaturity_T = float(SplitedStr[0].lower().split("m")[0])/12
                elif 'y' in SplitedStr[0].lower() : 
                    L1_RefSwapMaturity_T = float(SplitedStr[0].lower().split("y")[0]) 
                else : 
                    L1_RefSwapMaturity_T = float(SplitedStr[0]) 

                if 'm' in SplitedStr[1].lower() :
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("m")[0])/12
                elif 'y' in SplitedStr[1].lower() : 
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("y")[0]) 
                else : 
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1]) 
                L1_PowerSpreadFlag = 1
            else : 
                if 'm' in str(v_L1_RefSwapMaturity_T.get()).lower() : 
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L1_RefSwapMaturity_T.get()).lower() :
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L1_RefSwapMaturity_T = float(v_L1_RefSwapMaturity_T.get()) 
                L1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T
        else : 
            L1_RefSwapMaturity_T = 0.25
            L1_RefSwapMaturity_T_PowerSpread = 0.25
            
        L1_RefSwapNCPNOneYear_P1 = int(vb_L1_RefSwapNCPNOneYear_P1.get(vb_L1_RefSwapNCPNOneYear_P1.curselection())) if vb_L1_RefSwapNCPNOneYear_P1.curselection() else 4
        if L1_RefSwapMaturity_T == 0.25 : 
            L1_RefSwapNCPNOneYear_P1 = 4

        L1_RefRateMultiple_P1 = float(v_L1_RefRateMultiple_P1.get()) if len(str(v_L1_RefRateMultiple_P1.get())) > 0 else 0
        L1_RefRateMultiple_P2 = float(v_L1_RefRateMultiple_P2.get()) if len(str(v_L1_RefRateMultiple_P2.get())) > 0 else 0
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L1ResultPayoff = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff_P2 = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P2) + " + " +str(np.round(L1_FixedCpnRate_P2*100,4)) + "%"
        else : 
            L1ResultPayoff_P2 = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P2) + " + " +str(np.round(L1_FixedCpnRate_P2*100,4)) + "%"
        
        L2_NumCpnOneYear_P1 = int(vb_L2_NumCpnOneYear_P1.get(vb_L2_NumCpnOneYear_P1.curselection())) if vb_L2_NumCpnOneYear_P1.curselection() else 4
        L2_NumCpnOneYear_P2 = int(vb_L2_NumCpnOneYear_P2.get(vb_L2_NumCpnOneYear_P2.curselection())) if vb_L2_NumCpnOneYear_P2.curselection() else 4
        if len(str(v_L2_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P1.get()) : 
                L2_FixedCpnRate_P1 = float(v_L2_FixedCpnRate_P1.get())/100
            else : 
                L2_FixedCpnRate_P1 = float(str(v_L2_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P1 = 0

        if len(str(v_L2_FixedCpnRate_P2.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P2.get()) : 
                L2_FixedCpnRate_P2 = float(v_L2_FixedCpnRate_P2.get())/100
            else : 
                L2_FixedCpnRate_P2 = float(str(v_L2_FixedCpnRate_P2.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P2 = 0
        
        L2_PowerSpreadFlag = 0
        if len(str(v_L2_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L2_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L2_RefSwapMaturity_T.get()).split("-")
                if 'm' in SplitedStr[0].lower() :
                    L2_RefSwapMaturity_T = float(SplitedStr[0].lower().split("m")[0])/12
                elif 'y' in SplitedStr[0].lower() : 
                    L2_RefSwapMaturity_T = float(SplitedStr[0].lower().split("y")[0]) 
                else : 
                    L2_RefSwapMaturity_T = float(SplitedStr[0]) 

                if 'm' in SplitedStr[1].lower() :
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("m")[0])/12
                elif 'y' in SplitedStr[1].lower() : 
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("y")[0]) 
                else : 
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1]) 
                L2_PowerSpreadFlag = 1
            else : 
                if 'm' in str(v_L2_RefSwapMaturity_T.get()).lower() : 
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L2_RefSwapMaturity_T.get()).lower() :
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L2_RefSwapMaturity_T = float(v_L2_RefSwapMaturity_T.get()) 
                L2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T
        else : 
            L2_RefSwapMaturity_T = 0.25
            L2_RefSwapMaturity_T_PowerSpread = 0.25
            
        L2_RefSwapNCPNOneYear_P1 = int(vb_L2_RefSwapNCPNOneYear_P1.get(vb_L2_RefSwapNCPNOneYear_P1.curselection())) if vb_L2_RefSwapNCPNOneYear_P1.curselection() else 4
        if L2_RefSwapMaturity_T == 0.25 : 
            L2_RefSwapNCPNOneYear_P1 = 4
            
        L2_RefRateMultiple_P1 = float(v_L2_RefRateMultiple_P1.get()) if len(str(v_L2_RefRateMultiple_P1.get())) > 0 else 0
        L2_RefRateMultiple_P2 = float(v_L2_RefRateMultiple_P2.get()) if len(str(v_L2_RefRateMultiple_P2.get())) > 0 else 0
        L2_DayCount = int(str(vb_L2_DayCount.get(vb_L2_DayCount.curselection())).split(":")[0]) if vb_L2_DayCount.curselection() else (0 if L2_NumCpnOneYear_P1 != 0 else 3)
        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L2ResultPayoff = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"

        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff_P2 = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P2) + " + " +str(np.round(L2_FixedCpnRate_P2*100,4)) + "%"
        else : 
            L2ResultPayoff_P2 = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P2) + " + " +str(np.round(L2_FixedCpnRate_P2*100,4)) + "%"

        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        Holiday = str(vb_Holiday.get(vb_Holiday.curselection())).upper() if vb_Holiday.curselection() else "KRW"
        if 'KRW' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif "KRW" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else : 
            if Curr in HolidayData.columns : 
                HolidaysForSwap = HolidayData[Curr].unique().astype(np.int64)
            else : 
                HolidaysForSwap = []
                            
        OptionHolder = int(str(vb_OptionHolder.get(vb_OptionHolder.curselection())).split(":")[0]) if vb_OptionHolder.curselection() else 0    
        FirstOptPayDate = int(v_FirstOptPayDate.get()) if len(str(v_FirstOptPayDate.get())) > 0 else SwapEffectiveDate + 10000
        NYearBetweenOptionPay = float(str(vb_NYearBetweenOptionPay.get(vb_NYearBetweenOptionPay.curselection())).split("M")[0])/12 if vb_NYearBetweenOptionPay.curselection() else 1    
        MaxNumOpt = int(v_MaxNumOpt.get()) if len(str(v_MaxNumOpt.get())) > 0 else -1
        NBDateBetweenOptionFixToPay = int(v_NBDateBetweenOptionFixToPay.get()) if len(str(v_NBDateBetweenOptionFixToPay.get())) > 0 else 0
        
        GreekFlag = int(str(vb_GreekFlag.get(vb_GreekFlag.curselection())).split(":")[0]) if vb_GreekFlag.curselection() else 0
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        
        hwkappa = float(v_hwkappa.get()) if len(str(v_hwkappa.get())) > 0 else 0.001
        hwvolterm = [1.0]
        hwkappa2 = float(v_hwkappa2.get()) if len(str(v_hwkappa2.get())) > 0 else 0.001
        hwvolterm2 = [1.0]
        hwfactorcorr = float(v_hwfactorcorr.get()) if len(str(v_hwfactorcorr.get())) > 0 else -0.001
        
        if len(str(v_hwvol.get())) > 0 : 
            if '(' in str(v_hwvol.get()) or ')' in str(v_hwvol.get()) : 
                volstr = str(v_hwvol.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol.get()) or ']' in str(v_hwvol.get()) :
                volstr = str(v_hwvol.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol.get()).split(',')
            hwvol = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol = [0.001]

        if len(str(v_hwvol2.get())) > 0 : 
            if '(' in str(v_hwvol2.get()) or ')' in str(v_hwvol2.get()) : 
                volstr = str(v_hwvol2.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol2.get()) or ']' in str(v_hwvol2.get()) :
                volstr = str(v_hwvol2.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol2.get()).split(',')
            hwvol2 = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol2 = [0.001]

        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0
        L2FirstFixing = float(v_L2FirstFixing.get())/100 if str(v_L2FirstFixing.get()) else 0.0
        
        L1_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(365)]
        L1_FixingHistoryRate = [L1FirstFixing] * len(L1_FixingHistoryDate)    
        L2_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(366)] 
        L2_FixingHistoryRate = [L2FirstFixing] * len(L2_FixingHistoryDate)    
        OptionFixDate, OptionPayDate = Generate_OptionDate(FirstOptPayDate, SwapMaturity, NYearBetweenOptionPay, NBDateBetweenOptionFixToPay, MaxNumOpt, ModifiedFollow = 0)
        if GreekFlag == 0 : 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag = (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg1_Phase2 = L1_NumCpnOneYear_P2, Leg1_Phase2StartDate = Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2 = L1_RefRateMultiple_P2, Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,   
                    Leg2_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg2_Phase2 = L2_NumCpnOneYear_P2, Leg2_Phase2StartDate = Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2 = L2_RefRateMultiple_P2, Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,                    
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            GIRRDelta = 0
            GIRRCurvature = 0
            GIRRVega = 0
            
        else : 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag = (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg1_Phase2 = L1_NumCpnOneYear_P2, Leg1_Phase2StartDate = Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2 = L1_RefRateMultiple_P2, Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,   
                    Leg2_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg2_Phase2 = L2_NumCpnOneYear_P2, Leg2_Phase2StartDate = Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2 = L2_RefRateMultiple_P2, Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,                    
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            Result = Pricing_IRCallableSwap_HWFDM_Greek(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = False, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg1_Phase2 = L1_NumCpnOneYear_P2, Leg1_Phase2StartDate = Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2 = L1_RefRateMultiple_P2, Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,   
                    Leg2_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg2_Phase2 = L2_NumCpnOneYear_P2, Leg2_Phase2StartDate = Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2 = L2_RefRateMultiple_P2, Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,                    
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread,
                    GreekFlag = GreekFlag)
            
            DeltaGreek = pd.Series(Result["PV01"], index = CurveTerm1).reset_index()
            DeltaGreek.columns = ["PV01Term","PV01"]
            GIRRDelta = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(DeltaGreek, "PV01Term","PV01"), 4)
            Cvup = list(np.array(CurveRate1) + 0.012)
            Pu = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvup, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = False,
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg1_Phase2 = L1_NumCpnOneYear_P2, Leg1_Phase2StartDate = Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2 = L1_RefRateMultiple_P2, Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,   
                    Leg2_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg2_Phase2 = L2_NumCpnOneYear_P2, Leg2_Phase2StartDate = Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2 = L2_RefRateMultiple_P2, Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,                    
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            Cvdn = list(np.array(CurveRate1) - 0.012)
            Pd = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvdn, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = False,
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg1_Phase2 = L1_NumCpnOneYear_P2, Leg1_Phase2StartDate = Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2 = L1_RefRateMultiple_P2, Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,   
                    Leg2_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg2_Phase2 = L2_NumCpnOneYear_P2, Leg2_Phase2StartDate = Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2 = L2_RefRateMultiple_P2, Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,                    
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            GammaGreek = DeltaGreek.copy()
            GammaGreek.columns = ["Tenor","DeltaSensi"]
            GammaGreek["DeltaSensi"] = GammaGreek["DeltaSensi"] * 10000
            GammaGreek["Bucket"] ="KRW"
            GammaGreek["RiskWeight"] = GIRR_DeltaRiskWeight(list(DeltaGreek["PV01Term"].values), ["KRW"] * len(DeltaGreek), ["IRS"] * len(DeltaGreek))
            CVR_Plus = -(Pu - Result["Price"] - (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            CVR_Minus = -(Pd - Result["Price"] + (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            GIRRCurvature = max(abs(CVR_Plus), abs(CVR_Minus))
            T = DayCountAtoB(int(YYYYMMDD), SwapMaturity)/365
            if GreekFlag > 1 : 
                V = pd.Series(Result["VegaFRTB"][1:-1], Result["VegaTerm"][1:-1]).reset_index()
                V.columns = ["Tenor1","VegaSensi"]
                V["Tenor2"] = T - V["Tenor1"]
                V["Risk_Type"] = "Vega"
                V["Curve"] = UsedCurveName
                V["Risk_Class"] = "GIRR"
                V["Bucket"] = "KRW"
                GIRRVega = Calc_GIRRVega(V, SensitivityColumnName = "VegaSensi")["KB_M"].iloc[0]
            else : 
                GIRRVega = 0
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        resultframe = resultframe.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, resultframe.reset_index(), width = 100)
        if GreekFlag > 0 : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\n\nLeg1 Payoff: \n{L1ResultPayoff} (Ph1)\n{L1ResultPayoff_P2} (Ph2)\nLeg2 Payoff: \n{L2ResultPayoff} (Ph1)\n{L2ResultPayoff_P2} (Ph2)\nGIRR Delta: {np.round(GIRRDelta,4)}\nGIRR Curvature: {np.round(GIRRCurvature,4)}\nGIRR Vega: {np.round(GIRRVega,4)} ", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\n\nLeg1 Payoff: \n{L1ResultPayoff} (Ph1)\n{L1ResultPayoff_P2} (Ph2)\nLeg2 Payoff: \n{L2ResultPayoff} (Ph1)\n{L2ResultPayoff_P2} (Ph2)", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 3, pady = 3, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 12).pack()
    output_label = tk.Label(Result_frame2, text = "", anchor = "n")
    output_label.pack(padx = 3, pady = 2)

    root.mainloop()
    MainFlag2 = 0#input("종료하시겠습니까? (Y/N)\n->")

    return MainFlag2, 1, 1, 1

#############################################################################################################
#TK GUI Tool
def make_variable_interface(frame, VariableName, textfont = 12, anchor = 'w', padx = 5, pady = 2, bold = False, titlelable = False, titleName = "", defaultflag = False, defaultvalue = None) : 
    
    myfont = ("맑은 고딕", textfont) if bold == False else ("맑은 고딕", textfont, 'bold')
    if titlelable == True : 
        tk.Label(frame, text = titleName, font = ("맑은 고딕", textfont, 'bold')).pack(anchor = anchor, padx = padx, pady = pady)    
        
    tk.Label(frame, text = VariableName, font = myfont).pack(anchor = anchor, padx = padx, pady = pady)    
    entry = tk.Entry(frame)
    if defaultflag == True : 
        entry.insert(0, defaultvalue)
    entry.pack(anchor = anchor, padx = padx, pady = pady)
    return entry

def make_listvariable_interface(frame, VariableName, MyList, listheight = 5,textfont = 12, anchor = 'w', padx = 5, pady = 2, bold = False, titlelable = False, titleName = "", defaultflag = False, defaultvalue = 0, width = 20, DefaultStringList = []) : 
    
    myfont = ("맑은 고딕", textfont) if bold == False else ("맑은 고딕", textfont)
    if titlelable == True : 
        tk.Label(frame, text = titleName, font = ("맑은 고딕", textfont, 'bold')).pack(anchor = anchor, padx = padx, pady = pady)    
    
    tk.Label(frame, text = VariableName, font = myfont).pack(anchor = anchor, padx = padx, pady = pady)    
    listbox = tk.Listbox(frame, height = listheight, exportselection = False, width = width)
    for item in MyList : 
        if "|" not in item : 
            listbox.insert(tk.END, str(item))
        else : 
            mystr = item.split("|")
            mystr1 = mystr[0]
            mystr2 = mystr[1]
            lenmystr1 = len(mystr1)
            lenmystr2 = len(mystr2)
            needstradd1 = max(0, 8 - lenmystr1)
            needstradd2 = max(0, 8 - lenmystr2)
            MyString1 = mystr1 + (" " * needstradd1)
            MyString2 = mystr2 + (" " * needstradd2)
            listbox.insert(tk.END, str(MyString1 + " | " + MyString2))            
    
    listbox.pack(anchor = anchor, padx = padx, pady = pady)
    if defaultflag == True and len(DefaultStringList) == 0: 
        listbox.selection_set(defaultvalue)
    elif defaultflag == True and len(DefaultStringList) > 0 : 
        TempList = []
        for i in range(len(DefaultStringList)) : 
            targetinstring = DefaultStringList[i]
            if ',' not in targetinstring : 
                for j in range(len(MyList)) : 
                    TotalString = MyList[j]
                    if targetinstring.lower() in TotalString.lower() : 
                        listbox.selection_set(j)
                        TempList.append(j)
                        break             
    return listbox

def make_multilistvariable_interface(frame, VariableName, MyList, listheight = 5,textfont = 12, anchor = 'w', padx = 5, pady = 2, bold = False, titlelable = False, titleName = "", defaultflag = False, defaultvalue = 0, width = 20, DefaultStringList = []) : 
    n = len(MyList)
    myfont = ("맑은 고딕", textfont) if bold == False else ("맑은 고딕", textfont)
    if titlelable == True : 
        tk.Label(frame, text = titleName, font = ("맑은 고딕", textfont, 'bold')).pack(anchor = anchor, padx = padx, pady = pady)    
    
    tk.Label(frame, text = VariableName, font = myfont).pack(anchor = anchor, padx = padx, pady = pady)    
    listbox = tk.Listbox(frame, selectmode="multiple", height = listheight, exportselection = False, width = width)
    for item in MyList : 
        if "|" not in item : 
            listbox.insert(tk.END, str(item))
        else : 
            mystr = item.split("|")
            mystr1 = mystr[0]
            mystr2 = mystr[1]
            lenmystr1 = len(mystr1)
            lenmystr2 = len(mystr2)
            needstradd1 = max(0, 8 - lenmystr1)
            needstradd2 = max(0, 8 - lenmystr2)
            MyString1 = mystr1 + (" " * needstradd1)
            MyString2 = mystr2 + (" " * needstradd2)
            listbox.insert(tk.END, str(MyString1 + " | " + MyString2))            
    
    listbox.pack(anchor = anchor, padx = padx, pady = pady)
    if defaultflag == True and '[' not in str(defaultvalue) and len(DefaultStringList) == 0: 
        listbox.selection_set(defaultvalue)
    elif defaultflag == True and '[' in str(defaultvalue) and len(DefaultStringList) == 0:         
        for i in defaultvalue : 
            if i < 0 : 
                listbox.selection_set(n + i)
            else : 
                listbox.selection_set(i)
    elif defaultflag == True and len(DefaultStringList) > 0 : 
        TempList = []
        for i in range(len(DefaultStringList)) : 
            targetinstring = DefaultStringList[i]
            if ',' not in targetinstring : 
                for j in range(len(MyList)) : 
                    TotalString = MyList[j]
                    if targetinstring.lower() in TotalString.lower() : 
                        listbox.selection_set(j)
                        TempList.append(j)
                        break                        
            else : 
                targetinstring1 = targetinstring.split(",")[0].lower()
                targetinstring2 = targetinstring.split(",")[1].lower()
                for j in range(len(MyList)) : 
                    TotalString = MyList[j]
                    if targetinstring1 in TotalString.lower() and targetinstring2 in TotalString.lower() : 
                        listbox.selection_set(j)
                        TempList.append(j)
                        break                        
                
        if len(TempList) < len(DefaultStringList) and '[' not in str(defaultvalue): 
            listbox.selection_set(defaultvalue) 
        elif len(TempList) < len(DefaultStringList) and '[' in str(defaultvalue): 
            listbox.selection_set(defaultvalue[0] if defaultvalue[0] not in TempList else defaultvalue[1])                               
            
    return listbox

def termratestr(term, rate) : 
    return [str(np.round(x,4)) + '|' + str(y) for x, y in zip(term, rate)]

def insert_dataframe_to_treeview(treeview, dataframe, width = 50):
    # 기존 컬럼과 데이터 제거
    treeview.delete(*treeview.get_children())
    treeview["columns"] = list(dataframe.columns)
    treeview["show"] = "headings"

    # 컬럼 헤더 설정
    for col in dataframe.columns:
        treeview.heading(col, text=col)
        treeview.column(col, width=width, anchor="center")  # 너비 설정 가능

    # 데이터 삽입
    for _, row in dataframe.iterrows():
        treeview.insert("", tk.END, values=list(row))
    return 1
    
    
##############################################################################################################
########################################### 여기까지 Pricing Module ###########################################
########################################### 여기부터 FRTB Module ##############################################  
##############################################################################################################


def Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01 ,col = "PV01Term", bpv = "PV01") : 
    GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
    GIRR_DeltaRfCorr = np.array([[1.000,0.970,0.914,0.811,0.719,0.566,0.400,0.400,0.400,0.400 ],
                                [0.970,1.000,0.970,0.914,0.861,0.763,0.566,0.419,0.400,0.400 ],
                                [0.914,0.970,1.000,0.970,0.942,0.887,0.763,0.657,0.566,0.419 ],
                                [0.811,0.914,0.970,1.000,0.985,0.956,0.887,0.823,0.763,0.657 ],
                                [0.719,0.861,0.942,0.985,1.000,0.980,0.932,0.887,0.844,0.763 ],
                                [0.566,0.763,0.887,0.956,0.980,1.000,0.970,0.942,0.914,0.861 ],
                                [0.400,0.566,0.763,0.887,0.932,0.970,1.000,0.985,0.970,0.942 ],
                                [0.400,0.419,0.657,0.823,0.887,0.942,0.985,1.000,0.990,0.970 ],
                                [0.400,0.400,0.566,0.763,0.844,0.914,0.970,0.990,1.000,0.985 ],
                                [0.400,0.400,0.419,0.657,0.763,0.861,0.942,0.970,0.985,1.000 ]])    
    if len(PV01) == 0 : 
        return 0
    Data = MapGIRRDeltaGreeks(PV01.set_index(col)[bpv], GIRR_DeltaRiskFactor).reset_index()
    Data.columns = ["Tenor","Delta_Sensi"]
    Data["Delta_Sensi"] = Data["Delta_Sensi"] * 10000
    Data["Risk_Class"] = "GIRR"
    Data["Risk_Type"] = "Delta"
    Data["Curve"] = "IRS"
    Data["Type"] = "Rate"
    Data["Bucket"] = "KRW"
    Risk = Calc_GIRRDelta(Data, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, "Delta_Sensi").iloc[0]["KB_M"]
    return Risk

def Calc_CSRDeltaNotCorrelated_FromGreeks(PV01 ,col = "PV01Term", bpv = "PV01", bucket = 0) : 
    CSR_RiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)   
    Data = MapCSRDeltaGreeks(PV01.set_index(col)[bpv], CSR_RiskFactor).reset_index()
    Data.columns = ["Tenor","Delta_Sensi"]
    Data["Delta_Sensi"] = Data["Delta_Sensi"] * 10000
    Data["Risk_Class"] = "GIRR"
    Data["Risk_Type"] = "Delta"
    Data["Curve"] = "Bond"
    Data["Issuer"] = "TempIssuer"
    Data["Bucket"] = "KRW"    
    if bucket == 0 : 
        B = input("\n 채권 버킷을 입력하시오(숫자)\n버킷1:정부,중앙은행\n버킷2:지방정부,공공행정\n버킷3:금융\n버킷4:원자재\n버킷5:소비재\n버킷6:기술통신\n->")
    else : 
        B = str(bucket)
        
    if len(str(B)) == 0 or B == '0': 
        B = 1
    else : 
        B = int(B)
    Data["Bucket"] = B
    CSR_DeltaNonSecuritizedBucketCorr = np.array([[1.000,0.750,0.100,0.200,0.250,0.200,0.150,0.100,0.000,0.450,0.450],
                                            [0.750,1.000,0.050,0.150,0.200,0.150,0.100,0.100,0.000,0.450,0.450 ],
                                            [0.100,0.050,1.000,0.050,0.150,0.200,0.050,0.200,0.000,0.450,0.450 ],
                                            [0.200,0.150,0.050,1.000,0.200,0.250,0.050,0.050,0.000,0.450,0.450 ],
                                            [0.250,0.200,0.150,0.200,1.000,0.250,0.050,0.150,0.000,0.450,0.450 ],
                                            [0.200,0.150,0.200,0.250,0.250,1.000,0.050,0.200,0.000,0.450,0.450 ],
                                            [0.150,0.100,0.050,0.050,0.050,0.050,1.000,0.050,0.000,0.450,0.450 ],
                                            [0.100,0.100,0.200,0.050,0.150,0.200,0.050,1.000,0.000,0.450,0.450 ],
                                            [0.000,0.000,0.000,0.000,0.000,0.000,0.000,0.000,1.000,0.000,0.000 ],
                                            [0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.000,1.000,0.750 ],
                                            [0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.450,0.000,0.750,1.000 ]])
    
    Risk = Calc_CSRDelta(Data, CSR_DeltaNonSecuritizedBucketCorr, "Delta_Sensi").iloc[0]["KB_M"]
    return Risk, str(B)

def MapProductType(ProductType, DomesticEstCurveRate = [], USDEstCurveRate = []) : 
    x = str(ProductType).lower()
    if 'dp' in x or 'dg' in x : 
        return 0
    elif 'sp' in x or 'swappoint' in x: 
        return 2
    elif 'sw' in x : 
        return 1
    elif 'bs' in x : 
        return 3 
    elif len(DomesticEstCurveRate) > 0 and len(USDEstCurveRate) > 0 : 
        return 4 
    else : 
        return 5
    
def CalcZeroRateFromSwapPoint(rf, T, S, SwapPoint, SwapPointUnit) : 
    F = S + SwapPoint /SwapPointUnit
    rd = rf + 1.0 / T * np.log(F / S)
    return rd

def Calc_ZeroRate_FromDiscFactor(PriceDate, StartDate, EndDate, MarketQuote, DayCountFlag, ZeroTerm, ZeroRate) : 
    if (StartDate < 19000101) : 
        StartDate = ExcelDateToYYYYMMDD(StartDate)
    if (EndDate < 19000101) : 
        EndDate = ExcelDateToYYYYMMDD(EndDate)
    
    if (PriceDate == StartDate) : 
        r = 365/(DayCountAtoB(StartDate, EndDate)) * np.log(1.0 + MarketQuote * DayCountFractionAtoB(StartDate, EndDate, DayCountFlag))
    else : 
        t0 = DayCountAtoB(PriceDate, StartDate)/365
        DF_Start_To_EndDate = 1.0/(1.0 + MarketQuote * DayCountFractionAtoB(StartDate, EndDate, DayCountFlag))
        r0 = Linterp(ZeroTerm, ZeroRate, t0)
        DF_0_To_EndDate = np.exp(-r0 * t0) * DF_Start_To_EndDate
        r = -365.0/(DayCountAtoB(PriceDate, EndDate)) * np.log(DF_0_To_EndDate)
    return r

def MonthStringConvert(x) : 
    if len(str(x)) == 9 and '-' in str(x): 
        XX = str(x).lower()
        DD = XX[:2]
        YYYY = ('20' + XX[-2:])[-4:]
        if '-jan-' in XX : 
            return int(YYYY + '01' + DD)
        elif '-feb-' in XX : 
            return int(YYYY + '02' + DD)
        elif '-mar-' in XX : 
            return int(YYYY + '03' + DD)
        elif '-apr-' in XX : 
            return int(YYYY + '04' + DD)
        elif '-may-' in XX : 
            return int(YYYY + '05' + DD)
        elif '-jun-' in XX : 
            return int(YYYY + '06' + DD)
        elif '-jul-' in XX : 
            return int(YYYY + '07' + DD)
        elif '-aug-' in XX : 
            return int(YYYY + '08' + DD)
        elif '-sep-' in XX : 
            return int(YYYY + '09' + DD)
        elif '-oct-' in XX : 
            return int(YYYY + '10' + DD)
        elif '-nov-' in XX : 
            return int(YYYY + '11' + DD)
        elif '-dec-' in XX : 
            return int(YYYY + '12' + DD)
        else : 
            return x    
    else : 
        return x    

def ReadCSV(filedir, ParseMonthStringToInteger = False) :    
    try : 
        chunk_list = pd.read_csv(filedir, chunksize = 5000, engine = 'python')
    except UnicodeDecodeError : 
        try : 
            chunk_list = pd.read_csv(filedir, chunksize = 5000, engine = 'python', encoding = 'cp949')
        except UnicodeDecodeError : 
            chunk_list = pd.read_csv(filedir, chunksize = 5000, engine = 'python', encoding = 'utf-8')            
    
    df = pd.DataFrame()
    for i in chunk_list : 
        df = pd.concat([df,i],axis = 0)
    if ParseMonthStringToInteger == True : 
        return df.applymap(MonthStringConvert)
    else : 
        return df

def PreProcessingKDBData(KDBData, dataformat = 'Combined') : 
    '''
    Description : Preprocessing KDB FRTB Raw csvfile
    설명 : KDB FRTB 포지션별 개별 민감도 조회화면 csv 전처리
    Variables : KDBData - dataframe from csv
    return 전처리된 Preprocessed DataFrame
    '''
    Data = KDBData.rename(columns = {"부점명":"Depart","포트폴리오":"Portfolio","리스크군":"Risk_Class",
                                     "버킷":"Bucket","리스크요소1":"RiskFactor1","리스크요소2":"RiskFactor2",
                                     "리스크요소3":"RiskFactor3","델타민감도":"Delta_Sensi","베가민감도":"Vega_Sensi",
                                     "상향커버쳐":"CVR_Plus","하향커버쳐":"CVR_Minus","뮤렉스ID":"MurexID",
                                     "민감도유형":"Risk_Type"})
    DataCSR = Data[Data["Risk_Class"].isin(["CSR","신용스프레드","신용스프레드(CSR)"])]
    DataGIRR = Data[Data["Risk_Class"].isin(["GIRR","일반금리","일반금리(GIRR)"])]
    DataFXR = Data[Data["Risk_Class"].isin(["FXR","외환","외환(FXR)","외환리스크","외환리스크(FXR)"])]
    DataEQR = Data[Data["Risk_Class"].isin(["EQR","주식","주식(EQR)","주식리스크","주식리스크(EQR)"])]
    DataCOMR = Data[Data["Risk_Class"].isin(["COMR","일반상품","일반상품리스크","일반상품(COMR)","일반상품리스크(COMR)"])]
    if len(DataCSR) > 0 :
        DataCSR["Bucket"] = DataCSR["Bucket"].apply(lambda x : int(x.split("]")[0][-2:]) if (("매핑되지 않음" not in x) and ("매핑 필요" not in x)) else -1)
        DataCSR = DataCSR.rename(columns = {"RiskFactor2":"Curve","RiskFactor3":"Tenor","RiskFactor1":"Issuer"})
        DataCSRDelta = DataCSR[DataCSR["Risk_Type"].isin(["Delta","델타","델타(Delta)"])]
        DataCSRNonDelta = DataCSR.loc[DataCSR.index.difference(DataCSRDelta.index)]
        DataCSRDelta["Delta_Sensi"] = DataCSRDelta["Delta_Sensi"].apply(lambda x : x if ',' not in str(x) else str(x).replace(",",""))
        DataCSRDelta["Delta_Sensi"] = DataCSRDelta["Delta_Sensi"].astype(np.float64) * 10000
        DataCSR = pd.concat([DataCSRDelta, DataCSRNonDelta],axis = 0)
    if len(DataGIRR) > 0 : 
        DataGIRRVega = DataGIRR[DataGIRR["Risk_Type"].isin(["베가","Vega","베가(Vega)"])]
        DataGIRR_NonVega = DataGIRR.loc[DataGIRR.index.difference(DataGIRRVega.index)]
        DataGIRR_NonVega = DataGIRR_NonVega.rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Type"})
        DataGIRRVega = DataGIRRVega.rename(columns = {"RiskFactor3":"Curve","RiskFactor1":"Tenor1","RiskFactor2":"Tenor2"})        
        DataGIRR = pd.concat([DataGIRRVega, DataGIRR_NonVega],axis = 0)        
        DataGIRR["Delta_Sensi"] = DataGIRR["Delta_Sensi"].apply(lambda x : x if ',' not in str(x) else str(x).replace(",",""))
        DataGIRR["Delta_Sensi"] = DataGIRR["Delta_Sensi"].astype(np.float64) * 10000                
    if len(DataEQR) > 0 : 
        DataEQR["Bucket"] = DataEQR["Bucket"].apply(lambda x : int(x.split("]")[0][-2:]) if (("매핑되지 않음" not in x) and ("매핑 필요" not in x)) else -1)
        DataEQRDelta = DataEQR[DataEQR["Risk_Type"].isin(["Delta","델타","델타(Delta)"])]
        DataEQRVega = DataEQR[DataEQR["Risk_Type"].isin(["베가","Vega","베가(Vega)"])]
        DataEQRCurvature = DataEQR[DataEQR["Risk_Type"].isin(["Curvature","커버쳐","커버쳐(Curvature)"])]
        DataEQRDelta = DataEQRDelta.rename(columns = {"RiskFactor2":"StockName","RiskFactor1":"Type","RiskFactor3":"TempRiskFactor"})
        DataEQRCurvature = DataEQRCurvature.rename(columns = {"RiskFactor1":"StockName","RiskFactor2":"Type","RiskFactor3":"TempRiskFactor"})        
        DataEQRVega = DataEQRVega.rename(columns = {"RiskFactor2":"StockName","RiskFactor1":"Tenor","RiskFactor3":"TempRiskFactor"})
        DataEQR = pd.concat([DataEQRDelta,DataEQRCurvature, DataEQRVega],axis=0)
        DataEQR["Delta_Sensi"] = DataEQR["Delta_Sensi"].astype(np.float64) * 100                
    if len(DataFXR) > 0 : 
        DataFXR["Curve"] = DataFXR["RiskFactor1"]
        DataFXR["Tenor"] = DataFXR["RiskFactor1"]
        FXRDelta = DataFXR[DataFXR["Risk_Type"].isin(["Delta","델타","델타(Delta)"])]
        FXRDelta["Bucket"] = FXRDelta["Curve"]
        FXRCurvature = DataFXR[DataFXR["Risk_Type"].isin(["Curvature","커버쳐","커버쳐(Curvature)"])]
        FXRCurvature["Bucket"] = FXRCurvature["Curve"]
        FXRVega = DataFXR[DataFXR["Risk_Type"].isin(["Vega","베가","베가(Vega)"])]
        FXRVega["Bucket"] = FXRVega["Bucket"].fillna('nan')
        DataFXR = pd.concat([FXRDelta, FXRCurvature, FXRVega],axis = 0)
    if len(DataCOMR) > 0 :        
        DataCOMR["Bucket"] = DataCOMR["Bucket"].apply(lambda x : int(x.split("]")[0][-2:]) if (("매핑되지 않음" not in x) and ("매핑 필요" not in x)) else -1)
        DataCOMRDelta = DataCOMR[DataCOMR["Risk_Type"].isin(["Delta","델타","델타(Delta)"])]
        DataCOMRCurvature = DataCOMR[DataCOMR["Risk_Type"].isin(["Curvature","커버쳐","커버쳐(Curvature)"])]
        DataCOMRVega = DataCOMR[DataCOMR["Risk_Type"].isin(["Vega","베가","베가(Vega)"])]
        DataCOMRDelta = DataCOMRDelta.rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Tenor","RiskFactor3":"Delivery"})
        DataCOMRCurvature = DataCOMRCurvature.rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Delivery","RiskFactor3":"TempRiskFactor3"})
        DataCOMRVega = DataCOMRVega.rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Tenor","RiskFactor3":"Delivery"})
        DataCOMRVega["Tenor"].apply(lambda x : str(x).lower().split("y")[0] if 'y' in str(x).lower() else (str(float(str(x).lower().split("m")[0])/12) if 'm' in str(x).lower() else x))
        
        DataCOMR = pd.concat([DataCOMRDelta, DataCOMRCurvature, DataCOMRVega],axis = 0)
    if dataformat == 'Combined' : 
        return pd.concat([DataCSR,DataGIRR,DataFXR,DataEQR,DataCOMR],axis = 0)
    else : 
        return DataCSR,pd.DataFrame([]), pd.DataFrame([]), DataGIRR,DataFXR,DataEQR,DataCOMR
    
def PreProcessingMyData(RAWData) : 
    CSR = RAWData[RAWData["Risk_Class"].isin(["CSR","csr","신용스프레드","신용스프레드(CSR)"]) ]
    CSR_Delta = CSR[CSR["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    #CSR_Delta["Delta_Sensi" if "Delta_Sensi" in CSR_Delta.columns else "Delta"] = CSR_Delta["Delta_Sensi" if "Delta_Sensi" in CSR_Delta.columns else "Delta"] * 10000

    CSR_Curvature = CSR[CSR["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    CSR_Vega = CSR[CSR["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    Result_CSR = pd.concat([CSR_Delta, CSR_Curvature, CSR_Vega],axis = 0)
    
    CSR_SecuritizedNonCTP = RAWData[RAWData["Risk_Class"].isin(["CSR Securitized Non CTP","유동화(CTP 제외)", "CSR 유동화(CTP 제외)", "신용스프레드 유동화(CTP 제외)"]) ]
    CSR_SecuritizedNonCTPDelta = CSR_SecuritizedNonCTP[CSR_SecuritizedNonCTP["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Tranche"})
    #CSR_SecuritizedNonCTPDelta["Delta_Sensi" if "Delta_Sensi" in CSR_SecuritizedNonCTPDelta.columns else "Delta"] = CSR_SecuritizedNonCTPDelta["Delta_Sensi" if "Delta_Sensi" in CSR_SecuritizedNonCTPDelta.columns else "Delta"] * 10000
    CSR_SecuritizedNonCTPCurvature = CSR_SecuritizedNonCTP[CSR_SecuritizedNonCTP["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Tranche"})
    CSR_SecuritizedNonCTPVega = CSR_SecuritizedNonCTP[CSR_SecuritizedNonCTP["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Tranche"})
    Result_CSR_SecuritizedNonCTP = pd.concat([CSR_SecuritizedNonCTPDelta, CSR_SecuritizedNonCTPCurvature, CSR_SecuritizedNonCTPVega],axis = 0)

    CSR_CTP = RAWData[RAWData["Risk_Class"].isin(["CSR CTP","csr ctp","CSR 유동화(CTP)","신용스프레드 유동화(CTP)"]) ]
    CSR_CTP_Delta = CSR_CTP[CSR_CTP["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    CSR_CTP_Curvature = CSR_CTP[CSR_CTP["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    CSR_CTP_Vega = CSR_CTP[CSR_CTP["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    Result_CSR_CTP = pd.concat([CSR_CTP_Delta, CSR_CTP_Curvature, CSR_CTP_Vega],axis = 0)

    GIRR = RAWData[RAWData["Risk_Class"].isin(["GIRR","일반금리","일반금리(GIRR)"])]
    GIRR_Delta = GIRR[GIRR["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Type"})
    #GIRR_Delta["Delta_Sensi" if "Delta_Sensi" in GIRR_Delta.columns else "Delta"] = GIRR_Delta["Delta_Sensi" if "Delta_Sensi" in GIRR_Delta.columns else "Delta"] * 10000
    GIRR_Curvature = GIRR[GIRR["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Type"})
    GIRR_Vega = GIRR[GIRR["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor1","RiskFactor3":"Tenor2"})
    Result_GIRR = pd.concat([GIRR_Delta, GIRR_Curvature, GIRR_Vega],axis = 0)

    FXR = RAWData[RAWData["Risk_Class"].isin(["FXR","외환","외환(FXR)","외환리스크","외환리스크(FXR)"])]
    FXR_Delta = FXR[FXR["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Type"})
    FXR_Curvature = FXR[FXR["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Type"})
    FXR_Vega = FXR[FXR["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Temp_RiskFactor"})
    Result_FXR = pd.concat([FXR_Delta, FXR_Curvature, FXR_Vega],axis = 0)

    EQR = RAWData[RAWData["Risk_Class"].isin(["EQR","주식","주식(EQR)","주식리스크","주식리스크(EQR)"])]
    EQR_Delta = EQR[EQR["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Type","RiskFactor2":"StockName","RiskFactor3":"Temp_RiskFactor"})
    EQR_Curvature = EQR[EQR["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Type","RiskFactor2":"StockName","RiskFactor3":"Temp_RiskFactor"})
    EQR_Vega = EQR[EQR["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Type","RiskFactor2":"Tenor","RiskFactor3":"StockName"})
    Result_EQR = pd.concat([EQR_Delta, EQR_Curvature, EQR_Vega],axis = 0)

    COMR = RAWData[RAWData["Risk_Class"].isin(["COMR","일반상품","일반상품리스크","일반상품(COMR)","일반상품리스크(EQR)"])]
    COMR_Delta = COMR[COMR["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Tenor","RiskFactor3":"Delivery"})
    COMR_Curvature = COMR[COMR["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Tenor","RiskFactor3":"Delivery"})
    COMR_Vega = COMR[COMR["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Underlying","RiskFactor2":"Tenor","RiskFactor3":"Delivery"})
    Result_COMR = pd.concat([COMR_Delta, COMR_Curvature, COMR_Vega],axis = 0)
    
    DRC = RAWData[RAWData["Risk_Class"].isin(["DRC","부도리스크","부도리스크(DRC)"])]
    DRC = DRC.rename(columns = {"RiskFactor1" : "Rating", "RiskFactor2":"Issuer"})
    RRAO = RAWData[RAWData["Risk_Class"].isin(["RRAO","잔여리스크","잔여리스크(RRAO)"])]
    
    return Result_CSR, Result_CSR_SecuritizedNonCTP, Result_CSR_CTP, Result_GIRR, Result_FXR, Result_EQR, Result_COMR, DRC, RRAO

def PivotSensiByRiskFactor(Data, RiskFactorList, CurvatureFlag = 0) : 
    Data = Data.copy()
    for rf in RiskFactorList : 
        Data[rf] = Data[rf].fillna("NaN")
        
    if CurvatureFlag == 0 : 
        Groupped = Data.groupby(RiskFactorList)["WeightedSensi"].sum().reset_index()
        Others = Data.groupby(RiskFactorList).first().reset_index()[Data.columns.difference(list(RiskFactorList) + ["WeightedSensi"])]
        MyData =  pd.concat([Groupped, Others], axis = 1)
        MyData2 = MyData[(MyData["WeightedSensi"]> 0.01) | (MyData["WeightedSensi"]< -0.01) ]
    else : 
        Groupped1 = Data.groupby(RiskFactorList)["CVR_Plus"].sum()
        Groupped2 = Data.groupby(RiskFactorList)["CVR_Minus"].sum()
        Groupped = pd.concat([Groupped1, Groupped2],axis= 1).reset_index()
        Others = Data.groupby(RiskFactorList).first().reset_index()[Data.columns.difference(list(RiskFactorList) + ["CVR_Plus","CVR_Minus"])]
        MyData =  pd.concat([Groupped, Others], axis = 1)
        MyData2 = MyData[(MyData["CVR_Plus"]> 0.01) | (MyData["CVR_Plus"]< -0.01) | (MyData["CVR_Minus"]> 0.01) | (MyData["CVR_Minus"]< -0.01) ]
    return MyData2

def Calc_Kb_DeltaVega(WS, rho, median0up1dn2) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 44.다
    Description : Calculate Each Bucket RiskCharge(Kb) of Delta and Vega
    
    Variables :
    WS - Weighted Sensi 1d array
    rho - Sensi Corr 2d array
    median0up1dn2 - Correlation Scenario Flag (0: median, 1: up, 2: Dn)

    example : 
        WS = np.array([-1.112, -1.21, -9.112])
        rho = np.array([[1.0, 0.65, 0.5], [0.65, 1.0, 0.3], [0.5, 0.3, 1]])
        Calc_Kb_DeltaVega(WS, rho, 1) 
        -> 8.9011389
    '''
    n = len(WS)
    WSArray = np.zeros(n)
    rhoArray =np.zeros((n,n))
    for i in range(n) : 
        WSArray[i] = WS[i]
        for j in range(n) : 
            rhoArray[i][j] = rho[i][j]
    
    if median0up1dn2 == 1 : 
        for i in range(n) : 
            for j in range(n) : 
                rhoArray[i][j] = min(1, 1.25 * rhoArray[i][j])
    elif median0up1dn2 == 2 : 
        for i in range(n) : 
            for j in range(n) : 
                rhoArray[i][j] = max(2 * rhoArray[i][j] - 1, 0.75 * rhoArray[i][j])
            
    targetvalue = WSArray.dot(rhoArray).dot(WSArray)
    return np.sqrt(max(0, targetvalue))

#@jit('double(double[:],double[:],double[:,:], int64)', nopython = True)
def Calc_AggregatedDeltaVega(Kb, Sb, Corr, median0up1dn2) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 44.라
    Description : Calculate Bucket Aggregated RiskCharge of Delta and Vega    

    Variables :
    Kb - Kb 1d array by bucket
    Sb - Sb is groupby bucket and sum of each weighted sensi
    Corr - Kb Bucket Correlation Matrix 2D
    median0up1dn2 - Correlation Scenario Flag (0: median, 1: up, 2: Dn)
    
    example : 
        Kb = np.array([8.9011389, 4.2941, 5.9921])
        Sb = np.array([-9.21, 5.7781, 6.112])
        Corr = np.array([[1.0, 0.6, 0.5], [0.6, 1.0, 0.3], [0.5, 0.3, 1]])
        Calc_AggregatedDeltaVega(Kb, Sb, Corr, 0)
        -> 5.8833
    '''
    n = len(Kb)
    riskcharge_sqaure = 0
    riskcharge = 0

    targetvalue = 0
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetvalue += Kb[i] * Kb[j]
            else : 
                if median0up1dn2 == 1 : 
                    targetvalue += min(1, 1.25* Corr[i][j]) * Sb[i] * Sb[j]                
                elif median0up1dn2 == 2 : 
                    targetvalue += max(2 *Corr[i][j]-1,0.75 *Corr[i][j])  * Sb[i] * Sb[j]                
                else : 
                    targetvalue += Corr[i][j] * Sb[i] * Sb[j]
                
    riskcharge_sqaure = max(0, targetvalue)
    
    if (riskcharge_sqaure >= 0) : 
        riskcharge = np.sqrt(riskcharge_sqaure)
    else :
        NewSb = np.zeros(n)
        for i in range(n) : 
            NewSb[i] = max(-Kb[i], min(Sb[i], Kb[i]))
        
        targetvalue = 0
        for i in range(n) : 
            for j in range(n) : 
                if i == j : 
                    targetvalue += Kb[i] * Kb[j]
                else : 
                    if median0up1dn2 == 1 :
                        targetvalue += min(1, 1.25* Corr[i][j]) * NewSb[i] * NewSb[j]
                    elif median0up1dn2 == 2 : 
                        targetvalue += max(2 *Corr[i][j]-1,0.75 * Corr[i][j]) * NewSb[i] * NewSb[j]
                    else :     
                        targetvalue += Corr[i][j] * NewSb[i] * NewSb[j]
        
        riskcharge_sqaure = max(0, targetvalue)
        riskcharge = np.sqrt(riskcharge_sqaure)
    return riskcharge

#@jit('double(double[:],double[:],double[:], int32)', nopython = True)
def Calc_CVR(Vud, V, DeltaWS, plus0minus1) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 45.나
    Description : Calculate CVR+ or CVR- of Sensitivities by Each Risk factor   

    Variables :    
    Vud - Value(h + Up) or value(h + Down) 1d Array
    V - Value(h) 1d Array
    DeltaWS - Delta Weighted Sensi
    plus0minus1 - Flag CVR+ 0, CVR- 1
    
    example : 
        Vud = np.array([7.5218, 10.216])
        V = np.array([2.4018, 5.984])
        DeltaWS = np.array([14.214, 16.1])
        Calc_CVR(Vud, V, DeltaWS, 0)
        -> 20.962    
    
    '''    
    n = len(DeltaWS)
    targetvalue = 0
    if plus0minus1 == 0 : 
        for i in range(n) : 
            targetvalue += -(Vud[i] - V[i] - DeltaWS[i])
    else : 
        for i in range(n) : 
            targetvalue += -(Vud[i] - V[i] + DeltaWS[i])
    return targetvalue

#@jit('double(double[:],double[:,:], int32)', nopython = True)
def Calc_Kb_Curvature(CVRPlusMinus, rho, median0up1dn2) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 45.다(1)
    Description : Calculate RiskCharge(Kb) of Each Bucket   

    Variables :    
    CVRPlusMinus - CVR+ or CVR- 1d Array
    rho - Sensitivity Correlation Matrix - 2D Array    
    median0up1dn2 - Correlation Scenario (0:Median 1:Up 2:Dn)
    
    example : 
        CVRPlusMinus = np.array([20.962, 10.216])
        rho = np.array([[1,0.6], [0.6,1]])
        Calc_Kb_Curvature(CVRPlusMinus, rho, 0)
        -> 28.2975    
    '''
    n = len(CVRPlusMinus)
    targetvalue = 0
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetvalue += max(0, CVRPlusMinus[i]) * max(0, CVRPlusMinus[j])
            else : 
                if CVRPlusMinus[i] < 0 and CVRPlusMinus[j] < 0 : 
                    phi = 0
                else :
                    phi = 1
                    
                if median0up1dn2 == 1 :
                    targetvalue += min(1, 1.25* rho[i][j]) * CVRPlusMinus[i] * CVRPlusMinus[j] * phi
                elif median0up1dn2 == 2 : 
                    targetvalue += max(2 *rho[i][j]-1,0.75 * rho[i][j]) * CVRPlusMinus[i] * CVRPlusMinus[j] * phi
                else : 
                    targetvalue += rho[i][j] * CVRPlusMinus[i] * CVRPlusMinus[j] * phi
    return np.sqrt(max(0,targetvalue))

#@jit('double(double[:],double[:],double[:],double[:],double[:,:], int32)', nopython = True)
def Calc_AggregatedCurvature(KbPlus, KbMinus, SumCVRPlus, SumCVRMinus, Corr, median0up1dn2) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 45.다(2), 라
    Description : Calculate Aggregated Curvature integrating bucket

    Variables :    
    KbPlus - KbPlus By Bucket 1D Array
    KbMinus - KbMinus By Bucket 1D Array
    SumCVRPlus - CVR+ Sumation Groupby Bucket 1D Array
    SumCVRMinus - CVR- Sumation Groupby Bucket 1D Array
    Corr - Bucket Correlation Matrix - 2D Array    
    median0up1dn2 - Correlation Scenario (0:Median 1:Up 2:Dn)
    
    example : 
        KbPlus = np.array([0, 41.172])
        KbMinus = np.array([2.4, 34.35])
        SumCVRPlus = np.array([-70.5, 41.172])
        SumCVRMinus = np.array([-72.4, 34.35])
        Corr = np.array([[1,0.25], [0.25,1]])
        Calc_AggregatedCurvature(KbPlus, KbMinus, SumCVRPlus, SumCVRMinus, Corr, median0up1dn2)
        -> 14.50748
    '''
    n = len(KbPlus)
    
    Scenario = np.zeros(n)
    Kb = np.zeros(n)
    Sb = np.zeros(n)
    for i in range(n) : 
        if KbPlus[i] >= KbMinus[i] : 
            Scenario[i] = 0
            Kb[i] = KbPlus[i]
            Sb[i] = SumCVRPlus[i]
        else : 
            Scenario[i] = 1
            Kb[i] = KbMinus[i]
            Sb[i] = SumCVRMinus[i]
    
    targetvalue = 0
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetvalue += Kb[i] * Kb[j]
            else : 
                if Sb[i] < 0 and Sb[j] < 0 : 
                    phi = 0
                else : 
                    phi = 1
                
                if median0up1dn2 == 1 : 
                    targetvalue += Sb[i] * Sb[j] * min(1, 1.25* Corr[i][j]) * phi
                elif median0up1dn2 == 2 : 
                    targetvalue += Sb[i] * Sb[j] * max(2 *Corr[i][j]-1, 0.75 * Corr[i][j]) * phi
                else : 
                    targetvalue += Sb[i] * Sb[j] * Corr[i][j] * phi
                    
    return np.sqrt(max(0, targetvalue))

def Calc_GIRRDeltaSensiCorr(risktypelist, curvelist, tenorlist, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 64.다
    Description : Calculation GIRR Delta Sensitivities Correlation

    Variables :    
    risktypelist - Risk Type in ('Rate','CRS','INFLATION' ) 1D String Array
    curvelist - Curve Name (ex: 'KRW IRS', 'USD KRW CRS', ...) 1D String Array
    tenorlist - Tenor for floattype list (0.5, 1.0, ...)
    GIRR_DeltaRiskFactor - GIRR Delta Risk Factor 1D Array
                        -> pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
                        
    GIRR_DeltaRfCorr - GIRR RiskFree Correlation - 2D Array    
                    -> np.array([[1.000,0.970,0.914,0.811,0.719,0.566,0.400,0.400,0.400,0.400 ],
                                 [0.970,1.000,0.970,0.914,0.861,0.763,0.566,0.419,0.400,0.400 ],
                                 [0.914,0.970,1.000,0.970,0.942,0.887,0.763,0.657,0.566,0.419 ],
                                 [0.811,0.914,0.970,1.000,0.985,0.956,0.887,0.823,0.763,0.657 ],
                                 [0.719,0.861,0.942,0.985,1.000,0.980,0.932,0.887,0.844,0.763 ],
                                 [0.566,0.763,0.887,0.956,0.980,1.000,0.970,0.942,0.914,0.861 ],
                                 [0.400,0.566,0.763,0.887,0.932,0.970,1.000,0.985,0.970,0.942 ],
                                 [0.400,0.419,0.657,0.823,0.887,0.942,0.985,1.000,0.990,0.970 ],
                                 [0.400,0.400,0.566,0.763,0.844,0.914,0.970,0.990,1.000,0.985 ],
                                 [0.400,0.400,0.419,0.657,0.763,0.861,0.942,0.970,0.985,1.000 ]])
    example : 
        risktypelist = np.array(['Rate', 'Rate','CRS'])
        curvelist = np.array(['KRW IRS', 'KRW IRS','USD KRW CRS'])
        tenorlist = np.array([0.5, 1.0, 1.0])        
        Calc_GIRRDeltaSensiCorr(risktypelist, curvelist, tenorlist, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr)
        -> np.array([[1.        , 0.97044553, 0.        ],
                     [0.97044553, 1.        , 0.        ],
                     [0.        , 0.        , 1.        ]])
    '''
    
    murexflag = 1
    risktype = np.vectorize(lambda x : 'rate' if 'rate' in x.lower() else ('inf' if 'inf' in x.lower() else 'crs'))(list(risktypelist))
    curve = list(curvelist)
    tenor = list(tenorlist)
    n = len(tenor)
    targetcorr = np.identity(n)
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetcorr[i][j] = 1.0
            elif (risktype[i] == risktype[j]) and (curve[i] == curve[j]) and (tenor[i] == tenor[j]) : 
                targetcorr[i][j] = 1.0
            else : 
                if (risktype[i].lower() == 'rate' and risktype[j].lower() == 'rate') : 
                    if (curve[i] == curve[j] and str(tenor[i]) != str(tenor[j])) : 
                        # Same Curve different Tenor
                        idx1 = GIRR_DeltaRiskFactor[GIRR_DeltaRiskFactor == tenor[i]].index[0]
                        idx2 = GIRR_DeltaRiskFactor[GIRR_DeltaRiskFactor == tenor[j]].index[0]                        
                        c = GIRR_DeltaRfCorr[idx1, idx2]
                        if murexflag == 1 : 
                            c = max(np.exp(-0.03*np.abs((float(tenor[i])-float(tenor[j])))/min(float(tenor[i]),float(tenor[j]))),0.4)
                        targetcorr[i][j] = c
                    elif (curve[i] != curve[j] and str(tenor[i]) == str(tenor[j])) :
                        # Same Tenor Different Curve
                        targetcorr[i][j] = 0.999
                    else : 
                        # Different Curve Different Tenor
                        idx1 = GIRR_DeltaRiskFactor[GIRR_DeltaRiskFactor == tenor[i]].index[0]
                        idx2 = GIRR_DeltaRiskFactor[GIRR_DeltaRiskFactor == tenor[j]].index[0]
                        c = GIRR_DeltaRfCorr[idx1, idx2]
                        if murexflag == 1 : 
                            c = max(np.exp(-0.03*np.abs((float(tenor[i])-float(tenor[j])))/min(float(tenor[i]),float(tenor[j]))),0.4)
                        targetcorr[i][j] = c * 0.999                
                elif (risktype[i].lower() == 'rate' and 'inf' in risktype[j].lower()) : 
                    # Rf Rate vs Inflation
                    targetcorr[i][j] = 0.4
                elif (risktype[j].lower() == 'rate' and 'inf' in risktype[i].lower()) : 
                    # Rf Rate vs Inflation
                    targetcorr[i][j] = 0.4
                elif (risktype[i].lower() == 'rate' and risktype[j].lower() == 'crs' )  :
                    # Rf Rate vs CRS
                    targetcorr[i][j] = 0.
                elif (risktype[j].lower() == 'rate' and risktype[i].lower() == 'crs' )  :
                    # Rf Rate vs CRS
                    targetcorr[i][j] = 0.
                elif ('inf' in risktype[i].lower() and 'inf' in risktype[j].lower()) : 
                    # Inflation vs Inflation
                    targetcorr[i][j] = 0.999
                elif ('inf' in risktype[i].lower() and risktype[j].lower() == 'crs') : 
                    # Inflation vs CRS
                    targetcorr[i][j] = 0.
                elif ('inf' in risktype[j].lower() and risktype[i].lower() == 'crs') : 
                    # Inflation vs CRS
                    targetcorr[i][j] = 0.
                else :
                    # CRS vs CRS
                    targetcorr[i][j] = 0.
    return targetcorr

def GIRR_DeltaRiskWeight_Scalar(Tenor, Currency, Type) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 64.나
    Description : Calculate GIRR Delta Risk Weight by Tenor, Currency, Type

    Variables :    
    Tenor - Tenor of Curve Float
    Currency - Currency String
    Type - Rate of IRS or Inflation
    
    example : 
        np.vectorize(GIRR_DeltaRiskWeight_Scalar)( [0.5, 1.0, 3.0], ['USD','USD','USD'], ['IRS','IRS','IRS'])
        -> array([0.01202082, 0.01131371, 0.00848528])
    '''
    
    x = float(Tenor)
    c = str(Currency) in ["KRW","EUR","USD","GBP","AUD","JPY","SEK","CAD"]
    mytype = str(Type)
    
    div = np.sqrt(2) if c == True else 1
    
    if 'inf' in mytype.lower() or "xccy" in mytype.lower() or "crs" in mytype.lower(): 
        return 0.016/div    
    elif float(x) <= 0.25 : 
        return 0.017/div
    elif float(x) <= 0.5 : 
        return 0.017/div
    elif float(x) <= 1 : 
        return 0.016/div
    elif float(x) <= 2 : 
        return 0.013/div
    elif float(x) <= 3 : 
        return 0.012/div
    else : 
        return 0.011/div
GIRR_DeltaRiskWeight = np.vectorize(GIRR_DeltaRiskWeight_Scalar)    
    
def CSR_DeltaRiskWeight(bucket, flagb8 = False) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 65.나
    Description : Calculate CSR Delta Risk Weight by Tenor, Currency, Type

    Variables :    
    Bucket - Bucket of Credit
    flagb8 - is bucket flag 8?
    
    example : 
        np.vectorize(CSR_DeltaRiskWeight)( [1,1,1,2,3])
        -> array([0.005, 0.005, 0.005, 0.01 , 0.05 ])
    '''    
    b = int(bucket)
    MyIndex = np.arange(1,19)
    Value = np.array([0.5, 1, 5, 3, 3, 2, 
                      1.5, 2.5, 2, 4, 12, 
                      7, 8.5, 5.5, 5, 12, 1.5, 5], 
                     dtype = np.float64)/100
    if (b == 8 and flagb8 == True) : 
        w = 0.015
    else : 
        return pd.Series(Value, index = MyIndex).loc[b]

def CSRCTP_DeltaRiskWeight(bucket, flagb8 = False) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 67.나
    Description : Calculate CSR CTP Delta Risk Weight by Tenor, Currency, Type

    Variables :    
    Bucket - Bucket of Credit
    flagb8 - is bucket flag 8?
    
    example : 
        np.vectorize(CSRCTP_DeltaRiskWeight)( [1,1,1,2,3])
        -> array([0.04, 0.04, 0.04, 0.08 , 0.05 ])
    '''    
    b = int(bucket)
    MyIndex = np.arange(1,17)
    Value = np.array([4.0, 4.0, 8, 5, 4, 3, 
                      2, 6, 13, 13, 16, 
                      10, 12, 12, 12, 13], 
                     dtype = np.float64)/100
    return pd.Series(Value, index = MyIndex).loc[b]    
    
def FX_DeltaRiskWeight(FXPair, HighLiquidCurrency) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 69.나
    Description : Calculate CSR Delta Risk Weight by Tenor, Currency, Type

    Variables :    
    FXPair - Pair of string (ex: USD/KRW, EUR/USD, .... )
    HighLiquidCurrency - HighLiquidCurrency
    
    example : 
        FX_DeltaRiskWeight('USD/KRW', HighLiquidCurrency)
        -> 0.106066
    '''  
    MyPair = ["",""]
    if '-' in FXPair : 
        MyPair[0] = FXPair.split("-")[0]
        MyPair[1] = FXPair.split("-")[1]
    elif "/" in FXPair : 
        MyPair[0] = FXPair.split("/")[0]
        MyPair[1] = FXPair.split("/")[1]
    else : 
        raise ValueError("CheckFXPair String")
    
    if (MyPair[0] in HighLiquidCurrency) and (MyPair[1] in HighLiquidCurrency) : 
        return 0.10606601717798211
    else :
        return 0.15    
    
def MapEquityRiskWeight(Data,EQRWMappingDF,TypeColName = "Type", BucketColName = "Bucket") : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 68.나
    Description : Calc Risk Weight as EQ (1) RiskFactor type and (2) Bucket
    
    Variables : 
    Data = DataFrame that have columns Type(Price or Repo), Bucket(1, 2, 3, ...)
    EQRWMappingDF = DataFrame That have Risk Weight Series
    
    excample : 
    
        risktype = ["price","price","price","repo"]
        riskbucket = ["1","1","3","3"]
        df = pd.DataFrame([risktype,riskbucket], index = ["Type","Bucket"]).T        
        MapEquityRiskWeight(df,EQRWMappingDF,TypeColName = "Type", BucketColName = "Bucket")
        -> 0.55, 0.55, 0.45, 0.0045        
        
    '''
    def func(Data, EQRWMappingDF, TypeColName, BucketColName) : 
        if 'price' in str(Data[TypeColName]).lower() or '가격' in str(Data[TypeColName]).lower() : 
            if int(Data[BucketColName]) >= 0 :
                return EQRWMappingDF["SpotRW"].loc[int(Data[BucketColName])]
            else : 
                return 0
        else : 
            if int(Data[BucketColName]) >= 0 :            
                return EQRWMappingDF["RepoRW"].loc[int(Data[BucketColName])]    
            else : 
                return 0
    
    return Data.apply(func, axis = 1, EQRWMappingDF = EQRWMappingDF, TypeColName = TypeColName , BucketColName = BucketColName)

def CSR_sensicorrbucket(bucket, issuerlist, tenorlist, curvelist) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 65.다
    Description : Calculate CSR Delta Sensitivity Correlation Matrix by bucket, issuer, tenor, curve

    Variables :    
    Bucket(int) - Bucket number (Type : Integer)
    issuerlist - issuername list (Type : string list)
    tenorlist - tenorlist (Type : float list)
    curvelist - curvename list (ex: 'KRW IRS','KRW TREASURY',...)
    
    example : 
        CSR_sensicorrbucket(1, ['KRW GOVERN','KRW GOVERN','USD GOVERN'], [0.5,1.0,0.5], ['KRW TREASURY','KRW TREASURY','US TREASURY'])
        -> np.array([[1.       , 0.65     , 0.34965  ],
                     [0.65     , 1.       , 0.2272725],
                     [0.34965  , 0.2272725, 1.       ]])
    '''      
    b = bucket
    issuerlist = list(issuerlist)
    tenorlist = list(tenorlist)
    curvelist = list(curvelist)
    n = len(issuerlist)
    targetarray = np.identity(n)
    for i in range(n) :
        for j in range(n) : 
            if i == j : 
                c = 1
            else : 
                issuer1 = issuerlist[i]
                issuer2 = issuerlist[j]
                tenor1 = tenorlist[i]
                tenor2 = tenorlist[j]
                curve1 = curvelist[i]
                curve2 = curvelist[j]
                if (int(b) < 16 ) : 
                    c1 = 1.0 if issuer1 == issuer2 else 0.35
                    c2 = 1.0 if tenor1 == tenor2 else 0.65
                    c3 = 1.0 if curve1 == curve2 else 0.999
                    c = c1 * c2 * c3
                elif (int(b) > 16) :
                    c1 = 1.0 if issuer1 == issuer2 else 0.8
                    c2 = 1.0 if tenor1 == tenor2 else 0.65
                    c3 = 1.0 if curve1 == curve2 else 0.999
                    c = c1 * c2 * c3
                else : 
                    c = 1
            targetarray[i][j] = c
    return targetarray
            
def CSR_SecuritizedNonCTPDelta_sensicorr(bucket, tranche, tenorlist, curvelist) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 66.다
    Description : Calculate CSR Nonsecuritized Delta Sensitivity Correlation Matrix by bucket, tranche, tenor, curve

    Variables :    
    Bucket(int) - Bucket number (Type : Integer)
    tranche - tranche list (Type : string list)
    tenorlist - tenorlist (Type : float list)
    curvelist - curvename list (ex: 'KRW IRS','KRW TREASURY',...)
    
    example : 
        CSR_SecuritizedNonCTPDelta_sensicorr(1, ['Senior','Senior','Equity'], [0.5,1.0,0.5], ['CORP AAA','CORP AAA','CORP BBB'])
        -> np.array([[1.     , 0.8    , 0.3996 ],
                     [0.8    , 1.     , 0.31968],
                     [0.3996 , 0.31968, 1.     ]])
    '''         
    b = bucket
    tranchelist = list(tranche)
    tenorlist = list(tenorlist)
    curvelist = list(curvelist)
    n = len(tranchelist)
    targetarray = np.identity(n)
    for i in range(n) :
        for j in range(n) : 
            if i == j : 
                c = 1
            else : 
                tranche1 = tranchelist[i]
                tranche2 = tranchelist[j]
                tenor1 = tenorlist[i]
                tenor2 = tenorlist[j]
                curve1 = curvelist[i]
                curve2 = curvelist[j]
                if (int(b) < 25 ) : 
                    c1 = 1.0 if tranche1 == tranche2 else 0.4
                    c2 = 1.0 if tenor1 == tenor2 else 0.8
                    c3 = 1.0 if curve1 == curve2 else 0.999
                    c = c1 * c2 * c3
                else : 
                    c = 1
            targetarray[i][j] = c
    return targetarray    
    
def CSRDeltaBucketRatingCorr(bucketlist) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 65.라
    Description : Calculate CSR Bucket Rating Correlation

    Variables :    
    bucketlist - bucketlist(ex : [1,3,5,6,7 ...])
    
    example : 
        CSRDeltaBucketRatingCorr([1, 3, 7,8,9])
        -> np.array([[1. , 1. , 1. , 1. , 0.5],
                     [1. , 1. , 1. , 1. , 0.5],
                     [1. , 1. , 1. , 1. , 0.5],
                     [1. , 1. , 1. , 1. , 0.5],
                     [0.5, 0.5, 0.5, 0.5, 1. ]])
    '''         
    n = len(bucketlist)
    bucketlist = list(bucketlist)
    targetarray = np.identity(n)
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetarray[i][j] = 1
            else : 
                b1 = int(bucketlist[i])
                b2 = int(bucketlist[j])
                if b1 < 16 and b2 < 16 : 
                    if (b1 <= 8 and b2 > 8) or (b2 <= 8 and b1 > 8) : 
                        # 버킷 1 ~ 15이고 서로 신용도가 다르면 50%
                        c = 0.5
                    else : 
                        c = 1.0
                else : 
                    c = 1.0
                targetarray[i][j] = c
    return targetarray

def findbucketindex(bucket, bucketindex) : 
    resultindex = -1
    for i, ind in enumerate(bucketindex) : 
        if type(ind) == tuple or type(ind) == list : 
            if int(bucket) in ind : 
                resultindex = i
                break
        else : 
            if int(bucket) == int(ind) : 
                resultindex = i
                break
    return resultindex

def CSRDeltaBucketSectorCorr(bucketlist, CSR_DeltaNonSecurCorrDf) :   
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 65.라
    Description : Calculate CSR Bucket Sector Correlation

    Variables :    
    bucketlist - bucketlist(ex : [1,3,5,6,7 ...])
    CSR_DeltaNonSecurCorrDf - DataFrame CSR Sector Correlation Matrix
    
    example : 
        CSRDeltaBucketSectorCorr([1, 3, 7,8,9], CSR_DeltaNonSecurCorrDf)
        -> np.array([[1.  , 0.1 , 0.15, 0.1 , 1.  ],
                     [0.1 , 1.  , 0.05, 0.2 , 0.1 ],
                     [0.15, 0.05, 1.  , 0.05, 0.15],
                     [0.1 , 0.2 , 0.05, 1.  , 0.1 ],
                     [1.  , 0.1 , 0.15, 0.1 , 1.  ]])
    '''       
    bucketlist = list(bucketlist)
    n = len(bucketlist)
    targetarray = np.identity(n)
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetarray[i][j] = 1
            else : 
                b1 = int(bucketlist[i])
                b2 = int(bucketlist[j])
                col = findbucketindex(b1, CSR_DeltaNonSecurCorrDf.columns)
                ind = findbucketindex(b2, CSR_DeltaNonSecurCorrDf.index)
                c = CSR_DeltaNonSecurCorrDf.values[ind][col]
                targetarray[i][j] = c
    return targetarray

def EquityDeltaInBucketSensiCorr(Bucket, TypeList, StockNameList) :
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 68.다
    Description : Calculate EQR Sensitivities Correlation

    Variables :    
    Bucket - bucketnum (Integer)
    TypeList - Type String List whether PRICE or REPO (example : ['PRICE','PRICE','REPO'])
    StockNameList = StockName String List of Underlying (example : ['SAMSUNG','LG','LG'])
    
    example : 
        Bucket = 5
        TypeList = ['PRICE','PRICE','REPO']
        StockNameList = ['SAMSUNG','LG','LG']
        EquityDeltaInBucketSensiCorr(Bucket, TypeList, StockNameList)
        -> np.array([[1.  , 0.25, 0.25],
                     [0.25, 1.  , 0.25],
                     [0.25, 0.25, 1.  ]])
    '''       
    n = len(StockNameList)
    TypeList = list(TypeList)
    StockNameList = list(StockNameList)
    targetarray = np.identity(n)
    MyType = []
    for t in TypeList : 
        if ('rep' in t) or ('rp' in t) : 
            MyType.append('repo')
        else : 
            MyType.append('spot')
    Bucket = int(Bucket)
    if int(Bucket) < 5 : 
        c = 0.15
    elif int(Bucket) < 9 : 
        c = 0.25
    elif int(Bucket) == 9 : 
        c = 0.075
    elif int(Bucket) == 10 : 
        c = 0.125
    elif int(Bucket) == 11 : 
        c = 1
    elif int(Bucket) > 11 : 
        c = 0.8
    else : 
        c = 0
    
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetarray[i][j] = 1
            else : 
                if MyType[i] == MyType[j] : 
                    targetarray[i][j] = c
                else :
                    if StockNameList[i] == StockNameList[j] : 
                        targetarray[i][j] = 0.999
                    else : 
                        targetarray[i][j] = c * 0.999
    return targetarray

def EquityDeltaBucketAggregatedCorr(BucketList) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 68.다
    Description : Calculate Equity Bucket Aggregated Correlation Matrix 
    
    Variables :
    BucketList - Integer List of Each Bucket(example : [1,5,6,7])
    
    Example : 
    EquityDeltaBucketAggregatedCorr([1,5,6,7,13])
    ->np.array([[1.  , 0.15, 0.15, 0.15, 0.45],
                [0.15, 1.  , 0.15, 0.15, 0.45],
                [0.15, 0.15, 1.  , 0.15, 0.45],
                [0.15, 0.15, 0.15, 1.  , 0.45],
                [0.45, 0.45, 0.45, 0.45, 1.  ]])
    '''    
    n = len(BucketList)
    BucketList = list(BucketList)
    targetarray = np.identity(n)
    for i in range(n) : 
        for j in range(n) :             
            B1 = int(BucketList[i])
            B2 = int(BucketList[j])
            if int(B1) == int(B2) : 
                c = 1
            else : 
                if int(B1) < 10 and int(B2) < 10 :
                    c = 0.15
                elif int(B1) == 11 or int(B2) == 11 : 
                    c = 0.0
                elif int(B1) > 11 and int(B2) > 11 : 
                    c = 0.75
                else : 
                    c = 0.45
            targetarray[i][j] = c
    return targetarray                

def COMM_deltasensicorrbucket(bucket, commoditylist, tenorlist, locationlist) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 70.나
    Description : Calculate COMR Sensitivities Correlation Matrix 
    
    Variables :
    Bucket - Bucket Number(Integer)
    commoditylist - underlying commodity string list (['WTI','WTI','BIOOIL',...])
    tenorlist - underlying maturities float list ([1.0, 2.0, 1.0])
    location - underlying delivery location list (['LN','LN','NY'])
    
    Example : 
        bucket = 2
        commoditylist = ['WTI','WTI','BIOOIL']
        tenorlist = [1.0,2.0,1.0]
        locationlist = ['LN','LN','NY']
        COMM_deltasensicorrbucket(bucket, commoditylist, tenorlist, locationlist)
        ->np.array([[1.        , 0.999     , 0.94905   ],
                    [0.999     , 1.        , 0.94810095],
                    [0.94905   , 0.94810095, 1.        ]])
    '''      
    n = len(commoditylist)
    commoditylist = list(commoditylist)
    tenorlist = list(tenorlist)
    locationlist = list(locationlist)
    targetarray = np.identity(n)
    commcorrseries = pd.Series([0.55,0.95,0.40,0.80,0.6,
                                0.65,0.55,0.45,0.15,0.4,
                                0.15], index = np.arange(1,12))    
    cc = commcorrseries.loc[int(bucket)]
    for i in range(n) :
        for j in range(n) : 
            if i == j : 
                c = 1
            else : 
                if (commoditylist[i] == commoditylist[j]) : 
                    c1 = 1
                else :
                    c1 = cc
                
                if (tenorlist[i] == tenorlist[j]) : 
                    c2 = 1
                else : 
                    c2 = 0.999
                    
                if (locationlist[i] == locationlist[j]) : 
                    c3 = 1
                else : 
                    c3 = 0.999
                c = c1 * c2 * c3
                                    
            targetarray[i][j] = c
    return targetarray

def COMM_DeltaBucketAggregatedCorr(bucketlist) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 70.다
    Description : Calculate COMR Bucket Aggregated Correlation Matrix 
    
    Variables :
    BucketList - Integer List of Each Bucket(example : [1,5,6,7])
    
    Example : 
        COMM_DeltaBucketAggregatedCorr([1,5,6,7])
        ->np.array([[1. , 0.2, 0.2, 0.2],
                    [0.2, 1. , 0.2, 0.2],
                    [0.2, 0.2, 1. , 0.2],
                    [0.2, 0.2, 0.2, 1. ]])
    '''        
    n = len(bucketlist)
    bucketlist = list(bucketlist)
    targetarray = np.identity(n)
    
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetarray[i][j] = 1
            else : 
                if (int(bucketlist[i]) < 11 and int(bucketlist[j]) < 11) :
                    targetarray[i][j] = 0.2
                else :
                    targetarray[i][j] = 0
    return targetarray

optionmaturitycorr = lambda t_i, t_j : np.exp(-0.01*abs(t_i-t_j)/min(t_i, t_j))
def tenorcorr(TenorList) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 71.다
    Description : Calculate Vega Sensitivities maturity Corr 
    
    Variables :
    TenorList - TenorList(example : [0.5, 1,3,5])
    
    Example : 
        tenorcorr([1,5,6,7])
        ->np.array([[1.        , 0.96078944, 0.95122942, 0.94176453],
                    [0.96078944, 1.        , 0.998002  , 0.99600799],
                    [0.95122942, 0.998002  , 1.        , 0.99833472],
                    [0.94176453, 0.99600799, 0.99833472, 1.        ]])
    '''           
    targetarray = np.identity(len(TenorList)) 
    for i in range(len(TenorList)) : 
        for j in range(len(TenorList)) : 
            if i == j : 
                targetarray[i][j] = 1
            else :
                targetarray[i][j] = optionmaturitycorr(float(TenorList[i]), float(TenorList[j]))
    return targetarray

def GIRR_VegaSensiCorr(OptTenorList, UndTenorList) : 
    '''
    참고문헌 : 은행업감독업무 시행세칙 별표3의2 71.다
    Description : Calculate GIRR Vega Sensitivities Corr 
    
    Variables :
    OptTenorList - OptTenorList(example : [0.5, 0.5,1,2])
    UndTenorList - OptTenorList(example : [0.5, 1,1,1])
    
    Example : 
        GIRR_VegaSensiCorr([0.5, 0.5,1,2], [0.5, 1,1,1])
        ->np.array([[1.        , 0.99004983, 0.98019867, 0.96078944],
                    [0.99004983, 1.        , 0.99004983, 0.97044553],
                    [0.98019867, 0.99004983, 1.        , 0.99004983],
                    [0.96078944, 0.97044553, 0.99004983, 1.        ]])
    '''       
    n = len(OptTenorList)
    OptTenorList = list(OptTenorList)
    UndTenorList = list(UndTenorList)
    targetarray = np.identity(n)
    
    for i in range(n) : 
        for j in range(n) : 
            if (i == j) :
                targetarray[i][j] = 1
            else : 
                c1 = optionmaturitycorr(float(OptTenorList[i]), float(OptTenorList[j]))
                c2 = optionmaturitycorr(float(UndTenorList[i]), float(UndTenorList[j]))
                c = c1 * c2
                targetarray[i][j] = min(1, c)
    return targetarray

calcsb = lambda df : df["WeightedSensi"].sum()

def VegaRiskWeight_Scalar(Risk_Class, Bucket) : 
    rc = str(Risk_Class)
    b = str(Bucket)
    if ((rc in ["EQR","Equity","주식리스크","주식","주식리스크(EQR)"]) and (b in ["1","2","3","4","5","6","7","8","12","13"])) :
        return 0.7778
    else : 
        return 1.0
VegaRiskWeight = np.vectorize(VegaRiskWeight_Scalar)    

def Calc_CSRDelta_KB(DataByBucket, CorrScenario = 'm') : 
    '''
    설명 : 버킷(n)의 CSR KB를 계산한다
    Description : Calculate KB of bucket(n) 
    
    Variables :
    DataByBucket - DataFrame that have columns ['BucketCopy','Curve','Tenor','Issuer','WeightedSensi']
    
    Example : 
        mycol = ['BucketCopy','Curve','Tenor','Issuer','WeightedSensi']
        DataByBucket = pd.DataFrame([[1,'KRW TREASURY',0.5, 'KRW TREASURY',50.51],
                                    [1,'KRW TREASURY',1.0, 'KRW TREASURY',54.51],
                                    [1,'KRW TREASURY',2.0, 'KRW TREASURY',204.51]], columns = mycol)
        Calc_CSRDelta_KB(DataByBucket, CorrScenario = 'm')
        ->280.797369
    '''      
    # Sensi Netting    
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Curve","Tenor","Issuer"], CurvatureFlag = 0)    
    if len(sensidata) < 1 : 
        return 0
    
    corrsensi = CSR_sensicorrbucket(sensidata["BucketCopy"].iloc[0], sensidata["Issuer"], sensidata["Tenor"].astype(np.float64), sensidata["Curve"])
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    KB = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), corrsensi, ScenarioFlag)
    return float(KB)

def Calc_CSRDelta_KB_ByBucket(MyData) : 
    '''
    설명 : 버킷별 CSR KB를 계산한다
    Description : Calculate KB of all buckets 
    
    Variables :
    DataByBucket - DataFrame that have columns ['Bucket','Curve','Tenor','Issuer','WeightedSensi']
    
    Example : 
        mycol = ['Bucket','Curve','Tenor','Issuer','WeightedSensi']
        DataByBucket = pd.DataFrame([[3,'CORP AAA',0.5, 'IBK',-10.51],
                                    [3,'CORP AAA',1.0, 'IBK',-24.51],
                                    [1,'KRW TREASURY',0.5, 'KRW TREASURY',50.51],
                                    [1,'KRW TREASURY',1.0, 'KRW TREASURY',54.51],
                                    [1,'KRW TREASURY',2.0, 'KRW TREASURY',204.51]], columns = mycol)
        Calc_CSRDelta_KB_ByBucket(DataByBucket)
        ->	Bucket	KB_U	KB_M	KB_D	SB
                1	294.48	280.79	266.40	309.53
                3	33.61	32.34	31.02	-35.02
    '''     
    MyData["BucketCopy"] = MyData["Bucket"]

    KBByBucket_M = MyData.groupby("Bucket").apply(Calc_CSRDelta_KB, 'm')
    KBByBucket_D = MyData.groupby("Bucket").apply(Calc_CSRDelta_KB, 'd')
    KBByBucket_U = MyData.groupby("Bucket").apply(Calc_CSRDelta_KB, 'u')
    SBByBucket = MyData.groupby("Bucket").apply(calcsb)

    Data = pd.concat([KBByBucket_U,KBByBucket_M,KBByBucket_D,SBByBucket],axis = 1).reset_index()
    Data.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    return Data

def DRC_RW(RatingsString) : 
    RatingsString = str(RatingsString).lower()
    if 'aaa' in RatingsString : 
        return 0.005
    elif 'aa' in RatingsString : 
        return 0.02
    elif 'a' in RatingsString : 
        return 0.03
    elif 'bbb' in RatingsString : 
        return 0.06
    elif 'b' in RatingsString : 
        return 0.15
    elif 'b' in RatingsString : 
        return 0.3
    elif 'ccc' in RatingsString : 
        return 0.15
    else : 
        return 1.0

def HBR_bucket(MyData, col = "JTD") : 
    HBR_b =  MyData[MyData[col] > 0][col].sum() /(np.abs(MyData[col]).sum())
    return HBR_b

def DRC_b(MyData, col = "JTD", FixedHBR = 0) : 
    if len(MyData) == 0 : 
        return 0
    HBR_b =  MyData[MyData[col] > 0][col].sum() /(np.abs(MyData[col]).sum())
    JTDP = MyData[MyData[col] >= 0]
    JTDM = MyData[MyData[col] < 0]
    if FixedHBR > 0.00000001 : 
        v = max(0, (JTDP["RW"] * JTDP[col]).sum() -MyData["FixedHBR"].iloc[0] * (np.abs(JTDM["RW"] * JTDM[col]).sum()))
    else : 
        v = max(0, (JTDP["RW"] * JTDP[col]).sum() -HBR_b * (np.abs(JTDM["RW"] * JTDM[col]).sum()))
    return v

def Calc_CSRDelta(Delta_Data, CSR_DeltaNonSecurCorrDf, SensitivityColumnName = "Delta", CTPFlag = 0) :
    MyData = Delta_Data[Delta_Data["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])]
    if len(MyData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    MyData["Curve"] = MyData["Curve"].fillna("NaN")
    MyData["Tenor"] = MyData["Tenor"].fillna("NaN")
    MyData["Issuer"] = MyData["Issuer"].fillna("NaN")
    if CTPFlag == 0 : 
        MyData["RW"] = MyData["Bucket"].apply(CSR_DeltaRiskWeight)
    else : 
        MyData["RW"] = MyData["Bucket"].apply(CSRCTP_DeltaRiskWeight)
        
    MyData["WeightedSensi"] = MyData["RW"] * MyData[SensitivityColumnName]
    
    CSRDelta_ByBuc = Calc_CSRDelta_KB_ByBucket(MyData)
    
    BucketCorr = CSRDeltaBucketRatingCorr(CSRDelta_ByBuc["Bucket"]) * CSRDeltaBucketSectorCorr(CSRDelta_ByBuc["Bucket"],CSR_DeltaNonSecurCorrDf)
    CSRDelta_M = Calc_AggregatedDeltaVega(CSRDelta_ByBuc["KB_M"].values.astype(np.float64), CSRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 0)
    CSRDelta_D = Calc_AggregatedDeltaVega(CSRDelta_ByBuc["KB_D"].values.astype(np.float64), CSRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 2)
    CSRDelta_U = Calc_AggregatedDeltaVega(CSRDelta_ByBuc["KB_U"].values.astype(np.float64), CSRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 1)
    SB = CSRDelta_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,CSRDelta_U, CSRDelta_M, CSRDelta_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([CSRDelta_ByBuc, Result],axis = 0)    

def Calc_CSRKb_Curvature(Data_Sensi, CorrScenario) : 
    if Data_Sensi["CVR_Plus"].isna().sum() == len(Data_Sensi) and Data_Sensi["CVR_Minus"].isna().sum() == len(Data_Sensi) :    
        V = Data_Sensi["Value"].values.astype(np.float64)
        DeltaWS = Data_Sensi["DeltaWeightedSensi"].values
        Data_Sensi["CVR_Plus"] = Calc_CVR(Data_Sensi["Value_Up"].values.astype(np.float64), V, DeltaWS, 0)
        Data_Sensi["CVR_Minus"] = Calc_CVR(Data_Sensi["Value_Dn"].values.astype(np.float64), V, DeltaWS, 1)
        
    if len(Data_Sensi) > 0:
        Kb_plus = max(0,Data_Sensi["CVR_Plus"].sum())
        Kb_minus = max(0,Data_Sensi["CVR_Minus"].sum())
        Kb = max(Kb_plus, Kb_minus)
        Sb_plus = Data_Sensi["CVR_Plus"].sum()
        Sb_minus = Data_Sensi["CVR_Minus"].sum()    
        CurvatureScenario = 0 if Kb_plus > Kb_minus else 1
        Sb = Sb_plus if CurvatureScenario == 0 else Sb_minus
    else :
        Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, CurvatureScenario = 0,0,0,0,0,0,0
    return pd.Series([Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, int(CurvatureScenario), CorrScenario], index = ["KB","KB_PLUS","KB_MINUS","SB","SB_PLUS","SB_MINUS","PLUS0MINUS1","CorrScenario"])


def Calc_CSRCurvature(CurvatureData, CSR_DeltaNonSecurCorrDf, DeltaSensitivityColumnName = "Delta") :
    CurvatureData = CurvatureData[CurvatureData["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])]
    if len(CurvatureData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    

    if CurvatureData["CVR_Plus"].isna().sum() == len(CurvatureData) and CurvatureData["CVR_Minus"].isna().sum() == len(CurvatureData) :    
        CurvatureData["RW"] = CurvatureData["Bucket"].apply(CSR_DeltaRiskWeight)
        CurvatureData["DeltaWeightedSensi"] = CurvatureData["RW"] * CurvatureData[DeltaSensitivityColumnName]    
        
    KB_Median = CurvatureData.groupby("Bucket").apply(Calc_CSRKb_Curvature, 'm')
    KB_Up = CurvatureData.groupby("Bucket").apply(Calc_CSRKb_Curvature, 'u')
    KB_Dn = CurvatureData.groupby("Bucket").apply(Calc_CSRKb_Curvature, 'd')
    SB = max(max(KB_Dn["SB"].sum(), KB_Median["SB"].sum()),KB_Dn["SB"].sum())
    Data = pd.concat([KB_Up["KB"],KB_Median["KB"],KB_Dn["KB"]],axis = 1)
    Data.columns = ["KB_U","KB_M","KB_D"]
    Data["SB"] = np.maximum(np.maximum(KB_Median["SB"],KB_Up["SB"]),KB_Dn["SB"])
    DataByBucket = Data.reset_index()
    BucketCorr = (CSRDeltaBucketRatingCorr(DataByBucket["Bucket"]) * CSRDeltaBucketSectorCorr(DataByBucket["Bucket"],CSR_DeltaNonSecurCorrDf))**2
    
    KbPlus_Median = KB_Median["KB_PLUS"].values.astype(np.float64)
    KbMinus_Median = KB_Median["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Median = KB_Median["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Median = KB_Median["SB_MINUS"].values.astype(np.float64)

    KbPlus_Up = KB_Up["KB_PLUS"].values.astype(np.float64)
    KbMinus_Up = KB_Up["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Up = KB_Up["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Up = KB_Up["SB_MINUS"].values.astype(np.float64)

    KbPlus_Dn = KB_Dn["KB_PLUS"].values.astype(np.float64)
    KbMinus_Dn = KB_Dn["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Dn = KB_Dn["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Dn = KB_Dn["SB_MINUS"].values.astype(np.float64)

    Curvature_Median = Calc_AggregatedCurvature(KbPlus_Median, KbMinus_Median, SumCVRPlus_Median, SumCVRMinus_Median, BucketCorr, 0)
    Curvature_Up = Calc_AggregatedCurvature(KbPlus_Up, KbMinus_Up, SumCVRPlus_Up, SumCVRMinus_Up, BucketCorr, 1)
    Curvature_Dn = Calc_AggregatedCurvature(KbPlus_Dn, KbMinus_Dn, SumCVRPlus_Dn, SumCVRMinus_Dn, BucketCorr, 2)
    Result = pd.DataFrame([[99999,Curvature_Up, Curvature_Median, Curvature_Dn, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([DataByBucket, Result],axis = 0)      

def Calc_CSRVega_KB(DataByBucket, CorrScenario = 'm') : 
    
    # Sensi Netting
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Curve","Tenor","Issuer"], CurvatureFlag = 0)
    if len(sensidata) < 1 : 
        return 0
    tc = tenorcorr(sensidata["Tenor"])
    corrsensi = CSR_sensicorrbucket(sensidata["BucketCopy"].iloc[0], sensidata["Issuer"], sensidata["Tenor"].astype(np.float64), sensidata["Curve"]) * tc
        
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    KB = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), corrsensi, ScenarioFlag)
    return KB    

def Calc_CSRVega_KB_ByBucket(MyData) : 
    MyData["BucketCopy"] = MyData["Bucket"]

    KBByBucket_M = MyData.groupby("Bucket").apply(Calc_CSRVega_KB, 'm')
    KBByBucket_D = MyData.groupby("Bucket").apply(Calc_CSRVega_KB, 'd')
    KBByBucket_U = MyData.groupby("Bucket").apply(Calc_CSRVega_KB, 'u')
    SBByBucket = MyData.groupby("Bucket").apply(calcsb)

    Data = pd.concat([KBByBucket_U,KBByBucket_M,KBByBucket_D,SBByBucket],axis = 1).reset_index()
    Data.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    return Data

def Calc_CSRVega(Vega_Data, CSR_DeltaNonSecurCorrDf, SensitivityColumnName = "Vega") :
    MyData = Vega_Data[Vega_Data["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])]
    if len(MyData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    MyData["Curve"] = MyData["Curve"].fillna("NaN")
    MyData["Tenor"] = MyData["Tenor"].fillna("NaN")
    MyData["Issuer"] = MyData["Issuer"].fillna("NaN")
    MyData["RW"] = VegaRiskWeight(MyData["Risk_Class"].values, MyData["Bucket"].values)
    MyData["WeightedSensi"] = MyData["RW"] * MyData[SensitivityColumnName]    
    
    CSRVega_ByBuc = Calc_CSRVega_KB_ByBucket(MyData)
    
    BucketCorr = CSRDeltaBucketRatingCorr(CSRVega_ByBuc["Bucket"]) * CSRDeltaBucketSectorCorr(CSRVega_ByBuc["Bucket"],CSR_DeltaNonSecurCorrDf)
    CSRVega_M = Calc_AggregatedDeltaVega(CSRVega_ByBuc["KB_M"].values.astype(np.float64), CSRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 0)
    CSRVega_D = Calc_AggregatedDeltaVega(CSRVega_ByBuc["KB_D"].values.astype(np.float64), CSRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 2)
    CSRVega_U = Calc_AggregatedDeltaVega(CSRVega_ByBuc["KB_U"].values.astype(np.float64), CSRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 1)
    SB = CSRVega_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,CSRVega_U, CSRVega_M, CSRVega_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([CSRVega_ByBuc, Result],axis = 0)    

def Calc_CSRSecuritizedNonCTPDelta_KB(DataByBucket, CorrScenario = 'm') : 
    '''
    설명 : 버킷(n)의 CSR KB를 계산한다
    Description : Calculate KB of bucket(n) 
    
    Variables :
    DataByBucket - DataFrame that have columns ['BucketCopy','Curve','Tenor','Tranche','WeightedSensi']
    
    Example : 
        mycol = ['BucketCopy','Curve','Tenor','Issuer','WeightedSensi']
        DataByBucket = pd.DataFrame([[1,'CORP A',0.5, 'Senior',50.51],
                                    [1,'CORP A',1.0, 'Senior',54.51],
                                    [1,'CORP C',0.5, 'Junk',204.51]], columns = mycol)
        Calc_CSRSecuritizedNonCTPDelta_KB(DataByBucket, CorrScenario = 'm')
        ->280.797369
    '''      
    # Sensi Netting    
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Curve","Tenor","Tranche"], CurvatureFlag = 0)    
    if len(sensidata) < 1 : 
        return 0
    corrsensi = CSR_SecuritizedNonCTPDelta_sensicorr(sensidata["BucketCopy"].iloc[0], sensidata["Tranche"], sensidata["Tenor"].astype(np.float64), sensidata["Curve"])
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    KB = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), corrsensi, ScenarioFlag)
    return float(KB)

def Calc_CSRSecuritizedNonCTPDelta_KB_ByBucket(MyData) : 
    '''
    설명 : 버킷별 CSR KB를 계산한다
    Description : Calculate KB of all buckets 
    
    Variables :
    DataByBucket - DataFrame that have columns ['Bucket','Curve','Tenor','Issuer','WeightedSensi']
    
    Example : 
        mycol = ['Bucket','Curve','Tenor','Tranche','WeightedSensi']
        DataByBucket = pd.DataFrame([[3,'CORP AAA',0.5, 'Senior',-10.51],
                                    [3,'CORP AAA',1.0, 'Senior',-24.51],
                                    [1,'CORP AAA',0.5, 'Senior',50.51],
                                    [1,'CORP AAA',1.0, 'Senior',54.51],
                                    [1,'CORP C',2.0, 'Junk',204.51]], columns = mycol)
        Calc_CSRSecuritizedNonCTPDelta_KB_ByBucket(DataByBucket)
        ->	Bucket	KB_U	KB_M	KB_D	SB
                1	294.48	280.79	266.40	309.53
                3	33.61	32.34	31.02	-35.02
    '''     
    MyData["BucketCopy"] = MyData["Bucket"]

    KBByBucket_M = MyData.groupby("Bucket").apply(Calc_CSRSecuritizedNonCTPDelta_KB, 'm')
    KBByBucket_D = MyData.groupby("Bucket").apply(Calc_CSRSecuritizedNonCTPDelta_KB, 'd')
    KBByBucket_U = MyData.groupby("Bucket").apply(Calc_CSRSecuritizedNonCTPDelta_KB, 'u')
    SBByBucket = MyData.groupby("Bucket").apply(calcsb)

    Data = pd.concat([KBByBucket_U,KBByBucket_M,KBByBucket_D,SBByBucket],axis = 1).reset_index()
    Data.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    return Data

def Calc_CSRSecuritizedNonCTPDelta(Delta_Data, CSR_SecuritizedNonCTPDelta_RW, SensitivityColumnName = "Delta") :
    MyData = Delta_Data[Delta_Data["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])]
    if len(MyData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    MyData["RW"] = MyData["Bucket"].astype(np.int64).map(CSR_SecuritizedNonCTPDelta_RW).fillna(0)
    MyData["WeightedSensi"] = MyData["RW"] * MyData[SensitivityColumnName]
    CSRDelta_ByBuc = Calc_CSRSecuritizedNonCTPDelta_KB_ByBucket(MyData)
    CSRDelta_ByBucExcept25 = CSRDelta_ByBuc[CSRDelta_ByBuc["Bucket"].isin([25,"25"]) == False]
    CSRDelta_ByBuc25 = CSRDelta_ByBuc[CSRDelta_ByBuc["Bucket"].isin([25,"25"])]
    BucketCorr = np.identity(len(CSRDelta_ByBucExcept25))
    CSRDelta_M = Calc_AggregatedDeltaVega(CSRDelta_ByBucExcept25["KB_M"].values.astype(np.float64), CSRDelta_ByBucExcept25["SB"].values.astype(np.float64), BucketCorr, 0) + CSRDelta_ByBuc25["KB_M"].sum()
    CSRDelta_D = Calc_AggregatedDeltaVega(CSRDelta_ByBucExcept25["KB_D"].values.astype(np.float64), CSRDelta_ByBucExcept25["SB"].values.astype(np.float64), BucketCorr, 2) + CSRDelta_ByBuc25["KB_D"].sum()
    CSRDelta_U = Calc_AggregatedDeltaVega(CSRDelta_ByBucExcept25["KB_U"].values.astype(np.float64), CSRDelta_ByBucExcept25["SB"].values.astype(np.float64), BucketCorr, 1) + CSRDelta_ByBuc25["KB_U"].sum()
    SB = CSRDelta_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,CSRDelta_U, CSRDelta_M, CSRDelta_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([CSRDelta_ByBuc, Result],axis = 0)    

def Calc_CSRSecuritizedNonCTPCurvature(CurvatureData, CSR_SecuritizedNonCTPDelta_RW, DeltaSensitivityColumnName = "Delta") :
    CurvatureData = CurvatureData[CurvatureData["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])]
    if len(CurvatureData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    

    if CurvatureData["CVR_Plus"].isna().sum() == len(CurvatureData) and CurvatureData["CVR_Minus"].isna().sum() == len(CurvatureData) :    
        CurvatureData["RW"] = CurvatureData["Bucket"].astype(np.int64).map(CSR_SecuritizedNonCTPDelta_RW).fillna(0)
        CurvatureData["DeltaWeightedSensi"] = CurvatureData["RW"] * CurvatureData[DeltaSensitivityColumnName]
        
    KB_Median = CurvatureData.groupby("Bucket").apply(Calc_CSRKb_Curvature, 'm').reset_index()
    KB_Median25 = KB_Median[KB_Median["Bucket"].isin([25,'25'])].set_index("Bucket")
    KB_Median = KB_Median[KB_Median["Bucket"].isin([25,'25']) == False].set_index("Bucket")
    
    KB_Up = CurvatureData.groupby("Bucket").apply(Calc_CSRKb_Curvature, 'u').reset_index()
    KB_Up25 = KB_Up[KB_Up["Bucket"].isin([25,'25'])].set_index("Bucket")
    KB_Up = KB_Up[KB_Up["Bucket"].isin([25,'25']) == False].set_index("Bucket")

    KB_Dn = CurvatureData.groupby("Bucket").apply(Calc_CSRKb_Curvature, 'd').reset_index()
    KB_Dn25 = KB_Dn[KB_Dn["Bucket"].isin([25,'25'])].set_index("Bucket")
    KB_Dn = KB_Dn[KB_Dn["Bucket"].isin([25,'25']) == False].set_index("Bucket")

    SB = max(max(KB_Dn["SB"].sum(), KB_Median["SB"].sum()),KB_Dn["SB"].sum())
    SB +=  max(max(KB_Dn25["SB"].sum(), KB_Median25["SB"].sum()),KB_Dn25["SB"].sum()) 
    Data = pd.concat([KB_Up["KB"],KB_Median["KB"],KB_Dn["KB"]],axis = 1)
    Data.columns = ["KB_U","KB_M","KB_D"]
    Data["SB"] = np.maximum(np.maximum(KB_Median["SB"],KB_Up["SB"]),KB_Dn["SB"])
    DataByBucket = Data.reset_index()
    BucketCorr = np.identity(len(DataByBucket))
    
    KbPlus_Median = KB_Median["KB_PLUS"].values.astype(np.float64)
    KbMinus_Median = KB_Median["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Median = KB_Median["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Median = KB_Median["SB_MINUS"].values.astype(np.float64)

    KbPlus_Up = KB_Up["KB_PLUS"].values.astype(np.float64)
    KbMinus_Up = KB_Up["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Up = KB_Up["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Up = KB_Up["SB_MINUS"].values.astype(np.float64)

    KbPlus_Dn = KB_Dn["KB_PLUS"].values.astype(np.float64)
    KbMinus_Dn = KB_Dn["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Dn = KB_Dn["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Dn = KB_Dn["SB_MINUS"].values.astype(np.float64)

    Curvature_Median = Calc_AggregatedCurvature(KbPlus_Median, KbMinus_Median, SumCVRPlus_Median, SumCVRMinus_Median, BucketCorr, 0) + max(KB_Median25["KB_PLUS"].sum(),KB_Median25["KB_MINUS"].sum())
    Curvature_Up = Calc_AggregatedCurvature(KbPlus_Up, KbMinus_Up, SumCVRPlus_Up, SumCVRMinus_Up, BucketCorr, 1) + max(KB_Up25["KB_PLUS"].sum(),KB_Up25["KB_MINUS"].sum())
    Curvature_Dn = Calc_AggregatedCurvature(KbPlus_Dn, KbMinus_Dn, SumCVRPlus_Dn, SumCVRMinus_Dn, BucketCorr, 2) + max(KB_Dn25["KB_PLUS"].sum(),KB_Dn25["KB_MINUS"].sum())
    Result = pd.DataFrame([[99999,Curvature_Up, Curvature_Median, Curvature_Dn, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([DataByBucket, Result],axis = 0)    

def Calc_CSRSecuritizedNonCTPVega_KB(DataByBucket, CorrScenario = 'm') : 
    
    # Sensi Netting
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Curve","Tenor","Tranche"], CurvatureFlag = 0)
    if len(sensidata) < 1 : 
        return 0
    tc = tenorcorr(sensidata["Tenor"])
    corrsensi = CSR_SecuritizedNonCTPDelta_sensicorr(sensidata["BucketCopy"].iloc[0], sensidata["Tranche"], sensidata["Tenor"].astype(np.float64), sensidata["Curve"]) * tc
        
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    KB = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), corrsensi, ScenarioFlag)
    return KB    

def Calc_CSRSecuritizedNonCTPVega_KB_ByBucket(MyData) : 
    MyData["BucketCopy"] = MyData["Bucket"]

    KBByBucket_M = MyData.groupby("Bucket").apply(Calc_CSRSecuritizedNonCTPVega_KB, 'm')
    KBByBucket_D = MyData.groupby("Bucket").apply(Calc_CSRSecuritizedNonCTPVega_KB, 'd')
    KBByBucket_U = MyData.groupby("Bucket").apply(Calc_CSRSecuritizedNonCTPVega_KB, 'u')
    SBByBucket = MyData.groupby("Bucket").apply(calcsb)

    Data = pd.concat([KBByBucket_U,KBByBucket_M,KBByBucket_D,SBByBucket],axis = 1).reset_index()
    Data.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    return Data

def Calc_CSRSecuritizedNonCTPVega(VegaData, SensitivityColumnName = "Vega") :
    MyData = VegaData[VegaData["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])]
    if len(MyData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])       
    MyData["RW"] = VegaRiskWeight(MyData["Risk_Class"].values, MyData["Bucket"].values)
    MyData["WeightedSensi"] = MyData["RW"] * MyData[SensitivityColumnName]
    CSRVega_ByBuc = Calc_CSRSecuritizedNonCTPVega_KB_ByBucket(MyData)
    CSRVega_ByBucExcept25 = CSRVega_ByBuc[CSRVega_ByBuc["Bucket"].isin([25,"25"]) == False]
    CSRVega_ByBuc25 = CSRVega_ByBuc[CSRVega_ByBuc["Bucket"].isin([25,"25"])]
    BucketCorr = np.identity(len(CSRVega_ByBucExcept25))
    CSRDelta_M = Calc_AggregatedDeltaVega(CSRVega_ByBucExcept25["KB_M"].values.astype(np.float64), CSRVega_ByBucExcept25["SB"].values.astype(np.float64), BucketCorr, 0) + CSRVega_ByBuc25["KB_M"].sum()
    CSRDelta_D = Calc_AggregatedDeltaVega(CSRVega_ByBucExcept25["KB_D"].values.astype(np.float64), CSRVega_ByBucExcept25["SB"].values.astype(np.float64), BucketCorr, 2) + CSRVega_ByBuc25["KB_D"].sum()
    CSRDelta_U = Calc_AggregatedDeltaVega(CSRVega_ByBucExcept25["KB_U"].values.astype(np.float64), CSRVega_ByBucExcept25["SB"].values.astype(np.float64), BucketCorr, 1) + CSRVega_ByBuc25["KB_U"].sum()
    SB = CSRVega_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,CSRDelta_U, CSRDelta_M, CSRDelta_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([CSRVega_ByBuc, Result],axis = 0) 

def Calc_GIRRDelta_KB(DataByBucket, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, CorrScenario = 'm') :
    
    # Sensi Netting
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Curve","Tenor","Type"], CurvatureFlag = 0)
    if len(sensidata) < 1 : 
        return 0
    
    corrsensi = Calc_GIRRDeltaSensiCorr(sensidata["Type"], sensidata["Curve"], sensidata["Tenor"].astype(np.float64), GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr)
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    KB = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), corrsensi, ScenarioFlag)
    return float(KB)

def Calc_GIRRDelta_KB_ByBucket(MyData, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, SensitivityColumnName = "Delta") : 
    MyData["BucketCopy"] = MyData["Bucket"]
    MyData["WeightedSensi"] = MyData["RW"] * MyData[SensitivityColumnName]
    
    KBByBucket_M = MyData.groupby("Bucket").apply(Calc_GIRRDelta_KB, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr,'m')
    KBByBucket_D = MyData.groupby("Bucket").apply(Calc_GIRRDelta_KB, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr,'d')
    KBByBucket_U = MyData.groupby("Bucket").apply(Calc_GIRRDelta_KB, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr,'u')    
    SBByBucket = MyData.groupby("Bucket").apply(calcsb)
    
    Data = pd.concat([KBByBucket_U,KBByBucket_M,KBByBucket_D,SBByBucket],axis = 1).reset_index()
    Data.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    return Data

def GIRRBucketCorr(MyData) : 
    grirbc = 0.5
    c = np.identity(len(MyData)) * (1-grirbc) + grirbc
    return c

def Calc_GIRRDelta(Delta_Data, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, SensitivityColumnName = "Delta") :
    MyData = Delta_Data[Delta_Data["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])]
    if len(MyData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    MyData["RW"] = GIRR_DeltaRiskWeight(MyData["Tenor"].values, MyData["Bucket"].values, MyData["Type"].values)
    GIRRDelta_ByBuc = Calc_GIRRDelta_KB_ByBucket(MyData, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, SensitivityColumnName )
    BucketCorr = GIRRBucketCorr(GIRRDelta_ByBuc)

    GIRRDelta_M = Calc_AggregatedDeltaVega(GIRRDelta_ByBuc["KB_M"].values.astype(np.float64), GIRRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 0)
    GIRRDelta_D = Calc_AggregatedDeltaVega(GIRRDelta_ByBuc["KB_D"].values.astype(np.float64), GIRRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 2)
    GIRRDelta_U = Calc_AggregatedDeltaVega(GIRRDelta_ByBuc["KB_U"].values.astype(np.float64), GIRRDelta_ByBuc["SB"].values.astype(np.float64), BucketCorr, 1)
    SB = GIRRDelta_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,GIRRDelta_U, GIRRDelta_M, GIRRDelta_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])

    return pd.concat([GIRRDelta_ByBuc, Result],axis = 0)   

def Calc_GIRRKb_Curvature(Data_Sensi, CorrScenario, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensitivityColumnName = "Delta") : 
    if Data_Sensi["CVR_Plus"].isna().sum() == len(Data_Sensi) and Data_Sensi["CVR_Minus"].isna().sum() == len(Data_Sensi) :    
        V = Data_Sensi["Value"].values.astype(np.float64)
        DeltaWS = Data_Sensi["DeltaWeightedSensi"].values
        Data_Sensi["CVR_Plus"] = Calc_CVR(Data_Sensi["Value_Up"].values.astype(np.float64), V, DeltaWS, 0)
        Data_Sensi["CVR_Minus"] = Calc_CVR(Data_Sensi["Value_Dn"].values.astype(np.float64), V, DeltaWS, 1)
        
    if len(Data_Sensi) > 0:
        Kb_plus = max(0,Data_Sensi["CVR_Plus"].sum())
        Kb_minus = max(0,Data_Sensi["CVR_Minus"].sum())
        Kb = max(Kb_plus, Kb_minus)
        Sb_plus = Data_Sensi["CVR_Plus"].sum()
        Sb_minus = Data_Sensi["CVR_Minus"].sum()    
        CurvatureScenario = 0 if Kb_plus > Kb_minus else 1
        Sb = Sb_plus if CurvatureScenario == 0 else Sb_minus
    else :
        Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, CurvatureScenario = 0,0,0,0,0,0,0
    return pd.Series([Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, int(CurvatureScenario), CorrScenario], index = ["KB","KB_PLUS","KB_MINUS","SB","SB_PLUS","SB_MINUS","PLUS0MINUS1","CorrScenario"])

def Calc_GIRRCurvature(CurvatureData, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensitivityColumnName = "Delta") :
    CurvatureData = CurvatureData[CurvatureData["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])]
    if len(CurvatureData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    CurvatureData["Curve"] = CurvatureData["Curve"].fillna("NaN")
    CurvatureData["Tenor"] = CurvatureData["Tenor"].fillna("NaN")
    CurvatureData["Type"] = CurvatureData["Type"].fillna("NaN")
    if CurvatureData["CVR_Plus"].isna().sum() == len(CurvatureData) and CurvatureData["CVR_Minus"].isna().sum() == len(CurvatureData) :    
        CurvatureData["RW"] = GIRR_DeltaRiskWeight(CurvatureData["Tenor"].values, CurvatureData["Bucket"].values, CurvatureData["Type"].values)
        CurvatureData["DeltaWeightedSensi"] = CurvatureData["RW"] * CurvatureData[DeltaSensitivityColumnName]    
    
    KB_Median = CurvatureData.groupby("Bucket").apply(Calc_GIRRKb_Curvature, "m", GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensitivityColumnName)
    KB_Up = CurvatureData.groupby("Bucket").apply(Calc_GIRRKb_Curvature, "u", GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensitivityColumnName)
    KB_Dn = CurvatureData.groupby("Bucket").apply(Calc_GIRRKb_Curvature, "d", GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensitivityColumnName)
    SB = max(max(KB_Dn["SB"].sum(), KB_Median["SB"].sum()),KB_Dn["SB"].sum())
    Data = pd.concat([KB_Up["KB"],KB_Median["KB"],KB_Dn["KB"]],axis = 1)
    Data.columns = ["KB_U","KB_M","KB_D"]
    Data["SB"] = np.maximum(np.maximum(KB_Median["SB"],KB_Up["SB"]),KB_Dn["SB"])
    DataByBucket = Data.reset_index()
    KB_Corr = (GIRRBucketCorr(KB_Median))**2

    KbPlus_Median = KB_Median["KB_PLUS"].values.astype(np.float64)
    KbMinus_Median = KB_Median["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Median = KB_Median["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Median = KB_Median["SB_MINUS"].values.astype(np.float64)

    KbPlus_Up = KB_Up["KB_PLUS"].values.astype(np.float64)
    KbMinus_Up = KB_Up["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Up = KB_Up["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Up = KB_Up["SB_MINUS"].values.astype(np.float64)

    KbPlus_Dn = KB_Dn["KB_PLUS"].values.astype(np.float64)
    KbMinus_Dn = KB_Dn["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Dn = KB_Dn["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Dn = KB_Dn["SB_MINUS"].values.astype(np.float64)

    Curvature_Median = Calc_AggregatedCurvature(KbPlus_Median, KbMinus_Median, SumCVRPlus_Median, SumCVRMinus_Median, KB_Corr, 0)
    Curvature_Up = Calc_AggregatedCurvature(KbPlus_Up, KbMinus_Up, SumCVRPlus_Up, SumCVRMinus_Up, KB_Corr, 1)
    Curvature_Dn = Calc_AggregatedCurvature(KbPlus_Dn, KbMinus_Dn, SumCVRPlus_Dn, SumCVRMinus_Dn, KB_Corr, 2)
    Result = pd.DataFrame([[99999,Curvature_Up, Curvature_Median, Curvature_Dn, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([DataByBucket, Result],axis = 0)   
             
def Calc_GIRRVega_KB(DataByBucket, CorrScenario = 'm') : 
    
    # Sensi Netting
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Curve","Tenor1","Tenor2"], CurvatureFlag = 0)
    if len(sensidata) < 1 : 
        return 0
    
    sensicorr = GIRR_VegaSensiCorr(sensidata["Tenor1"], sensidata["Tenor2"])
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    Kb = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), sensicorr, ScenarioFlag)
    return Kb    

def Calc_GIRRVega_KB_ByBucket(VegaData, SensitivityColumnName = "Vega") : 
    if "RW" not in VegaData.columns:
        VegaData["RW"] = VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
        VegaData["WeightedSensi"] = VegaData["RW"] * VegaData[SensitivityColumnName]    
    KBByBucket_M = VegaData.groupby("Bucket").apply(Calc_GIRRVega_KB,'m')
    KBByBucket_D = VegaData.groupby("Bucket").apply(Calc_GIRRVega_KB,'d')
    KBByBucket_U = VegaData.groupby("Bucket").apply(Calc_GIRRVega_KB,'u')   
    SBByBucket = VegaData.groupby("Bucket").apply(calcsb)
    
    Data = pd.concat([KBByBucket_U,KBByBucket_M,KBByBucket_D,SBByBucket],axis = 1).reset_index()
    Data.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]    
    return Data

def Calc_GIRRVega(VegaData, SensitivityColumnName = "Vega") :    
    VegaData = VegaData[VegaData["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])]
    if len(VegaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    
    VegaData["RW"] = VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
    VegaData["WeightedSensi"] = VegaData["RW"] * VegaData[SensitivityColumnName]    
    VegaData["Curve"] = VegaData["Curve"].fillna("NaN")
    VegaData["Tenor1"] = VegaData["Tenor1"].fillna("NaN")
    VegaData["Tenor2"] = VegaData["Tenor2"].fillna("NaN")    
    GIRRVega_ByBuc = Calc_GIRRVega_KB_ByBucket(VegaData, SensitivityColumnName)
    BucketCorr = GIRRBucketCorr(GIRRVega_ByBuc)
    GIRRVega_M = Calc_AggregatedDeltaVega(GIRRVega_ByBuc["KB_M"].values.astype(np.float64), GIRRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 0)
    GIRRVega_D = Calc_AggregatedDeltaVega(GIRRVega_ByBuc["KB_D"].values.astype(np.float64), GIRRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 2)
    GIRRVega_U = Calc_AggregatedDeltaVega(GIRRVega_ByBuc["KB_U"].values.astype(np.float64), GIRRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 1)
    SB = GIRRVega_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,GIRRVega_U, GIRRVega_M, GIRRVega_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([GIRRVega_ByBuc, Result],axis = 0) 

def FXRBucketCorr(MyData) : 
    grirbc = 0.6
    c = np.identity(len(MyData)) * (1-grirbc) + grirbc
    return c

def Calc_FXRDelta(FXRDeltaData, HighLiquidCurrency, SensitivityColumnName = "Delta") :    
    FXRDeltaData = FXRDeltaData[FXRDeltaData["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])]    
    if len(FXRDeltaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    FXRDeltaData["RW"] = FXRDeltaData["Bucket"].apply(lambda x : FX_DeltaRiskWeight(x, HighLiquidCurrency))
    FXRDeltaData["WeightedSensi"] = FXRDeltaData["RW"] * FXRDeltaData[SensitivityColumnName]
    FXR_SB_ByBucket = FXRDeltaData.groupby("Bucket")["WeightedSensi"].sum()
    FXR_KB_ByBucket = np.abs(FXR_SB_ByBucket)
    BucketCorr = FXRBucketCorr(FXR_KB_ByBucket)
    Data = pd.concat([FXR_KB_ByBucket,FXR_KB_ByBucket,FXR_KB_ByBucket,FXR_SB_ByBucket],axis=1)
    Data.columns = ["KB_U","KB_M","KB_D","SB"]

    KB_M = Calc_AggregatedDeltaVega(Data["KB_U"].values.astype(np.float64), Data["SB"].values.astype(np.float64), BucketCorr, 0)
    KB_U = Calc_AggregatedDeltaVega(Data["KB_M"].values.astype(np.float64), Data["SB"].values.astype(np.float64), BucketCorr, 1)
    KB_D = Calc_AggregatedDeltaVega(Data["KB_D"].values.astype(np.float64), Data["SB"].values.astype(np.float64), BucketCorr, 2)
    Data_ByBucket = Data.reset_index()
    SB = Data_ByBucket["SB"].sum()
    Result = pd.DataFrame([[99999,KB_U, KB_M, KB_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([Data_ByBucket, Result],axis = 0) 

def Calc_FXRKb_Curvature(Data_Sensi, CorrScenario, DeltaSensitivityColumnName = "Delta") : 
    if Data_Sensi["CVR_Plus"].isna().sum() == len(Data_Sensi) and Data_Sensi["CVR_Minus"].isna().sum() == len(Data_Sensi) :    
        Data_Sensi["DeltaWeightedSensi"] = Data_Sensi["RW"] * Data_Sensi[DeltaSensitivityColumnName]    
        V = Data_Sensi["Value"].values.astype(np.float64)
        DeltaWS = Data_Sensi["DeltaWeightedSensi"].values
        Data_Sensi["CVR_Plus"] = Calc_CVR(Data_Sensi["Value_Up"].values.astype(np.float64), V, DeltaWS, 0)
        Data_Sensi["CVR_Minus"] = Calc_CVR(Data_Sensi["Value_Dn"].values.astype(np.float64), V, DeltaWS, 1)
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    Kb_plus = max(0.,Data_Sensi["CVR_Plus"].sum())
    Kb_minus =max(0.,Data_Sensi["CVR_Minus"].sum())
    Kb = max(Kb_plus, Kb_minus)
    Sb_plus = Data_Sensi["CVR_Plus"].sum()
    Sb_minus = Data_Sensi["CVR_Minus"].sum()    
    CurvatureScenario = 0 if Kb_plus > Kb_minus else 1
    Sb = Sb_plus if CurvatureScenario == 0 else Sb_minus
    return pd.Series([Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, int(CurvatureScenario), CorrScenario], index = ["KB","KB_PLUS","KB_MINUS","SB","SB_PLUS","SB_MINUS","PLUS0MINUS1","CorrScenario"])

def Calc_FXRCurvature(FXRCurvatureData, HighLiquidCurrency, DeltaSensitivityColumnName = "Delta") :   
    FXRCurvatureData = FXRCurvatureData[FXRCurvatureData["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])]                            
    if len(FXRCurvatureData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])        
    FXRCurvatureData["RW"] = FXRCurvatureData["Bucket"].apply(lambda x : FX_DeltaRiskWeight(x, HighLiquidCurrency))
    FXRCurvatureData["DeltaWeightedSensi"] = FXRCurvatureData["RW"] * FXRCurvatureData[DeltaSensitivityColumnName]

    KB_Median = FXRCurvatureData.groupby("Bucket").apply(Calc_FXRKb_Curvature, "m", DeltaSensitivityColumnName)
    KB_Up = FXRCurvatureData.groupby("Bucket").apply(Calc_FXRKb_Curvature, "u", DeltaSensitivityColumnName)
    KB_Dn = FXRCurvatureData.groupby("Bucket").apply(Calc_FXRKb_Curvature, "d", DeltaSensitivityColumnName)
    SB = max(max(KB_Dn["SB"].sum(), KB_Median["SB"].sum()),KB_Dn["SB"].sum())
    Data = pd.concat([KB_Up["KB"],KB_Median["KB"],KB_Dn["KB"]],axis = 1)
    Data.columns = ["KB_U","KB_M","KB_D"]
    Data["SB"] = np.maximum(np.maximum(KB_Median["SB"],KB_Up["SB"]),KB_Dn["SB"])
    DataByBucket = Data.reset_index()
    KB_Corr = (FXRBucketCorr(KB_Median))**2

    KbPlus_Median = KB_Median["KB_PLUS"].values.astype(np.float64)
    KbMinus_Median = KB_Median["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Median = KB_Median["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Median = KB_Median["SB_MINUS"].values.astype(np.float64)

    KbPlus_Up = KB_Up["KB_PLUS"].values.astype(np.float64)
    KbMinus_Up = KB_Up["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Up = KB_Up["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Up = KB_Up["SB_MINUS"].values.astype(np.float64)

    KbPlus_Dn = KB_Dn["KB_PLUS"].values.astype(np.float64)
    KbMinus_Dn = KB_Dn["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Dn = KB_Dn["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Dn = KB_Dn["SB_MINUS"].values.astype(np.float64)

    Curvature_Median = Calc_AggregatedCurvature(KbPlus_Median, KbMinus_Median, SumCVRPlus_Median, SumCVRMinus_Median, KB_Corr, 0)
    Curvature_Up = Calc_AggregatedCurvature(KbPlus_Up, KbMinus_Up, SumCVRPlus_Up, SumCVRMinus_Up, KB_Corr, 1)
    Curvature_Dn = Calc_AggregatedCurvature(KbPlus_Dn, KbMinus_Dn, SumCVRPlus_Dn, SumCVRMinus_Dn, KB_Corr, 2)
    Result = pd.DataFrame([[99999,Curvature_Up, Curvature_Median, Curvature_Dn, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([DataByBucket, Result],axis = 0)       
    
def FXR_VegaSensiCorr(OptTenorList) : 
    n = len(OptTenorList)
    OptTenorList = list(OptTenorList)
    targetarray = np.identity(n) 
    for i in range(n) : 
        for j in range(n) : 
            if i == j : 
                targetarray[i][j] = 1
            else : 
                c = optionmaturitycorr(float(OptTenorList[i]),float(OptTenorList[j]))
                targetarray[i][j] = min(1,c)
    return targetarray
    
def Calc_FXRVega_KB(DataByBucket, CorrScenario = 'm') : 
    
    # Sensi Netting
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Curve","Tenor"], CurvatureFlag = 0)
    if len(sensidata) < 1 : 
        return 0
    
    sensicorr = FXR_VegaSensiCorr(list(sensidata["Tenor"]))
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    Kb = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), sensicorr, ScenarioFlag)
    return Kb    

def Calc_FXRVega_KB_ByBucket(VegaData, SensitivityColumnName = "Vega") : 
    if "RW" not in VegaData.columns : 
        VegaData["RW"] =  VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
        VegaData["WeightedSensi"] = VegaData["RW"] * VegaData[SensitivityColumnName]    
    KBByBucket_M = VegaData.groupby("Bucket").apply(Calc_FXRVega_KB,'m')
    KBByBucket_D = VegaData.groupby("Bucket").apply(Calc_FXRVega_KB,'d')
    KBByBucket_U = VegaData.groupby("Bucket").apply(Calc_FXRVega_KB,'u')   
    SBByBucket = VegaData.groupby("Bucket").apply(calcsb)
    
    Data = pd.concat([KBByBucket_U,KBByBucket_M,KBByBucket_D,SBByBucket],axis = 1).reset_index()
    Data.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]    
    return Data

def Calc_FXRVega(VegaData, SensitivityColumnName = "Vega") :    
    VegaData = VegaData[VegaData["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])]    
    if len(VegaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    
    VegaData["Bucket"] = VegaData["Bucket"].fillna("NaN")
    VegaData["Curve"] = VegaData["Curve"].fillna("NaN")
    VegaData["Tenor"] = VegaData["Tenor"].fillna("NaN")
    VegaData["RW"] =  VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
    VegaData["WeightedSensi"] = VegaData["RW"] * VegaData[SensitivityColumnName]    
    FXRVega_ByBuc = Calc_FXRVega_KB_ByBucket(VegaData, SensitivityColumnName)
    BucketCorr = FXRBucketCorr(FXRVega_ByBuc)
    FXRVega_M = Calc_AggregatedDeltaVega(FXRVega_ByBuc["KB_M"].values.astype(np.float64), FXRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 0)
    FXRVega_D = Calc_AggregatedDeltaVega(FXRVega_ByBuc["KB_D"].values.astype(np.float64), FXRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 2)
    FXRVega_U = Calc_AggregatedDeltaVega(FXRVega_ByBuc["KB_U"].values.astype(np.float64), FXRVega_ByBuc["SB"].values.astype(np.float64), BucketCorr, 1)
    SB = FXRVega_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,FXRVega_U, FXRVega_M, FXRVega_D, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([FXRVega_ByBuc, Result],axis = 0)     

def Calc_EQRDelta_KB(DataByBucket, CorrScenario = 'm') : 
    groupped = PivotSensiByRiskFactor(DataByBucket, ["Type","StockName"], CurvatureFlag = 0)
    if len(groupped) == 0 : 
        return 0
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    c = EquityDeltaInBucketSensiCorr(groupped["BucketCopy"].iloc[0], groupped["Type"], groupped["StockName"])
    KB = Calc_Kb_DeltaVega(groupped["WeightedSensi"].values.astype(np.float64), c, ScenarioFlag)
    return KB

def Calc_EQRDelta(DeltaData, SensitivityColumnName = "Delta") : 
    DeltaData = DeltaData[DeltaData["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])]        
    if len(DeltaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    DeltaData = DeltaData.copy()
    DeltaData["BucketCopy"] = DeltaData["Bucket"]
    DeltaData["RW"] = MapEquityRiskWeight(DeltaData, EQDeltaRWMappingDF, TypeColName = "Type",BucketColName = "Bucket")
    DeltaData["WeightedSensi"] = DeltaData["RW"] * DeltaData[SensitivityColumnName]
    
    KB_M = DeltaData.groupby("Bucket").apply(Calc_EQRDelta_KB,'m')
    KB_D = DeltaData.groupby("Bucket").apply(Calc_EQRDelta_KB,'d')
    KB_U = DeltaData.groupby("Bucket").apply(Calc_EQRDelta_KB,'u')
    SB = DeltaData.groupby("Bucket").apply(calcsb)
    
    EQRDelta_ByBuc = pd.concat([KB_U,KB_M,KB_D,SB],axis=1).reset_index()
    EQRDelta_ByBuc.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    
    c = EquityDeltaBucketAggregatedCorr(EQRDelta_ByBuc["Bucket"])
    EQRDelta_M = Calc_AggregatedDeltaVega(EQRDelta_ByBuc["KB_M"].values.astype(np.float64), EQRDelta_ByBuc["SB"].values.astype(np.float64),c,0)
    EQRDelta_U = Calc_AggregatedDeltaVega(EQRDelta_ByBuc["KB_U"].values.astype(np.float64), EQRDelta_ByBuc["SB"].values.astype(np.float64),c,1)
    EQRDelta_D = Calc_AggregatedDeltaVega(EQRDelta_ByBuc["KB_D"].values.astype(np.float64), EQRDelta_ByBuc["SB"].values.astype(np.float64),c,2)
    TOTALSB = EQRDelta_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,EQRDelta_U, EQRDelta_M, EQRDelta_D, TOTALSB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([EQRDelta_ByBuc, Result],axis = 0)     
    
def Calc_EQRKb_Curvature(DataByBucket, CorrScenario, DeltaSensitivityColumnName = "Delta") : 
    if DataByBucket["CVR_Plus"].isna().sum() == len(DataByBucket) and DataByBucket["CVR_Minus"].isna().sum() == len(DataByBucket) :    
        V = DataByBucket["Value"].values.astype(np.float64)
        DeltaWS = DataByBucket["DeltaWeightedSensi"].values
        DataByBucket["CVR_Plus"] = Calc_CVR(DataByBucket["Value_Up"].values.astype(np.float64), V, DeltaWS, 0)
        DataByBucket["CVR_Minus"] = Calc_CVR(DataByBucket["Value_Dn"].values.astype(np.float64), V, DeltaWS, 1)
    groupped = PivotSensiByRiskFactor(DataByBucket, ["Type","StockName"], CurvatureFlag = 1)
    CVRP = groupped["CVR_Plus"].values.astype(np.float64)
    CVRM = groupped["CVR_Minus"].values.astype(np.float64)
    TYPE = groupped["Type"]
    NAME = groupped["StockName"]

    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    c = EquityDeltaInBucketSensiCorr(DataByBucket["BucketCopy"].iloc[0], TYPE, NAME)**2
    Kb_plus = Calc_Kb_Curvature(CVRP, c , ScenarioFlag)
    Kb_minus = Calc_Kb_Curvature(CVRM, c , ScenarioFlag)
    Kb = max(Kb_plus, Kb_minus)
    Sb_plus = DataByBucket["CVR_Plus"].sum()
    Sb_minus = DataByBucket["CVR_Minus"].sum()    
    CurvatureScenario = 0 if Kb_plus > Kb_minus else 1
    Sb = Sb_plus if CurvatureScenario == 0 else Sb_minus
    return pd.Series([Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, int(CurvatureScenario), CorrScenario], index = ["KB","KB_PLUS","KB_MINUS","SB","SB_PLUS","SB_MINUS","PLUS0MINUS1","CorrScenario"])    
    
def Calc_EQRCurvature(CurvatureData, EQDeltaRWMappingDF, DeltaSensitivityColumnName = "Delta_Sensi") :  
    CurvatureData = CurvatureData[CurvatureData["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])]                                
    if len(CurvatureData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    CurvatureData = CurvatureData.copy()
    CurvatureData["StockName"] = CurvatureData["StockName"].fillna("NaN")
    CurvatureData["Type"] = CurvatureData["Type"].fillna("NaN")
    CurvatureData["BucketCopy"] = CurvatureData["Bucket"]
    
    CurvatureData["RW"] = MapEquityRiskWeight(CurvatureData, EQDeltaRWMappingDF, TypeColName = "Type",BucketColName = "Bucket")
    CurvatureData["DeltaWeightedSensi"] = CurvatureData["RW"] * CurvatureData[DeltaSensitivityColumnName]
    KB_Median = CurvatureData.groupby("Bucket").apply(Calc_EQRKb_Curvature, "m", DeltaSensitivityColumnName)
    KB_Up = CurvatureData.groupby("Bucket").apply(Calc_EQRKb_Curvature, "u", DeltaSensitivityColumnName)
    KB_Dn = CurvatureData.groupby("Bucket").apply(Calc_EQRKb_Curvature, "d", DeltaSensitivityColumnName)
    SB = max(max(KB_Dn["SB"].sum(), KB_Median["SB"].sum()),KB_Dn["SB"].sum())
    Data = pd.concat([KB_Up["KB"],KB_Median["KB"],KB_Dn["KB"]],axis = 1)
    Data.columns = ["KB_U","KB_M","KB_D"]
    Data["SB"] = np.maximum(np.maximum(KB_Median["SB"],KB_Up["SB"]),KB_Dn["SB"])
    DataByBucket = Data.reset_index()
    KB_Corr = (EquityDeltaBucketAggregatedCorr(DataByBucket["Bucket"]))**2

    KbPlus_Median = KB_Median["KB_PLUS"].values.astype(np.float64)
    KbMinus_Median = KB_Median["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Median = KB_Median["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Median = KB_Median["SB_MINUS"].values.astype(np.float64)

    KbPlus_Up = KB_Up["KB_PLUS"].values.astype(np.float64)
    KbMinus_Up = KB_Up["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Up = KB_Up["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Up = KB_Up["SB_MINUS"].values.astype(np.float64)

    KbPlus_Dn = KB_Dn["KB_PLUS"].values.astype(np.float64)
    KbMinus_Dn = KB_Dn["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Dn = KB_Dn["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Dn = KB_Dn["SB_MINUS"].values.astype(np.float64)

    Curvature_Median = Calc_AggregatedCurvature(KbPlus_Median, KbMinus_Median, SumCVRPlus_Median, SumCVRMinus_Median, KB_Corr, 0)
    Curvature_Up = Calc_AggregatedCurvature(KbPlus_Up, KbMinus_Up, SumCVRPlus_Up, SumCVRMinus_Up, KB_Corr, 1)
    Curvature_Dn = Calc_AggregatedCurvature(KbPlus_Dn, KbMinus_Dn, SumCVRPlus_Dn, SumCVRMinus_Dn, KB_Corr, 2)
    Result = pd.DataFrame([[99999,Curvature_Up, Curvature_Median, Curvature_Dn, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([DataByBucket, Result],axis = 0)   

def Calc_EQRVega_KB(DataByBucket, CorrScenario = 'm') : 
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Tenor","StockName"])
    if len(sensidata) < 1 : 
        return 0
    c = EquityDeltaInBucketSensiCorr(sensidata["BucketCopy"].iloc[0], ["Price"] * len(sensidata) , sensidata["StockName"]) * tenorcorr(sensidata["Tenor"])
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    KB = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), c, ScenarioFlag)
    return KB

def Calc_EQRVega(VegaData, SensitivityColumnName = "Vega") : 
    VegaData = VegaData[VegaData["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])]        
    if len(VegaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    VegaData = VegaData.copy()
    VegaData["RW"] = VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
    VegaData["WeightedSensi"] = VegaData[SensitivityColumnName] * VegaData["RW"]
    VegaData["BucketCopy"] = VegaData["Bucket"]
    
    KB_M = VegaData.groupby("Bucket").apply(Calc_EQRVega_KB,'m')
    KB_D = VegaData.groupby("Bucket").apply(Calc_EQRVega_KB,'d')
    KB_U = VegaData.groupby("Bucket").apply(Calc_EQRVega_KB,'u')
    SB = VegaData.groupby("Bucket").apply(calcsb)
    
    EQRVega_ByBuc = pd.concat([KB_U,KB_M,KB_D,SB],axis=1).reset_index()
    EQRVega_ByBuc.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    
    c = EquityDeltaBucketAggregatedCorr(EQRVega_ByBuc["Bucket"])
    EQRVega_M = Calc_AggregatedDeltaVega(EQRVega_ByBuc["KB_M"].values.astype(np.float64), EQRVega_ByBuc["SB"].values.astype(np.float64),c,0)
    EQRVega_U = Calc_AggregatedDeltaVega(EQRVega_ByBuc["KB_U"].values.astype(np.float64), EQRVega_ByBuc["SB"].values.astype(np.float64),c,1)
    EQRVega_D = Calc_AggregatedDeltaVega(EQRVega_ByBuc["KB_D"].values.astype(np.float64), EQRVega_ByBuc["SB"].values.astype(np.float64),c,2)
    TOTALSB = EQRVega_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,EQRVega_U, EQRVega_M, EQRVega_D, TOTALSB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([EQRVega_ByBuc, Result],axis = 0)  

def Calc_COMRDelta_KB(DataByBucket, CorrScenario = 'm') : 
    sensidata = PivotSensiByRiskFactor(DataByBucket, ["Underlying","Tenor","Delivery"])
    if len(sensidata) == 0 : 
        return 0
    ScenarioFlag = 0 if 'm' in str(CorrScenario) else (1 if 'u' in str(CorrScenario) else 2)
    c = COMM_deltasensicorrbucket(sensidata["BucketCopy"].iloc[0], sensidata["Underlying"], sensidata["Tenor"], sensidata["Delivery"]) 
    KB = Calc_Kb_DeltaVega(sensidata["WeightedSensi"].values.astype(np.float64), c, ScenarioFlag)
    return KB

def Calc_COMRDelta(DeltaData, DeltaSensitivityColumnName = "Delta") : 
    DeltaData = DeltaData[DeltaData["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])]        
    
    if len(DeltaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    DeltaData = DeltaData.copy()
    DeltaData["RW"] = DeltaData["Bucket"].astype(np.int64).map(COMM_Delta_RWMapping)
    DeltaData["WeightedSensi"] = DeltaData["RW"] * DeltaData[DeltaSensitivityColumnName]
    DeltaData["BucketCopy"] = DeltaData["Bucket"]
    
    KB_M = DeltaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'m')
    KB_D = DeltaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'d')
    KB_U = DeltaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'u')
    SB = DeltaData.groupby("Bucket").apply(calcsb)
    
    COMRDelta_ByBuc = pd.concat([KB_U,KB_M,KB_D,SB],axis=1).reset_index()
    COMRDelta_ByBuc.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    
    c = COMM_DeltaBucketAggregatedCorr(COMRDelta_ByBuc["Bucket"])
    COMRDelta_M = Calc_AggregatedDeltaVega(COMRDelta_ByBuc["KB_M"].values.astype(np.float64), COMRDelta_ByBuc["SB"].values.astype(np.float64),c,0)
    COMRDelta_U = Calc_AggregatedDeltaVega(COMRDelta_ByBuc["KB_U"].values.astype(np.float64), COMRDelta_ByBuc["SB"].values.astype(np.float64),c,1)
    COMRDelta_D = Calc_AggregatedDeltaVega(COMRDelta_ByBuc["KB_D"].values.astype(np.float64), COMRDelta_ByBuc["SB"].values.astype(np.float64),c,2)
    TOTALSB = COMRDelta_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,COMRDelta_U, COMRDelta_M, COMRDelta_D, TOTALSB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([COMRDelta_ByBuc, Result],axis = 0)     
    
def Calc_COMRKb_Curvature(DataByBucket, CorrScenario, DeltaSensitivityColumnName = "Delta") : 
    if DataByBucket["CVR_Plus"].isna().sum() == len(DataByBucket) and DataByBucket["CVR_Minus"].isna().sum() == len(DataByBucket) :    
        V = DataByBucket["Value"].values.astype(np.float64)
        DeltaWS = DataByBucket["DeltaWeightedSensi"].values
        DataByBucket["CVR_Plus"] = Calc_CVR(DataByBucket["Value_Up"].values.astype(np.float64), V, DeltaWS, 0)
        DataByBucket["CVR_Minus"] = Calc_CVR(DataByBucket["Value_Dn"].values.astype(np.float64), V, DeltaWS, 1)

    Kb_plus = max(0, DataByBucket["CVR_Plus"].sum())
    Kb_minus = max(0, DataByBucket["CVR_Minus"].sum())
    Kb = max(Kb_plus, Kb_minus)
    Sb_plus = DataByBucket["CVR_Plus"].sum()
    Sb_minus = DataByBucket["CVR_Minus"].sum()    
    CurvatureScenario = 0 if Kb_plus > Kb_minus else 1
    Sb = Sb_plus if CurvatureScenario == 0 else Sb_minus
    return pd.Series([Kb, Kb_plus, Kb_minus, Sb, Sb_plus, Sb_minus, int(CurvatureScenario), CorrScenario], index = ["KB","KB_PLUS","KB_MINUS","SB","SB_PLUS","SB_MINUS","PLUS0MINUS1","CorrScenario"])    
    
def Calc_COMRCurvature(CurvatureData, DeltaSensitivityColumnName = "Delta") : 
    CurvatureData = CurvatureData[CurvatureData["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])]                                

    if len(CurvatureData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])    
    CurvatureData = CurvatureData.copy()
    CurvatureData["RW"] = CurvatureData["Bucket"].astype(np.int64).map(COMM_Delta_RWMapping)
    CurvatureData["DeltaWeightedSensi"] = CurvatureData["RW"] * CurvatureData[DeltaSensitivityColumnName]
    CurvatureData["BucketCopy"] = CurvatureData["Bucket"]
    
    KB_Median = CurvatureData.groupby("Bucket").apply(Calc_COMRKb_Curvature, "m", DeltaSensitivityColumnName)
    KB_Up = CurvatureData.groupby("Bucket").apply(Calc_COMRKb_Curvature, "u", DeltaSensitivityColumnName)
    KB_Dn = CurvatureData.groupby("Bucket").apply(Calc_COMRKb_Curvature, "d", DeltaSensitivityColumnName)
    SB = max(max(KB_Dn["SB"].sum(), KB_Median["SB"].sum()),KB_Dn["SB"].sum())
    Data = pd.concat([KB_Up["KB"],KB_Median["KB"],KB_Dn["KB"]],axis = 1)
    Data.columns = ["KB_U","KB_M","KB_D"]
    Data["SB"] = np.maximum(np.maximum(KB_Median["SB"],KB_Up["SB"]),KB_Dn["SB"])
    DataByBucket = Data.reset_index()    
    KB_Corr = COMM_DeltaBucketAggregatedCorr(DataByBucket["Bucket"])**2
    
    KbPlus_Median = KB_Median["KB_PLUS"].values.astype(np.float64)
    KbMinus_Median = KB_Median["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Median = KB_Median["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Median = KB_Median["SB_MINUS"].values.astype(np.float64)

    KbPlus_Up = KB_Up["KB_PLUS"].values.astype(np.float64)
    KbMinus_Up = KB_Up["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Up = KB_Up["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Up = KB_Up["SB_MINUS"].values.astype(np.float64)

    KbPlus_Dn = KB_Dn["KB_PLUS"].values.astype(np.float64)
    KbMinus_Dn = KB_Dn["KB_MINUS"].values.astype(np.float64)
    SumCVRPlus_Dn = KB_Dn["SB_PLUS"].values.astype(np.float64)
    SumCVRMinus_Dn = KB_Dn["SB_MINUS"].values.astype(np.float64)

    Curvature_Median = Calc_AggregatedCurvature(KbPlus_Median, KbMinus_Median, SumCVRPlus_Median, SumCVRMinus_Median, KB_Corr, 0)
    Curvature_Up = Calc_AggregatedCurvature(KbPlus_Up, KbMinus_Up, SumCVRPlus_Up, SumCVRMinus_Up, KB_Corr, 1)
    Curvature_Dn = Calc_AggregatedCurvature(KbPlus_Dn, KbMinus_Dn, SumCVRPlus_Dn, SumCVRMinus_Dn, KB_Corr, 2)
    Result = pd.DataFrame([[99999,Curvature_Up, Curvature_Median, Curvature_Dn, SB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([DataByBucket, Result],axis = 0)   
        
def Calc_COMRVega(VegaData, SensitivityColumnName = "Vega") : 
    VegaData = VegaData[VegaData["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])]            
    if len(VegaData) == 0 : 
        return pd.DataFrame([], columns = ["Bucket","KB_U","KB_M","KB_D","SB"])
    VegaData = VegaData.copy()
    VegaData["RW"] = VegaRiskWeight(VegaData["Risk_Class"].values, VegaData["Bucket"].values)
    VegaData["WeightedSensi"] = VegaData["RW"] * VegaData[SensitivityColumnName]
    VegaData["BucketCopy"] = VegaData["Bucket"]
    
    KB_M = VegaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'m')
    KB_D = VegaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'d')
    KB_U = VegaData.groupby("Bucket").apply(Calc_COMRDelta_KB,'u')
    SB = VegaData.groupby("Bucket").apply(calcsb)
    
    COMRVega_ByBuc = pd.concat([KB_U,KB_M,KB_D,SB],axis=1).reset_index()
    COMRVega_ByBuc.columns = ["Bucket","KB_U","KB_M","KB_D","SB"]
    
    c = COMM_DeltaBucketAggregatedCorr(COMRVega_ByBuc["Bucket"])
    COMRVega_M = Calc_AggregatedDeltaVega(COMRVega_ByBuc["KB_M"].values.astype(np.float64), COMRVega_ByBuc["SB"].values.astype(np.float64),c,0)
    COMRVega_U = Calc_AggregatedDeltaVega(COMRVega_ByBuc["KB_U"].values.astype(np.float64), COMRVega_ByBuc["SB"].values.astype(np.float64),c,1)
    COMRVega_D = Calc_AggregatedDeltaVega(COMRVega_ByBuc["KB_D"].values.astype(np.float64), COMRVega_ByBuc["SB"].values.astype(np.float64),c,2)
    TOTALSB = COMRVega_ByBuc["SB"].sum()
    Result = pd.DataFrame([[99999,COMRVega_U, COMRVega_M, COMRVega_D, TOTALSB]], columns = ["Bucket","KB_U","KB_M","KB_D","SB"], index = [99999])
    return pd.concat([COMRVega_ByBuc, Result],axis = 0)     

def CalcRRAORiskCharge(RRAO_Data) : 
    RRAO_Data = RRAO_Data[RRAO_Data["Risk_Class"].isin(["RRAO","잔여리스크","RRAO(잔여리스크)","잔여리스크(RRAO)"])]
    if len(RRAO_Data) > 0 : 
        exotic = RRAO_Data[RRAO_Data["Risk_Type"].apply(lambda x : True if 'exotic' in str(x).lower() else False)]
        etc = RRAO_Data[RRAO_Data["Risk_Type"].apply(lambda x : False if 'exotic' in str(x).lower() else True)]
        b1 = exotic["DRC_RRAO_Nominal"].astype(np.float64).sum() * 0.01
        b2 = etc["DRC_RRAO_Nominal"].astype(np.float64).sum() * 0.001
        rrao = b1 + b2 
        ResultData = pd.DataFrame([], index = [1,2,3])
        ResultData["Risk_Type"] = ["RRAO_Exotic","RRAO_Etc","99999"]
        ResultData["Bucket"] = ["RRAO_Exotic","RRAO_Etc","99999"]
        ResultData["KB_U"] = ResultData["KB_M"] = ResultData["KB_D"] = ResultData["SB"] = [b1, b2, rrao]
        ResultData["Risk_Class"] = "RRAO"
    else : 
        ResultData = pd.DataFrame([])
    return ResultData
        
def CalcDRC3RiskCharge(DRC_Data) : 
    if len(DRC_Data) > 0 : 
        DRC_Data["JTD"] = DRC_Data["DRC_RRAO_Nominal"].astype(np.float64) * DRC_Data["DRC_LGD"].astype(np.float64).fillna(0) * DRC_Data["DRC_Position"].astype(np.float64) + DRC_Data["DRC_PL"].fillna(0)
        DRC1Data = pd.DataFrame([])
        DRC2Data = pd.DataFrame([])
        DRC3Data = pd.DataFrame([])

        DRC1 = DRC[DRC["Risk_Type"].isin(["DRC","DRC1"])]
        if len(DRC1) > 0 : 
            DRC1["RW"] = DRC1["Rating"].apply(DRC_RW)
            DRC1_DRC_ByBuc = DRC1.groupby("Bucket").apply(DRC_b, "JTD")
            DRC1_DRC = DRC1_DRC_ByBuc.sum()    
            DRC1Data["Bucket"] = list(DRC1_DRC_ByBuc.index) + [99999]
            DRC1Data["KB_U"] = DRC1Data["KB_M"] = DRC1Data["KB_D"] = DRC1Data["SB"] = list(DRC1_DRC_ByBuc) + [DRC1_DRC]
        
        DRC2 = DRC[DRC["Risk_Type"].isin(["DRC","DRC1","DRC_CTP","DRC3"]) == False]
        if len(DRC2) > 0 : 
            DRC2["RW"] = DRC2["DRC_RW"].fillna(0)
            DRC2_DRC_ByBuc = DRC2.groupby("Bucket").apply(DRC_b, "JTD")
            DRC2_DRC = DRC2_DRC_ByBuc.sum()
            DRC2Data["Bucket"] = list(DRC2_DRC_ByBuc.index) + [99999]
            DRC2Data["KB_U"] = DRC2Data["KB_M"] = DRC2Data["KB_D"] = DRC2Data["SB"] = list(DRC2_DRC_ByBuc) + [DRC2_DRC]

        DRC3 = DRC[DRC["Risk_Type"].isin(["DRC_CTP","DRC3"])]
        if len(DRC3) > 0 :
            DRC3_Tranche = DRC3[DRC3["Issuer"].isin(["Tranche","tranche"])]
            DRC3_Tranche["RW"] = DRC3_Tranche["DRC_RW"].fillna(0)
            DRC3_NonTranche = DRC3[DRC3["Issuer"].isin(["Tranche","tranche"]) == False]
            DRC3_NonTranche["RW"] = DRC3_NonTranche["Rating"].apply(DRC_RW)
            DRC3_Adj = pd.concat([DRC3_Tranche, DRC3_NonTranche],axis = 0)
            HBRMap = DRC3_Adj.groupby("Bucket").apply(HBR_bucket, "JTD")
            DRC3_Adj["FixedHBR"] = DRC3_Adj["Bucket"].map(HBRMap)
            DRC3_Adj_DRC_ByBuc = DRC3_Adj.groupby("Bucket").apply(DRC_b, "JTD", 1)
            DRC3_DRC = max(0,(np.maximum(0, DRC3_Adj_DRC_ByBuc) + 0.5 * np.minimum(0, DRC3_Adj_DRC_ByBuc)).sum())
            DRC3Data["Bucket"] = list(DRC3_Adj_DRC_ByBuc.index) + [99999]
            DRC3Data["KB_U"] = DRC3Data["KB_M"] = DRC3Data["KB_D"] = DRC3Data["SB"] = list(DRC3_Adj_DRC_ByBuc) + [DRC3_DRC]
        DRC_NonSecNonCTP = DRC1Data
        DRC_NonSecNonCTP["Risk_Class"] = ["DRC"] * len(DRC1Data)
        DRC_NonSecNonCTP["Risk_Type"] = ["DRC_NonSec"] * len(DRC1Data)
        
        DRC_SecData = DRC2Data
        DRC_SecData["Risk_Class"] = ["DRC"] * len(DRC1Data)
        DRC_SecData["Risk_Type"] = ["DRC_SecNonCTP"] * len(DRC1Data)

        DRC_CTPData = DRC3Data
        DRC_CTPData["Risk_Class"] = ["DRC"] * len(DRC1Data)
        DRC_CTPData["Risk_Type"] = ["DRC_CTP"] * len(DRC1Data)
        
        return pd.concat([DRC_NonSecNonCTP, DRC_SecData, DRC_CTPData],axis = 0)
    else : 
        return pd.DataFrame([])
  
def AggregatedFRTB_RiskCharge(CSR_Data, GIRR_Data, FXR_Data, EQR_Data, COMR_Data, CSR_Sec_NonCTP_Data, CSR_CTP_Data, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 0, DRC = [], RRAO = []) : 
    if GroupbyFlag == 0 : 
        if (len(CSR_Data) > 0) :  
            CSRDelta_Total = Calc_CSRDelta(CSR_Data, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
            CSRCurvature_Total = Calc_CSRCurvature(CSR_Data, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
            CSRVega_Total = Calc_CSRVega(CSR_Data, CSR_DeltaNonSecurCorrDf,  VegaSensiName).reset_index()
        else : 
            CSRDelta_Total = CSRCurvature_Total = CSRVega_Total = pd.DataFrame([])

        if (len(CSR_Sec_NonCTP_Data) > 0) : 
            CSRSecNonCTP_Delta_Total = Calc_CSRSecuritizedNonCTPDelta(CSR_Sec_NonCTP_Data, CSR_SecuritizedNonCTPDelta_RW, DeltaSensiName).reset_index()
            CSRSecNonCTP_Curvature_Total = Calc_CSRSecuritizedNonCTPCurvature(CSR_Sec_NonCTP_Data, CSR_SecuritizedNonCTPDelta_RW, DeltaSensiName).reset_index()
            CSRSecNonCTP_Vega_Total = Calc_CSRSecuritizedNonCTPVega(CSR_Sec_NonCTP_Data, VegaSensiName).reset_index()
        else : 
            CSRSecNonCTP_Delta_Total = CSRSecNonCTP_Curvature_Total = CSRSecNonCTP_Vega_Total = pd.DataFrame([])

        if (len(CSR_CTP_Data) > 0) : 
            CSRCTPDelta_Total = Calc_CSRDelta(CSR_CTP_Data, CSR_DeltaNonSecurCorrDf, DeltaSensiName, 1).reset_index()
            CSRCTPCurvature_Total = Calc_CSRCurvature(CSR_CTP_Data, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
            CSRCTPVega_Total = Calc_CSRVega(CSR_CTP_Data, CSR_DeltaNonSecurCorrDf,  VegaSensiName).reset_index()
        else : 
            CSRCTPDelta_Total = CSRCTPCurvature_Total = CSRCTPVega_Total = pd.DataFrame([])

        if (len(GIRR_Data) > 0) : 
            GIRRDelta_Total = Calc_GIRRDelta(GIRR_Data, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
            GIRRCurvature_Total = Calc_GIRRCurvature(GIRR_Data, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
            GIRRVega_Total = Calc_GIRRVega(GIRR_Data, VegaSensiName).reset_index()
        else : 
            GIRRDelta_Total = GIRRCurvature_Total = GIRRVega_Total = pd.DataFrame([])            
        
        if (len(FXR_Data) > 0) : 
            FXRDelta_Total = Calc_FXRDelta(FXR_Data, HighLiquidCurrency, DeltaSensiName).reset_index()
            FXRCurvature_Total = Calc_FXRCurvature(FXR_Data, HighLiquidCurrency, DeltaSensiName).reset_index()
            FXRVega_Total = Calc_FXRVega(FXR_Data, VegaSensiName).reset_index()
        else : 
            FXRDelta_Total = FXRCurvature_Total = FXRVega_Total = pd.DataFrame([])     
        
        if (len(EQR_Data) > 0) : 
            EQRDelta_Total = Calc_EQRDelta(EQR_Data, DeltaSensiName).reset_index()
            EQRCurvature_Total = Calc_EQRCurvature(EQR_Data,EQDeltaRWMappingDF, DeltaSensiName).reset_index()
            EQRVega_Total = Calc_EQRVega(EQR_Data,VegaSensiName).reset_index()
        else : 
            EQRDelta_Total = EQRCurvature_Total = EQRVega_Total = pd.DataFrame([])     
                    
        if (len(COMR_Data) > 0) : 
            COMRDelta_Total = Calc_COMRDelta(COMR_Data, DeltaSensiName).reset_index()
            COMRCurvature_Total = Calc_COMRCurvature(COMR_Data, DeltaSensiName).reset_index()
            COMRVega_Total = Calc_COMRVega(COMR_Data, VegaSensiName).reset_index()  
        else : 
            COMRDelta_Total = COMRCurvature_Total = COMRVega_Total = pd.DataFrame([])  
                    
        if len(DRC) > 0 :
            DRC_Total = CalcDRC3RiskCharge(DRC).reset_index()
        
        if len(RRAO) > 0 : 
            RRAO_Total = CalcRRAORiskCharge(RRAO).reset_index()
        
    elif GroupbyFlag == 1 : 
        if (len(CSR_Data) > 0) :          
            CSRDelta_Total = CSR_Data.groupby("Depart").apply(Calc_CSRDelta, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
            CSRCurvature_Total = CSR_Data.groupby("Depart").apply(Calc_CSRCurvature, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
            CSRVega_Total = CSR_Data.groupby("Depart").apply(Calc_CSRVega, CSR_DeltaNonSecurCorrDf,  VegaSensiName).reset_index()
        else : 
            CSRDelta_Total = CSRCurvature_Total = CSRVega_Total = pd.DataFrame([])
        
        if (len(CSR_Sec_NonCTP_Data) > 0) :         
            CSRSecNonCTP_Delta_Total = CSR_Sec_NonCTP_Data.groupby("Depart").apply(Calc_CSRSecuritizedNonCTPDelta, CSR_SecuritizedNonCTPDelta_RW, DeltaSensiName).reset_index()
            CSRSecNonCTP_Curvature_Total = CSR_Sec_NonCTP_Data.groupby("Depart").apply(Calc_CSRSecuritizedNonCTPCurvature, CSR_SecuritizedNonCTPDelta_RW, DeltaSensiName).reset_index()
            CSRSecNonCTP_Vega_Total = CSR_Sec_NonCTP_Data.groupby("Depart").apply(Calc_CSRSecuritizedNonCTPVega, VegaSensiName).reset_index()        
        else : 
            CSRSecNonCTP_Delta_Total = CSRSecNonCTP_Curvature_Total = CSRSecNonCTP_Vega_Total = pd.DataFrame([])

        if (len(CSR_CTP_Data) > 0) : 
            CSRCTPDelta_Total = CSR_CTP_Data.groupby("Depart").apply(Calc_CSRDelta, CSR_DeltaNonSecurCorrDf, DeltaSensiName, 1).reset_index()
            CSRCTPCurvature_Total = CSR_CTP_Data.groupby("Depart").apply(Calc_CSRCurvature, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
            CSRCTPVega_Total = CSR_CTP_Data.groupby("Depart").apply(Calc_CSRVega, CSR_DeltaNonSecurCorrDf,  VegaSensiName).reset_index()
        else : 
            CSRCTPDelta_Total = CSRCTPCurvature_Total = CSRCTPVega_Total = pd.DataFrame([])
                    
        if (len(GIRR_Data) > 0) : 
            GIRRDelta_Total = GIRR_Data.groupby("Depart").apply(Calc_GIRRDelta, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
            GIRRCurvature_Total = GIRR_Data.groupby("Depart").apply(Calc_GIRRCurvature, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
            GIRRVega_Total = GIRR_Data.groupby("Depart").apply(Calc_GIRRVega, VegaSensiName).reset_index()
        else : 
            GIRRDelta_Total = GIRRCurvature_Total = GIRRVega_Total = pd.DataFrame([])   
                    
        if (len(FXR_Data) > 0) :                     
            FXRDelta_Total = FXR_Data.groupby("Depart").apply(Calc_FXRDelta, HighLiquidCurrency, DeltaSensiName).reset_index()
            FXRCurvature_Total = FXR_Data.groupby("Depart").apply(Calc_FXRCurvature, HighLiquidCurrency, DeltaSensiName).reset_index()
            FXRVega_Total = FXR_Data.groupby("Depart").apply(Calc_FXRVega, VegaSensiName).reset_index()
        else : 
            FXRDelta_Total = FXRCurvature_Total = FXRVega_Total = pd.DataFrame([]) 

        if (len(EQR_Data) > 0) :                    
            EQRDelta_Total = EQR_Data.groupby("Depart").apply(Calc_EQRDelta, DeltaSensiName).reset_index()
            EQRCurvature_Total = EQR_Data.groupby("Depart").apply(Calc_EQRCurvature,EQDeltaRWMappingDF, DeltaSensiName).reset_index()
            EQRVega_Total = EQR_Data.groupby("Depart").apply(Calc_EQRVega,VegaSensiName).reset_index()
        else : 
            EQRDelta_Total = EQRCurvature_Total = EQRVega_Total = pd.DataFrame([]) 
                    
        if (len(COMR_Data) > 0) :                     
            COMRDelta_Total = COMR_Data.groupby("Depart").apply(Calc_COMRDelta, DeltaSensiName).reset_index()
            COMRCurvature_Total = COMR_Data.groupby("Depart").apply(Calc_COMRCurvature, DeltaSensiName).reset_index()
            COMRVega_Total = COMR_Data.groupby("Depart").apply(Calc_COMRVega, VegaSensiName).reset_index()  
        else : 
            COMRDelta_Total = COMRCurvature_Total = COMRVega_Total = pd.DataFrame([]) 
            
        if len(DRC) > 0 :
            DRC_Total = DRC.groupby("Depart").apply(CalcDRC3RiskCharge).reset_index()
           
        if len(RRAO) > 0 : 
            RRAO_Total = RRAO.groupby("Depart").apply(CalcRRAORiskCharge).reset_index()
            
    else : 
        if (len(CSR_Data) > 0) :            
            CSRDelta_Total = CSR_Data.groupby("Portfolio").apply(Calc_CSRDelta, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
            CSRCurvature_Total = CSR_Data.groupby("Portfolio").apply(Calc_CSRCurvature, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
            CSRVega_Total = CSR_Data.groupby("Portfolio").apply(Calc_CSRVega, CSR_DeltaNonSecurCorrDf,  VegaSensiName).reset_index()
        else : 
            CSRDelta_Total = CSRCurvature_Total = CSRVega_Total = pd.DataFrame([])
            
        if (len(CSR_Sec_NonCTP_Data) > 0) :  
            CSRSecNonCTP_Delta_Total = CSR_Sec_NonCTP_Data.groupby("Portfolio").apply(Calc_CSRSecuritizedNonCTPDelta, CSR_SecuritizedNonCTPDelta_RW, DeltaSensiName).reset_index()
            CSRSecNonCTP_Curvature_Total = CSR_Sec_NonCTP_Data.groupby("Portfolio").apply(Calc_CSRSecuritizedNonCTPCurvature, CSR_SecuritizedNonCTPDelta_RW, DeltaSensiName).reset_index()
            CSRSecNonCTP_Vega_Total = CSR_Sec_NonCTP_Data.groupby("Portfolio").apply(Calc_CSRSecuritizedNonCTPVega, VegaSensiName).reset_index()        
        else : 
            CSRSecNonCTP_Delta_Total = CSRSecNonCTP_Curvature_Total = CSRSecNonCTP_Vega_Total = pd.DataFrame([])
            
        if (len(CSR_Sec_NonCTP_Data) > 0) : 
            CSRCTPDelta_Total = CSR_CTP_Data.groupby("Portfolio").apply(Calc_CSRDelta, CSR_DeltaNonSecurCorrDf, DeltaSensiName, 1).reset_index()
            CSRCTPCurvature_Total = CSR_CTP_Data.groupby("Portfolio").apply(Calc_CSRCurvature, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
            CSRCTPVega_Total = CSR_CTP_Data.groupby("Portfolio").apply(Calc_CSRVega, CSR_DeltaNonSecurCorrDf,  VegaSensiName).reset_index()
        else : 
            CSRCTPDelta_Total = CSRCTPCurvature_Total = CSRCTPVega_Total = pd.DataFrame([])

        if (len(GIRR_Data) > 0) :                     
            GIRRDelta_Total = GIRR_Data.groupby("Portfolio").apply(Calc_GIRRDelta, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
            GIRRCurvature_Total = GIRR_Data.groupby("Portfolio").apply(Calc_GIRRCurvature, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
            GIRRVega_Total = GIRR_Data.groupby("Portfolio").apply(Calc_GIRRVega, VegaSensiName).reset_index()
        else : 
            GIRRDelta_Total = GIRRCurvature_Total = GIRRVega_Total = pd.DataFrame([])   

        if (len(FXR_Data) > 0) :                     
            FXRDelta_Total = FXR_Data.groupby("Portfolio").apply(Calc_FXRDelta, HighLiquidCurrency, DeltaSensiName).reset_index()
            FXRCurvature_Total = FXR_Data.groupby("Portfolio").apply(Calc_FXRCurvature, HighLiquidCurrency, DeltaSensiName).reset_index()
            FXRVega_Total = FXR_Data.groupby("Portfolio").apply(Calc_FXRVega, VegaSensiName).reset_index()
        else : 
            FXRDelta_Total = FXRCurvature_Total = FXRVega_Total = pd.DataFrame([]) 

        if (len(EQR_Data) > 0) :                    
            EQRDelta_Total = EQR_Data.groupby("Portfolio").apply(Calc_EQRDelta, DeltaSensiName).reset_index()
            EQRCurvature_Total = EQR_Data.groupby("Portfolio").apply(Calc_EQRCurvature,EQDeltaRWMappingDF, DeltaSensiName).reset_index()
            EQRVega_Total = EQR_Data.groupby("Portfolio").apply(Calc_EQRVega,VegaSensiName).reset_index()
        else : 
            EQRDelta_Total = EQRCurvature_Total = EQRVega_Total = pd.DataFrame([]) 

        if (len(COMR_Data) > 0) :                      
            COMRDelta_Total = COMR_Data.groupby("Portfolio").apply(Calc_COMRDelta, DeltaSensiName).reset_index()
            COMRCurvature_Total = COMR_Data.groupby("Portfolio").apply(Calc_COMRCurvature, DeltaSensiName).reset_index()
            COMRVega_Total = COMR_Data.groupby("Portfolio").apply(Calc_COMRVega, VegaSensiName).reset_index()  
        else : 
            COMRDelta_Total = COMRCurvature_Total = COMRVega_Total = pd.DataFrame([]) 
    
        if len(DRC) > 0 :
            DRC_Total = DRC.groupby("Portfolio").apply(CalcDRC3RiskCharge).reset_index()    
    
        if len(RRAO) > 0 : 
            RRAO_Total = RRAO.groupby("Portfolio").apply(CalcRRAORiskCharge).reset_index()

    
    CSRDelta_Total["Risk_Type"] = "CSR_Delta"
    CSRDelta_Total["Risk_Class"] = "CSR"
    CSRCurvature_Total["Risk_Type"] = "CSR_Curvature"
    CSRCurvature_Total["Risk_Class"] = "CSR"
    CSRVega_Total["Risk_Type"] = "CSR_Vega"
    CSRVega_Total["Risk_Class"] = "CSR"    
    CSRSecNonCTP_Delta_Total["Risk_Type"] = "CSRSecNonCTP_Delta"
    CSRSecNonCTP_Delta_Total["Risk_Class"] = "CSRSecNonCTP"
    CSRSecNonCTP_Curvature_Total["Risk_Type"] = "CSRSecNonCTP_Curvature"
    CSRSecNonCTP_Curvature_Total["Risk_Class"] = "CSRSecNonCTP"
    CSRSecNonCTP_Vega_Total["Risk_Type"] = "CSRSecNonCTP_Vega"
    CSRSecNonCTP_Vega_Total["Risk_Class"] = "CSRSecNonCTP"    
    CSRCTPDelta_Total["Risk_Type"] = "CSRCTP_Delta"
    CSRCTPDelta_Total["Risk_Class"] = "CSRCTP"
    CSRCTPCurvature_Total["Risk_Type"] = "CSRCTP_Curvature"
    CSRCTPCurvature_Total["Risk_Class"] = "CSRCTP"
    CSRCTPVega_Total["Risk_Type"] = "CSRCTP_Vega"
    CSRCTPVega_Total["Risk_Class"] = "CSRCTP"    
    GIRRDelta_Total["Risk_Type"] = "GIRR_Delta"
    GIRRDelta_Total["Risk_Class"] = "GIRR"
    GIRRCurvature_Total["Risk_Type"] = "GIRR_Curvature"
    GIRRCurvature_Total["Risk_Class"] = "GIRR"
    GIRRVega_Total["Risk_Type"] = "GIRR_Vega"
    GIRRVega_Total["Risk_Class"] = "GIRR"
    FXRDelta_Total["Risk_Type"] = "FXR_Delta"
    FXRDelta_Total["Risk_Class"] = "FXR"
    FXRCurvature_Total["Risk_Type"] = "FXR_Curvature"
    FXRCurvature_Total["Risk_Class"] = "FXR"
    FXRVega_Total["Risk_Type"] = "FXR_Vega"
    FXRVega_Total["Risk_Class"] = "FXR"
    EQRDelta_Total["Risk_Type"] = "EQR_Delta"
    EQRDelta_Total["Risk_Class"] = "EQR"
    EQRCurvature_Total["Risk_Type"] = "EQR_Curvature"
    EQRCurvature_Total["Risk_Class"] = "EQR"
    EQRVega_Total["Risk_Type"] = "EQR_Vega"
    EQRVega_Total["Risk_Class"] = "EQR"
    COMRDelta_Total["Risk_Type"] = "COMR_Delta"
    COMRDelta_Total["Risk_Class"] = "COMR"
    COMRCurvature_Total["Risk_Type"] = "COMR_Curvature"
    COMRCurvature_Total["Risk_Class"] = "COMR"
    COMRVega_Total["Risk_Type"] = "COMR_Vega"
    COMRVega_Total["Risk_Class"] = "COMR"
    
    if len(DRC) == 0 :
        AggregatedData = pd.concat([CSRDelta_Total, CSRCurvature_Total, CSRVega_Total,
                                    CSRSecNonCTP_Delta_Total, CSRSecNonCTP_Curvature_Total, CSRSecNonCTP_Vega_Total,
                                    CSRCTPDelta_Total, CSRCTPCurvature_Total, CSRCTPVega_Total,
                                    GIRRDelta_Total, GIRRCurvature_Total, GIRRVega_Total,
                                    FXRDelta_Total, FXRCurvature_Total, FXRVega_Total,
                                    EQRDelta_Total, EQRCurvature_Total, EQRVega_Total,
                                    COMRDelta_Total, COMRCurvature_Total, COMRVega_Total
                                ], axis = 0)
    else : 
        AggregatedData = pd.concat([CSRDelta_Total, CSRCurvature_Total, CSRVega_Total,
                                    CSRSecNonCTP_Delta_Total, CSRSecNonCTP_Curvature_Total, CSRSecNonCTP_Vega_Total,
                                    CSRCTPDelta_Total, CSRCTPCurvature_Total, CSRCTPVega_Total,
                                    GIRRDelta_Total, GIRRCurvature_Total, GIRRVega_Total,
                                    FXRDelta_Total, FXRCurvature_Total, FXRVega_Total,
                                    EQRDelta_Total, EQRCurvature_Total, EQRVega_Total,
                                    COMRDelta_Total, COMRCurvature_Total, COMRVega_Total,
                                    DRC_Total], axis = 0)
    if len(RRAO) > 0: 
        AggregatedData = pd.concat([AggregatedData, RRAO_Total],axis=0)
        
    if GroupbyFlag == 0 : 
        AggregatedGroupbyData = AggregatedData.groupby(["Risk_Class","Risk_Type","Bucket"])[["KB_U","KB_M","KB_D","SB"]].sum().reset_index()
        TotalClass = AggregatedGroupbyData[AggregatedGroupbyData["Bucket"].isin(['99999',99999])].groupby("Risk_Class")[["KB_U","KB_M","KB_D","SB"]].sum()
        TotalClass.loc["FRTB_SA"] = TotalClass.sum(0)
        TotalClass = TotalClass.reset_index()
        TotalClass["Risk_Type"] = "*"
        TotalClass["Bucket"] = "*"
        TotalClass = pd.concat([AggregatedData, TotalClass], axis = 0).set_index(["Risk_Class","Risk_Type","Bucket"])
    elif GroupbyFlag == 1 :
        AggregatedGroupbyData = AggregatedData.groupby(["Depart","Risk_Class","Risk_Type","Bucket"])[["KB_U","KB_M","KB_D","SB"]].sum().reset_index()
        TotalClass = AggregatedGroupbyData[AggregatedGroupbyData["Bucket"].isin(['99999',99999])].groupby(["Depart","Risk_Class"])[["KB_U","KB_M","KB_D","SB"]].sum()
        TotalClassRiskCharge = TotalClass.groupby("Depart")[["KB_U","KB_M","KB_D","SB"]].sum().reset_index()
        TotalClassRiskCharge["Risk_Class"] = "FRTB_SA"
        TotalClassRiskCharge = TotalClassRiskCharge.set_index(["Depart","Risk_Class"])
        TotalClass = pd.concat([TotalClass, TotalClassRiskCharge],axis = 0).sort_index()
    else : 
        AggregatedGroupbyData = AggregatedData.groupby(["Portfolio","Risk_Class","Risk_Type","Bucket"])[["KB_U","KB_M","KB_D","SB"]].sum().reset_index()
        TotalClass = AggregatedGroupbyData[AggregatedGroupbyData["Bucket"].isin(['99999',99999])].groupby(["Portfolio","Risk_Class"])[["KB_U","KB_M","KB_D","SB"]].sum()
        TotalClassRiskCharge = TotalClass.groupby("Portfolio")[["KB_U","KB_M","KB_D","SB"]].sum().reset_index()
        TotalClassRiskCharge["Risk_Class"] = "FRTB_SA"
        TotalClassRiskCharge = TotalClassRiskCharge.set_index(["Portfolio","Risk_Class"])
        TotalClass = pd.concat([TotalClass, TotalClassRiskCharge],axis = 0).sort_index()
    return TotalClass
    
def FileListPrint(currdir) : 
    files = os.listdir(currdir)
    FileList = np.array(files)[np.vectorize(lambda x : True if ("raw" in str(x).lower()) or ("girr" in str(x).lower()) or ("csr" in str(x).lower()) or ("fxr" in str(x).lower())or ("eqr" in str(x).lower())or ("comr" in str(x).lower()) else False)(files)]
    filenum, filenames, filenamesprint = [], [], []
    k = 1
    for name in FileList : 
        if '.' not in name : 
            newdir = currdir + '\\' + name 
            files2 = os.listdir(newdir)
            FileList2 = np.array(files2)[np.vectorize(lambda x : True if ("raw" in str(x).lower()) or ("girr" in str(x).lower()) or ("csr" in str(x).lower()) or ("fxr" in str(x).lower())or ("eqr" in str(x).lower())or ("comr" in str(x).lower()) else False)(files2)]
            for name2 in FileList2 : 
                if '.pia' not in name2 : 
                    filenum.append(k)
                    filenames.append(newdir + '\\' + name2)
                    filenamesprint.append(str(k) + '. ' + newdir + '\\' + name2)
                    k += 1
        else : 
            if '.pia' not in name : 
                filenum.append(k)
                filenames.append(currdir + '\\' + name)
                filenamesprint.append(str(k) + '. ' + currdir + '\\' + name)
                k += 1
    return pd.DataFrame([filenum,filenames,filenamesprint],index = ["Number","Directory","DirectoryPrint"]).T   

def MarketDataFileListPrint(currdir, namein = "", namenotin = "") : 
    files = os.listdir(currdir) 
    YYYYMMDD, filenum, folder, filenames, filenamesprint = [], [], [], [], []
    k = 1
    for name in files : 
        if "." not in name : 
            newdir = currdir + '\\' + name
            files2 = os.listdir(newdir)
            for name2 in files2 : 
                if '.pia' not in str(name2) : 
                    if '.' not in name : 
                        newdir2 = newdir + '\\' + name2
                        files3 = os.listdir(newdir2)
                        for name3 in files3 : 
                            if len(str(namein)) == 0 and len(str(namenotin)) == 0: 
                                filenum.append(k)
                                folder.append(newdir2)
                                filenames.append(newdir2 + '\\' + name3)
                                filenamesprint.append(str(k) + ". " + newdir2 + "\\" + name3)
                                YYYYMMDD.append(name)
                                k += 1
                            elif len(str(namein)) == 0 and len(str(namenotin)) > 0 : 
                                if str(namenotin).lower() not in name3.lower() : 
                                    filenum.append(k)
                                    folder.append(newdir2)
                                    filenames.append(newdir2 + '\\' + name3)
                                    filenamesprint.append(str(k) + ". " + newdir2 + "\\" + name3)
                                    YYYYMMDD.append(name)
                                    k += 1                                                                    
                            else : 
                                if str(namein).lower() in name3.lower() : 
                                    filenum.append(k)
                                    folder.append(newdir2)
                                    filenames.append(newdir2 + '\\' + name3)
                                    filenamesprint.append(str(k) + ". " + newdir2 + "\\" + name3)
                                    YYYYMMDD.append(name)
                                    k += 1                                
                    else : 
                        if len(str(namein)) == 0 and len(str(namenotin)) == 0:                         
                            filenum.append(k)
                            folder.append(newdir)
                            filenames.append(newdir + '\\' + name2)
                            filenamesprint.append(str(k) + ". " + newdir + '\\' + name2)
                            YYYYMMDD.append(name)
                            k += 1
                        elif len(str(namein)) == 0 and len(str(namenotin)) > 0:
                            if str(namenotin).lower() not in name2.lower() : 
                                filenum.append(k)
                                folder.append(newdir)
                                filenames.append(newdir + '\\' + name2)
                                filenamesprint.append(str(k) + ". " + newdir + '\\' + name2)
                                YYYYMMDD.append(name)
                                k += 1                                                            
                        else : 
                            if str(namein).lower() in name2.lower() : 
                                filenum.append(k)
                                folder.append(newdir)
                                filenames.append(newdir + '\\' + name2)
                                filenamesprint.append(str(k) + ". " + newdir + '\\' + name2)
                                YYYYMMDD.append(name)
                                k += 1                            
    Result = pd.DataFrame([YYYYMMDD, filenum, folder, filenames, filenamesprint], index = ["YYYYMMDD","Number","Folder","Directory","DirectoryPrint"]).T
    return Result

def UsedMarketDataSetToPricing(MarketDataDir, FixedDate = "TEMPSTRING", namein = "", namenotin = "", Comments = "", MainComments = "", MultiSelection = True, defaultvalue = 0, DefaultStringList = []) : 
    Data = MarketDataFileListPrint(MarketDataDir, namein ,namenotin ).sort_values(by = "YYYYMMDD")[-50:]
    
    GroupbyYYYYMMDD = Data.groupby("YYYYMMDD").first().reset_index()
    PrintDate = MainComments + "\n 다음 중 사용하실 MarketData 날짜를 고르세요. (번호선택)\n"
    FixedDateInFlag = 0
    n = 0
    for x, y in zip(GroupbyYYYYMMDD["Number"], GroupbyYYYYMMDD["YYYYMMDD"]) : 
        PrintDate += str(n+1) + ": " + str(y) + "\n"
        if FixedDate in str(y).lower() : 
            FixedDateInFlag = n
            break
        n = n + 1
    #if FixedDateInFlag == 0 : 
    #    DateMarketDataIdx = input(PrintDate + "-> ")
    #else : 
    #    DateMarketDataIdx = FixedDateInFlag + 1

    YYYYMMDD = MainViewer(Title = 'MarketData:Date', MyText = '사용하실 마켓데이터 날짜는?(번호입력)', MyList = list(GroupbyYYYYMMDD["YYYYMMDD"]), size = "800x450+30+30", splitby = ".", listheight = 8, textfont = 13, titlelable = False, titleName = "Name", defaultvalue=-1)        
    YYYYMMDD = str(YYYYMMDD)
    #YYYYMMDD = GroupbyYYYYMMDD["YYYYMMDD"].isin([TargetDate, str(TargetDate)])
    TargetFiles = Data[Data["YYYYMMDD"].isin([YYYYMMDD, int(YYYYMMDD)])].groupby("Directory").first().reset_index()

    if len(Comments) == 0 : 
        PrintMarketData = "\n 다음 중 사용하실 MarketData를 고르세요.(example : 1 || example2 : 1, 2, 3 와 같은 여러개 선택가능)\n"
        PrintComments = "다음 중 사용하실 MarketData를 고르세요." + ("\n(example : 1 || example2 : 1, 2, 3 와 같은 여러개 선택가능" if MultiSelection == True else "")
    else : 
        PrintMarketData = "\n" + Comments + "\n"
        PrintComments = Comments + "\n"
    TargetList = []
    for idxx, x in enumerate(TargetFiles["Directory"]) : 
        PrintMarketData += ' ' + str(idxx+1) +". "+ str(x) + "\n"
    DataMarketData = MainViewer(Title = 'Viewer', MyText = PrintComments, MyList = TargetFiles["DirectoryPrint"], size = "800x450+30+30", splitby = ".", listheight = 6, textfont = 13, titlelable = False, titleName = "Name", MultiSelection = MultiSelection, defaultvalue = defaultvalue, DefaultStringList = DefaultStringList)#input(PrintMarketData + '->')
    DataMarketData = str(DataMarketData)
    MarketDataList = []
    MarketDataName = []
    
    if len(DataMarketData) == 1 : 
        NumberList = DataMarketData.replace(" ","").split(",")
        idx = TargetFiles["Number"].astype(str).isin(NumberList)
        MarketDataList.append(ReadCSV(TargetFiles["Directory"][idx].iloc[0], True).dropna(how = 'all'))
        MarketDataName.append(TargetFiles["Directory"][idx].iloc[0])
    else : 
        NumberList = DataMarketData.replace(" ","").split(",")
        #for n in NumberList : 
            #TargetList.append(TargetFiles["Number"].iloc[int(n)-1])
        #    TargetFiles[TargetFiles["Number"].isin([int(n), str(n)])]
        #TargetFiles2 = TargetFiles[TargetFiles["Number"].astype(np.int64).isin(TargetList)]
        TargetFiles2 = TargetFiles[TargetFiles["Number"].astype(str).isin(NumberList)]
        for idx in range(len(TargetFiles2)) : 
            MarketDataList.append(ReadCSV(TargetFiles2["Directory"].iloc[idx], True))
            MarketDataName.append(TargetFiles2["Directory"].iloc[idx])
    
    for i in range(len(MarketDataList)) : 
        MarketDataList[i] = MarketDataList[i].dropna(how = 'all')#.applymap(lambda x : str(x).replace("-",""))
        if "Rate" in MarketDataList[i].columns and "Term" in MarketDataList[i].columns : 
            Term = list(MarketDataList[i]["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64))
            Rate = list(MarketDataList[i]["Rate"].astype(np.float64))
            PriceDate = int(str(MarketDataList[i]["PriceDate"].iloc[0]).replace("-",""))
            Preprocessing_Term(Term, int(PriceDate))
            MarketDataList[i]["Term"] = Term
            MarketDataList[i]["Rate"] = Rate
        elif "rate" in MarketDataList[i].columns and "term" in MarketDataList[i].columns : 
            Term = list(MarketDataList[i]["term"].apply(lambda x : str(x).replace("-","")).astype(np.float64))
            Rate = list(MarketDataList[i]["rate"].astype(np.float64))
            PriceDate = int(str(MarketDataList[i]["PriceDate"].iloc[0]).replace("-",""))
            Preprocessing_Term(Term, int(PriceDate))
            MarketDataList[i]["term"] = Term
            MarketDataList[i]["rate"] = Rate
        if "StartDate" in MarketDataList[i].columns : 
            MarketDataList[i]["StartDate"] = MarketDataList[i]["StartDate"].apply(lambda x : int(str(x).replace("-","")) if type(x) == str else (ExcelDateToYYYYMMDD(int(x)) if int(x) < 19000101 else int(x)))
        if "Maturity" in MarketDataList[i].columns : 
            MarketDataList[i]["Maturity"] = MarketDataList[i]["Maturity"].apply(lambda x : int(str(x).replace("-","")) if type(x) == str else (ExcelDateToYYYYMMDD(int(x)) if int(x) < 19000101 else int(x)))
        if "MarketQuote" in MarketDataList[i].columns : 
            MarketDataList[i]["MarketQuote"] = MarketDataList[i]["MarketQuote"].apply(lambda x : str(x).replace(",","")).astype(np.float64)
            
    return YYYYMMDD, MarketDataName, MarketDataList

def LoggingUsedFileNames(MyFiles, MyClass = 'FRTB') : 
    PrintStr = '\n'+MyClass+' 계산에 필요한 RAW 데이터 파일은 다음 중 무엇입니까?(번호입력)\n'
    n = 0
    for i in MyFiles["DirectoryPrint"] : 
        if MyClass.lower() in i.lower() : 
            PrintStr += i + str("\n")
            n += 1
    if n == 0 : 
        return ''
    else : 
        return PrintStr
    
def MainFunction(currdir = os.getcwd()) : 
    MyFiles = FileListPrint(currdir)
    MyFiles["RiskClass"] = MyFiles["DirectoryPrint"].apply(lambda x : 'girr' if 'girr' in x.lower() else (
                                                            'csr' if 'csr' in x.lower() else (
                                                                'fxr' if 'fx' in x.lower() else (
                                                                    'eqr' if 'eq' in x.lower() else (
                                                                        'comr' if 'com' in x.lower() else (
                                                                            'frtb' if 'frtb' in x.lower() else "None"))))))
    GIRRFiles = MyFiles[MyFiles["RiskClass"] == 'girr']
    CSRFiles = MyFiles[MyFiles["RiskClass"] == 'csr']
    EQRFiles = MyFiles[MyFiles["RiskClass"] == 'eqr']
    FXRFiles = MyFiles[MyFiles["RiskClass"] == 'fxr']
    COMRFiles = MyFiles[MyFiles["RiskClass"] == 'comr']
    FRTBTotalFiles = MyFiles[MyFiles["RiskClass"] == 'frtb']
    
    root = tk.Tk()
    root.title("FRTB Files")
    root.geometry("1000x750+30+30")
    root.resizable(False, False)
    GIRRFileSelection, CSRFileSelection, EQRFileSelection, FXRFileSelection, COMRFileSelection, FRTBFileSelection = None, None, None, None, None, None
    if len(FRTBTotalFiles) > 0 : 
        FRTBFilesLen = len(FRTBTotalFiles)
        left_frame = tk.Frame(root)
        left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
        FRTBFileSelection = make_listvariable_interface(left_frame, 'FRTB FileName\n(리스트에서 선택)', list(FRTBTotalFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if FRTBFilesLen > 0 else None
    else : 
        GIRRFilesLen = len(GIRRFiles)
        CSRFilesLen = len(CSRFiles)
        EQRFilesLen = len(EQRFiles)
        FXRFilesLen = len(FXRFiles)
        COMRFilesLen = len(COMRFiles)
        left_frame = tk.Frame(root)
        left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
        GIRRFileSelection = make_listvariable_interface(left_frame, 'GIRR FileName\n(리스트에서 선택)', list(GIRRFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if GIRRFilesLen > 0 else None
        CSRFileSelection = make_listvariable_interface(left_frame, 'CSR FileName\n(리스트에서 선택)', list(CSRFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if CSRFilesLen > 0 else None
        EQRFileSelection = make_listvariable_interface(left_frame, 'EQR FileName\n(리스트에서 선택)', list(EQRFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if EQRFilesLen > 0 else None
        FXRFileSelection = make_listvariable_interface(left_frame, 'FXR FileName\n(리스트에서 선택)', list(FXRFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if FXRFilesLen > 0 else None
        COMRFileSelection = make_listvariable_interface(left_frame, 'COMR FileName\n(리스트에서 선택)', list(COMRFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if COMRFilesLen > 0 else None

    PrevTreeFlag = 0
    tree, scrollbar, scrollbar2 = None, None, None
    GIRRNumberArray = []
    CSRNumberArray = []
    EQRNumberArray = []
    FXRNumberArray = []
    COMRNumberArray = []
    FRTBNumberArray = []
    MyArray = [tree, PrevTreeFlag, scrollbar, scrollbar2]
    def run_function(GIRRNumberArray, CSRNumberArray, EQRNumberArray, FXRNumberArray, COMRNumberArray, FRTBNumberArray,MyArray) :
        if len(FRTBTotalFiles) > 0 : 
            FRTBNumber = int(str(FRTBFileSelection.get(FRTBFileSelection.curselection())).split(".")[0]) if FRTBFileSelection.curselection() else 0
            FRTBNumberArray.append(FRTBNumber)
        else : 
            GIRRNumber = int(str(GIRRFileSelection.get(GIRRFileSelection.curselection())).split(".")[0]) if GIRRFileSelection.curselection() else 0
            GIRRNumberArray.append(GIRRNumber)
            CSRNumber = int(str(CSRFileSelection.get(CSRFileSelection.curselection())).split(".")[0]) if CSRFileSelection.curselection() else 0
            CSRNumberArray.append(CSRNumber)
            EQRNumber = int(str(EQRFileSelection.get(EQRFileSelection.curselection())).split(".")[0]) if EQRFileSelection.curselection() else 0
            EQRNumberArray.append(EQRNumber)
            FXRNumber = int(str(FXRFileSelection.get(FXRFileSelection.curselection())).split(".")[0]) if FXRFileSelection.curselection() else 0
            FXRNumberArray.append(FXRNumber)
            COMRNumber = int(str(COMRFileSelection.get(COMRFileSelection.curselection())).split(".")[0]) if COMRFileSelection.curselection() else 0
            COMRNumberArray.append(COMRNumber)
        root.destroy()
    temp_function = lambda : run_function(GIRRNumberArray, CSRNumberArray, EQRNumberArray, FXRNumberArray, COMRNumberArray, FRTBNumberArray, MyArray)
    tk.Button(left_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_function, width = 15).pack()
    root.mainloop()            
    if len(FRTBTotalFiles) > 0 : 
        Data = ReadCSV(MyFiles[MyFiles["Number"] == FRTBNumberArray[-1]]["Directory"].iloc[0])
    else : 
        Data1 = ReadCSV(MyFiles[MyFiles["Number"] == GIRRNumberArray[-1]]["Directory"].iloc[0])
        Data2 = ReadCSV(MyFiles[MyFiles["Number"] == CSRNumberArray[-1]]["Directory"].iloc[0])
        Data3 = ReadCSV(MyFiles[MyFiles["Number"] == EQRNumberArray[-1]]["Directory"].iloc[0])
        Data4 = ReadCSV(MyFiles[MyFiles["Number"] == FXRNumberArray[-1]]["Directory"].iloc[0])
        Data5 = ReadCSV(MyFiles[MyFiles["Number"] == COMRNumberArray[-1]]["Directory"].iloc[0])
        Data = pd.concat([Data1, Data2, Data3, Data4, Data5],axis = 0)
    return Data

def ViewFRTB(Data) : 
    root = tk.Tk()
    root.title("FRTB Result")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    tree = ttk.Treeview(root)
    DataDF = Data.reset_index().applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
    tree.pack(padx=5, pady=5, fill="both", expand=True)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.configure(xscrollcommand=scrollbar2.set)
    scrollbar.pack(side="right", fill="y")    
    scrollbar2.pack(side="bottom", fill="x")    
    PrevTreeFlag = insert_dataframe_to_treeview(tree, DataDF, width = 100)
    root.mainloop()    

def MainViewer(Title = 'Viewer', MyText = '사용하실 기능은?(번호입력)', MyList = ["1: Pricing 및 CSR, GIRR 간이 시뮬레이션","2: FRTB SA Risk Calculation","3: CurveGenerator","4: IR Swaption ImpliedVol Calculation","5: Cap Floor Implied Vol Calibration",'6: HW Kappa1F VolRatio Calib(미완)'], size = "800x450+30+30", splitby = ":", listheight = 7, textfont = 13, titlelable = False, titleName = "Name", MultiSelection = False, defaultvalue = 0, addtreeflag = False, treedata = pd.DataFrame([]), DefaultStringList = []) : 
    root = tk.Tk()
    root.title(Title)
    root.geometry(size)
    root.resizable(False, False)
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    if MultiSelection == False : 
        FunctionSelection = make_listvariable_interface(left_frame, MyText, MyList, listheight = listheight, textfont = textfont, defaultflag = True, defaultvalue=(len(MyList) - 1) if defaultvalue < 0 else defaultvalue, width = 95, titlelable= titlelable, titleName=titleName, DefaultStringList = DefaultStringList)
    else : 
        FunctionSelection = make_multilistvariable_interface(left_frame, MyText, MyList, listheight = listheight, textfont = textfont, width = 95, titlelable= titlelable, titleName=titleName, defaultflag = True, defaultvalue = defaultvalue, DefaultStringList = DefaultStringList)
    FunctionSelected = []
    PrevTreeFlag = 0
    tree, scrollbar, scrollabar2 = None, None, None
    if addtreeflag == True : 
        tree = ttk.Treeview(root)
        treedata = treedata.reset_index().applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        PrevTreeFlag = insert_dataframe_to_treeview(tree, treedata, width = 100)
        
    def run_function(FunctionSelected) : 
        if MultiSelection == False : 
            Number = int(str(FunctionSelection.get(FunctionSelection.curselection())).split(splitby)[0]) if FunctionSelection.curselection() else 1
            FunctionSelected.append(Number)
        else : 
            selected_indices = FunctionSelection.curselection()  # 선택된 인덱스들
            selected_values = [FunctionSelection.get(i) for i in selected_indices]
            templst = []
            for v in selected_values : 
                templst.append(int(v.split(splitby)[0]))            
            if len(templst) > 0 : 
                FunctionSelected.append(str(templst).replace("[","").replace("]",""))                
            else : 
                FunctionSelected.append(0)
        if tree : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
        root.destroy()
    temp_function = lambda : run_function(FunctionSelected)
    tk.Button(left_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_function, width = 15).pack()
    root.mainloop()            
    return FunctionSelected[-1]    

def MainViewer2(Title = "Viewer", MyText = "데이터인풋", size = "800x450+30+30", textfont = 13, defaultvalue = 0, bold = True) : 
    root = tk.Tk()
    root.title(Title)
    root.geometry(size)
    root.resizable(False, False)
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    Contents = make_variable_interface(left_frame, MyText, bold = bold, textfont = textfont, defaultflag = True, defaultvalue = defaultvalue)
    FunctionSelected = []
    def run_function(FunctionSelected) : 
        Number = str(Contents.get()) if len(str(Contents.get())) else str(defaultvalue)
        FunctionSelected.append(Number)
        root.destroy()
    temp_function = lambda : run_function(FunctionSelected)
    tk.Button(left_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_function, width = 15).pack()
    root.mainloop()            
    return FunctionSelected[-1]        

def CalcFXRateToKRW(FXData, Currency = "USD", BaseDate = "20250627") :    
    if "-" in str(FXData.index[0]) :
        FXData = FXData.copy()
        FXData.index = np.vectorize(lambda x : str(x).replace("-","").split(" ")[0])(pd.to_datetime(FXData.index))
    elif int(FXData.index[0]) < 19000101 : 
        FXData = FXData.copy()
        NewIndex = [ExcelDateToYYYYMMDD(int(s)) for s in FXData.index]
        FXData.index = NewIndex
         
    if Currency.upper() == "KRW" : 
        return 1
    
    if len(FXData.shape) == 1 : 
        #Series
        NewIndex = pd.Series(FXData.index).apply(lambda x : x.split("-")[0].upper() + "/" + x.split("-")[1].upper() if "-" in str(x) else str(x).upper())
        NewSeries = pd.Series(FXData.values, NewIndex)
    else :
        if int(BaseDate) > FXData.index[-1] : 
            NewSeries = FXData.loc[FXData.index[FXData.index <= int(BaseDate)]].iloc[-1]
        else : 
            NewSeries = FXData.loc[FXData.index[FXData.index >= int(BaseDate)]].iloc[0]
            
    if Currency.upper() == "USD" : 
        return NewSeries.loc["USD/KRW"]

    if Currency + "/KRW" in NewSeries.index :
        return NewSeries.loc[Currency + "/KRW"]
    elif Currency + "/USD" in NewSeries.index: 
        return NewSeries.loc[Currency + "/USD"] * NewSeries.loc["USD/KRW"]
    else : 
        return NewSeries.loc[Currency + "/EUR"] * NewSeries.loc["EUR/KRW"]        

def PrintingMarketDataInformation(YYYYMMDD, NameList, MyMarketDataList) : 
    print("\n##########################################################################################\n\n     세팅된 커브는 다음과 같습니다. \n     평가날짜 : " + YYYYMMDD)
    curvename = ''
    for i in range(len(NameList)) : 
        if "Rate" in MyMarketDataList[i].columns or 'rate' in MyMarketDataList[i].columns : 
            curvename += '\n\n     ' + str(i+1) + '. ' + NameList[i].split('\\')[-1] + '\n'
            Term = list(MyMarketDataList[i]["Term" if "Term" in MyMarketDataList[i].columns else "term"].round(5))[:10]
            PrintTerm = [DayPlus(int(YYYYMMDD), int(t * 365 + 1e-9)) for t in Term]
            Rate = list(MyMarketDataList[i]["Rate" if "Rate" in MyMarketDataList[i].columns else "rate"].round(5))[:10]
            curvename += '\n     Term = ' + str(PrintTerm).split(']')[0] + ', ...]'
            curvename += '\n     Rate = ' + str(Rate).split(']')[0] + ', ...]'
        elif "Moneyness/Tenor" in MyMarketDataList[i].columns :             
            curvename += '\n\n     ' + str(i+1) + '. ' + NameList[i].split('\\')[-1] + '\n'
            Term = ["parity/tenor"] + [np.round(float(i), 3) for i in MyMarketDataList[i].columns[1:]]
            curvename += '\n '+str(Term)+'\n'
            curvename += '           '+str(np.round(MyMarketDataList[i].values, 3)).replace("\n","\n           ") 
        elif "SwapMat/OptMat" in MyMarketDataList[i].columns :
            curvename += '\n\n     ' + str(i+1) + '. ' + NameList[i].split('\\')[-1] + '\n'
            myind = MyMarketDataList[i].values[:,0]
            values = (MyMarketDataList[i].values[:,1:] * 100000).astype(np.int64)/1000
            Term = ["SwapMat/OptMat"] + [int(i) for i in MyMarketDataList[i].columns[1:]]
            curvename += '\n '+str(Term).replace(',',',  ') +'\n'
            for j in range(len(values)) : 
                curvename += '            [' + str(myind[j]) + ' | '
                curvename += str(values[j]).replace("  "," ").replace("\n","\n  ").replace('[','')  + '\n'
        elif "스왑만기/옵션만기" in MyMarketDataList[i].columns :
            curvename += '\n\n     ' + str(i+1) + '. ' + NameList[i].split('\\')[-1] + '\n'
            values = np.concatenate([MyMarketDataList[i].values[:,0:1],(MyMarketDataList[i].values[:,1:] *100).round(2)],axis=1)
            Term = ["스왑만기/옵션만기"] + [np.round(float(i), 4) for i in MyMarketDataList[i].columns[1:]]
            curvename += '\n '+str(Term)+'\n'
            curvename += '           '+str(values).replace("\n","\n           ") 
            
    PrintingContents = curvename
    return PrintingContents    

def PricingEquityOptionProgram(currdir = os.getcwd(), HolidayDate = pd.DataFrame([])) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata', 
                                                                  namenotin = "waption",
                                                                  Comments = "옵션 Pricing을 위한 Zero 커브 번호 및 Volatility 번호를 입력하시오.\n  (반드시 ZeroCurve, Vol Data 2개 선택)\n ex : 1, 2",
                                                                  DefaultStringList= ["IRS","Vol"]) 
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    Currency = Name[0].split("\\")[-2]
    Holidays = list(HolidayDate[Currency].dropna().unique()) if Currency in HolidayDate.columns else []
    print(curvename)    
    MyMarketDataList_ExceptVol = []
    NameList_ExceptVol = []
    N_EQVol = -1
    for i in range(len(Name)) : 
        if ("eq" in Name[i].lower() or "vol" in Name[i].lower()) and N_EQVol == -1: 
            N_EQVol = i
        else : 
            MyMarketDataList_ExceptVol.append(MyMarketDataList[i])
            NameList_ExceptVol.append(Name[i])

    VolData = MyMarketDataList[N_EQVol].set_index(MyMarketDataList[N_EQVol].columns[0])
    TermVol = np.array(VolData.columns, dtype = np.float64)
    ParityVol = np.array(VolData.index, dtype = np.float64)
    Vols2D = VolData.values.astype(np.float64)

    if len(NameList_ExceptVol) == 1 : 
        DiscTerm = MyMarketDataList_ExceptVol[0]["Term"]
        DiscRate = MyMarketDataList_ExceptVol[0]["Rate"]
        EstTerm = []
        EstRate = []
    else : 
        mystr = ""
        mystr += "  기초자산의 할인커브는 " + NameList_ExceptVol[0].split('\\')[-1] + ","
        mystr += "\n  레퍼런스커브는 " + NameList_ExceptVol[1].split('\\')[-1] + '\n 와 같이 세팅합니다. 맞습니까?(Y/N)\n->'
        myinput = input(mystr)
        if len(myinput) == 0 or myinput.lower() == 'y' : 
            DiscTerm = MyMarketDataList_ExceptVol[0]["Term"]
            DiscRate = MyMarketDataList_ExceptVol[0]["Rate"]
            EstTerm = MyMarketDataList_ExceptVol[1]["Term"]
            EstRate = MyMarketDataList_ExceptVol[1]["Rate"]            
        else :        
            DiscTerm = MyMarketDataList_ExceptVol[1]["Term"]
            DiscRate = MyMarketDataList_ExceptVol[1]["Rate"]
            EstTerm = MyMarketDataList_ExceptVol[0]["Term"]
            EstRate = MyMarketDataList_ExceptVol[0]["Rate"]            
             
    Preprocessing_ZeroTermAndRate(DiscTerm, DiscRate, int(YYYYMMDD))
    Preprocessing_ZeroTermAndRate(EstTerm, EstRate, int(YYYYMMDD))
    
    root = tk.Tk()
    root.title("Equity Option Pricer")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_StockOrForward = make_listvariable_interface(left_frame, '기초자산가격/선도가격여부\n(리스트에서 선택)', ["0: 기초자산가격","1: 선도가격"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    v_S = make_variable_interface(left_frame, '기초자산가격', bold = False, textfont = 11, defaultflag = True, defaultvalue=250)
    v_F = make_variable_interface(left_frame, '선도가격(사용할경우)', bold = False, textfont = 11, defaultflag = True, defaultvalue=0)
    v_X = make_variable_interface(left_frame, '행사가격', bold = False, textfont = 11, defaultflag = True, defaultvalue=240)
    v_Maturity = make_variable_interface(left_frame, '옵션만기(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=int(YYYYMMDD)+10000)
    v_QuantoCorr = make_variable_interface(left_frame, 'QuantoCorr', bold = False, textfont = 11, titlelable= True, titleName = "QuantoInfo", defaultflag = True, defaultvalue=0)
    v_FXVol = make_variable_interface(left_frame, 'FXVol', bold = False, textfont = 11, defaultflag = True, defaultvalue=0)
    v_AvgStartDate = make_variable_interface(left_frame, '평균시작일\n(아시안옵션의경우입력)', bold = False, textfont = 11, defaultflag = True,titleName = "아시안옵션평가시입력", titlelable=True,defaultvalue=int(YYYYMMDD))
    v_AvgEndDate = make_variable_interface(left_frame, '평균종료일\n(아시안옵션의경우입력)', bold = False, textfont = 11, defaultflag = True,defaultvalue=int(YYYYMMDD)+10000)
    v_MeanPrice = make_variable_interface(left_frame, 'Fixed과거평균가격\n(아시안옵션의경우입력)', bold = False, textfont = 11, defaultflag = True, defaultvalue=250)
    
    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(center_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_Div = make_variable_interface(center_frame, '배당수익률(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=0)
    v_c_or_p = make_listvariable_interface(center_frame, '콜(C)/풋(P)\n(리스트에서 선택)', ["C: Call","P: Put"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0)
    v_ATMVolFlag = make_listvariable_interface(center_frame, 'ATMVolFlag', ["0: Surface","1: ATMVol","2: 자체입력"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    v_SelfVol = make_variable_interface(center_frame, '자체입력Vol(%)', bold = True, textfont = 11, defaultflag = True, defaultvalue = 20)
    vb_zerocurve = make_listvariable_interface(center_frame, 'ZeroCurve(자동Load)', termratestr(DiscTerm, DiscRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)
    
    Right_frame = tk.Frame(root)
    Right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_Plain0Barrier1Digital2 = make_listvariable_interface(Right_frame, '배리어옵션여부', ["0: 배리어사용X","1: 배리어옵션","2: 디지털옵션","3: AsianOption"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, titlelable=True, titleName="배리어사용시입력")
    v_H = make_variable_interface(Right_frame, '배리어', bold = False, textfont = 11, defaultflag = True, defaultvalue=250)
    vb_Down0Up1Flag = make_listvariable_interface(Right_frame, 'Down0Up1Flag', ["0: Down","1: Up"], listheight = 2, textfont = 11,defaultflag = 0, defaultvalue = 0)
    vb_In0Out1Flag = make_listvariable_interface(Right_frame, 'In0Out1Flag', ["0: In","1: Out"], listheight = 2, textfont = 11,defaultflag = 0, defaultvalue = 0)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)
    Value = 0
    Price, Delta, Gamma = None, None, None
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]   

        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        SelfVol = float(v_SelfVol.get())/100 if len(str(v_SelfVol.get())) > 0 else 0.2
        ForwardUseFlag = int(str(v_StockOrForward.get(v_StockOrForward.curselection())).split(":")[0]) if v_StockOrForward.curselection() else 0
        if ForwardUseFlag == 0 : 
            ForwardPrice = 0
        else : 
            ForwardPrice = float(v_F.get()) if len(str(v_F.get())) > 0 else 0 
        MeanPrice = float(v_MeanPrice.get()) if len(str(v_MeanPrice.get())) > 0 else 0
        AvgStartDate = int(v_AvgStartDate.get()) if len(str(v_AvgStartDate.get())) > 0 else int(YYYYMMDD)
        AvgEndDate = int(v_AvgEndDate.get()) if len(str(v_AvgEndDate.get())) > 0 else int(YYYYMMDD)+10000        
        
        S = float(v_S.get())
        X = float(v_X.get())
        H = float(v_H.get()) if len(str(v_H.get())) > 0 else 0.0001
        Maturity = float(v_Maturity.get()) if len(str(v_Maturity.get())) > 0 else (int(YYYYMMDD) + 10000)
        DivTerm = [0]
        if ForwardPrice > 0 : 
            DivRate = [0]
        else : 
            DivRate = [float(v_Div.get())/100] if len(str(v_Div.get())) > 0 else [0]
        QuantoCorr = float(v_QuantoCorr.get()) if len(str(v_QuantoCorr.get())) else 0
        FX_Vol = float(v_FXVol.get()) if len(str(v_FXVol.get())) else 0
        c_or_p = str(v_c_or_p.get(v_c_or_p.curselection())).split(":")[0] if v_c_or_p.curselection() else 'C'
        ATMVolFlag = int(str(v_ATMVolFlag.get(v_ATMVolFlag.curselection())).split(":")[0]) if v_ATMVolFlag.curselection() else 0
        VolsATM = []
        if ATMVolFlag == 1 : 
            if np.abs(ParityVol).max() < 10 : 
                for i in range(Vols2D.shape[1]) : 
                    VolsATM.append(np.interp(1, ParityVol, Vols2D[:,i]))
            else : 
                for i in range(Vols2D.shape[1]) : 
                    VolsATM.append(np.interp(S, ParityVol, Vols2D[:,i]))

        if c_or_p in ['c','C'] : 
            TypeFlag = 'c'
        else :
            TypeFlag = 'p'    
        VolsATMAry = np.array(VolsATM).reshape(1,-1)
        VolsATMParity = [1]    
        
        BarrierCall1Put2 = 1 if c_or_p == "C" else 2 
        Plain0Barrier1 = int(str(v_Plain0Barrier1Digital2.get(v_Plain0Barrier1Digital2.curselection())).split(":")[0]) if v_Plain0Barrier1Digital2.curselection() else 0
        Down0Up1Flag = int(str(vb_Down0Up1Flag.get(vb_Down0Up1Flag.curselection())).split(":")[0]) if vb_Down0Up1Flag.curselection() else 0
        In0Out1Flag = int(str(vb_In0Out1Flag.get(vb_In0Out1Flag.curselection())).split(":")[0]) if vb_In0Out1Flag.curselection() else 0

        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        if Plain0Barrier1 == 0 : 
            Price, Delta, Gamma, Vega, Theta, Rho, v = BS_Option(int(PriceDate), int(Maturity), S, X, DiscTerm, 
                    DiscRate, DivTerm, DivRate, Vols2D if ATMVolFlag != 2 else SelfVol, QuantoCorr = QuantoCorr, 
                    FXVolTerm = [0], FXVol = [FX_Vol], DivFlag = 0, EstTerm = EstTerm, EstRate = EstRate, 
                    ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir, VolTerm = TermVol, VolParity = ParityVol,TypeFlag = TypeFlag, ATMVolFlag = ATMVolFlag, ATMVol = VolsATM)
        elif Plain0Barrier1 == 1 : 
            Price, Delta, Gamma, Vega, Theta, Rho, v = BSBarrierOption(int(PriceDate), BarrierCall1Put2, S, X, H, DiscTerm, 
                                DiscRate, DiscTerm, DiscRate, DivTerm, DivRate, 
                                QuantoCorr, [0], [FX_Vol], TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, 
                                Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 0, int(Maturity), int(Maturity), 
                                Down0Up1Flag, In0Out1Flag, Reb = 0, ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir)
        elif Plain0Barrier1 == 2 : 
            Price, Delta, Gamma, Vega, Theta, Rho, v = BSDigitalOption(BarrierCall1Put2, int(PriceDate), int(Maturity), int(Maturity), S,
                                                                       X, DiscTerm, DiscRate, DiscTerm, DiscRate, 
                                                                       DivTerm, DivRate, TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 
                                                                       QuantoCorr, [0], [FX_Vol], 0, ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir)            
        else : 
            Price, Delta, Gamma, Vega, Theta, Rho, v = Arithmetic_Asian_Opt_Pricing_Preprocessing(0, 0 if TypeFlag == 'c' else 1, int(PriceDate), AvgStartDate, AvgEndDate, 
                                                                                                  int(Maturity), S, X, MeanPrice, DiscTerm, 
                                                                                                  DiscRate, DivTerm, DivRate, QuantoCorr, [0], 
                                                                                                  [FX_Vol], TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 0, 
                                                                                                  Holidays = Holidays, ForwardTerm = [] if ForwardPrice == 0 else [1], ForwardPrice = [ForwardPrice])            
            
            
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        VolDF = VolData.reset_index().applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    

        PrevTreeFlag = insert_dataframe_to_treeview(tree, VolDF, width = 100)

        output_label.config(text = f"\n결과: {np.round(Price,4)}\nDelta: {np.round(Delta,4)}\nGamma: {np.round(Gamma,4)}\nVega: {np.round(Vega,4)}\nTheta: {np.round(Theta,4)}\nRho: {np.round(Rho,4)}\nFRTB EQ Delta:{np.round(Price*0.25,2)}\nFRTB EQ Vega:{np.round(np.array(Vols2D).mean() * Vega * 0.25,2)}\nFRTB EQ Curvature:{np.round(abs(Gamma * (S * 0.25 * S * 0.25 * 0.5) - Price*0.25),2)}\n변동성:\n{np.round(v*100,4)}%", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
    root.mainloop()            
            
    MainFlag2 = ""#input("\n종료하시겠습니까? (Y/N)\n->")

    return MainFlag2, Price, Delta, Gamma

def BS_CapFloor_Program(HolidayDate, currdir) : 
    YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\outputdata",MultiSelection=False, namenotin = "Vol", Comments="Pricing을 위한 ZeroCurve", DefaultStringList=["IRS"])
    ZeroCurve = Data[0]
    ZeroTerm = ZeroCurve["Term"].astype(np.float64)
    ZeroRate = ZeroCurve["Rate"].astype(np.float64)
    
    ZeroCurveName = Name[0].split("\\")[-1].replace(".csv","")  
    Currency = Name[0].split("\\")[-2]
    Holidays = list(HolidayDate[Currency].dropna().unique()) if Currency in HolidayDate.columns else []
    root = tk.Tk()
    root.title("Cap Floor Pricer")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=EDate_YYYYMMDD(int(YYYYMMDD), 3))
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=EDate_YYYYMMDD(int(YYYYMMDD), 3 + 60))
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    vb_zerocurve = make_listvariable_interface(left_frame, 'ZeroCurve(자동Load)', termratestr(ZeroTerm, ZeroRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_DayCount = make_listvariable_interface(center_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)
    vb_CapFloorFlag = make_listvariable_interface(center_frame, 'Cap:0,Floor:1', ["0: Cap","1: Floor"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    vb_StrikeFlag = make_listvariable_interface(center_frame, '행사가격Flag', ["0: 직접입력","1: ATM","2: SwapRate"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    v_StrikePrice = make_variable_interface(center_frame, '(직접입력)\nStrike Rate(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=2.56)
    vb_VolFlag = make_listvariable_interface(center_frame, 'VolFlag', ["0: Black Vol","1: Normal Vol"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=1)
    v_Vol = make_variable_interface(center_frame, '변동성(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=0.99)
    v_FirstFixingRate = make_variable_interface(center_frame, '최근 Fixing Rate(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=0)
    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    Result = [0,0,0,0]
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, Result]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else EDate_YYYYMMDD(int(YYYYMMDD), 3)
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else EDate_YYYYMMDD(int(YYYYMMDD), 3 + 60)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        DayCount = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else 0
        CapFloorFlag = int(str(vb_CapFloorFlag.get(vb_CapFloorFlag.curselection())).split(":")[0]) if vb_CapFloorFlag.curselection() else 0    
        StrikeFlag = int(str(vb_StrikeFlag.get(vb_StrikeFlag.curselection())).split(":")[0]) if vb_StrikeFlag.curselection() else 0    
        StrikePrice = float(v_StrikePrice.get())/100 if len(str(v_StrikePrice.get())) > 0 else 0
        VolFlag = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 0    
        Vol = float(v_Vol.get())/100 if len(str(v_Vol.get())) > 0 else 0.01
        FirstFixingRate = 0 
        if PriceDate > SwapEffectiveDate : 
            FirstFixingRate = float(v_FirstFixingRate.get()) if len(str(v_FirstFixingRate.get())) > 0 else 0
        ResultValue = [0,0,0,0]
        Pricing_CapFloor(CapFloorFlag,PriceDate,SwapEffectiveDate,SwapMaturity,L1_NumCpnOneYear_P1,
                        Nominal,Vol,StrikePrice,0,ZeroTerm,
                        ZeroRate,DayCount,VolFlag,Holidays,FirstFixingRate,
                        0,StrikeFlag,ResultValue)  
        OptPrice = ResultValue[0]
        SwapRate = ResultValue[1]      
        output_label.config(text = f"\n결과: {np.round(OptPrice/Nominal*100,6)}%\nSwapRate: \n{np.round(SwapRate*100,6)}%\n행사가격:\n{np.round(StrikePrice*100,6)}%", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2     
        MyArrays[4] = ResultValue 
          
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop()     
    return 0,0,0,0

def CapFloorCalibrationProgram(currdir) : 
    YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\inputdata",MultiSelection=False, Comments="제너레이터를 위한 Cap데이터", DefaultStringList= ["Cap"])
    try : 
        HolidayDate = ReadCSV(currdir + "\\MarketData\\holidays\\Holidays.csv").fillna("19990101").applymap(lambda x : str(x).replace("-","")).astype(np.float64)        
    except FileNotFoundError : 
        HolidayDate = []
    MyData = Data[0].astype(np.float64)
    Tenor = MyData["Tenor"]
    Quote = MyData["QuotePercent"].astype(np.float64)/100
    ZeroCurveName = Name[0]
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namenotin = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    Data = Data[Data['DirectoryPrint'].apply(lambda x : ('EQ' in str(x).upper() and 'VOL' in str(x).upper()) == False)] #Out EQ Vol 
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == YYYYMMDD]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))                 
        
    Currency = Name[0].split("\\")[-2]
    ZeroCurveRawData = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Currency"] == Currency]

    root = tk.Tk()
    root.title("Swaption Pricer")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = False, textfont = 11, defaultflag = True, defaultvalue=int(YYYYMMDD))    
    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=100)    
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    vb_DayCount = make_listvariable_interface(left_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)    
    vb_CapFloorFlag = make_listvariable_interface(left_frame, 'CapFloorFlag', ["0: Cap","1: Floor"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    vb_Logging = make_listvariable_interface(left_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, pady = 10)
    v_SaveName = make_variable_interface(left_frame, '저장할 커브볼 명\n(ex: KRW Cap Vol)', bold = True, textfont = 11, defaultflag = True, defaultvalue="")

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_SelectedCurve_P1 = make_listvariable_interface(center_frame, 'ZeroCurve 선택', list(GroupbyYYYYMMDD["ListName"]), listheight = 5, textfont = 11, titlelable = True, titleName = "MarketData Info", defaultflag = True, defaultvalue = 0, width = 50, DefaultStringList=["IRS"])
    vb_VolFlag = make_listvariable_interface(center_frame, 'VolFlag', ["0: Black Vol","1: Normal Vol"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=1)
    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    Result = [0,0,0,0]
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2,Result]

    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        NCPNOneYear = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        DayCountFlag = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else 0
        CapFloorFlag = int(str(vb_CapFloorFlag.get(vb_CapFloorFlag.curselection())).split(":")[0]) if vb_CapFloorFlag.curselection() else 0
        VolFlag = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 0
        StrikeFlag = 2
        StrikePrice = 0
        NSelectedCurve = int(str(vb_SelectedCurve_P1.get(vb_SelectedCurve_P1.curselection())).split(".")[0]) if vb_SelectedCurve_P1.curselection() else 1
        Holidays = HolidayDate[Currency].dropna() if Currency in HolidayDate.columns else []
        StartDate = NextNthBusinessDate(PriceDate, 1, Holidays)
        TenorYYYYMMDD = Tenor.apply(lambda x : EDate_YYYYMMDD(StartDate, int(x)) if float(x) < 1200 else (ExcelDateToYYYYMMDD(x) if float(x) < 19000101 else float(x)))
        CurveDirectory = ZeroCurveRawData[ZeroCurveRawData["Number"] == NSelectedCurve]["Directory"].iloc[0]
        CurveInfo = ReadCSV(CurveDirectory, True)
        ZeroTerm = CurveInfo["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        ZeroRate = CurveInfo["Rate"].astype(np.float64)
        Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)
        NA = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 100
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        SaveName = str(v_SaveName.get()) if len(str(v_SaveName.get())) > 0 else "TempCapVol"
        dblErrorRange = 0.00001
        ResultCapFloorImvol = []
        FwdSwpRate = []

        Calibration = True
        for i in range(len(TenorYYYYMMDD)) : 
            SwapMaturityDate = TenorYYYYMMDD[i]
            Price = float(Quote[i])
            MaxVol = 1.0
            MinVol = 0.000001
            TargetVol = MaxVol
            ResultValue = [0,0,0,0]
            #print(CapFloorFlag, PriceDate, StartDate, SwapMaturityDate, NCPNOneYear, 
            #                     NA, TargetVol, StrikePrice, 0, ZeroTerm, 
            #                     ZeroRate, DayCountFlag, VolFlag, Holidays, 0,
            #                     0, 2 if StrikePrice == 0 else 0, ResultValue)
            for j in range(1000) : 
                Pricing_CapFloor(CapFloorFlag, PriceDate, StartDate, SwapMaturityDate, NCPNOneYear, 
                                 NA, TargetVol, StrikePrice, 0, ZeroTerm, 
                                 ZeroRate, DayCountFlag, VolFlag, Holidays, 0,
                                 0, 2 if StrikePrice == 0 else 0, ResultValue)
                CalcRate = ResultValue[0]/NA - Price
                if abs(CalcRate) < dblErrorRange : 
                    break
                if (CalcRate > 0) : 
                    MaxVol = TargetVol
                else : 
                    MinVol = TargetVol
                TargetVol = (MinVol + MaxVol) / 2
                
            if j == 1000 : 
                print("VolCalibration Fail Tenor" + str(SwapMaturityDate))
                Calibration = False
            ResultCapFloorImvol.append(TargetVol)
            FwdSwpRate.append(ResultValue[1])
        ResultData = pd.DataFrame(ResultCapFloorImvol, index = TenorYYYYMMDD, columns = ["CapFloorVol"])
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        ResultData["FwdSwpRate"] = FwdSwpRate
        ResultData = ResultData.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=False)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, (ResultData*100).round(4).reset_index(), width = 80)
        SaveYN, SaveDir = 0, ""
        if LoggingFlag > 0 : 
            if YYYYMMDD not in os.listdir(currdir + "\\MarketData\\outputdata") : 
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(PriceDate))
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(PriceDate) + "\\" + Currency)    
                    
            cvname = SaveName
            targetdir = currdir + "\\MarketData\\outputdata\\" + str(PriceDate) + "\\" + str(Currency)
            print("\n저장시도\n")
            try : 
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultData.to_csv(TheName, index = True, encoding = "cp949")
                    SaveYN = 1
                    SaveDir = TheName
                    print("\n저장완료\n")
            except FileNotFoundError : 
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(PriceDate) + "\\" + Currency)    
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultData.to_csv(TheName, index = True, encoding = "cp949")
                    SaveYN = 1
                    SaveDir = TheName
                    print("\n저장완료\n")

        output_label.config(text = f"\n결과: {Calibration}\n저장:{SaveYN}\n저장경로:\n{SaveDir}", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
        MyArrays[4] = ResultCapFloorImvol
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop()     
    return 0,0,0,0        

def BS_Swaption_Program(HolidayDate, currdir) : 
    YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\outputdata",MultiSelection=False, namenotin = "Vol", Comments="Pricing을 위한 ZeroCurve", DefaultStringList= ["IRS"])
    ZeroCurve = Data[0]
    ZeroTerm = ZeroCurve["Term"].astype(np.float64)
    ZeroRate = ZeroCurve["Rate"].astype(np.float64)
    
    ZeroCurveName = Name[0].split("\\")[-1].replace(".csv","")  
    Currency = Name[0].split("\\")[-2]
    Holidays = list(HolidayDate[Currency].dropna().unique()) if Currency in HolidayDate.columns else []
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namein = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    Data = Data[Data['DirectoryPrint'].apply(lambda x : ('EQ' in str(x).upper() and 'VOL' in str(x).upper()) == False)] #Out EQ Vol 
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == YYYYMMDD]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))            

    root = tk.Tk()
    root.title("Swaption Pricer")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=EDate_YYYYMMDD(int(YYYYMMDD), 3))
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=EDate_YYYYMMDD(int(YYYYMMDD), 3 + 60))
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_SelectedCurve_P1 = make_listvariable_interface(center_frame, 'Swaption Vol 선택', list(GroupbyYYYYMMDD["ListName"]), listheight = 5, textfont = 11, titlelable = True, titleName = "Swaption Info", defaultflag = True, defaultvalue = 0, width = 50, DefaultStringList=["Vol"])
    vb_DayCount = make_listvariable_interface(center_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)
    vb_FixedPayer0Receiver1 = make_listvariable_interface(center_frame, 'FixedPayer:0,Receiver:1', ["0: Fixed Payer Swaption","1: Fixed Receive Swaption"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    v_StrikePrice = make_variable_interface(center_frame, 'Strike Rate(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=2.56)
    vb_VolFlag = make_listvariable_interface(center_frame, 'VolFlag', ["0: Black Vol","1: Normal Vol"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=1)
    
    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    vb_zerocurve = make_listvariable_interface(Result_frame, 'ZeroCurve(자동Load)', termratestr(ZeroTerm, ZeroRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)

    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else EDate_YYYYMMDD(int(YYYYMMDD), 3)
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else EDate_YYYYMMDD(int(YYYYMMDD), 3 + 60)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        DayCount = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)
        FixedPayer0Receiver1 = int(str(vb_FixedPayer0Receiver1.get(vb_FixedPayer0Receiver1.curselection())).split(":")[0]) if vb_FixedPayer0Receiver1.curselection() else 0    
        StrikePrice = float(v_StrikePrice.get())/100 if len(str(v_StrikePrice.get())) > 0 else 0
        SelectedNumber = int(str(vb_SelectedCurve_P1.get(vb_SelectedCurve_P1.curselection())).split(".")[0]) if vb_SelectedCurve_P1.curselection() else 1
        BSVol0NormalVol1 = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 1
        
        NMonthOpt = DayCountAtoB(PriceDate, SwapEffectiveDate)/365*12
        NMonthSwap = DayCountAtoB(SwapEffectiveDate, SwapMaturity)/365*12
        SwaptionVolRaw = ReadCSV(GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == SelectedNumber]["Directory"].iloc[0], True)
        SwaptionVolRawSetIndex = SwaptionVolRaw.astype(np.float64).set_index(SwaptionVolRaw.columns[0])
        SwaptionVolRawSetIndex.columns = SwaptionVolRawSetIndex.columns.astype(np.float64)
        SwaptionVolArray = SwaptionVolRawSetIndex.values.astype(np.float64)
        Vol = Linterp2D(list(SwaptionVolRawSetIndex.columns), list(SwaptionVolRawSetIndex.index), SwaptionVolArray,NMonthOpt, NMonthSwap)

        Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)

        ResultDict = BS_Swaption(PriceDate, SwapEffectiveDate, SwapMaturity, L1_NumCpnOneYear_P1, Nominal, Vol, StrikePrice, ZeroTerm, ZeroRate, DayCountFracFlag = DayCount, VolFlag = BSVol0NormalVol1, HolidaysFixing = Holidays, HolidaysPay = Holidays, NBDayFromEndDateToPay = 0, FixedPayer0Receiver1 = FixedPayer0Receiver1)
        P = ResultDict["Price"]
        V = ResultDict["Value"]
        F = ResultDict["ForwardSwapRate"]
        X = ResultDict["ExerciseValue"]        
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        SwaptionVolRawSetIndex = SwaptionVolRawSetIndex.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=False)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, (SwaptionVolRawSetIndex*100).round(2).reset_index(), width = 80)

        output_label.config(text = f"\n결과: {np.round(P,4)}({np.round(P/Nominal*100,4)}%)\n\nValue: \n{np.round(V)}\n\nForwardSwapRate: \n{np.round(F*100,4)}% \n사용된 변동성:\n{np.round(Vol*100,4)}%", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop()     
    return 0,0,0,0

def PricingBondProgram(HolidayDate = pd.DataFrame([]), currdir = os.getcwd()) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata', 
                                                                  namenotin = "vol",
                                                                  Comments = "채권 Pricing을 위한 커브 번호를 입력하시오.",
                                                                  MultiSelection = False, defaultvalue=-1, DefaultStringList=["CORP"]) 
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    print(curvename)    
    if len(MyMarketDataList) == 1 : 
        Curve = MyMarketDataList[0]
        UsedCurveName = Name[0]
    elif len(MyMarketDataList) == 0 : 
        MainFlag2 = MainViewer(Title = 'Continue', MyText = '해당 폴더에 MarketData가 없습니다\n종료하시겠습니까', MyList = ["0: 종료", "1: 계속 다른업무 실행"], size = "800x450+30+30", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
        return MainFlag2, "","",""
    else : 
        print("\n     채권을 평가하기 위해 사용할 커브 번호를 입력하세요.\n")        
        n = int(input())
        Curve = MyMarketDataList[n-1]
        UsedCurveName = Name[n-1]
    Curr = UsedCurveName.split("\\")[-2].lower()
    HolidaysForSwap = []
    YYYY = int(YYYYMMDD) // 10000
    if 'krw' in Curr : 
        HolidaysForSwap = KoreaHolidaysFromStartToEnd(YYYY-1, YYYY + 60)
    elif "usd" in Curr : 
        HolidaysForSwap = USHolidaysFromStartToEnd(YYYY-1, YYYY + 60)            
    else : 
        if Curr.upper() in HolidayDate.columns : 
            HolidaysForSwap = list(HolidayDate[Curr.upper()].values)
        else : 
            HolidaysForSwap = []
        
    CurveTerm = list(Curve["Term" if "Term" in Curve.columns else "term"])
    CurveRate = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
    
    root = tk.Tk()
    root.title("Bond Pricer(Single Phase)")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-1) * 10000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+19) * 10000 + 929)
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], titlelable = True, titleName = "Leg1 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    v_SwapMaturityToPayDate = make_variable_interface(left_frame, '기말일TO지급일까지영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 2)
    v_L1_FixedCpnRate_P1 = make_variable_interface(left_frame, 'Leg1 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =2.79)
    v_FloatFlag = make_variable_interface(left_frame, '변동금리채여부(0 or 1)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0)
    vb_L1_DayCount = make_listvariable_interface(left_frame, 'Leg1 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(center_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_L1FirstFixing = make_variable_interface(center_frame, 'Leg1)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_zerocurve = make_listvariable_interface(center_frame, 'ZeroCurve(자동Load)', termratestr(CurveTerm, CurveRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)
    v_YTMRate = make_variable_interface(center_frame, 'YTM금리(%)\n(YTM평가시 입력)', bold = False, textfont = 11)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)
    vb_Book = make_listvariable_interface(Result_frame, 'Book', ["0: Book 안함","1: Booking"], listheight = 2, textfont = 11, pady = 10)
    vb_CSRBucket = make_listvariable_interface(Result_frame, 'CSRBucket', ["1: 정부,중앙은행","2: 지방정부, 공공행정","3: 금융","4: 원자재","5: 소비재","6: 기술통신"], listheight = 4, textfont = 11, pady = 10)

    Value = 0
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        SwapMaturityToPayDate = int(v_SwapMaturityToPayDate.get()) if len(str(v_SwapMaturityToPayDate.get())) > 0 else 0
        FloatFlag= int(v_FloatFlag.get()) if len(str(v_FloatFlag.get())) > 0 else 0
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P1.get()) : 
                L1_FixedCpnRate_P1 = float(v_L1_FixedCpnRate_P1.get())/100
            else : 
                L1_FixedCpnRate_P1 = float(str(v_L1_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P1 = 0
        if FloatFlag > 0 :
            L1ResultPayoff = "R(T) x 1" + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L1ResultPayoff = str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
            
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else 0
        
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        BookFlag = int(str(vb_Book.get(vb_Book.curselection())).split(":")[0]) if vb_Book.curselection() else 0
        Bucket= int(str(vb_CSRBucket.get(vb_CSRBucket.curselection())).split(":")[0]) if vb_CSRBucket.curselection() else 1
        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0
        YTMRate = float(v_YTMRate.get())/100 if str(v_YTMRate.get()) else 0.0
        YTMFlag = YTMRate > 0
        T = DayCountFractionAtoB(int(PriceDate),SwapMaturity, L1_DayCount)
        ErrorFlag, ErrorString = Calc_Schedule_ErrorCheck(Nominal, SwapEffectiveDate, int(PriceDate), SwapMaturity, CurveTerm, 
                              CurveRate, L1_NumCpnOneYear_P1, L1_DayCount)
        AIList = [0]
        if ErrorFlag == 0 : 
            Value, PV01, TempPV01 = Calc_Bond_PV01(Nominal, 1, FloatFlag, L1FirstFixing, SwapEffectiveDate, 
                    int(PriceDate), SwapMaturity, L1_FixedCpnRate_P1, CurveTerm if YTMFlag == 0 else [T], CurveRate if YTMFlag == 0 else [YTMRate], 
                    L1_NumCpnOneYear_P1, L1_DayCount+5, KoreanHoliday = False, MaturityToPayDate = SwapMaturityToPayDate, EstZeroCurveTerm = [],
                    EstZeroCurveRate = [], FixingHolidayList = HolidaysForSwap, AdditionalPayHolidayList  = HolidaysForSwap, NominalDateIsNominalPayDate = False,
                    LoggingFlag = LoggingFlag, LoggingDir = currdir, ModifiedFollow = 1, DiscCurveName = UsedCurveName, YTMPricing=YTMFlag, AIList = AIList)         
            GIRRRisk = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01, "PV01Term","PV01"), 2 if Value > 10000 else 4)
            CSRRisk, BKT = Calc_CSRDeltaNotCorrelated_FromGreeks(PV01, "PV01Term","PV01", Bucket)
            CSRRisk = np.round(CSRRisk, 2 if Value > 10000 else 4)
            if PrevTreeFlag == 0 : 
                tree = ttk.Treeview(root)
            else : 
                tree.destroy()
                scrollbar.destroy()
                scrollbar2.destroy()
                tree = ttk.Treeview(root)
            PV01 = PV01.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
            tree.pack(padx=5, pady=5, fill="both", expand=True)
            scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
            scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.configure(xscrollcommand=scrollbar2.set)
            scrollbar.pack(side="right", fill="y")    
            scrollbar2.pack(side="bottom", fill="x")    
            
            PrevTreeFlag = insert_dataframe_to_treeview(tree, PV01.reset_index(), width = 100)
            if BookFlag in ["y","Y","1",1] : 
                GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
                Data_GIRR = MapGIRRDeltaGreeks(PV01.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
                Data_GIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"]
                GIRR = pd.DataFrame([list(Data_GIRR["GIRR_Delta_Sensi"])], columns = list(Data_GIRR["GIRR_Tenor"].apply(lambda x : "GIRR_" + str(x))))
                CSR_RiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
                Data_CSR = MapCSRDeltaGreeks(PV01.set_index("PV01Term")["PV01"], CSR_RiskFactor).reset_index()
                Data_CSR.columns = ["CSR_Tenor","CSR_Delta_Sensi"]
                CSR = pd.DataFrame([list(Data_CSR["CSR_Delta_Sensi"])], columns = list(Data_CSR["CSR_Tenor"].apply(lambda x : "CSR_" + str(x))))
                
                df_pre = ReadCSV(currdir + "\\Book\\Bond\\Bond.csv")
                MyCol = ["Nominal","FloatFlag","FixingRate","EffectiveDate","EndDate",
                        "NBDFromEndDateToPayDate","CpnRate","NumCpnOneYear","DayCountFlag","ModifiedFollowing",
                        "DiscCurveName","EstCurveName","Currency","Holiday","MTM","PriceDate","Bucket"]
                Contents = [Nominal, FloatFlag, L1FirstFixing, SwapEffectiveDate, SwapMaturity, 
                            SwapMaturityToPayDate, L1_FixedCpnRate_P1, L1_NumCpnOneYear_P1, L1_DayCount, 1, 
                            UsedCurveName.split("\\")[-1], UsedCurveName.split("\\")[-1], UsedCurveName.split("\\")[-2], UsedCurveName.split("\\")[-2], Value, YYYYMMDD, str(BKT)]
                data2 = pd.DataFrame([Contents], columns = MyCol)
                data2 = pd.concat([data2, GIRR, CSR],axis = 1)
                df = pd.concat([df_pre, data2],axis = 0)
                df.index = np.arange(len(df))
                df.to_csv(currdir + "\\Book\\Bond\\Bond.csv", index = False, encoding = "cp949")            
            output_label.config(text = f"\n결과: {np.round(Value,4)}\nAccrued Interest: \n{np.round(AIList[0],4)}\nLeg1 Payoff: \n{L1ResultPayoff}\nGIRR: \n{GIRRRisk}\nCSR: \n{CSRRisk}\nBooking = {bool(BookFlag)}", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"\n결과: \n{ErrorString}", font = ("맑은 고딕", 12, 'bold'))
            
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
    root.mainloop()
    
    MainFlag2 = 0
    return MainFlag2, Value, PV01, TempPV01

def PricingIRSProgram(HolidayData = pd.DataFrame([]), FXData = pd.DataFrame([]) , ComplexIRSFlag = 0, CMSUseFlag = 0) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                  namenotin = "vol",
                                                                  Comments = "IRS Pricing을 위한 커브 번호를 입력하시오.\n(Estimation Curve와 Discount Curve가 다른 경우 1, 2 등 두개 입력)",DefaultStringList = ["IRS"])     
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    print(curvename)  
    HolidaysForSwap = []
    Curr, UsedCurveName1 = "", ""
    YYYY = int(YYYYMMDD) // 10000
    if len(MyMarketDataList) == 1 : 
        Curve = MyMarketDataList[0]
        UsedCurveName1 = Name[0]
        Curr = Name[0].split("\\")[-2].lower()
        if 'krw' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(YYYY-1, YYYY + 60)
        elif "usd" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(YYYY-1, YYYY + 60)
        CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
        CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
        CurveTerm2, CurveRate2 = CurveTerm1, CurveRate1     
        UsedCurveName2 = ""
    else : 
        Curve, Curve2 = MyMarketDataList[0], MyMarketDataList[1]
        UsedCurveName1, UsedCurveName2 = Name[0], Name[1]
        if "STD" not in Name[0].upper() and "IRS" not in Name[0].upper() and "OIS" not in Name[0].upper() :
            Curve, Curve2 = MyMarketDataList[1], MyMarketDataList[0]
            UsedCurveName1, UsedCurveName2 = Name[1], Name[0]
             
        Curr = Name[0].split("\\")[-2].lower()
        if 'krw' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(YYYY-1, YYYY + 60)
        elif "usd" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(YYYY-1, YYYY + 60)
        CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
        CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
        CurveTerm2 = list(Curve2["Term" if "Term" in Curve2.columns else "term"]) 
        CurveRate2 = list(Curve2["Rate" if "Rate" in Curve2.columns else "rate"])
        
    if len(HolidayData) > 0 : 
        if Curr.upper() in HolidayData.columns : 
            HolidaysForSwap = list(HolidayData[Curr.upper()].dropna().unique())    
    if CMSUseFlag == True : 
        YYYYMMDD2, Name2, MyMarketDataList2 = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                        namein = "tion",
                                                                        Comments = "Convexity Adjustment를 위한 Swaption Vol Curve를 선택하시오\n->",
                                                                        MainComments = "\nCMS, CMT Pricing을 위해 Volatility 마켓데이터를 선택해야합니다.",MultiSelection=False,DefaultStringList=["Vol"])     
    else : 
        YYYYMMDD2, Name2, MyMarketDataList2 = YYYYMMDD, Name, MyMarketDataList                    

    root = tk.Tk()
    root.title("IRS Pricer(Single Phase)")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-1)*10000+929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+19)*10000+929)
    vb_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    v_SwapMaturityToPayDate = make_variable_interface(left_frame, '기말일TO지급일까지영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 2)
    vb_FixedPayer = make_listvariable_interface(left_frame, '변동금리 수취여부', ["0: 고정수취, 변동지급","1: 변동수취, 고정지급"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 1)
    v_FixedCpnRate_P1 = make_variable_interface(left_frame, '고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =2.427565)
    if CMSUseFlag == True : 
        v_RefSwapMaturity_T = make_variable_interface(left_frame, '변동금리 만기\n(3M-> 0.25, 5Y-> 5)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11)
        vb_RefSwapNCPNOneYear_P1 = make_listvariable_interface(left_frame, '변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 2)
    else : 
        v_RefSwapMaturity_T, vb_RefSwapNCPNOneYear_P1 = None, None        
    vb_DayCount = make_listvariable_interface(left_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_Nominal = make_variable_interface(center_frame, 'Nominal Amount', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_PriceDate = make_variable_interface(center_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_L1FirstFixing = make_variable_interface(center_frame, '최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_zerocurve = make_listvariable_interface(center_frame, 'ZeroDiscCurve(자동Load)', termratestr(CurveTerm1, CurveRate1), titleName = "MARKET DATA INFO", titlelable= True, listheight = 11, textfont = 11)
    vb_zerocurve2 = make_listvariable_interface(center_frame, 'ZeroEstCurve(자동Load)', termratestr(CurveTerm2, CurveRate2), listheight = 11, textfont = 11)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_LookBackDays = make_variable_interface(right_frame, 'LookBackDays', bold = False, textfont = 11, titleName = "SOFR설정(필요시입력)", titlelable= True, defaultflag = True, defaultvalue = 0)
    vb_ObservShift = make_listvariable_interface(right_frame, 'ObservShift', ["0: FALSE","1: TRUE"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue= 0)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)
    vb_Book = make_listvariable_interface(Result_frame, 'Book', ["0: Book 안함","1: Booking"], listheight = 2, textfont = 11, pady = 10)
    Value = 0
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        VolSearch = 0
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        SwapMaturityToPayDate = int(v_SwapMaturityToPayDate.get()) if len(str(v_SwapMaturityToPayDate.get())) > 0 else 0

        FixedPayer = int(str(vb_FixedPayer.get(vb_FixedPayer.curselection())).split(":")[0]) if vb_FixedPayer.curselection() else 1
        NumCpnOneYear_P1 = int(vb_NumCpnOneYear_P1.get(vb_NumCpnOneYear_P1.curselection())) if vb_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_FixedCpnRate_P1.get()) : 
                FixedCpnRate_P1 = float(v_FixedCpnRate_P1.get())/100
            else : 
                FixedCpnRate_P1 = float(str(v_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            FixedCpnRate_P1 = 0
            
        if CMSUseFlag == True : 
            if len(str(v_RefSwapMaturity_T.get())) > 0 :         
                if 'm' in str(v_RefSwapMaturity_T.get()).lower() : 
                    RefSwapMaturity_T = float(str(v_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_RefSwapMaturity_T.get()).lower() :
                    RefSwapMaturity_T = float(str(v_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    RefSwapMaturity_T = float(v_RefSwapMaturity_T.get()) 
            else : 
                RefSwapMaturity_T = 0.25
            RefSwapNCPNOneYear_P1 = int(vb_RefSwapNCPNOneYear_P1.get(vb_RefSwapNCPNOneYear_P1.curselection())) if vb_RefSwapNCPNOneYear_P1.curselection() else 4
        else : 
            RefSwapMaturity_T = 0.25
            RefSwapNCPNOneYear_P1 = 4
        if FixedPayer == 1 : 
            if CMSUseFlag == True  : 
                ResultPayoff = "R(T="+ str(np.round(RefSwapMaturity_T, 2))+") x 1" + " - " +str(np.round(FixedCpnRate_P1*100,4)) + "%"
            else : 
                ResultPayoff = "R(T) x 1" + " - " +str(np.round(FixedCpnRate_P1*100,4)) + "%"
        else : 
            ResultPayoff = str(np.round(FixedCpnRate_P1*100,4)) + "% - R(T) x 1"
            
        DayCount = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else 0
        
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        LookBackDays = int(v_LookBackDays.get()) if len(str(v_LookBackDays.get())) > 0 else 0
        ObservShift = int(str(vb_Logging.get(vb_ObservShift.curselection())).split(":")[0]) if vb_ObservShift.curselection() else 0
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        BookFlag = int(str(vb_Book.get(vb_Book.curselection())).split(":")[0]) if vb_Book.curselection() else 0
        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0              
        VolArray, TermVol = [], []            
        if CMSUseFlag == True : 
            OptionData = pd.DataFrame([])
            for i in range(len(Name2)) :
                if "SwapMat/OptMat" in MyMarketDataList2[i].columns or "스왑만기/옵션만기" in MyMarketDataList2[i].columns :
                    OptData = MyMarketDataList2[i].set_index(MyMarketDataList2[i].columns[0])
                    MyInd = OptData.index.astype(np.float64)/12
                    MyCol = OptData.columns.astype(np.float64)/12
                    OptionData = pd.DataFrame(OptData.values, columns = MyCol, index = MyInd)
                    break        
            if i == len(Name) : 
                VolSearch = 0
            else : 
                VolSearch = 1                    
            t = DayCountAtoB(int(PriceDate), SwapMaturity)/365

            if VolSearch == 1 : 
                x = np.array(OptionData.index)
                TermVol = list(OptionData.columns)
                for i in range(len(OptionData.columns)) : 
                    y = OptionData.values[:,i]
                    v = Linterp(x, y, t)
                    VolArray.append(v)               
            else : 
                TermVol = [1]
                VolArray = [0.01]
        ErrorFlag, ErrorString = Calc_Schedule_ErrorCheck(Nominal, SwapEffectiveDate, int(PriceDate), SwapMaturity, CurveTerm1, 
                              CurveRate1, NumCpnOneYear_P1, DayCount)
        if ErrorFlag == 0 : 
            Value, PV01, TempPV01 = Calc_IRS_PV01(Nominal, L1FirstFixing, SwapEffectiveDate, 
                    int(PriceDate), SwapMaturity, FixedCpnRate_P1, CurveTerm1, CurveRate1, 
                    NumCpnOneYear_P1, DayCount, KoreanHoliday = False, MaturityToPayDate = SwapMaturityToPayDate, EstZeroCurveTerm = CurveTerm2,
                    EstZeroCurveRate = CurveRate2, FixingHolidayList = HolidaysForSwap, AdditionalPayHolidayList  = HolidaysForSwap, NominalDateIsNominalPayDate = False,
                    LoggingFlag = LoggingFlag, LoggingDir = currdir, ModifiedFollow = 1, FixedPayerFlag = FixedPayer, 
                    DiscCurveNameLeg1 = UsedCurveName1, EstCurveNameLeg1 = UsedCurveName2, DiscCurveNameLeg2 = UsedCurveName1, EstCurveNameLeg2 = UsedCurveName2, LookBackDays = LookBackDays,
                    ObservShift = ObservShift, CMSFlag = CMSUseFlag, RefSwapMaturity_T = RefSwapMaturity_T, RefSwapNCPNAnn = RefSwapNCPNOneYear_P1, TermVol = TermVol, Vol = VolArray)         
            GIRRRisk1 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01, "PV01Term","PV01"), 4 if Value > 10000 else 2)
            GIRRRisk2 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(TempPV01, "PV01TermEst","PVEst01"), 4 if Value > 10000 else 2)
            GIRRRisk = np.round(GIRRRisk1 + GIRRRisk2, 4)
            if PrevTreeFlag == 0 : 
                tree = ttk.Treeview(root)
            else : 
                tree.destroy()
                scrollbar.destroy()
                scrollbar2.destroy()
                tree = ttk.Treeview(root)
            PV01 = PV01.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
            tree.pack(padx=5, pady=5, fill="both", expand=True)
            scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
            scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.configure(xscrollcommand=scrollbar2.set)
            scrollbar.pack(side="right", fill="y")    
            scrollbar2.pack(side="bottom", fill="x")    
            
            PrevTreeFlag = insert_dataframe_to_treeview(tree, PV01.reset_index(), width = 100)        
            
            if BookFlag in ["y","Y","1",1] : 
                GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
                Data_GIRR = MapGIRRDeltaGreeks(PV01.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
                Data_GIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"]
                GIRR = pd.DataFrame([list(Data_GIRR["GIRR_Delta_Sensi"])], columns = list(Data_GIRR["GIRR_Tenor"].apply(lambda x : "GIRR_" + str(x))))
                
                df_pre = ReadCSV(currdir + "\\Book\\IRS\\IRS.csv")
                MyCol = ["Nominal","FixingRate","EffectiveDate","EndDate",
                        "NBDFromEndDateToPayDate","CpnRate","NumCpnOneYear","DayCountFlag","ModifiedFollowing",
                        "DiscCurveNameLeg1","EstCurveNameLeg1","DiscCurveNameLeg2","EstCurveNameLeg2",
                        "Currency","Holiday","MTM","PriceDate"]
                Contents = [Nominal, L1FirstFixing, SwapEffectiveDate, SwapMaturity, 
                            SwapMaturityToPayDate, FixedCpnRate_P1, NumCpnOneYear_P1, DayCount, 1, 
                            UsedCurveName1.split("\\")[-1], UsedCurveName2.split("\\")[-1], UsedCurveName1.split("\\")[-1], UsedCurveName2.split("\\")[-1],
                            UsedCurveName1.split("\\")[-2], UsedCurveName1.split("\\")[-2], Value , YYYYMMDD]
                data2 = pd.DataFrame([Contents], columns = MyCol)
                data2 = pd.concat([data2, GIRR],axis = 1)
                df = pd.concat([df_pre, data2],axis = 0)
                df.index = np.arange(len(df))
                df.to_csv(currdir + "\\Book\\IRS\\IRS.csv", index = False, encoding = "cp949")

            output_label.config(text = f"\n결과: {np.round(Value,4)}\nPayoff: \n{ResultPayoff}\n\nGIRR: {GIRRRisk}\n\nBooking = {bool(BookFlag)}\n\nVolSearch ={bool(VolSearch)}", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"\n결과: \n{ErrorString}", font = ("맑은 고딕", 12, 'bold'))
            
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
    root.mainloop()
                
    MainFlag2 = 0
    return MainFlag2, Value, PV01, TempPV01

def PricingFXSwapProgram(HolidayDate = pd.DataFrame([]), SpotData = pd.DataFrame([]), currdir = os.getcwd()) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',namenotin = "vol", Comments = "FX Swap을 평가하기 위해서는 최소 두가지 커브를 선택해야 합니다.\n", defaultvalue=[0, 1], DefaultStringList = ["CRS","USD"]) 
    if len(Name) == 1 : 
        print("\n FX Swap을 평가하기 위해서는 최소 두가지 커브가 필요하므로 종료합니다.\n")
    CurveNameShort = np.vectorize(lambda x : x.split("\\")[-1].replace(".csv",""))(Name)
    CurveNameShortList = [str(n) + ": " + i for n, i in enumerate(CurveNameShort)]       
    Curr = np.vectorize(lambda x : x.split("\\")[-2].replace(".csv","") + "/" + "KRW")(Name)
    Spotidx = list(SpotData.index).index(YYYYMMDD) if YYYYMMDD in SpotData.index else -1
    fx1temp = SpotData[Curr[0]].iloc[Spotidx] if Curr[0] in SpotData.columns else 1
    fx2temp = SpotData[Curr[-1]].iloc[Spotidx] if Curr[-1] in SpotData.columns else 1
    root = tk.Tk()
    root.title("FX Swap Pricer")
    root.geometry("1000x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_BuySellFlag = make_listvariable_interface(left_frame, 'Swap구분', ["0: 외화Buy/Sell","1: 외화Sell/Buy"], pady = 3, listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0)
    vb_LDHoliday = make_listvariable_interface(left_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 3, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)
    v_Nominal = make_variable_interface(left_frame, 'Nominal(외화기준)', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_SpotDate = make_variable_interface(left_frame, 'SpotDate', bold = True, textfont = 11, defaultflag = True, defaultvalue = NextNthBusinessDate(int(YYYYMMDD), 2,[]))
    v_SpotPrice = make_variable_interface(left_frame, 'Spot 환율', bold = True, textfont = 11, defaultflag = True, defaultvalue = fx1temp if fx1temp != 1 else fx2temp)
    v_NearDate = make_variable_interface(left_frame, 'NearDate', bold = True, textfont = 11, defaultflag = True, defaultvalue = NextNthBusinessDate(int(YYYYMMDD), 2,[]))
    v_NearPrice = make_variable_interface(left_frame, 'Near 환율', bold = True, textfont = 11, defaultflag = True, defaultvalue = fx1temp if fx1temp != 1 else fx2temp)
    v_FarDate = make_variable_interface(left_frame, 'FarDate', bold = True, textfont = 11, defaultflag = True, defaultvalue = EDate_YYYYMMDD(NextNthBusinessDate(int(YYYYMMDD), 2,[]), 12))
    v_FarPrice = make_variable_interface(left_frame, 'Far 환율', bold = True, textfont = 11, defaultflag = True, defaultvalue = fx1temp if fx1temp != 1 else fx2temp)
    
    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')    
    vb_SelectedCurve_D = make_listvariable_interface(right_frame, 'DomesticCurve 선택', CurveNameShortList, listheight = 5, textfont = 11, titlelable = True, titleName = "Domestic INFO", defaultflag = True, defaultvalue = 0, pady = 10, width = 50)
    vb_SelectedCurve_F = make_listvariable_interface(right_frame, 'ForeignCurve 선택', CurveNameShortList, listheight = 5, textfont = 11, titlelable = True, titleName = "Foreign INFO", defaultflag = True, defaultvalue = 1, width = 50)
    
    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')    
    Variables = []
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, Variables]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        long0short1 = int(str(vb_BuySellFlag.get(vb_BuySellFlag.curselection())).split(":")[0]) if vb_BuySellFlag.curselection() else 0
        HolidayCurr = vb_LDHoliday.get(vb_LDHoliday.curselection()) if vb_LDHoliday.curselection() else "KRW"
        Holidays = HolidayDate[HolidayCurr].dropna() if HolidayCurr in HolidayDate.columns else []
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        CalculatedSpotDate = NextNthBusinessDate(PriceDate, 2, Holidays)
        SpotDate = int(v_SpotDate.get()) if len(str(v_SpotDate.get())) > 0 else CalculatedSpotDate
        SpotPrice = float(v_SpotPrice.get()) if len(str(v_SpotPrice.get())) > 0 else (fx1temp if fx1temp != 1 else fx2temp)
        NearDate = int(v_NearDate.get()) if len(str(v_NearDate.get())) > 0 else CalculatedSpotDate
        NearPrice = float(v_NearPrice.get()) if len(str(v_NearPrice.get())) > 0 else (fx1temp if fx1temp != 1 else fx2temp)
        FarDate = int(v_FarDate.get()) if len(str(v_FarDate.get())) > 0 else EDate_YYYYMMDD(CalculatedSpotDate, 12)
        FarPrice = float(v_FarPrice.get()) if len(str(v_FarPrice.get())) > 0 else (fx1temp if fx1temp != 1 else fx2temp)
        NSelectedCurve_D = int(str(vb_SelectedCurve_D.get(vb_SelectedCurve_D.curselection())).split(":")[0]) if vb_SelectedCurve_D.curselection() else 0
        NSelectedCurve_F = int(str(vb_SelectedCurve_F.get(vb_SelectedCurve_F.curselection())).split(":")[0]) if vb_SelectedCurve_F.curselection() else 0
        DomesticTerm = MyMarketDataList[NSelectedCurve_D]["Term"].astype(np.float64)
        DomesticRate = MyMarketDataList[NSelectedCurve_D]["Rate"].astype(np.float64)
        ForeignTerm = MyMarketDataList[NSelectedCurve_F]["Term"].astype(np.float64)
        ForeignRate = MyMarketDataList[NSelectedCurve_F]["Rate"].astype(np.float64)
        Preprocessing_ZeroTermAndRate(DomesticTerm, DomesticRate, PriceDate)            
        Preprocessing_ZeroTermAndRate(ForeignTerm, ForeignRate, PriceDate)           
        SpotT = DayCountAtoB(PriceDate, SpotDate)/365 if SpotDate > 0 else DayCountAtoB(PriceDate, CalculatedSpotDate)/365
        T1, T2 = DayCountAtoB(PriceDate, NearDate)/365, DayCountAtoB(PriceDate, FarDate)/365 
        F1, F2 = NearPrice, FarPrice
        v, vD, vF = Calc_Value_FXSwap(SpotPrice, T1, T2, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, long0short1, SpotT, Nominal, F1, F2)
        VariableList = [SpotPrice, T1, T2, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, long0short1, SpotT, Nominal, F1, F2]
        v1 = format(np.round(v, 4), ",f")
        v2 = format(np.round(vD, 4), ",f")
        v3 = format(np.round(vF, 4), ",f")
        output_label.config(text = f"NPV: \n{v1}\nDomestic NPV: \n{v2}\nForeign NPV: \n{v3}", font = ("맑은 고딕", 12, 'bold'))
            
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
        MyArrays[4] = VariableList        

    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop() 
    return 0, 0, 0, 0
        
def PricingCRSProgram(HolidayData = pd.DataFrame([]), SpotData = pd.DataFrame([])) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',namenotin = "vol", Comments = "Currency Swap을 평가하기 위해서는 최소 두가지 커브를 선택해야 합니다.\n", defaultvalue=[0, 1], DefaultStringList=["CRS","USD,IRS"]) 

    if len(Name) == 1 : 
        print("\n Currency Swap을 평가하기 위해서는 최소 두가지 커브가 필요하므로 종료합니다.\n")
        return "", 0, pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([])
    CurveNameShort = np.vectorize(lambda x : x.split("\\")[-1].replace(".csv",""))(Name)
    CurveNameShortList = [str(n) + ": " + i for n, i in enumerate(CurveNameShort)]       
    Curr = np.vectorize(lambda x : x.split("\\")[-2].replace(".csv","") + "/" + "KRW")(Name)
    YYYY = int(YYYYMMDD) // 10000
    Spotidx = list(SpotData.index).index(YYYYMMDD) if YYYYMMDD in SpotData.index else -1
    fx1temp = SpotData[Curr[0]].iloc[Spotidx] if Curr[0] in SpotData.columns else 1
    fx2temp = SpotData[Curr[-1]].iloc[Spotidx] if Curr[-1] in SpotData.columns else 1
    root = tk.Tk()
    root.title("CRS Pricer(Single Phase)")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_Nominal1 = make_variable_interface(left_frame, 'Leg1 Nominal Amount', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_Nominal2 = make_variable_interface(left_frame, 'Leg2 Nominal Amount', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000/1400)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))

    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-1) * 10000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+19) * 10000 + 929)
    v_SwapMaturityToPayDate = make_variable_interface(left_frame, '기말일TO지급일까지\n영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 2)
    vb_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["0","1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3)
    vb_FixedPayer = make_listvariable_interface(left_frame, 'Fixed PayerFlag', ["0: Leg1 수취 \nLeg2 지급","1: Leg1 지급 \nLeg2 수취"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, width = 20)
    vb_Logging = make_listvariable_interface(left_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, pady = 10)
    vb_Book = make_listvariable_interface(left_frame, 'Book', ["0: Book 안함","1: Booking"], listheight = 2, textfont = 11, pady = 10)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_DomeDiscNum = make_listvariable_interface(right_frame, 'Discount Curve \n(리스트에서 선택)', CurveNameShortList, listheight = 3, textfont = 11, titlelable = True, titleName = "(Leg1)MarketDataSet", defaultflag = True, defaultvalue=0, width = 30)
    vb_DomeEstNum = make_listvariable_interface(right_frame, 'Estimation Curve', ["-1: EstimationCurve 미사용"] + CurveNameShortList, listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0, width = 30)
    v_FixedCpnRate_P1 = make_variable_interface(right_frame, 'Leg1 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =2.19)
    vb_LD_DayCount = make_listvariable_interface(right_frame, 'Leg1 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag=True, defaultvalue=0)
    v_LDFirstFixing = make_variable_interface(right_frame, '최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_LDPricingFXRate = make_variable_interface(right_frame, 'Leg1 Pricing 환율', bold = False, textfont = 11, defaultflag = True, defaultvalue = fx1temp)
    vb_LDHoliday = make_listvariable_interface(right_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 3, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)
    v_LD_LookBackDays = make_variable_interface(right_frame, 'LookBackDays', bold = False, textfont = 11, titleName = "SOFR설정(필요시입력)", titlelable= True, defaultflag = True, defaultvalue = 0)

    rightright_frame = tk.Frame(root)
    rightright_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_ForeDiscNum = make_listvariable_interface(rightright_frame, 'Discount Curve \n(리스트에서 선택)', CurveNameShortList, listheight = 3, textfont = 11, titlelable = True, titleName = "(Leg2)MarketDataSet", defaultflag = True, defaultvalue=1, width = 30)
    vb_ForeEstNum = make_listvariable_interface(rightright_frame, 'Estimation Curve', CurveNameShortList, listheight = 3, textfont = 11, defaultflag = True, defaultvalue=1, width = 30)
    vb_LF_DayCount = make_listvariable_interface(rightright_frame, 'Leg2 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag=True, defaultvalue=1)
    v_LFFirstFixing = make_variable_interface(rightright_frame, '최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_LFPricingFXRate = make_variable_interface(rightright_frame, 'Leg2 Pricing 환율', bold = False, textfont = 11, defaultflag = True, defaultvalue = fx2temp)
    vb_LFHoliday = make_listvariable_interface(rightright_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 3, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 1)
    v_LF_LookBackDays = make_variable_interface(rightright_frame, 'LookBackDays', bold = False, textfont = 11, titleName = "SOFR설정(필요시입력)", titlelable= True, defaultflag = True, defaultvalue = 0)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    
    for i in range(len(Name)) : 
        vb_zerocurve = make_listvariable_interface(center_frame, CurveNameShortList[i], termratestr(MyMarketDataList[i]["Term"], MyMarketDataList[i]["Rate"]), titleName = "MARKET DATA INFO", titlelable= (i == 0), listheight = 11, textfont = 11)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    Value = 0
    PV01, PV01DomesticDisc, PV01ForeignDisc, PV01DomesticEst, PV01ForeignEst = None, None, None, None, None 
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal1 = float(v_Nominal1.get()) if len(str(v_Nominal1.get())) > 0 else 10000
        Nominal2 = float(v_Nominal2.get()) if len(str(v_Nominal2.get())) > 0 else 10000
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        SwapMaturityToPayDate = int(v_SwapMaturityToPayDate.get()) if len(str(v_SwapMaturityToPayDate.get())) > 0 else 0

        FixedPayer = int(str(vb_FixedPayer.get(vb_FixedPayer.curselection())).split(":")[0]) if vb_FixedPayer.curselection() else 1
        NumCpnOneYear_P1 = int(vb_NumCpnOneYear_P1.get(vb_NumCpnOneYear_P1.curselection())) if vb_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_FixedCpnRate_P1.get()) : 
                FixedCpnRate_P1 = float(v_FixedCpnRate_P1.get())/100
            else : 
                FixedCpnRate_P1 = float(str(v_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            FixedCpnRate_P1 = 0

        DomeDiscNum = int(str(vb_DomeDiscNum.get(vb_DomeDiscNum.curselection())).split(":")[0]) if vb_DomeDiscNum.curselection() else 0
        DomeEstNum = int(str(vb_DomeEstNum.get(vb_DomeEstNum.curselection())).split(":")[0]) if vb_DomeEstNum.curselection() else -1
        
        DomeDiscTerm = MyMarketDataList[DomeDiscNum]["Term"]
        DomeDiscRate = MyMarketDataList[DomeDiscNum]["Rate"]
        if DomeEstNum == -1 : 
            DomeEstTerm = []
            DomeEstRate = []
        else : 
            DomeEstTerm = MyMarketDataList[DomeEstNum]["Term"]
            DomeEstRate = MyMarketDataList[DomeEstNum]["Rate"]
        DomeDiscName = Name[DomeDiscNum]
        DomeEstName = Name[DomeEstNum]
        
        LD_DayCount = int(str(vb_LD_DayCount.get(vb_LD_DayCount.curselection())).split(":")[0]) if vb_LD_DayCount.curselection() else 0
        LDFirstFixing = float(v_LDFirstFixing.get())/100 if len(str(v_LDFirstFixing.get())) > 0 else 0.0              
        LDPricingFXRate = float(v_LDPricingFXRate.get())/100 if len(str(v_LDPricingFXRate.get())) > 0 else 0.0              
        LD_LookBackDays = int(v_LD_LookBackDays.get()) if len(str(v_LD_LookBackDays.get())) > 0 else 0
        LD_Holiday_Curr = vb_LDHoliday.get(vb_LDHoliday.curselection()) if vb_LDHoliday.curselection() else "KRW"
        if LD_Holiday_Curr.upper() in HolidayData.columns : 
            LD_HolidaysForSwap = list(HolidayData[LD_Holiday_Curr.upper()].dropna().unique())  
        elif LD_Holiday_Curr.upper() == 'KRW' : 
            LD_HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif LD_Holiday_Curr.upper() == 'USD' :
            LD_HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else :
            LD_HolidaysForSwap = []

        ForeDiscNum = int(str(vb_ForeDiscNum.get(vb_ForeDiscNum.curselection())).split(":")[0]) if vb_ForeDiscNum.curselection() else 0
        ForeEstNum = int(str(vb_ForeEstNum.get(vb_ForeEstNum.curselection())).split(":")[0]) if vb_ForeEstNum.curselection() else 0
        ForeDiscTerm = MyMarketDataList[ForeDiscNum]["Term"]
        ForeDiscRate = MyMarketDataList[ForeDiscNum]["Rate"]
        ForeEstTerm = MyMarketDataList[ForeEstNum]["Term"]
        ForeEstRate = MyMarketDataList[ForeEstNum]["Rate"]
        ForeDiscName = Name[ForeDiscNum]
        ForeEstName = Name[ForeEstNum]
        if FixedPayer == 0 : 
            ResultPayoff = ("R(Leg1, T) x 1 + " if DomeEstNum >= 0 else "") + str(np.round(FixedCpnRate_P1*100,4)) + "%" + " - R(Leg2, T)"
        else :
            ResultPayoff = "R(Leg2, T) x 1" + " - " + ("R(Leg1, T) x 1 - " if DomeEstNum >= 0 else "") + str(np.round(FixedCpnRate_P1*100,4)) + "%"
             
        LF_DayCount = int(str(vb_LF_DayCount.get(vb_LF_DayCount.curselection())).split(":")[0]) if vb_LF_DayCount.curselection() else 0
        LFFirstFixing = float(v_LFFirstFixing.get())/100 if len(str(v_LFFirstFixing.get())) > 0 else 0.0              
        LFPricingFXRate = float(v_LFPricingFXRate.get())/100 if len(str(v_LFPricingFXRate.get())) > 0 else 0.0              
        LF_LookBackDays = int(v_LF_LookBackDays.get()) if len(str(v_LF_LookBackDays.get())) > 0 else 0
        LF_Holiday_Curr = vb_LFHoliday.get(vb_LFHoliday.curselection()) if vb_LFHoliday.curselection() else "KRW"
        if LF_Holiday_Curr.upper() in HolidayData.columns : 
            LF_HolidaysForSwap = list(HolidayData[LF_Holiday_Curr.upper()].dropna().unique())  
        elif LF_Holiday_Curr.upper() == 'KRW' : 
            LF_HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif LF_Holiday_Curr.upper() == 'USD' :
            LF_HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else :
            LF_HolidaysForSwap = []
        HolidaysForSwap = sorted(list(set(list(LD_HolidaysForSwap) + list(LF_HolidaysForSwap))))
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        BookFlag = int(str(vb_Book.get(vb_Book.curselection())).split(":")[0]) if vb_Book.curselection() else 0
        ErrorFlag, ErrorString = Calc_Schedule_ErrorCheck(Nominal1*Nominal2, SwapEffectiveDate, int(PriceDate), SwapMaturity, DomeDiscTerm, 
                        DomeDiscRate, NumCpnOneYear_P1, LD_DayCount)
        if ErrorFlag == 0 : 
            Value, PV01DomesticDisc, PV01ForeignDisc, PV01DomesticEst, PV01ForeignEst = CalC_CRS_PV01(Nominal1, Nominal2, LDFirstFixing, SwapEffectiveDate, int(PriceDate), SwapMaturity, 
                    FixedCpnRate_P1, DomeDiscTerm, DomeDiscRate, NumCpnOneYear_P1, LD_DayCount, 
                    LF_DayCount, KoreanHoliday = False, MaturityToPayDate = SwapMaturityToPayDate, EstZeroCurveTermDomestic = DomeEstTerm, EstZeroCurveRateDomestic = DomeEstRate, 
                    EstZeroCurveTermForeign = ForeEstTerm, EstZeroCurveRateForeign = ForeEstRate, ZeroCurveTermForeign = ForeDiscTerm, ZeroCurveRateForeign = ForeDiscRate, FixingHolidayListDomestic = LD_HolidaysForSwap, 
                    FixingHolidayListForeign = LF_HolidaysForSwap, AdditionalPayHolidayList = HolidaysForSwap, NominalDateIsNominalPayDate = True, LoggingFlag = LoggingFlag, LoggingDir = currdir, 
                    ModifiedFollow = 1,LookBackDaysDomestic = LD_LookBackDays, LookBackDaysForeign = LF_LookBackDays, ObservShift = False, DomesticPayerFlag = FixedPayer, 
                    DiscCurveName = DomeDiscName, EstCurveName = DomeEstName, ValuationDomesticFX = LDPricingFXRate, ValuationForeignFX = LFPricingFXRate, SOFRFlag = False, 
                    FixFixFlag = False, FirstFloatFixRateForeign= LFFirstFixing, DiscCurveNameForeign = ForeDiscName, EstCurveNameForeign = ForeEstName)    
            
            GIRRRisk1 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01DomesticDisc.fillna(0), "PV01TermDomesticDisc","PV01DomesticDisc"), 4 if Value > 10000 else 2)
            GIRRRisk2 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01DomesticEst.fillna(0), "PV01TermDomesticEst","PV01DomesticEst"), 4 if Value > 10000 else 2)
            GIRRRisk3 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01ForeignDisc.fillna(0), "PV01TermForeignDisc","PV01ForeignDisc"), 4 if Value > 10000 else 2)
            GIRRRisk4 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01ForeignEst.fillna(0), "PV01TermForeignEst","PV01ForeignEst"), 4 if Value > 10000 else 2)
            GIRRRisk = np.round(GIRRRisk1 + GIRRRisk2 + GIRRRisk3 + GIRRRisk4, 4)

            if PrevTreeFlag == 0 : 
                tree = ttk.Treeview(root)
            else : 
                tree.destroy()
                scrollbar.destroy()
                scrollbar2.destroy()
                tree = ttk.Treeview(root)
            PV01 = pd.concat([PV01DomesticDisc, PV01ForeignDisc, PV01DomesticEst, PV01ForeignEst],axis = 1).fillna(0)
            PV01 = PV01.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
            tree.pack(padx=5, pady=5, fill="both", expand=True)
            scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
            scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.configure(xscrollcommand=scrollbar2.set)
            scrollbar.pack(side="right", fill="y")    
            scrollbar2.pack(side="bottom", fill="x")    
            
            PrevTreeFlag = insert_dataframe_to_treeview(tree, PV01.reset_index(), width = 100)    
            output_label.config(text = f"Payoff: \n{ResultPayoff}\n\n결과: {np.round(Value,4)}\n\nGIRR: {GIRRRisk}\n\nBooking = {bool(BookFlag)}", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"Payoff: \n{ErrorString}", font = ("맑은 고딕", 12, 'bold'))
            
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop() 
    
    MainFlag2 = 0#input("종료하시겠습니까? (Y/N)\n->")
    return MainFlag2, Value, PV01DomesticDisc, PV01ForeignDisc, PV01DomesticEst, PV01ForeignEst

def ZeroCurveMaker(MyData, currdir, YYYYMMDD, HolidayDate, FXSpot, CurveName = "") : 
    MyData["Type"] = MyData["Type"].apply(lambda x : str(x).lower())
    ForeignCurveNeeded = 1 if 'sp' in list(MyData["Type"]) else 0
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namenotin = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == YYYYMMDD]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))
    Currency = CurveName.split("\\")[-2]
    DefaultSpot = 1.0
    if ('krw' in Currency.lower()) and (int(YYYYMMDD) in FXSpot.index) : 
        DefaultSpot = FXSpot.loc[int(YYYYMMDD)]["USD/KRW"]
    elif Currency + "/KRW" in FXSpot.columns : 
        DefaultSpot = FXSpot.iloc[-1][Currency + "/KRW"]
        
    DomesticCurveData = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Currency"] == Currency]
    ForeignCurveData = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Currency"] != Currency]
    c1 = DomesticCurveData["DirectoryPrint"].iloc[0].split("\\")[-2]
    c2 = ForeignCurveData["DirectoryPrint"].iloc[0].split("\\")[-2]
    
    root = tk.Tk()
    root.title("ZeroMaker")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_DomesticEst_P1 = make_listvariable_interface(left_frame, 'Domestic Estimation Curve \n(-1: Fix - Flo Swap의 경우)', ["-1. Domestic Estimation 필요없음"] + list(DomesticCurveData["ListName"]), listheight = 4, textfont = 11, titlelable = True, titleName = "Domestic Leg INFO", defaultflag = True, defaultvalue = 0, pady = 10, width = 30)
    vb_LDHoliday = make_listvariable_interface(left_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 3, textfont = 11, pady = 2, defaultflag = True, defaultvalue = (1 if c1 == 'USD' else 0))
    vb_LD_DayCount = make_listvariable_interface(left_frame, 'Domestic DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag=True, defaultvalue=1 if c1 == "USD" else 0)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_Foreign_P1 = make_listvariable_interface(right_frame, 'Foreign Estimation Curve \n', list(ForeignCurveData["ListName"]) if ForeignCurveNeeded else ["-1. 미사용"], listheight = 4, textfont = 11, titlelable = True, titleName = "Foreign Leg INFO", defaultflag = True, defaultvalue = 1 if len(ForeignCurveData) >= 2 else 0, pady = 10)
    vb_LFHoliday = make_listvariable_interface(right_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"] if ForeignCurveNeeded else ["-1: 미사용"], listheight = 3, textfont = 11, pady = 2, defaultflag = True, defaultvalue = (1 if c2 == 'USD' else 0))
    vb_LF_DayCount = make_listvariable_interface(right_frame, 'Foreign DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"] if ForeignCurveNeeded else ["-1: 미사용"], listheight = 3, textfont = 11, defaultflag=True, defaultvalue=1 if c2 == "USD" else 0)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(Result_frame, 'PriceDate', bold = True, textfont = 11, defaultflag = True, defaultvalue=int(YYYYMMDD))
    v_Spot = make_variable_interface(Result_frame, 'Spot 환율\n(외화1단위당 국내통화)' if ForeignCurveNeeded else "미사용변수", bold = True, textfont = 11, defaultflag = True, defaultvalue=DefaultSpot)
    v_SwapPointUnit = make_variable_interface(Result_frame, 'SwapPointUnit' if ForeignCurveNeeded else "미사용변수", bold = True, textfont = 11, defaultflag = True, defaultvalue=100)
    vb_NumCpnOneYear_P1 = make_listvariable_interface(Result_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0 if c1 == "USD" else 2)
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, pady = 10)
    v_SaveName = make_variable_interface(Result_frame, '저장할 커브명\n(ex: KRW IRS ZeroCurve)', bold = True, textfont = 11, defaultflag = True, defaultvalue="")

    newtree = ttk.Treeview(root, height = 30)
    newtree.pack(side = 'left', padx=5, pady=10, expand=False, anchor = 'n')        
    NewTreeFlag = insert_dataframe_to_treeview(newtree, MyData, width = 75)       
    PrevTreeFlag, tree, scrollbar, scrollbar2, ResultDF = 0, None, None, None, pd.DataFrame([])
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, ResultDF]    
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]  
        ResultDF = MyArrays[4]
        
        N_DomesticEst_P1 = int(str(vb_DomesticEst_P1.get(vb_DomesticEst_P1.curselection())).split(".")[0]) if vb_DomesticEst_P1.curselection() else -1
        if N_DomesticEst_P1 >= 0 :
            DomesticEstCurveDirectory = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == N_DomesticEst_P1]["Directory"].iloc[0]
            DomesticEstCurve = ReadCSV(DomesticEstCurveDirectory, True).applymap(lambda x : str(x).replace("-","") if "-" in str(x) else x)
            DomesticEstTerm = DomesticEstCurve["Term"].astype(np.float64)
            DomesticEstRate = DomesticEstCurve["Rate"].astype(np.float64)
        else : 
            DomesticEstTerm, DomesticEstRate = [], []
        
        LD_Holiday_Curr = vb_LDHoliday.get(vb_LDHoliday.curselection()) if vb_LDHoliday.curselection() else "KRW"
        if LD_Holiday_Curr.upper() in HolidayDate.columns : 
            HolidayDomestic = list(HolidayDate[LD_Holiday_Curr.upper()].dropna().unique())  
        elif LD_Holiday_Curr.upper() == 'KRW' : 
            HolidayDomestic = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif LD_Holiday_Curr.upper() == 'USD' :
            HolidayDomestic = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else :
            HolidayDomestic = []

        N_DomesticEst_P1 = int(str(vb_DomesticEst_P1.get(vb_DomesticEst_P1.curselection())).split(".")[0]) if vb_DomesticEst_P1.curselection() else -1
        if N_DomesticEst_P1 >= 0 :
            DomesticEstCurveDirectory = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == N_DomesticEst_P1]["Directory"].iloc[0]
            DomesticEstCurve = ReadCSV(DomesticEstCurveDirectory, True).applymap(lambda x : str(x).replace("-","") if "-" in str(x) else x)
            DomesticEstTerm = DomesticEstCurve["Term"].astype(np.float64)
            DomesticEstRate = DomesticEstCurve["Rate"].astype(np.float64)
        else : 
            DomesticEstTerm, DomesticEstRate = [], []

        DayCountFlag = int(str(vb_LD_DayCount.get(vb_LD_DayCount.curselection())).split(":")[0]) if vb_LD_DayCount.curselection() else 0
        
        LF_Holiday_Curr = vb_LFHoliday.get(vb_LFHoliday.curselection()) if vb_LFHoliday.curselection() else "KRW"
        if LF_Holiday_Curr.upper() in HolidayDate.columns : 
            HolidayForeign = list(HolidayDate[LF_Holiday_Curr.upper()].dropna().unique())  
        elif LF_Holiday_Curr.upper() == 'KRW' : 
            HolidayForeign = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif LF_Holiday_Curr.upper() == 'USD' :
            HolidayForeign = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else :
            HolidayForeign = []
        HolidayPay = sorted(list(set(HolidayDomestic + HolidayForeign)))
        
        N_Foreign_P1 = int(str(vb_Foreign_P1.get(vb_Foreign_P1.curselection())).split(".")[0]) if vb_Foreign_P1.curselection() else 0
        if N_Foreign_P1 >= 0 and ForeignCurveNeeded == 1:
            ForeignCurveDirectory = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == N_Foreign_P1]["Directory"].iloc[0]
            ForeignCurve = ReadCSV(ForeignCurveDirectory, True).applymap(lambda x : str(x).replace("-","") if "-" in str(x) else x)
            ForeignTerm = ForeignCurve["Term"].astype(np.float64)
            ForeignRate = ForeignCurve["Rate"].astype(np.float64)
        else : 
            ForeignTerm, ForeignRate = [], []            

        if ForeignCurveNeeded == 0 : 
            ForeignTerm, ForeignRate = [], []

        DayCountFlagForeign = int(str(vb_LF_DayCount.get(vb_LF_DayCount.curselection())).split(":")[0]) if vb_LF_DayCount.curselection() else 0
            
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)            
        Spot = float(v_Spot.get()) if len(str(v_Spot.get())) > 0 else -1
        if Spot < 0 : 
            raise ValueError("Check Spot Price")            
        SwapPointUnit = float(v_SwapPointUnit.get()) if len(str(v_SwapPointUnit.get())) > 0 else 100
        NumCpnOneYear = int(vb_NumCpnOneYear_P1.get(vb_NumCpnOneYear_P1.curselection())) if vb_NumCpnOneYear_P1.curselection() else 4
        Preprocessing_ZeroTermAndRate(ForeignTerm, ForeignRate, PriceDate)
        ZeroTermForeign = ForeignTerm 
        ZeroRateForeign = ForeignRate
        ForeignEstCurveTerm = ForeignTerm
        ForeignEstCurveRate = ForeignRate
        DomesticEstCurveTerm = DomesticEstTerm
        DomesticEstCurveRate = DomesticEstRate
        Preprocessing_ZeroTermAndRate(DomesticEstCurveTerm, DomesticEstCurveRate, PriceDate)
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        SaveName = str(v_SaveName.get()) if len(str(v_SaveName.get())) > 0 else "TempCurve"          
        
        NBDList, ZeroTerm, ZeroRate, ScheduleStart, ScheduleEnd, SchedulePay, MktQuote = [], [], [], [], [], [], []
        if len(MyData[MyData["Type"].isin(['sp','Sp'])]) == 0 : 
            tstartdate = 0
            dffo = 1
        else : 
            try : 
                SwapStartDate = MyData[MyData["Type"].isin(["sw","Sw","Bs","bs"])]["StartDate"].iloc[0]
            except IndexError : 
                SwapStartDate = MyData[MyData["Type"].isin(["sp","Sp"])]["StartDate"].iloc[0]
                
            tstartdate = DayCountAtoB(int(PriceDate), SwapStartDate)/365
            rfo = Linterp(ZeroTermForeign, ZeroRateForeign, tstartdate)
            dffo = np.exp(-rfo * tstartdate)
        
        for i in range(len(MyData)) : 
            ResultEndDate = [0]
            ProductTypeString = str(MyData["Type"].iloc[i].replace(" ",""))
            ProductType = MapProductType(ProductTypeString, DomesticEstCurveRate, ZeroRateForeign)
            StartDate = int(MyData["StartDate"].iloc[i])
            SwapMat = int(MyData["Maturity"].iloc[i])
            DayAtoB = DayCountAtoB(StartDate, SwapMat)
            MarketQuote = float(MyData["MarketQuote"].iloc[i])
            ScheduleStart.append(StartDate)
            
            if ProductType == 0: 
                ScheduleEnd.append(SwapMat)
                SchedulePay.append(SwapMat)
                NBDList.append(0)
            elif ProductType == 1 or ProductType >= 3: 
                if DayAtoB < 7 : 
                    #1일 스왑
                    EndDate = ParseBusinessDateIfHoliday(DayPlus(StartDate, 1), HolidayPay)
                    NBD = NBusinessCountFromEndToPay(EndDate, SwapMat, HolidayPay, 1, ResultEndDate)
                elif DayAtoB < 14 : 
                    #7일 스왑
                    EndDate = ParseBusinessDateIfHoliday(DayPlus(StartDate, 7), HolidayPay)
                    NBD = NBusinessCountFromEndToPay(EndDate, SwapMat, HolidayPay, 1, ResultEndDate)
                elif DayAtoB < 21 : 
                    #14일 스왑
                    EndDate = ParseBusinessDateIfHoliday(DayPlus(StartDate, 14), HolidayPay)
                    NBD = NBusinessCountFromEndToPay(EndDate, SwapMat, HolidayPay, 1, ResultEndDate)
                elif DayAtoB < 28 : 
                    #21일 스왑
                    EndDate = ParseBusinessDateIfHoliday(DayPlus(StartDate, 21), HolidayPay)
                    NBD = NBusinessCountFromEndToPay(EndDate, SwapMat, HolidayPay, 1, ResultEndDate)
                else : 
                    NBD = NBusinessCountFromEndToPay(StartDate, SwapMat, HolidayPay, 1, ResultEndDate)
                    if ((i > 5) and (MyData["Type"].iloc[i] == MyData["Type"].iloc[i-1])) : 
                        NBD = NBDList[i-1]
                    EndDate = (ResultEndDate[0])//100 * 100 + (StartDate - (StartDate//100) * 100)
                    
                ScheduleEnd.append(EndDate)
                SchedulePay.append(SwapMat)
                NBDList.append(NBD)
            elif ProductType == 2 : 
                ScheduleEnd.append(SwapMat)
                SchedulePay.append(SwapMat)
                NBDList.append(0)
            
            if (ProductTypeString.lower() in ['dp','dg','deposit']) : 
                r = Calc_ZeroRate_FromDiscFactor(PriceDate, StartDate, SwapMat, MarketQuote/100, DayCountFlag, ZeroTerm, ZeroRate)
                ZeroTerm.append(DayCountAtoB(PriceDate, SwapMat)/365)
                ZeroRate.append(r)
                
            elif (ProductTypeString.lower().replace(" ","") in ['sp','swappoint']) : 
                T = DayCountAtoB(PriceDate, SwapMat)/365
                rf = Linterp(ZeroTermForeign, ZeroRateForeign, T)
                #print(rf, T, Spot, MarketQuote, SwapPointUnit)
                r = CalcZeroRateFromSwapPoint(rf, T, Spot, MarketQuote, SwapPointUnit)
                ZeroTerm.append(T)
                ZeroRate.append(r)
            elif (ProductTypeString.lower() in ['bs','sw','swap']) :
                T = DayCountAtoB(PriceDate, SwapMat)/365
                ZeroArray = np.r_[np.array(ZeroRate), 0.0]
                MaxRate = max(0.3, np.array(ZeroRate).mean() * 4)
                MinRate = min(-0.04, np.array(ZeroRate).min() - 0.03)
                TargetRate = MaxRate
                FloatFloatFlag = True if (len(DomesticEstCurveTerm) > 0 and len(ForeignEstCurveTerm) > 0) else False
                DF_to_StartDate = np.exp(-Linterp(ZeroTerm, ZeroRate, tstartdate) * tstartdate)
                ZeroTerm.append(T)
                for j in range(500) : 
                    ZeroArray[-1] = TargetRate
                    if len(ZeroTermForeign) > 0 : 
                        if FloatFloatFlag == False : 
                            Err = Calc_CRS(100, 100, 0.0, ScheduleStart[i], PriceDate, ScheduleEnd[i], MarketQuote/100, ZeroTerm, ZeroArray, NumCpnOneYear, DayCountFlag, DayCountFlagForeign, False, NBDList[i], DomesticEstCurveTerm, DomesticEstCurveRate, ForeignEstCurveTerm, ForeignEstCurveRate, ZeroTermForeign, ZeroRateForeign, HolidayDomestic, HolidayForeign, HolidayPay )
                        else : 
                            Err = Calc_CRS(100, 100 * dffo/DF_to_StartDate, 0.0, ScheduleStart[i], PriceDate, ScheduleEnd[i], MarketQuote/100, ZeroTerm, ZeroArray, NumCpnOneYear, DayCountFlag, DayCountFlagForeign, False, NBDList[i], [], [], [], [], ZeroTermForeign, ZeroRateForeign, HolidayDomestic, HolidayForeign, HolidayPay )
                    else : 
                        Err = Calc_IRS(100, 0.0, ScheduleStart[i], PriceDate, ScheduleEnd[i], MarketQuote/100, ZeroTerm, ZeroArray, NumCpnOneYear, DayCountFlag, True if Currency == "KRW" else False, NBDList[i], [], [], HolidayDomestic, HolidayDomestic )
                    
                    if abs(Err) < 0.000001 : 
                        break
                    elif Err < 0 : 
                        MaxRate = TargetRate
                        TargetRate = (MaxRate + MinRate)/2
                    else : 
                        MinRate = TargetRate
                        TargetRate = (MaxRate + MinRate)/2
                if j == 499 : 
                    raise ValueError("Error")
                ZeroRate.append(TargetRate)
            else : 
                raise ValueError("Check the Product Type")
        for i in range(len(ZeroRate)) : 
            ZeroRate[i] *= 100
            
        ResultDF = pd.DataFrame(ZeroRate, ZeroTerm).reset_index()
        ResultDF.columns = ["Term","Rate"]
        ResultDF["PriceDate"] = [PriceDate] * len(ResultDF)  # pylint: disable=unsupported-assignment-operation
        ResultDF["NBD"] = NBDList                            # pylint: disable=unsupported-assignment-operation
        ResultDF["StartDate"] = ScheduleStart                # pylint: disable=unsupported-assignment-operation
        ResultDF["EndDate"] = ScheduleEnd                    # pylint: disable=unsupported-assignment-operation
        ResultDF["PayDate"] = SchedulePay                    # pylint: disable=unsupported-assignment-operation
        CurrencyName = Currency if ForeignCurveNeeded == 0 else str(Currency).replace(" ","").split(",")[0]
        SavePrint = ""
        if LoggingFlag > 0 : 
            if YYYYMMDD not in os.listdir(currdir + "\\MarketData\\outputdata") : 
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD))
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD) + "\\" + CurrencyName)    
                    
            cvname = SaveName
            targetdir = currdir + "\\MarketData\\outputdata\\" + str(YYYYMMDD) + "\\" + str(CurrencyName)
            try : 
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultDF.to_csv(TheName, index = False, encoding = "cp949")
                    SavePrint = ("\n" + TheName + "저장 완료\n")
            except FileNotFoundError : 
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD) + "\\" + CurrencyName)    
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultDF.to_csv(TheName, index = False, encoding = "cp949")
                    SavePrint = ("\n" + TheName + "저장 완료\n")        
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)

        ResultDF = ResultDF.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, ResultDF, width = 100)          
        output_label.config(text = f"저장: \n{SavePrint}", font = ("맑은 고딕", 12, 'bold'))

        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2 
        MyArrays[4] = ResultDF 
               
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
                
    root.mainloop()
    return MyArrays[4]

def PriceToSwaptionVolProgram(YYYYMMDD, Name, Data, currdir, HolidayFile) : 
    MyData = Data[0].set_index("스왑만기/옵션만기" if "스왑만기/옵션만기" in Data[0].columns else "SwapMat/OptMat")
    ZeroCurveName = Name[0]    
    Currency = ZeroCurveName.split("\\")[-2]
    Holidays = list(HolidayFile[Currency].dropna().unique())
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namenotin = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == YYYYMMDD]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))

    root = tk.Tk()
    root.title("ZeroMaker")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_SelectedCurve_P1 = make_listvariable_interface(left_frame, 'ZeroCurve', list(GroupbyYYYYMMDD["ListName"]), listheight = 5, textfont = 11, titlelable = True, titleName = "ZeroCurve INFO", defaultflag = True, defaultvalue = 0, pady = 10, DefaultStringList=["IRS"])
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, defaultflag = True, defaultvalue=int(YYYYMMDD))
    vb_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0 if Currency == "USD" else 2)
    vb_DayCount = make_listvariable_interface(left_frame, 'DayCountFlag', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 4, textfont = 11, defaultflag=True, defaultvalue=1 if Currency == "USD" else 0)
    vb_VolFlag = make_listvariable_interface(left_frame, 'VolFlag', ["0: Black Vol","1: Normal Vol"], listheight = 2, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 1)
    vb_Logging = make_listvariable_interface(left_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, pady = 10)
    v_SaveName = make_variable_interface(left_frame, '저장할 커브볼 명\n(ex: KRW IRS Swaption Vol)', bold = True, textfont = 11, defaultflag = True, defaultvalue="")
        
    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')

    newtree = ttk.Treeview(root, height = 30)
    newtree.pack(side = 'left', padx=5, pady=10, expand=False, anchor = 'n')        
    NewTreeFlag = insert_dataframe_to_treeview(newtree, (MyData*100).round(2).reset_index(), width = 50)       
    PrevTreeFlag, tree, tree2, scrollbar, scrollbar2, ResultDF = 0, None, None, None, None, pd.DataFrame([])
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, ResultDF, tree2]    
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]  
        ResultDF = MyArrays[4]
        tree2 = MyArrays[5]
        
        N_Curve_P1 = int(str(vb_SelectedCurve_P1.get(vb_SelectedCurve_P1.curselection())).split(".")[0]) if vb_SelectedCurve_P1.curselection() else 0
        CurveDirectory = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == N_Curve_P1]["Directory"].iloc[0]
        MyData2 = ReadCSV(CurveDirectory, True).applymap(lambda x : str(x).replace("-","") if "-" in str(x) else x)
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)  
        if PriceDate < 19000101 : 
            PriceDate = ExcelDateToYYYYMMDD(PriceDate)          
        elif PriceDate < 1 : 
            raise ValueError("Check PriceDate")
        NCPN_Ann = int(vb_NumCpnOneYear_P1.get(vb_NumCpnOneYear_P1.curselection())) if vb_NumCpnOneYear_P1.curselection() else 4
        DayCountFlag = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else 0
        VolFlag = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 0
        Term = MyData2["Term"].astype(np.float64).values
        Rate = MyData2["Rate"].astype(np.float64).values
        Preprocessing_ZeroTermAndRate(Term, Rate, PriceDate)
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        SaveName = str(v_SaveName.get()) if len(str(v_SaveName.get())) > 0 else "TempSwaptionVolCurve"
        ResultValues = np.zeros(shape = MyData.shape)
        ResultValues2 = np.zeros(shape = MyData.shape)
        CurrencyName = Currency
        for i in range((MyData.shape[0])) : 
            for j in range((MyData.shape[1])) : 
                TargetPrice = MyData.values[i][j]
                StartDate = EDate_YYYYMMDD(PriceDate, int(MyData.columns[j])) 
                EndDate = EDate_YYYYMMDD(StartDate, int(MyData.index[i])) 
                v = FindSwaptionImpliedVolatility(PriceDate, StartDate, EndDate, NCPN_Ann, Term, Rate, TargetPrice, DayCountFlag, VolFlag, Nominal = 1, HolidayFlag = 'kr' if 'KRW' == CurrencyName else '', SelfHolidays= Holidays, FixedPayer0Receiver1=0)
                ResultValues[i][j] = v["ImpliedVol"]
                ResultValues2[i][j] = v["ForwardSwapRate"]
        SaveYN, SaveDir = 0, ""
        ResultDF = pd.DataFrame(ResultValues, index = MyData.index, columns = MyData.columns)
        ResultDF2 = pd.DataFrame(ResultValues2, index = MyData.index, columns = MyData.columns)
        if LoggingFlag > 0 : 
            if YYYYMMDD not in os.listdir(currdir + "\\MarketData\\outputdata") : 
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD))
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD) + "\\" + CurrencyName)    
                    
            cvname = SaveName
            targetdir = currdir + "\\MarketData\\outputdata\\" + str(YYYYMMDD) + "\\" + str(CurrencyName)
            print("\n저장시도\n")
            try : 
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultDF.to_csv(TheName, index = True, encoding = "cp949")
                    SaveYN = 1
                    SaveDir = TheName
                    print("\n저장완료\n")
            except FileNotFoundError : 
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD) + "\\" + CurrencyName)    
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultDF.to_csv(TheName, index = True, encoding = "cp949")
                    SaveYN = 1
                    SaveDir = TheName
                    print("\n저장완료\n")
        
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
            tree2 = ttk.Treeview(root)
        else : 
            tree.destroy()
            tree2.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
            tree2 = ttk.Treeview(root)

        ResultDF = ResultDF.applymap(lambda x : np.round(x, 6) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=False)
        tree2.pack(padx=5, pady=5, fill="both", expand=False)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, (ResultDF*100).round(4).reset_index(), width = 50)
        PrevTreeFlag2 = insert_dataframe_to_treeview(tree2, (ResultDF2*100).round(4).reset_index(), width = 50)          
        output_label.config(text = f"저장: \n{SaveYN}\n저장위치:\n{SaveDir}", font = ("맑은 고딕", 12, 'bold'))

        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2 
        MyArrays[4] = ResultDF 
        MyArrays[5] = tree2
               
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 10, pady = 10, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 10).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2) 
    root.mainloop()    
    return 1    
    
def Calc_dSdx(t, PriceDate, SwapStart, ResultForwardEnd, ZeroTerm, ZeroRate, DayCountFlag, kappa) : 
    T0 = DayCountAtoB(PriceDate, SwapStart)/365
    T_i = np.vectorize(DayCountAtoB)([PriceDate], ResultForwardEnd)/365
    T = np.r_[[T0],T_i]
    FwdDscFunc = np.vectorize(lambda Time : Calc_ForwardDiscount_Factor(ZeroTerm, ZeroRate, t, Time))
    DF = FwdDscFunc(T)
    DateList = np.r_[[SwapStart],ResultForwardEnd]
    Deltat = np.vectorize(DayCountFractionAtoB)(DateList[:-1],DateList[1:], [DayCountFlag])
    Annuity = DF[1:] * Deltat
    ForwardSwapRate = (DF[0] - DF[-1])/(Annuity.sum())
    BtT = np.vectorize(lambda t1, t2: B_s_to_t(t1, t2, kappa))([t],T)
    dSdx = -1/(Annuity.sum()) * (DF[0] * BtT[0] - DF[-1] * BtT[-1]) + ForwardSwapRate / (Annuity.sum()) * (Annuity * BtT[1:]).sum()
    return dSdx

def Calc_SwaptionNormalVolatilityAnalytic(kappa, swaptionvol, PriceDate, SwapStart, SwapMat, ZeroTerm, ZeroRate, NumCpnOneYear = 4, DayCountFlag = 0, Holidays = []) : 
    ResultForwardStart, ResultForwardEnd, ResultPayDate, ResultNBD = MappingCouponDates(1,SwapStart,SwapMat,0,NumCpnOneYear,1,Holidays,Holidays,1)
    f = np.vectorize(lambda t : Calc_dSdx(t, PriceDate, SwapStart, ResultForwardEnd, ZeroTerm, ZeroRate, DayCountFlag, kappa))
    tstart = DayCountAtoB(PriceDate, SwapStart)/365
    tarray = np.linspace(0, tstart, 5)
    dtarray = tarray[1:] - tarray[:-1]
    dSdXArray = f(tarray[1:]) 
    normalv = np.sqrt(1/tstart * (dSdXArray * dSdXArray * swaptionvol * swaptionvol * dtarray).sum())
    return normalv

def ErrorVolatilityRatio(kappa, PriceDate, SwapStartArray, SwapMaturity1Array, SwapMaturity2Array, SwaptionVol1Array, SwaptionVol2Array, ZeroTerm, ZeroRate, NumCpnOneYear, DayCountFlag, KoreanHolidayFlag = True, AddHolidays = []) : 
    if KoreanHolidayFlag == True : 
        Holidays = KoreaHolidaysFromStartToEnd(SwapStartArray[0]//10000, SwapMaturity2Array[-1]//10000)
    else : 
        Holidays = AddHolidays
    f = np.vectorize(lambda k, Start, Mat, v: Calc_SwaptionNormalVolatilityAnalytic(k, v, PriceDate, Start, Mat, ZeroTerm, ZeroRate, NumCpnOneYear, DayCountFlag, Holidays))
    v1model = f([kappa], SwapStartArray, SwapMaturity1Array, SwaptionVol1Array)
    v2model = f([kappa], SwapStartArray, SwapMaturity2Array, SwaptionVol2Array)
    VRatioModel = v2model/v1model
    vRatioMarket = np.array(SwaptionVol2Array)/np.array(SwaptionVol1Array)
    ErrSquare = ((VRatioModel - vRatioMarket)**2).sum()
    return np.maximum(0.00001,np.minimum(1000000000,ErrSquare))

def CalibrationKappaFromSwapRatio(PriceDate, SwapStartArray, SwapMaturity1Array, SwapMaturity2Array, SwaptionVol1Array, SwaptionVol2Array, ZeroTerm, ZeroRate, NumCpnOneYear, DayCountFlag, KoreanHolidayFlag = False, AddHolidays = [], KAPPAMIN = -0.05, KAPPAMAX = 0.15) : 
    if KoreanHolidayFlag == True : 
        Holidays = KoreaHolidaysFromStartToEnd(SwapStartArray[0]//10000, SwapMaturity2Array[-1]//10000)
    else : 
        Holidays = AddHolidays
    kappamin = min(KAPPAMIN, KAPPAMAX)    
    kappamax = max(KAPPAMIN, KAPPAMAX)
    kappas = np.linspace(kappamin, kappamax, 41)
    kappas = kappas[kappas != 0]
    f = np.vectorize(lambda k : ErrorVolatilityRatio(k, PriceDate, SwapStartArray, SwapMaturity1Array, SwapMaturity2Array, SwaptionVol1Array, SwaptionVol2Array, ZeroTerm, ZeroRate, NumCpnOneYear, DayCountFlag, KoreanHolidayFlag = False, AddHolidays = Holidays))
    errs = f(kappas)
    kappamin = kappas[errs.argmin()] - 0.02
    kappamax = kappas[errs.argmin()] + 0.02
    kappas = np.linspace(kappamin, kappamax, 21)
    kappas = kappas[kappas != 0]
    errs = f(kappas)
    calibratedkappa = kappas[errs.argmin()]
    f = np.vectorize(lambda k, Start, Mat, v: Calc_SwaptionNormalVolatilityAnalytic(k, v, PriceDate, Start, Mat, ZeroTerm, ZeroRate, NumCpnOneYear, DayCountFlag, Holidays))
    v1model = f([calibratedkappa], SwapStartArray, SwapMaturity1Array, SwaptionVol1Array)
    v2model = f([calibratedkappa], SwapStartArray, SwapMaturity2Array, SwaptionVol2Array)
    VRatioModel = v2model/v1model
    vRatioMarket = np.array(SwaptionVol2Array)/np.array(SwaptionVol1Array)
    ErrSquare = ((VRatioModel - vRatioMarket)**2).sum()    
    Err = VRatioModel - vRatioMarket
    return {'kappa':calibratedkappa, 'v1market':SwaptionVol1Array,'v2market':SwaptionVol2Array,'v1model':v1model, 'v2model':v2model, 'VRatioModel':VRatioModel,'vRatioMarket':vRatioMarket, 'ErrSquare':ErrSquare, 'Err': Err}

def KappaCalibration(HolidayDate, currdir = os.getcwd()) : 
    YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\outputdata",MultiSelection=False, namenotin = "Vol", Comments="Pricing을 위한 ZeroCurve", DefaultStringList= ["IRS"])
    ZeroCurve = Data[0]
    ZeroTerm = ZeroCurve["Term"].astype(np.float64)
    ZeroRate = ZeroCurve["Rate"].astype(np.float64)
    ZeroCurveName = Name[0].split("\\")[-1].replace(".csv","")  
    Currency = Name[0].split("\\")[-2]
    Holidays = list(HolidayDate[Currency].dropna().unique()) if Currency in HolidayDate.columns else []
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namein = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    Data = Data[Data['DirectoryPrint'].apply(lambda x : ('EQ' in str(x).upper() and 'VOL' in str(x).upper()) == False)] #Out EQ Vol 
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == YYYYMMDD]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))            

    root = tk.Tk()
    root.title("Kappa Calibration")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(left_frame, 'ZeroCurve(자동Load)', termratestr(ZeroTerm, ZeroRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)
    vb_SelectedCurve_P1 = make_listvariable_interface(left_frame, 'Swaption Vol 선택', list(GroupbyYYYYMMDD["ListName"]), listheight = 5, textfont = 11, titlelable = True, titleName = "Swaption Info", defaultflag = True, defaultvalue = 0, width = 40, DefaultStringList=["Vol"])
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    vb_DayCount = make_listvariable_interface(left_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    Result = {'CalibrationTrue':False}
    PrevTreeFlag, tree, scrollbar, scrollbar2, tree2, tree3 = 0, None, None, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, Result, tree2, tree3]
    def run_function(MyArrays) :     

        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]  
        CalcResult = MyArrays[4] 
        tree2 = MyArrays[5]     
        tree3 = MyArrays[6]
        PriceDate = int(YYYYMMDD)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        DayCount = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)
        SelectedNumber = int(str(vb_SelectedCurve_P1.get(vb_SelectedCurve_P1.curselection())).split(".")[0]) if vb_SelectedCurve_P1.curselection() else 1
        VolRawData = ReadCSV(GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == SelectedNumber]['Directory'].iloc[0])
        voldf = VolRawData.set_index(VolRawData.columns[0])
        SwapStartList = []
        SwapMaturity1List = []
        SwapMaturity2List = []
        v1List = []
        v2List = []
        i = 0
        j1 = 0
        j2 = -1
        for i in range(len(voldf.columns)) : 
            SwapStartDate = EDate_YYYYMMDD(PriceDate, int(voldf.columns[i]))
            SwapMaturityDate1 = EDate_YYYYMMDD(SwapStartDate, int(voldf.index[j1]))
            SwapMaturityDate2 = EDate_YYYYMMDD(SwapStartDate, int(voldf.index[j2]))
            v1 = voldf[voldf.columns[i]].iloc[j1]
            v2 = voldf[voldf.columns[i]].iloc[j2]
            SwapStartList.append(SwapStartDate)
            SwapMaturity1List.append(SwapMaturityDate1)
            SwapMaturity2List.append(SwapMaturityDate2)
            v1List.append(v1)
            v2List.append(v2)    
        Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)
        CalibResult = CalibrationKappaFromSwapRatio(PriceDate, SwapStartList, SwapMaturity1List, SwapMaturity2List, v1List, v2List, ZeroTerm, ZeroRate, L1_NumCpnOneYear_P1, DayCount, KoreanHolidayFlag = False, AddHolidays = Holidays)
        CalcResult['CalibrationTrue'] = True
        CalcResult['kappa'] = CalibResult['kappa']
        CalcResult['v1market'] = CalibResult['v1market']
        CalcResult['v2market'] = CalibResult['v2market']    
        CalcResult['v1model'] = CalibResult['v1model']
        CalcResult['v2model'] = CalibResult['v2model']
        CalcResult['VRatioModel'] = CalibResult['VRatioModel']
        CalcResult['vRatioMarket'] = CalibResult['vRatioMarket']
        CalcResult['ErrSquare'] = CalibResult['ErrSquare']
        CalcResult['Err'] = CalibResult['Err']
        
        v1mar = pd.Series(CalibResult["v1market"], name = "v1market") * 100
        v2mar = pd.Series(CalibResult["v2market"], name = "v2market") * 100
        v1mod = pd.Series(CalibResult["v1model"], name = "v1model") * 100
        v2mod = pd.Series(CalibResult["v2model"], name = "v2model") * 100
        VRatioModel = pd.Series(CalibResult["VRatioModel"], name = "VRatioModel")
        vRatioMarket = pd.Series(CalibResult["vRatioMarket"], name = "vRatioMarket")
        resultdf = pd.concat([v1mar, v2mar, v1mod, v2mod, VRatioModel, vRatioMarket],axis = 1)
        resultdf['kappa'] = CalibResult['kappa']
        resultdf['ErrSquareSum'] = CalibResult['ErrSquare']
        resultdf['Err'] = CalibResult['Err']
        
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        tree.pack(padx=5, pady=5, fill="both", expand=False)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, resultdf.round(6), width = 80)

        output_label.config(text = f"\n결과: \nkappa ={np.round(float(resultdf['kappa'].iloc[0]),6)}", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop()      
    return 0, 0, 0, 0    
    
def PreprocessingFXSpotData(DataDirectory) :     
    try : 
        FXSpot = ReadCSV(DataDirectory).dropna(how = 'all').fillna(method = 'ffill').applymap(lambda x : str(x).replace(",","").replace("-","")).astype(np.float64)
        FXSpot["Date"] = FXSpot["Date"].astype(np.int64)
        FXSpot = FXSpot.set_index("Date")
        if FXSpot.index[0] < 19000101 : 
            MyList = []
            for i in range(len(FXSpot.index)) : 
                MyList.append(ExcelDateToYYYYMMDD(FXSpot.index[i]))
            FXSpot.index = MyList
    except FileNotFoundError : 
        FXSpot = pd.DataFrame([])
    return FXSpot    

def AddFRTB_BookedPosition(currdir, RAWData, RAWFORMAT) : 
    ResultAddData = pd.DataFrame([])
    try : 
        Bond = ReadCSV(currdir + '\\Book\\Bond\\Bond.csv')
        Bond["ProductType"] = "Bond"
        IRS = ReadCSV(currdir + '\\Book\\IRS\\IRS.csv')
        IRS["ProductType"] = "IRS"
        concatdata = pd.concat([Bond, IRS],axis = 0)
        concatdata.index = np.arange(len(concatdata))
        FXSpot = PreprocessingFXSpotData(currdir + "\\MarketData\\spot\\FXSpot.csv")                
        if RAWFORMAT == 1 : 
            PriceDate = RAWData["기준일자"].iloc[0]
            if len(Bond) + len(IRS) > 0 : 
                #AddBookedPosition = input("\nBooking된 " + str(len(Bond) + len(IRS)) + "건의 포지션을 FRTB SA 계산에 추가하겠습니까?(Y/N)\n->").lower()
                AddBookedPosition = MainViewer(Title = 'Continue', MyText = currdir + "\\Book\n에 Booking된 " + str(len(Bond) + len(IRS)) + "건의 포지션을 FRTB SA 계산에 추가하겠습니까?", MyList = ["0: 추가안함", "1: 추가함"], size = "1800x450+30+30", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name", addtreeflag=True, treedata = concatdata)
                if AddBookedPosition == 1 :
                    Depart = MainViewer2(Title = "Department Name",MyText = "부점명을 입력하시오",size = "800x450+30+30", textfont = 14, defaultvalue = "TempDepart")#input("\n 부점명을 입력하시오. (ex : 자금운용실)\n-> ")
                    for i in range(len(Bond)) : 
                        cvname = Bond["DiscCurveName"].iloc[i].replace(".csv","")
                        girrcol = [s for s in Bond.columns if "girr_" in s.lower()]
                        girrtenor = [float(s.replace("GIRR_","")) for s in girrcol]
                        csrcol = [s for s in Bond.columns if "csr_" in s.lower()]
                        csrtenor = [float(s.replace("CSR_","")) for s in csrcol]
                        if "ZeroCurve" in cvname : 
                            cvname = cvname.replace("ZeroCurve","")
                        elif "Zero" in cvname : 
                            cvname = cvname.replace("Zero","")
                        
                        if "IRS" in cvname : 
                            cvname = cvname.replace("IRS",":Std")
                        elif "CRS" in cvname : 
                            cvname = cvname.replace("CRS","FX")
                        
                        TempData = pd.DataFrame(Bond[girrcol].iloc[i].values, columns = ["델타민감도"])
                        fxrate = CalcFXRateToKRW(FXSpot, Bond["Currency"].iloc[i], PriceDate)
                        TempData["델타민감도"] = TempData["델타민감도"].astype(np.float64) * fxrate
                        TempData["기준일자"] = PriceDate
                        TempData["계정구분코드"] = 10
                        TempData["계정명"] = "은행"
                        TempData["부점코드"] = 12345
                        TempData["부점명"] = Depart
                        TempData["팀코드"] = 12345
                        TempData["팀명"] = "TempTeam"
                        TempData["데스크코드"] = 12345
                        TempData["데스크명"] = "TempDesk"
                        TempData["포트폴리오"] = "TempPort"
                        TempData["리스크군"] = "일반금리(GIRR)"
                        TempData["민감도유형"] = "델타"
                        TempData["포지션 ID"] = 12345
                        TempData["뮤렉스 ID"] = 12345
                        TempData["버킷"] = Bond["Currency"].iloc[i]
                        
                        TempData["리스크요소1"] = cvname
                        TempData["리스크요소2"] = girrtenor
                        TempData["리스크요소3"] = "RATE"
                        TempData["베가민감도"] = 0
                        TempData["상향커버쳐"] = 0
                        TempData["하향커버쳐"] = 0

                        TempData2 = pd.DataFrame(Bond[csrcol].iloc[i].values, columns = ["델타민감도"])
                        TempData2["델타민감도"] = TempData2["델타민감도"].astype(np.float64) * fxrate
                        
                        TempData2["기준일자"] = PriceDate
                        TempData2["계정구분코드"] = 10
                        TempData2["계정명"] = "은행"
                        TempData2["부점코드"] = 12345
                        TempData2["부점명"] = Depart
                        TempData2["팀코드"] = 12345
                        TempData2["팀명"] = "TempTeam"
                        TempData2["데스크코드"] = 12345
                        TempData2["데스크명"] = "TempDesk"
                        TempData2["포트폴리오"] = "TempPort"
                        TempData2["리스크군"] = "신용스프레드(CSR)"
                        TempData2["민감도유형"] = "델타"
                        TempData2["포지션 ID"] = 12345
                        TempData2["뮤렉스 ID"] = 12345
                        TempData2["버킷"] = "[" + ('0' + str(Bond["Bucket"].iloc[i]))[-2:] + "]"
                        TempData2["리스크요소1"] = "TempIssuer" + str(Bond["Bucket"].iloc[i])
                        TempData2["리스크요소2"] = cvname
                        TempData2["리스크요소3"] = csrtenor
                        TempData2["베가민감도"] = 0
                        TempData2["상향커버쳐"] = 0
                        TempData2["하향커버쳐"] = 0                        
                        ResultAddData = pd.concat([ResultAddData, TempData, TempData2],axis = 0)

                    for i in range(len(IRS)) : 
                        cvname = IRS["DiscCurveNameLeg1"].iloc[i].replace(".csv","")
                        girrcol = [s for s in IRS.columns if "girr_" in s.lower()]
                        girrtenor = [float(s.replace("GIRR_","")) for s in girrcol]
                        if "ZeroCurve" in cvname : 
                            cvname = cvname.replace("ZeroCurve","")
                        elif "Zero" in cvname : 
                            cvname = cvname.replace("Zero","")
                        
                        if "IRS" in cvname : 
                            cvname = cvname.replace("IRS",":Std")
                        elif "CRS" in cvname : 
                            cvname = cvname.replace("CRS","FX")
                        
                        TempData = pd.DataFrame(IRS[girrcol].iloc[i].values, columns = ["델타민감도"])
                        fxrate = CalcFXRateToKRW(FXSpot, IRS["Currency"].iloc[i], PriceDate)
                        TempData["델타민감도"] = TempData["델타민감도"].astype(np.float64) * fxrate
                                                
                        TempData["기준일자"] = PriceDate
                        TempData["계정구분코드"] = 10
                        TempData["계정명"] = "은행"
                        TempData["부점코드"] = 12345
                        TempData["부점명"] = Depart
                        TempData["팀코드"] = 12345
                        TempData["팀명"] = "TempTeam"
                        TempData["데스크코드"] = 12345
                        TempData["데스크명"] = "TempDesk"
                        TempData["포트폴리오"] = "TempPort"
                        TempData["리스크군"] = "일반금리(GIRR)"
                        TempData["민감도유형"] = "델타"
                        TempData["포지션 ID"] = 12345
                        TempData["뮤렉스 ID"] = 12345
                        TempData["버킷"] = IRS["Currency"].iloc[i]
                        TempData["리스크요소1"] = cvname
                        TempData["리스크요소2"] = girrtenor
                        TempData["리스크요소3"] = "RATE"
                        TempData["베가민감도"] = 0
                        TempData["상향커버쳐"] = 0
                        TempData["하향커버쳐"] = 0                   
                        ResultAddData = pd.concat([ResultAddData, TempData],axis = 0)
        else : 
            if len(Bond) + len(IRS) > 0 : 
                #AddBookedPosition = input("\nBooking된 " + str(len(Bond) + len(IRS)) + "건의 포지션을 FRTB SA 계산에 추가하겠습니까?(Y/N)\n->").lower()
                AddBookedPosition = MainViewer(Title = 'Continue', MyText = currdir + "\\Book\n에 Booking된 " + str(len(Bond) + len(IRS)) + "건의 포지션을 FRTB SA 계산에 추가하겠습니까?", MyList = ["0: 추가안함", "1: 추가함"], size = "1800x450+30+30", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name", addtreeflag=True, treedata = concatdata)
                if AddBookedPosition == 1 :
                    Depart = MainViewer2(Title = "Department Name",MyText = "부점명을 입력하시오",size = "800x450+30+30", textfont = 14, defaultvalue = "TempDepart")#input("\n 부점명을 입력하시오. (ex : 자금운용실)\n-> ")
                    for i in range(len(Bond)) : 
                        cvname = Bond["DiscCurveName"].iloc[i].replace(".csv","")
                        girrcol = [s for s in Bond.columns if "girr_" in s.lower()]
                        girrtenor = [float(s.replace("GIRR_","")) for s in girrcol]
                        csrcol = [s for s in Bond.columns if "csr_" in s.lower()]
                        csrtenor = [float(s.replace("CSR_","")) for s in csrcol]
                        TempData = pd.DataFrame(Bond[girrcol].iloc[i].values, columns = ["Delta_Sensi"])
                        fxrate = CalcFXRateToKRW(FXSpot, Bond["Currency"].iloc[i], Bond["PriceDate"].iloc[i])
                        TempData["Delta_Sensi"] = TempData["Delta_Sensi"].astype(np.float64) * fxrate
                        TempData["Depart"] = Depart
                        TempData["Risk_Class"] = "GIRR"
                        TempData["Risk_Type"] = "Delta"
                        TempData["Portfolio"] = "TempPort"
                        TempData["Bucket"] = Bond["Currency"].iloc[i]
                        TempData["RiskFactor1"] = cvname
                        TempData["RiskFactor2"] = girrtenor
                        TempData["RiskFactor3"] = "Rate"
                        TempData["Vega_Sensi"] = 0
                        TempData["CVR_Plus"] = 0
                        TempData["CVR_Minus"] = 0                        

                        TempData2 = pd.DataFrame(Bond[csrcol].iloc[i].values, columns = ["Delta_Sensi"])
                        TempData2["Delta_Sensi"] = TempData2["Delta_Sensi"].astype(np.float64) * fxrate

                        TempData2["Depart"] = Depart
                        TempData2["Risk_Class"] = "CSR"
                        TempData2["Risk_Type"] = "Delta"
                        TempData2["Portfolio"] = "TempPort"
                        TempData2["Bucket"] = str(Bond["Bucket"].iloc[i])
                        TempData2["RiskFactor1"] = cvname
                        TempData2["RiskFactor2"] = csrtenor
                        TempData2["RiskFactor3"] = "TempIssuer" + str(Bond["Bucket"].iloc[i])
                        TempData2["Vega_Sensi"] = 0
                        TempData2["CVR_Plus"] = 0
                        TempData2["CVR_Minus"] = 0   
                        ResultAddData = pd.concat([ResultAddData, TempData, TempData2],axis = 0)
                                             
                    for i in range(len(IRS)) : 
                        cvname = IRS["DiscCurveNameLeg1"].iloc[i].replace(".csv","")
                        girrcol = [s for s in IRS.columns if "girr_" in s.lower()]
                        girrtenor = [float(s.replace("GIRR_","")) for s in girrcol]
                        TempData = pd.DataFrame(IRS[girrcol].iloc[i].values, columns = ["Delta_Sensi"])
                        fxrate = CalcFXRateToKRW(FXSpot, IRS["Currency"].iloc[i], IRS["PriceDate"].iloc[i])
                        TempData["Delta_Sensi"] = TempData["Delta_Sensi"].astype(np.float64) * fxrate
                        
                        TempData["Depart"] = Depart
                        TempData["Risk_Class"] = "GIRR"
                        TempData["Risk_Type"] = "Delta"
                        TempData["Portfolio"] = "TempPort"
                        TempData["Bucket"] = IRS["Currency"].iloc[i]
                        TempData["RiskFactor1"] = cvname
                        TempData["RiskFactor2"] = girrtenor
                        TempData["RiskFactor3"] = "Rate"
                        TempData["Vega_Sensi"] = 0
                        TempData["CVR_Plus"] = 0
                        TempData["CVR_Minus"] = 0                        
                        ResultAddData = pd.concat([ResultAddData, TempData],axis = 0)
            
    except FileNotFoundError : 
        None
    return ResultAddData

while True : 
    MainFlag = MainViewer(size = "800x450+50+50")#input("사용하실 기능은?(번호입력) \n 1: Pricing 및 CSR, GIRR 간이 시뮬레이션 \n 2: FRTB SA Risk Calculation \n 3: CurveGenerator \n 4: IR Swaption ImpliedVol Calculation \n-> ")
    if len(str(MainFlag)) == 0 : 
        print("\n###########################\n### 프로그램을 종료합니다.###\n###########################")
        break
    elif MainFlag not in [1,2,3,4,5,6,'1','2','3','4','5','6'] : 
        print("\n###########################\n### 프로그램을 종료합니다.###\n###########################")
        break
    elif MainFlag in [2,'2'] :         
        #RAWFORMAT = 0#int(input("자체데이터 RAWData 엑셀 포멧이면 0을 KDB RAW Data 포멧의 경우 1을 입력하시오\n-> "))
        RAWFORMAT = MainViewer(Title = 'Continue', MyText = 'RawData 포멧을 선택하시오', MyList = ["0: My Raw Data", "1: KDB Raw Data"], defaultvalue=0, size = "800x450+30+30", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
        RAWData = MainFunction(currdir)
        AddedData = AddFRTB_BookedPosition(currdir, RAWData, RAWFORMAT)
        if len(AddedData) > 0 : 
            RAWData = pd.concat([RAWData, AddedData],axis = 0)
        if RAWFORMAT == 0 : 
            CSR,CSR_SecuritizedNonCTP,CSR_CTP,GIRR, FXR, EQR, COMR, DRC, RRAO = PreProcessingMyData(RAWData)
        else : 
            CSR,CSR_SecuritizedNonCTP,CSR_CTP,GIRR, FXR, EQR, COMR = PreProcessingKDBData(RAWData, dataformat = 'splited') 
            DRC = pd.DataFrame([])
            RRAO = pd.DataFrame([])
        print("\n####################\n######산출중########\n####################\n")
        ResultData1 = AggregatedFRTB_RiskCharge(CSR, GIRR, FXR, EQR, COMR, CSR_SecuritizedNonCTP, CSR_CTP, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 0, DRC = DRC, RRAO= RRAO)
        print("\n####################\n####산출중(33%)#####\n####################\n")
        ResultData2 = AggregatedFRTB_RiskCharge(CSR, GIRR, FXR, EQR, COMR, CSR_SecuritizedNonCTP, CSR_CTP, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 1, DRC = DRC, RRAO= RRAO)
        print("\n####################\n####산출중(66%)#####\n####################\n")
        ResultData3 = AggregatedFRTB_RiskCharge(CSR, GIRR, FXR, EQR, COMR, CSR_SecuritizedNonCTP, CSR_CTP, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 2, DRC = DRC, RRAO= RRAO)
        writer = pd.ExcelWriter('ResultFRTB.xlsx', engine='xlsxwriter') # pylint: disable=abstract-class-instantiated
        ResultData1.to_excel(writer, sheet_name = 'ByBucket')
        ResultData2.to_excel(writer, sheet_name = 'ByDepart')
        ResultData3.to_excel(writer, sheet_name = 'ByPortfolio')
        writer.save()
        writer.close()
        for i in range(10) : 
            ViewerFRTBFlag = MainViewer(Title = 'Continue', MyText = '산출완료되었습니다.\n 확인할 뷰어를 선택하시오.', MyList = ["0: 버킷별", "1: 부서별","2: 포트별","3: 종료"], size = "800x450+30+30", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
            if ViewerFRTBFlag == 0 : 
                ViewFRTB(ResultData1)
            elif ViewerFRTBFlag == 1 : 
                ViewFRTB(ResultData2)
            elif ViewerFRTBFlag == 2 : 
                ViewFRTB(ResultData3)
            else : 
                break
            
        print("#################\n####산출완료#####\n#################\n")
        MainFlag2 = MainViewer(Title = 'Continue', MyText = '종료하시겠습니까', MyList = ["0: 종료", "1: 계속 다른업무 실행"], size = "800x450+30+30", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
        if MainFlag2 == 0:
            print("\n###########################\n### 프로그램을 종료합니다.###\n###########################")
            break
    elif MainFlag in [1,'1'] :                     
        HolidayDate = ReadCSV(currdir + "\\MarketData\\holidays\\Holidays.csv").fillna("19990101").applymap(lambda x : str(x).replace("-","")).astype(np.float64)        
        try : 
            FXSpot = PreprocessingFXSpotData(currdir + "\\MarketData\\spot\\FXSpot.csv")        
        except FileNotFoundError : 
            FXSpot = pd.DataFrame([])
        MainFlag2 = ""
        n = MainViewer(Title = 'Pricer', MyText = 'Pricer를 선택하시오', MyList = ["1: 채권", "2: IRS", "3: CMS Swap", "4: Currency Swap","5: Equity Option", "6: IRStructuredSwap(1Factor FDM Single Phase)","7: Plain Swaption","8: Plain FX Swap","9: Cap Floor","10: IRStructuredSwap(2Factor FDM Single Phase)","11: IRStructuredSwap(1Factor FDM DoublePhase)","12: IRStructuredSwap(2Factor FDM DoublePhase)"], size = "800x450+50+50", splitby = ":", listheight = 12, textfont = 13, titlelable = False, titleName = "Name")
        if int(n) == 1 or n == "채권" or str(n).lower() == "bond": 
            MainFlag2, Value, PV01, TempPV01 = PricingBondProgram(HolidayDate, currdir)
        elif int(n) == 2 or n == "IRS" or str(n).lower() == "irs" : 
            MainFlag2, Value, PV01, TempPV01 = PricingIRSProgram(HolidayDate, FXSpot)            
        elif int(n) == 3 or n == "CMS" or str(n).lower() == "cms" : 
            MainFlag2, Value, PV01, TempPV01 = PricingIRSProgram(HolidayDate, FXSpot, CMSUseFlag=1)            
        elif int(n) == 4 or n == "CRS" or str(n).lower() == "crs" : 
            MainFlag2, Value, PV01, TempPV01, TempPV01Est, TempPV01Est2 = PricingCRSProgram(HolidayDate, FXSpot)
        elif int(n) == 5 or n == "옵션" or str(n).lower() == "option" :
            MainFlag2, Value, PV01, TempPV01 = PricingEquityOptionProgram(currdir, HolidayDate)
        elif int(n) == 6 :
            MainFlag2, Value, PV01, TempPV01 = PricingIRStructuredSwapProgram(HolidayDate, currdir)             
        elif int(n) == 7 : 
            MainFlag2, Value, PV01, TempPV01 = BS_Swaption_Program(HolidayDate, currdir)
        elif int(n) == 8 : 
            MainFlag2, Value, PV01, TempPV01 = PricingFXSwapProgram(HolidayDate, FXSpot, currdir)
        elif int(n) == 9 : 
            MainFlag2, Value, PV01, TempPV01 = BS_CapFloor_Program(HolidayDate, currdir)
        elif int(n) == 10 :
            MainFlag2, Value, PV01, TempPV01 = PricingIRStructuredSwapProgram2F(HolidayDate, currdir)             
        elif int(n) == 11 :
            MainFlag2, Value, PV01, TempPV01 = PricingIRStructuredSwapProgramDoublePhase(HolidayDate, currdir)             
        elif int(n) == 12 :
            MainFlag2, Value, PV01, TempPV01 = PricingIRStructuredSwapProgram2FDoublePhase(HolidayDate, currdir)             
        
        MainFlag2 = MainViewer(Title = 'Continue', MyText = '종료하시겠습니까', MyList = ["0: 종료", "1: 계속 다른업무 실행"], size = "800x450+50+50", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
        if MainFlag2 == 0:
            print("\n###########################\n### 프로그램을 종료합니다.###\n###########################")
            break

        if str(MainFlag2).lower() == 'y' or len(str(MainFlag2)) == 0:
            print("\n###########################\n### 프로그램을 종료합니다.###\n###########################")
            break
    elif MainFlag in [3,'3'] : 
        HolidayDate = ReadCSV(currdir + "\\MarketData\\holidays\\Holidays.csv").fillna("19990101").applymap(lambda x : str(x).replace("-","")).astype(np.float64)        
        FXSpot = PreprocessingFXSpotData(currdir + "\\MarketData\\spot\\FXSpot.csv")        
        YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\inputdata",MultiSelection=False, namenotin = "ption", defaultvalue=0, DefaultStringList = ["IRS"])
        MyData = Data[0]
        ZeroCurveName = Name[0]
        ResultDF = ZeroCurveMaker(MyData, currdir, YYYYMMDD, HolidayDate, FXSpot, ZeroCurveName)
        MainFlag2 = MainViewer(Title = 'Continue', MyText = '종료하시겠습니까', MyList = ["0: 종료", "1: 계속 다른업무 실행"], size = "800x450+50+50", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
        if MainFlag2 == 0:
            print("\n###########################\n### 프로그램을 종료합니다.###\n###########################")
            break

    elif MainFlag in [4,'4'] : 
        HolidayDate = ReadCSV(currdir + "\\MarketData\\holidays\\Holidays.csv").fillna("19990101").applymap(lambda x : str(x).replace("-","")).astype(np.float64)        
        YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\inputdata", namein = 'sw')
        PriceToSwaptionVolProgram(YYYYMMDD, Name, Data, currdir, HolidayDate)
        MainFlag2 = MainViewer(Title = 'Continue', MyText = '종료하시겠습니까', MyList = ["0: 종료", "1: 계속 다른업무 실행"], size = "800x450+50+50", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
        if MainFlag2 == 0:
            print("\n###########################\n### 프로그램을 종료합니다.###\n###########################")
            break        
    elif MainFlag in [5, '5'] : 
        CapFloorCalibrationProgram(currdir)
        MainFlag2 = MainViewer(Title = 'Continue', MyText = '종료하시겠습니까', MyList = ["0: 종료", "1: 계속 다른업무 실행"], size = "800x450+50+50", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
        if MainFlag2 == 0:
            print("\n###########################\n### 프로그램을 종료합니다.###\n###########################")
            break        
    elif MainFlag in [6, '6'] : 
        HolidayDate = ReadCSV(currdir + "\\MarketData\\holidays\\Holidays.csv").fillna("19990101").applymap(lambda x : str(x).replace("-","")).astype(np.float64)        
        KappaCalibration(HolidayDate, currdir)
        MainFlag2 = MainViewer(Title = 'Continue', MyText = '종료하시겠습니까', MyList = ["0: 종료", "1: 계속 다른업무 실행"], size = "800x450+50+50", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
        if MainFlag2 == 0:
            print("\n###########################\n### 프로그램을 종료합니다.###\n###########################")
            break        
# %%

#x, y = Generate_OptionDate(20190929, 20460929, 1, 20, -1, ModifiedFollow = 0)
#Result = Pricing_IRCallableSwap_HWFDM(
#            20000, 20160929, 20250304, 20460929, 0,         
#            0.0, 0.25, 4, 0.0237, 3, 
#            4, 1.0, 0.25, 4, -0.0012, 
#            0, 
#            x,#[20190902,20200903,20210831,20220901,20230904,20240830,20250903,20260901,20270831,20280905,20290903,20300830,20310903,20320901,20330831,20340831,20350903,20360903,20370903,20380903,20390905,20400905,20410904,20420903,20430904,20440905,20450905], 
#            y,#[20190930,20200929,20210929,20220929,20231004,20240930,20250929,20260929,20270929,20280929,20291001,20300930,20310929,20320929,20330929,20340929,20351001,20360929,20370929,20380929,20390929,20401001,20410930,20421001,20430929,20440929,20450929], 
#            1,
#            [0.00274, 0.00548, 0.25479, 0.506849, 0.756164, 1.00274, 1.512329, 2.00274, 3.00822, 4.00548, 5.00548, 6.00548, 7.008219, 8.013699, 9.010959, 10.00822, 12.01096, 15.0137, 20.01918, 25.02466, 30.02192],
#            [0.027989, 0.027992, 0.028394, 0.027554, 0.026807, 0.02633, 0.025806, 0.025455, 0.025154, 0.025235, 0.025264, 0.025397, 0.025531, 0.025638, 0.025719, 0.025856, 0.026049, 0.025598, 0.024243, 0.022474, 0.021085],
#            [DayPlus(20240102, i) for i in range(365)], 
#            [0.0344]*365, 
#            [DayPlus(20240102, i) for i in range(365)], 
#            [0.0344]*365, 
#            kappa = -0.0133,
#            kappa2 = 0.01,
#            HWVolTerm = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
#            HWVol = [0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368],
#            HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
#            HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
#            LoggingFlag = 0)

# %%

# %%a

# %%

# %%
#Arithmetic_Asian_Opt_Pricing_Preprocessing(Long0Short1 = 0, Call0Put1 = 0, PriceDate = 20240627, AverageStartDate = 20240601, AverageEndDate = 20240927, OptionMaturityDate = 20240927, S = 100, K = 95, PrevAverage = 98, DiscTerm = [1, 2, 3], DiscRate = [0.03, 0.03, 0.03], DivTerm = [1], DivRate = [0.02], QuantoCorr = 0, FXVolTerm = [1], FXVol = [0], VolTerm = [0], VolParity = [0], Vols2D = 0.3, DivTypeFlag = 0, Holidays = KoreaHolidaysFromStartToEnd(2020,2040))


# %%

#CalResult = CalibrationKappaFromSwapRatio(20240625, [20250627, 20300627], [20300627, 20350627], [20350627, 20400627], [0.01, 0.01], [0.0095, 0.0095], [1, 2, 3], [0.034, 0.035, 0.036], 4, 0, KoreanHolidayFlag = False, AddHolidays = [])
