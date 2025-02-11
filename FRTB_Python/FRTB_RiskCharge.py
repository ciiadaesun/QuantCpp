#%%
"""
Created By Daesun Lim (CIIA(R), FRM(R))
Risk Quant Manager
My FRTB Module 
v1.0.1 
"""
import numpy as np
import pandas as pd
# JIT은 쓰지말자
#from numba import jit
import warnings
import os
currdir = os.getcwd()
warnings.filterwarnings('ignore')
print("#####################################\nCreated By Daesun Lim (CIIA(R), FRM(R))\nRisk Quant Manager\nMy FRTB Module \nv1.0.1 \n#####################################\n")

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
                        20220601, 20231002, 20240410, 20241001, 20250127]

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

def Linterp(x, y, targetx) : 
    x = np.array(x, dtype = np.float64)
    y = np.array(y, dtype = np.float64)
    targetx = float(targetx)
    srs = pd.Series(y, x).sort_index()
    if targetx <= srs.index[0] : 
        return srs.values[0]
    elif targetx >= srs.index[-1] : 
        return srs.values[-1]
    else : 
        if targetx in srs.index : 
            return srs.loc[targetx]
        else : 
            srs.loc[targetx] = np.nan
            return srs.sort_index().interpolate(method = 'linear').loc[targetx]

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
    else : 
        raise ValueError("Check The Month (Whether less then 13)") 

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
    else : 
        raise ValueError("Check The Month (Whether less then 13)") 

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

def Number_of_Coupons(
    ProductType,              # 상품종류 0이면 Futures, 1이면 Swap
    PriceDate,                # 평가일
    SwapMat,                  # 스왑 만기
    AnnCpnOneYear,            # 연 스왑쿠폰지급수
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
    if AnnCpnOneYear > 6:
        return -1

    HolidayYYYYMMDD = [ExcelDateToYYYYMMDD(h) if 0 <= h < 19000000 else h for h in Holidays]

    PriceYYYY = PriceDateYYYYMMDD // 10000
    PriceMM = (PriceDateYYYYMMDD % 10000) // 100
    PriceDD = PriceDateYYYYMMDD % 100

    SwapMatYYYY = SwapMat_YYYYMMDD // 10000
    SwapMatMM = (SwapMat_YYYYMMDD % 10000) // 100
    SwapMatDD = SwapMat_YYYYMMDD % 100

    if DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) <= 62 and AnnCpnOneYear < 6:
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

            CpnDate, firstcpndate = malloc_cpn_date_holiday(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, HolidayYYYYMMDD if HolidayUseFlag > 0 else [], ModifiedFollowingFlag)[0]
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
        
        CpnDate, firstcpndate = malloc_cpn_date_holiday(PriceDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, HolidayYYYYMMDD if HolidayUseFlag > 0 else [], ModifiedFollowingFlag)[0]

        return len(CpnDate)

def MappingCouponDates(
    ProductType,               # 상품종류 0이면 Futures, 1이면 Swap
    StartDate,                 # 시작일
    SwapMat,                   # 스왑 만기
    NBDayFromEndDate,          # N영업일 뒤 지급(만약 -1일 경우 EndDate To PayDate 자동 계산)
    AnnCpnOneYear,             # 연 스왑쿠폰지급수
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
    
    NumberCoupon = Number_of_Coupons(ProductType, StartDate, SwapMat, AnnCpnOneYear, HolidayUseFlag, Holidays, ModifiedFollowingFlag)
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
            if (SwapMat_DD < 7 and StartDD >= 24) :
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
        if (SwapMat_DD < 7 and StartDD >= 24) : 
            ##########################################
            ## If PayDate is next month of EndDate  ##
            ##########################################
            NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDDPayDate, ModifiedFollowingFlag, TempEndList)
            EndDateYYYYMMDD = TempEndList[0]                
        else :
            EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD

        CpnDate, firstcpndate = malloc_cpn_date_holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, HolidayYYYYMMDD if HolidayUseFlag > 0 else [], ModifiedFollowingFlag)[0]
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
        DFT1 = EXP_APPROX ** (-Linterp(TermArray, RateArray, T1) * T1)
        DFT2 = EXP_APPROX ** (-Linterp(TermArray, RateArray, T2) * T2)
        FRate = (1.0 / DeltaT) * (DFT1 / DFT2 - 1.0)
    elif T1 <= TermArray[0]:
        DFT1 = EXP_APPROX ** (-RateArray[0] * T1)
        DFT2 = EXP_APPROX ** (-Linterp(TermArray, RateArray, T2) * T2)
        FRate = (1.0 / DeltaT) * (DFT1 / DFT2 - 1.0)
    else:
        DFT1 = EXP_APPROX ** (-RateArray[LengthArray - 1] * T1)
        DFT2 = EXP_APPROX ** (-RateArray[LengthArray - 1] * T2)
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
    return PI_0 - 1.0, AnnualizedOISRate

def istermtype(termlist) : 
    term = np.array(termlist, dtype = np.float64)
    if term.min() >= 19000101 : 
        return "YYYYMMDD"
    elif term.min() > 30.0 : 
        return "ExcelDate"
    else : 
        return "Term"

def Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate) : 
    if len(ZeroTerm) > 0 : 
        istermtype_ZeroTerm = istermtype(ZeroTerm)
        if istermtype_ZeroTerm == "YYYYMMDD" : 
            for i in range(len(ZeroTerm)) : 
                ZeroTerm[i] = (DayCountAtoB(PriceDate, ZeroTerm[i])/365)
        elif istermtype_ZeroTerm == "ExcelDate" :
            ExcelPriceDate = YYYYMMDDToExcelDate(PriceDate) if int(PriceDate) >= 19000101 else PriceDate
            for i in range(len(ZeroTerm)) : 
                ZeroTerm[i] = ((ZeroTerm[i] - ExcelPriceDate)/365)
        
        if np.abs(np.array(ZeroRate)).mean() > 0.6 : 
            for i in range(len(ZeroRate)) : 
                ZeroRate[i] = ZeroRate[i]/100

def Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
              PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
              AnnCpnOneYear, DayCountFlag, KoreanHoliday = True, MaturityToPayDate = 0, EstZeroCurveTerm = [],
              EstZeroCurveRate = [], FixingHolidayList = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False,
              LoggingFlag = 0, LoggingDir = '', ModifiedFollow = 1, OverNightRateDateHistory = [], OverNightRateHistory = [], LookBackDays = 0, ObservShift = False) :
    
    LoggingStart = []
    LoggingEnd = []
    LoggingPayDate = []
    LoggingFraction = []
    LoggingForwardRate = []
    LoggingCpnFix = []
    LoggingCpnRate = []
    LoggingDF = []
    
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
    if (AnnCpnOneYear >= 4 and DayCountAtoB(EffectiveDateYYYYMMDD, MaturityYYYYMMDD) < 70) or (DayCountAtoB(EffectiveDateYYYYMMDD, MaturityYYYYMMDD) < 10) : 
        Generated_CpnDate = np.array([MaturityYYYYMMDD], dtype = np.int64)
    else : 
        Generated_CpnDate, firstcpndate = malloc_cpn_date_holiday(EffectiveDateYYYYMMDD, MaturityYYYYMMDD, AnnCpnOneYear, FixingHolidayYYYYMMDD, ModifiedFollow)

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
        
        f = 0
        if LastFixingDate < PriceDateYYYYMMDD : 
            f = FirstFloatFixRate
        elif LastFixingDate >= PriceDateYYYYMMDD : 
            if len(EstZeroCurveRate) == 0 and len(EstZeroCurveTerm) == 0 :
                if FloatFlag == 2 : 
                    Start = EDate_YYYYMMDD(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, -1)
                    End = Generated_CpnDate[i]
                    BusinessDate = BDate[(BDate >= Start) & (BDate <= End)]
                    NBDCount = DayCountBDate[(BDate >= Start) & (BDate <= End)]
                    CompValue, f = SOFR_ForwardRate_Compound(PriceDateYYYYMMDD,    ZeroCurveTerm,    ZeroCurveRate,     Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD,    Generated_CpnDate[i],
                                                            0,    LookBackDays,    ObservShift,    0,    BusinessDate,    NBDCount,
                                                            OverNightRateDateHistory,    OverNightRateHistory,    365 if DayCountFlag == 0 else 360,    1)
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
                    CompValue, f = SOFR_ForwardRate_Compound(PriceDateYYYYMMDD,    EstZeroCurveTerm,    EstZeroCurveTerm,     Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD,    Generated_CpnDate[i],
                                                            0,    LookBackDays,    ObservShift,    0,    BusinessDate,    NBDCount,
                                                            OverNightRateDateHistory,    OverNightRateHistory,    365 if DayCountFlag == 0 else 360,    1)
                else : 
                    r1 = Linterp(EstZeroCurveTerm, EstZeroCurveRate, tstart)
                    r2 = Linterp(EstZeroCurveTerm, EstZeroCurveRate, tend)
                    f = 1.0 / deltat * (np.exp(-r1 * tstart)/np.exp(-r2 * tend) - 1.0)
                    
            
        r = Linterp(ZeroCurveTerm, ZeroCurveRate, tpay)
        if tpay > 0 : 
            if DayCountFlag != 3 : 
                cpn = (f * (FloatFlag > 0) + CpnRate) * Nominal * deltat * np.exp(-r * tpay)
            else : 
                if (AnnCpnOneYear == 1) : 
                    cpn = (f * (FloatFlag > 0) + CpnRate) * Nominal * np.exp(-r * tpay) 
                elif (AnnCpnOneYear == 2) : 
                    cpn = (f * (FloatFlag > 0) + CpnRate) * 0.5 * Nominal * np.exp(-r * tpay) 
                elif (AnnCpnOneYear == 3) : 
                    cpn = (f * (FloatFlag > 0) + CpnRate) * 0.3333333333 * Nominal * np.exp(-r * tpay) 
                elif (AnnCpnOneYear == 4) : 
                    cpn = (f * (FloatFlag > 0) + CpnRate) * 0.25 * Nominal * np.exp(-r * tpay) 
                elif (AnnCpnOneYear == 6) : 
                    cpn = (f * (FloatFlag > 0) + CpnRate) * 0.166666666667 * Nominal * np.exp(-r * tpay) 
                elif (AnnCpnOneYear == 12) : 
                    cpn = (f * (FloatFlag > 0) + CpnRate) * 0.083333333333 * Nominal * np.exp(-r * tpay) 
                else : 
                    raise ValueError("Check AnnCpnNum")
        else : 
            cpn = 0
        
        s += cpn
        if LoggingFlag > 0 : 
            LoggingStart.append(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD)
            LoggingEnd.append(Generated_CpnDate[i])
            LoggingPayDate.append(YYYYMMDDofNextDate)
            LoggingFraction.append(deltat)
            LoggingForwardRate.append(f)
            LoggingCpnFix.append(CpnRate)
            LoggingCpnRate.append(cpn)
            LoggingDF.append(np.exp(-r * tpay))
                    
    if NominalFlag == 1 : 
        if NominalDateIsNominalPayDate == True : 
            tpay = DayCountAtoB(PriceDateYYYYMMDD, Generated_CpnDate[-1])/365
            r = Linterp(ZeroCurveTerm, ZeroCurveRate, tpay)
        s += Nominal * np.exp(-r * tpay)
        if (LoggingFlag > 0) : 
            LoggingStart.append(EffectiveDateYYYYMMDD)
            LoggingEnd.append(Generated_CpnDate[-1])
            LoggingPayDate.append(YYYYMMDDofNextDate if NominalDateIsNominalPayDate == False else Generated_CpnDate[-1])
            LoggingFraction.append(tpay)
            LoggingForwardRate.append(r)
            LoggingCpnFix.append(CpnRate)
            LoggingCpnRate.append(Nominal)
            LoggingDF.append(np.exp(-r * tpay))             
    
    if LoggingFlag == 1 : 
        LoggingDF = pd.DataFrame([LoggingStart,LoggingEnd,LoggingPayDate,LoggingFraction, LoggingForwardRate, LoggingCpnFix, LoggingCpnRate, LoggingDF], index = ["Start","End","Pay","Frac","ForwardRate","CpnFixed","Cpn","DF"]).T               
        LoggingDF["Price"] = s
        LoggingDF.to_csv(LoggingDir + "\\LoggingFiles.csv", index = False)
    elif LoggingFlag == 2 : 
        df = ReadCSV(LoggingDir + "\\LoggingFiles.csv")
        LoggingDF = pd.DataFrame([LoggingStart,LoggingEnd,LoggingPayDate,LoggingFraction, LoggingForwardRate, LoggingCpnFix, LoggingCpnRate, LoggingDF], index = ["Start","End","Pay","Frac","ForwardRate","CpnFixed","Cpn","DF"]).T               
        LoggingDF["Price"] = s
        pd.concat([df, LoggingDF],axis = 1).to_csv(LoggingDir + "\\LoggingFiles.csv", index = False)
    
    return s                               

def Calc_Bond_PV01(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
                    PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
                    AnnCpnOneYear, DayCountFlag, KoreanHoliday = True, MaturityToPayDate = 0, EstZeroCurveTerm = [],
                    EstZeroCurveRate = [], FixingHolidayList = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False,
                    LoggingFlag = 0, LoggingDir = '', ModifiedFollow = 1, OverNightRateDateHistory = [], OverNightRateHistory = [], LookBackDays = 0, ObservShift = False) :
    
    P = Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
            PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
            AnnCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm ,
            EstZeroCurveRate , FixingHolidayList , AdditionalPayHolidayList , NominalDateIsNominalPayDate ,
            LoggingFlag, LoggingDir, ModifiedFollow , OverNightRateDateHistory, OverNightRateHistory , LookBackDays , ObservShift )

    ResultArray = np.zeros(len(ZeroCurveRate))
    for i in range(len(ZeroCurveTerm)) : 
        ZeroUp = np.array(ZeroCurveRate).copy()
        ZeroUp[i] += 0.0001
        Pu = Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
                PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroUp, 
                AnnCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm ,
                EstZeroCurveRate , FixingHolidayList , AdditionalPayHolidayList , NominalDateIsNominalPayDate ,
                0, '', ModifiedFollow , OverNightRateDateHistory, OverNightRateHistory , LookBackDays , ObservShift )

        ResultArray[i] = Pu - P
        # Reset
        
    if (len(EstZeroCurveRate) > 0 and len(EstZeroCurveTerm) > 0 and len(EstZeroCurveRate) == len(EstZeroCurveTerm)) : 
        ResultArray2 = np.zeros(len(EstZeroCurveTerm))
        for i in range(len(EstZeroCurveRate)) : 
            ZeroUp = np.array(EstZeroCurveRate).copy()
            ZeroUp[i] += 0.0001            
            Pu = Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
                    PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
                    AnnCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm ,
                    ZeroUp , FixingHolidayList , AdditionalPayHolidayList , NominalDateIsNominalPayDate ,
                    0, '', ModifiedFollow , OverNightRateDateHistory, OverNightRateHistory , LookBackDays , ObservShift )
            ResultArray[i] = Pu - P
            # Reset
            ZeroUp[i] = EstZeroCurveRate[i]
        df2 = pd.Series(ResultArray, index = ZeroCurveTerm).reset_index()
        df2.columns = ["PV01Term","PV01"]
        df3 = pd.Series(ResultArray2, index = EstZeroCurveTerm).reset_index()
        df3.columns = ["PV01TermEst","PVEst01"]
        if LoggingFlag > 0 : 
            df = ReadCSV(LoggingDir + "\\LoggingFiles.csv")
            pd.concat([df, df2, df3],axis = 1).to_csv(LoggingDir + "\\LoggingFiles.csv", index = False)
        return P, df2, df3

    df2 = pd.Series(ResultArray, index = ZeroCurveTerm).reset_index()
    df2.columns = ["PV01Term","PV01"]
    if LoggingFlag > 0 : 
        df = ReadCSV(LoggingDir + "\\LoggingFiles.csv")
        pd.concat([df, df2],axis = 1).to_csv(LoggingDir + "\\LoggingFiles.csv", index = False)
    return P, df2            
    
def Calc_IRS(Nominal, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTerm, ZeroCurveRate, AnnCpnOneYear, DayCountFlag, 
             KoreanHoliday = True, MaturityToPayDate = 0, EstZeroCurveTerm = [], EstZeroCurveRate = [], FixingHolidayList = [], 
             AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False, LoggingFlag = 0, LoggingDir = '', 
             ModifiedFollow = 1, OverNightRateDateHistory = [], OverNightRateHistory = [], LookBackDays = 0, ObservShift = False, 
             FixedPayerFlag = 0) :
    
    LoggingFlag1, LoggingFlag2 = 0,0
    if LoggingFlag > 0 : 
        LoggingFlag1, LoggingFlag2 = 1, 2 

    Preprocessing_ZeroTermAndRate(ZeroCurveTerm, ZeroCurveRate, PriceDateYYYYMMDD)
    
    FixedLeg = Calc_Bond(Nominal, 0, 0, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
              PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
              AnnCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm = EstZeroCurveTerm,
              EstZeroCurveRate = EstZeroCurveTerm, FixingHolidayList = FixingHolidayList, AdditionalPayHolidayList  = AdditionalPayHolidayList, NominalDateIsNominalPayDate = NominalDateIsNominalPayDate,
              LoggingFlag = LoggingFlag1, LoggingDir = LoggingDir, ModifiedFollow = ModifiedFollow, OverNightRateDateHistory = OverNightRateDateHistory, OverNightRateHistory = OverNightRateHistory, LookBackDays = LookBackDays, ObservShift = ObservShift)

    if len(EstZeroCurveTerm) >= 0 and len(EstZeroCurveRate) >= 0 : 
        Preprocessing_ZeroTermAndRate(EstZeroCurveTerm, EstZeroCurveRate, PriceDateYYYYMMDD)

    FloatLeg = Calc_Bond(Nominal, 0, 1, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
            PriceDateYYYYMMDD, MaturityYYYYMMDD, 0.0, ZeroCurveTerm, ZeroCurveRate, 
            AnnCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm = EstZeroCurveTerm,
            EstZeroCurveRate = EstZeroCurveRate, FixingHolidayList = FixingHolidayList, AdditionalPayHolidayList  = AdditionalPayHolidayList, NominalDateIsNominalPayDate = NominalDateIsNominalPayDate,
            LoggingFlag = LoggingFlag2, LoggingDir = LoggingDir, ModifiedFollow = ModifiedFollow, OverNightRateDateHistory = OverNightRateDateHistory, OverNightRateHistory = OverNightRateHistory, LookBackDays = LookBackDays, ObservShift = ObservShift)
    return FixedLeg - FloatLeg if FixedPayerFlag == 0 else FloatLeg - FixedLeg    
    
def ReadCSV(filedir) :
    try : 
        chunk_list = pd.read_csv(filedir, chunksize = 5000, engine = 'python')
    except UnicodeDecodeError : 
        chunk_list = pd.read_csv(filedir, chunksize = 5000, engine = 'python', encoding = 'cp949')
    
    df = pd.DataFrame()
    for i in chunk_list : 
        df = pd.concat([df,i],axis = 0)
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
        DataCSRDelta["Delta_Sensi"] = DataCSRDelta["Delta_Sensi"].astype(np.float64) * 10000
        DataCSR = pd.concat([DataCSRDelta, DataCSRNonDelta],axis = 0)
    if len(DataGIRR) > 0 : 
        DataGIRRVega = DataGIRR[DataGIRR["Risk_Type"].isin(["베가","Vega","베가(Vega)"])]
        DataGIRR_NonVega = DataGIRR.loc[DataGIRR.index.difference(DataGIRRVega.index)]
        DataGIRR_NonVega = DataGIRR_NonVega.rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Type"})
        DataGIRRVega = DataGIRRVega.rename(columns = {"RiskFactor3":"Curve","RiskFactor1":"Tenor1","RiskFactor2":"Tenor2"})        
        DataGIRR = pd.concat([DataGIRRVega, DataGIRR_NonVega],axis = 0)        
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
        
        DataCOMR = pd.concat([DataCOMRDelta, DataCOMRCurvature, DataCOMRVega],axis = 0)
    if dataformat == 'Combined' : 
        return pd.concat([DataCSR,DataGIRR,DataFXR,DataEQR,DataCOMR],axis = 0)
    else : 
        return DataCSR,pd.DataFrame([]), pd.DataFrame([]), DataGIRR,DataFXR,DataEQR,DataCOMR
    
def PreProcessingMyData(RAWData) : 
    CSR = RAWData[RAWData["Risk_Class"].isin(["CSR","csr","신용스프레드","신용스프레드(CSR)"]) ]
    CSR_Delta = CSR[CSR["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    CSR_Curvature = CSR[CSR["Risk_Type"].isin(["CURVATURE","Curvature","curvature","커버쳐","커버쳐(Curvature)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    CSR_Vega = CSR[CSR["Risk_Type"].isin(["VEGA","Vega","vega","베가","베가(Vega)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Issuer"})
    Result_CSR = pd.concat([CSR_Delta, CSR_Curvature, CSR_Vega],axis = 0)
    
    CSR_SecuritizedNonCTP = RAWData[RAWData["Risk_Class"].isin(["CSR Securitized Non CTP","유동화(CTP 제외)", "CSR 유동화(CTP 제외)", "신용스프레드 유동화(CTP 제외)"]) ]
    CSR_SecuritizedNonCTPDelta = CSR_SecuritizedNonCTP[CSR_SecuritizedNonCTP["Risk_Type"].isin(["DELTA","Delta","delta","델타","델타(Delta)"])].rename(columns = {"RiskFactor1":"Curve","RiskFactor2":"Tenor","RiskFactor3":"Tranche"})
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
        CSRDelta_Total = Calc_CSRDelta(CSR_Data, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
        CSRCurvature_Total = Calc_CSRCurvature(CSR_Data, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
        CSRVega_Total = Calc_CSRVega(CSR_Data, CSR_DeltaNonSecurCorrDf,  VegaSensiName).reset_index()

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

        GIRRDelta_Total = Calc_GIRRDelta(GIRR_Data, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
        GIRRCurvature_Total = Calc_GIRRCurvature(GIRR_Data, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
        GIRRVega_Total = Calc_GIRRVega(GIRR_Data, VegaSensiName).reset_index()
        
        FXRDelta_Total = Calc_FXRDelta(FXR_Data, HighLiquidCurrency, DeltaSensiName).reset_index()
        FXRCurvature_Total = Calc_FXRCurvature(FXR_Data, HighLiquidCurrency, DeltaSensiName).reset_index()
        FXRVega_Total = Calc_FXRVega(FXR_Data, VegaSensiName).reset_index()
        
        EQRDelta_Total = Calc_EQRDelta(EQR_Data, DeltaSensiName).reset_index()
        EQRCurvature_Total = Calc_EQRCurvature(EQR_Data,EQDeltaRWMappingDF, DeltaSensiName).reset_index()
        EQRVega_Total = Calc_EQRVega(EQR_Data,VegaSensiName).reset_index()
        
        COMRDelta_Total = Calc_COMRDelta(COMR_Data, DeltaSensiName).reset_index()
        COMRCurvature_Total = Calc_COMRCurvature(COMR_Data, DeltaSensiName).reset_index()
        COMRVega_Total = Calc_COMRVega(COMR_Data, VegaSensiName).reset_index()  
        
        if len(DRC) > 0 :
            DRC_Total = CalcDRC3RiskCharge(DRC).reset_index()
        
        if len(RRAO) > 0 : 
            RRAO_Total = CalcRRAORiskCharge(RRAO).reset_index()
        
    elif GroupbyFlag == 1 : 
        CSRDelta_Total = CSR_Data.groupby("Depart").apply(Calc_CSRDelta, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
        CSRCurvature_Total = CSR_Data.groupby("Depart").apply(Calc_CSRCurvature, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
        CSRVega_Total = CSR_Data.groupby("Depart").apply(Calc_CSRVega, CSR_DeltaNonSecurCorrDf,  VegaSensiName).reset_index()
        
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
                    
        GIRRDelta_Total = GIRR_Data.groupby("Depart").apply(Calc_GIRRDelta, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
        GIRRCurvature_Total = GIRR_Data.groupby("Depart").apply(Calc_GIRRCurvature, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
        GIRRVega_Total = GIRR_Data.groupby("Depart").apply(Calc_GIRRVega, VegaSensiName).reset_index()
        
        FXRDelta_Total = FXR_Data.groupby("Depart").apply(Calc_FXRDelta, HighLiquidCurrency, DeltaSensiName).reset_index()
        FXRCurvature_Total = FXR_Data.groupby("Depart").apply(Calc_FXRCurvature, HighLiquidCurrency, DeltaSensiName).reset_index()
        FXRVega_Total = FXR_Data.groupby("Depart").apply(Calc_FXRVega, VegaSensiName).reset_index()
        
        EQRDelta_Total = EQR_Data.groupby("Depart").apply(Calc_EQRDelta, DeltaSensiName).reset_index()
        EQRCurvature_Total = EQR_Data.groupby("Depart").apply(Calc_EQRCurvature,EQDeltaRWMappingDF, DeltaSensiName).reset_index()
        EQRVega_Total = EQR_Data.groupby("Depart").apply(Calc_EQRVega,VegaSensiName).reset_index()
        
        COMRDelta_Total = COMR_Data.groupby("Depart").apply(Calc_COMRDelta, DeltaSensiName).reset_index()
        COMRCurvature_Total = COMR_Data.groupby("Depart").apply(Calc_COMRCurvature, DeltaSensiName).reset_index()
        COMRVega_Total = COMR_Data.groupby("Depart").apply(Calc_COMRVega, VegaSensiName).reset_index()  

        if len(DRC) > 0 :
            DRC_Total = DRC.groupby("Depart").apply(CalcDRC3RiskCharge).reset_index()
           
        if len(RRAO) > 0 : 
            RRAO_Total = RRAO.groupby("Depart").apply(CalcRRAORiskCharge).reset_index()
            
    else : 
        CSRDelta_Total = CSR_Data.groupby("Portfolio").apply(Calc_CSRDelta, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
        CSRCurvature_Total = CSR_Data.groupby("Portfolio").apply(Calc_CSRCurvature, CSR_DeltaNonSecurCorrDf, DeltaSensiName).reset_index()
        CSRVega_Total = CSR_Data.groupby("Portfolio").apply(Calc_CSRVega, CSR_DeltaNonSecurCorrDf,  VegaSensiName).reset_index()

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
                    
        GIRRDelta_Total = GIRR_Data.groupby("Portfolio").apply(Calc_GIRRDelta, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
        GIRRCurvature_Total = GIRR_Data.groupby("Portfolio").apply(Calc_GIRRCurvature, GIRR_DeltaRiskFactor, GIRR_DeltaRfCorr, DeltaSensiName).reset_index()
        GIRRVega_Total = GIRR_Data.groupby("Portfolio").apply(Calc_GIRRVega, VegaSensiName).reset_index()
        
        FXRDelta_Total = FXR_Data.groupby("Portfolio").apply(Calc_FXRDelta, HighLiquidCurrency, DeltaSensiName).reset_index()
        FXRCurvature_Total = FXR_Data.groupby("Portfolio").apply(Calc_FXRCurvature, HighLiquidCurrency, DeltaSensiName).reset_index()
        FXRVega_Total = FXR_Data.groupby("Portfolio").apply(Calc_FXRVega, VegaSensiName).reset_index()
        
        EQRDelta_Total = EQR_Data.groupby("Portfolio").apply(Calc_EQRDelta, DeltaSensiName).reset_index()
        EQRCurvature_Total = EQR_Data.groupby("Portfolio").apply(Calc_EQRCurvature,EQDeltaRWMappingDF, DeltaSensiName).reset_index()
        EQRVega_Total = EQR_Data.groupby("Portfolio").apply(Calc_EQRVega,VegaSensiName).reset_index()
        
        COMRDelta_Total = COMR_Data.groupby("Portfolio").apply(Calc_COMRDelta, DeltaSensiName).reset_index()
        COMRCurvature_Total = COMR_Data.groupby("Portfolio").apply(Calc_COMRCurvature, DeltaSensiName).reset_index()
        COMRVega_Total = COMR_Data.groupby("Portfolio").apply(Calc_COMRVega, VegaSensiName).reset_index()  
    
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

def MarketDataFileListPrint(currdir) : 
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
                            filenum.append(k)
                            folder.append(newdir2)
                            filenames.append(newdir2 + '\\' + name3)
                            filenamesprint.append(str(k) + ". " + newdir2 + "\\" + name3)
                            YYYYMMDD.append(name)
                            k += 1
                    else : 
                        filenum.append(k)
                        folder.append(newdir)
                        filenames.append(newdir + '\\' + name2)
                        filenamesprint.append(str(k) + ". " + newdir + '\\' + name2)
                        YYYYMMDD.append(name)
                        k += 1
    return pd.DataFrame([YYYYMMDD, filenum, folder, filenames, filenamesprint], index = ["YYYYMMDD","Number","Folder","Directory","DirectoryPrint"]).T

def UsedMarketDataSetToPricing(MarketDataDir) : 
    Data = MarketDataFileListPrint(MarketDataDir).sort_values(by = "YYYYMMDD")[-50:]
    GroupbyYYYYMMDD = Data.groupby("YYYYMMDD").first().reset_index()
    PrintDate = "\n 다음 중 MarketData 날짜를 고르세요. \n"
    n = 0
    for x, y in zip(GroupbyYYYYMMDD["Number"], GroupbyYYYYMMDD["YYYYMMDD"]) : 
        PrintDate += str(n+1) + ". " + str(y) + "\n"
        n = n + 1
    DateMarketDataIdx = input(PrintDate + "-> ")
    YYYYMMDD = GroupbyYYYYMMDD["YYYYMMDD"].iloc[int(DateMarketDataIdx) - 1]
    TargetFiles = Data[Data["YYYYMMDD"].astype(str) == YYYYMMDD].groupby("Directory").first().reset_index()
    PrintMarketData = "\n 다음 중 MarketData를 고르세요.(ex : 1, ex2: 1, 2, 3 와 같은 여러개 선택)\n"
    for x in TargetFiles["DirectoryPrint"] : 
        PrintMarketData += ' ' + str(x) + "\n"
    DataMarketData = input(PrintMarketData)
    MarketDataList = []
    MarketDataName = []
    
    if len(DataMarketData) == 1 : 
        MarketDataList.append(ReadCSV(TargetFiles[TargetFiles["Number"] == int(DataMarketData)]["Directory"].iloc[0]))
        MarketDataName.append(TargetFiles[TargetFiles["Number"] == int(DataMarketData)]["Directory"].iloc[0])
    else : 
        NumberList = DataMarketData.replace(" ","").split(",")
        TargetFiles2 = TargetFiles[TargetFiles["Number"].astype(str).isin(NumberList)]
        for idx in range(len(TargetFiles2)) : 
            MarketDataList.append(ReadCSV(TargetFiles2["Directory"].iloc[idx]))
            MarketDataName.append(TargetFiles2["Directory"].iloc[idx])
    
    for i in range(len(MarketDataList)) : 
        MarketDataList[i] = MarketDataList[i].applymap(lambda x : str(x).replace("-",""))
        if "Rate" in MarketDataList[i].columns and "Term" in MarketDataList[i].columns : 
            Term = list(MarketDataList[i]["Term"].astype(np.float64))
            Rate = list(MarketDataList[i]["Rate"].astype(np.float64))
            PriceDate = MarketDataList[i]["PriceDate"].iloc[0]
            Preprocessing_ZeroTermAndRate(Term, Rate, int(PriceDate))
            MarketDataList[i]["Term"] = Term
            MarketDataList[i]["Rate"] = Rate
        elif "rate" in MarketDataList[i].columns and "term" in MarketDataList[i].columns : 
            Term = list(MarketDataList[i]["trm"].astype(np.float64))
            Rate = list(MarketDataList[i]["rate"].astype(np.float64))
            PriceDate = MarketDataList[i]["PriceDate"].iloc[0]
            Preprocessing_ZeroTermAndRate(Term, Rate, int(PriceDate))
            MarketDataList[i]["term"] = Term
            MarketDataList[i]["rate"] = Rate

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
    
def MainFunction(currdir) : 
    MyFiles = FileListPrint(currdir)
    print("\n전체 리스크가 포함된 RAW 파일의 경우 0를 입력하시오.(ex: FRTB_RAW.csv)\n리스크 클래스별 RAW 파일로 각각 입력할경우 숫자 1을 입력하시오.(GIRR_RAW.csv,CSR_RAW.csv,...)\n")
    mynum = int(input("입력 -> "))
    if mynum == 0 : 
        PrintStr = LoggingUsedFileNames(MyFiles, MyClass = 'FRTB')
        print(PrintStr)
        Num = int(input('입력 ->'))
        Data = ReadCSV(MyFiles[MyFiles["Number"] == Num]["Directory"].iloc[0])
    else : 
        PrintStr1 = LoggingUsedFileNames(MyFiles, MyClass = 'GIRR')
        if PrintStr1 == '' : 
            Data1 = pd.DataFrame([])
        else : 
            print(PrintStr1)
            GIRRFileNum = int(input('입력 ->'))
            Data1 = ReadCSV(MyFiles[MyFiles["Number"] == GIRRFileNum]["Directory"].iloc[0])

        PrintStr2 = LoggingUsedFileNames(MyFiles, MyClass = 'CSR')
        if PrintStr2 == '' : 
            Data2 = pd.DataFrame([])
        else : 
            print(PrintStr2)
            CSRFileNum = int(input('입력 ->'))
            Data2 = ReadCSV(MyFiles[MyFiles["Number"] == CSRFileNum]["Directory"].iloc[0])

        PrintStr3 = LoggingUsedFileNames(MyFiles, MyClass = 'FXR')
        if PrintStr3 == '' : 
            Data3 = pd.DataFrame([])
        else : 
            print(PrintStr3)
            FXRFileNum = int(input('입력 ->'))
            Data3 = ReadCSV(MyFiles[MyFiles["Number"] == FXRFileNum]["Directory"].iloc[0])

        PrintStr4 = LoggingUsedFileNames(MyFiles, MyClass = 'EQR')
        if PrintStr4 == '' : 
            Data4 = pd.DataFrame([])
        else : 
            print(PrintStr4)
            EQRFileNum = int(input('입력 ->'))
            Data4 = ReadCSV(MyFiles[MyFiles["Number"] == EQRFileNum]["Directory"].iloc[0])

        PrintStr5 = LoggingUsedFileNames(MyFiles, MyClass = 'COMR')
        if PrintStr5 == '' : 
            Data5 = pd.DataFrame([])
        else : 
            print(PrintStr5)
            COMRFileNum = int(input('입력 ->'))
            Data5 = ReadCSV(MyFiles[MyFiles["Number"] == COMRFileNum]["Directory"].iloc[0])
        Data = pd.concat([Data1, Data2, Data3, Data4, Data5],axis = 0)
    return Data    

def PricingBondProgram(YYYYMMDD, Name, MyMarketDataList) : 
    print("\n 세팅된 커브는 다음과 같습니다. \n 평가날짜 : " + YYYYMMDD)
    curvename = ''
    for i in range(len(Name)) : 
        if "Rate" in Data[i].columns or 'rate' in Data[i].columns : 
            curvename += '\n\n' + str(i+1) + '. ' + Name[i].split('\\')[-1] + '\n'
            Term = list(Data[i][Data[i].columns[1]].round(5))[:10]
            Rate = list(Data[i][Data[i].columns[2]].round(5))[:10]
            curvename += '\n Term = ' + str(Term).split(']')[0] + ', ...]'
            curvename += '\n Rate = ' + str(Rate).split(']')[0] + ', ...]'
    print(curvename)    
    if len(MyMarketDataList) == 1 : 
        Curve = MyMarketDataList[0]
    else : 
        print("\n 채권을 평가하기 위해 사용할 커브 번호를 입력하세요.\n")        
        n = int(input())
        Curve = MyMarketDataList[n-1]
    CurveTerm = list(Curve["Term" if "Term" in Curve.columns else "term"])
    CurveRate = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
    print("\n 채권 발행일(YYYYMMDD)을 입력하시오.\n")        
    EffectiveDate = int(input())
    print("\n 채권 만기일(YYYYMMDD)을 입력하시오.(지급일 X)\n")        
    MaturityDate = int(input())
    print("\n 채권 만기일에서 대금결제일까지 영업일수를 입력하시오.\n")        
    MaturityToPayDate = int(input())
    print("\n 변동금리채라면 1을 입력하시오.\n")        
    FloatFlag = int(input())
    print("\n 쿠폰금리를 입력하시오(0.03, 0.05 등).\n")        
    CpnRate = float(input())
    print("\n 1년에 이자지급횟수를 입력하시오.\n")        
    AnnCpnOneYear = int(input())
    print("\n Act365는 0을 | Act360은 1을 | ACTACT이면 2를 | 30/360이면 3를 입력하시오 \n")        
    DayCountFlag = int(input())
    FixingRate = 0.0
    if FloatFlag in [1,'1', 2,'2'] : 
        print("\n 최초 Fixing금리를 입력하시오. 입력안해도 되면 0을 입력하시오. \n")        
        FixingRate = float(input())
    
    Value, PV01 = Calc_Bond_PV01(10000, 1, FloatFlag, FixingRate, EffectiveDate, 
            int(YYYYMMDD), MaturityDate, CpnRate, CurveTerm, CurveRate, 
            AnnCpnOneYear, DayCountFlag, KoreanHoliday = True, MaturityToPayDate = MaturityToPayDate, EstZeroCurveTerm = [],
            EstZeroCurveRate = [], FixingHolidayList = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False,
            LoggingFlag = 1, LoggingDir = currdir, ModifiedFollow = 1)         
    
    print("##############\n채권가격은 " + str(np.round(Value,6)) + "\n##############\n")
    print("##############\n####산출완료#####\n##############\n")
    MainFlag2 = input("종료하시겠습니까? (Y/N)")
    return MainFlag2

def PricingIRSProgram(YYYYMMDD, Name, MyMarketDataList) : 
    print("\n 세팅된 커브는 다음과 같습니다. \n 평가날짜 : " + YYYYMMDD)
    curvename = ''
    for i in range(len(Name)) : 
        if "Rate" in Data[i].columns or 'rate' in Data[i].columns : 
            curvename += '\n\n' + str(i+1) + '. ' + Name[i].split('\\')[-1] + '\n'
            Term = list(Data[i][Data[i].columns[1]].round(5))[:10]
            Rate = list(Data[i][Data[i].columns[2]].round(5))[:10]
            curvename += '\n Term = ' + str(Term).split(']')[0] + ', ...]'
            curvename += '\n Rate = ' + str(Rate).split(']')[0] + ', ...]'
    print(curvename)  
    if len(MyMarketDataList) == 1 : 
        Curve = MyMarketDataList[0]
    else : 
        print("\n IRS 스왑을 평가하기 위해 사용할 커브 번호를 입력하세요. \n * 두 커브를 선택할 경우 DiscCurveNum, EstCurveNum 순으로 입력하시오 (예 1, 2 -> 1DiscCurve, 2EstCurve)\n")        
        MyStr = input()
        if len(str(MyStr)) == 0 : 
            print("\n 오입력으로 프로그램 종료합니다.")
            return "" 
        elif len(str(MyStr)) == 1: 
            n = int(MyStr)
            Curve = MyMarketDataList[n-1]
            CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
            CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
            CurveTerm2, CurveRate2 = [], []
        elif ',' in str(MyStr) : 
            Splited = MyStr.replace(" ","").split(',')
            n = Splited[0]
            n2 = Splited[1]
            Curve = MyMarketDataList[n-1]
            CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
            CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
            Curve2 = MyMarketDataList[n2-1]
            CurveTerm2 = list(Curve2["Term" if "Term" in Curve2.columns else "term"])
            CurveRate2 = list(Curve2["Rate" if "Rate" in Curve2.columns else "rate"])
            
    print("\n IRS 발행일(YYYYMMDD)을 입력하시오.\n")        
    EffectiveDate = int(input())
    print("\n IRS 만기일(YYYYMMDD)을 입력하시오.(지급일 X)\n")        
    MaturityDate = int(input())
    print("\n IRS 만기일에서 대금결제일까지 영업일수를 입력하시오.\n")        
    MaturityToPayDate = int(input())
    print("\n 쿠폰금리를 입력하시오(0.03, 0.05 등).\n")        
    CpnRate = float(input())
    print("\n 1년에 이자지급횟수를 입력하시오.\n")        
    AnnCpnOneYear = int(input())
    print("\n Act365는 0을 | Act360은 1을 | ACTACT이면 2를 | 30/360이면 3를 입력하시오 \n")        
    DayCountFlag = int(input())
    print("\n 최초 Fixing금리를 입력하시오. 입력안해도 되면 0을 입력하시오. \n")        
    FixingRate = float(input())
    
    Value = Calc_IRS(10000, FixingRate, EffectiveDate, 
              int(YYYYMMDD), MaturityDate, CpnRate, CurveTerm1, CurveRate1, 
              AnnCpnOneYear, DayCountFlag, KoreanHoliday = True, MaturityToPayDate = MaturityToPayDate, EstZeroCurveTerm = CurveTerm2,
              EstZeroCurveRate = CurveRate2, FixingHolidayList = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False,
              LoggingFlag = 1, LoggingDir = currdir, ModifiedFollow = 1)         
    
    print("##############\nIRS 가격은 " + str(np.round(Value,6)) + "\n##############\n")
    print("##############\n####산출완료#####\n##############\n")
    MainFlag2 = input("종료하시겠습니까? (Y/N)")
    return MainFlag2

while True : 
    MainFlag = input("사용하실 기능은? \n 1: Pricer \n 2: FRTB SA Risk Calculation \n 3: CurveGenerator \n-> ")
    if len(str(MainFlag)) == 0 : 
        print("\n#########################\n### 프로그램을 종료합니다.###\n#########################")
        break
    elif MainFlag not in [1,2,3,'1','2','3'] : 
        print("\n#########################\n### 프로그램을 종료합니다.###\n#########################")
        break
    elif MainFlag in [2,'2'] :         
        RAWFORMAT = int(input("자체데이터 RAWData 엑셀 포멧이면 0을 KDB RAW Data 포멧의 경우 1을 입력하시오\n-> "))
        RAWData = MainFunction(currdir)
        if RAWFORMAT == 0 : 
            CSR,CSR_SecuritizedNonCTP,CSR_CTP,GIRR, FXR, EQR, COMR, DRC, RRAO = PreProcessingMyData(RAWData)
        else : 
            CSR,CSR_SecuritizedNonCTP,CSR_CTP,GIRR, FXR, EQR, COMR = PreProcessingKDBData(RAWData, dataformat = 'splited') 
            DRC = pd.DataFrame([])
            RRAO = pd.DataFrame([])
        print("##############\n####산출중#####\n##############\n")
        ResultData1 = AggregatedFRTB_RiskCharge(CSR, GIRR, FXR, EQR, COMR, CSR_SecuritizedNonCTP, CSR_CTP, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 0, DRC = DRC, RRAO= RRAO)
        ResultData2 = AggregatedFRTB_RiskCharge(CSR, GIRR, FXR, EQR, COMR, CSR_SecuritizedNonCTP, CSR_CTP, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 1, DRC = DRC, RRAO= RRAO)
        ResultData3 = AggregatedFRTB_RiskCharge(CSR, GIRR, FXR, EQR, COMR, CSR_SecuritizedNonCTP, CSR_CTP, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 2, DRC = DRC, RRAO= RRAO)

        writer = pd.ExcelWriter('ResultFRTB.xlsx', engine='xlsxwriter')
        ResultData1.to_excel(writer, sheet_name = 'ByBucket')
        ResultData2.to_excel(writer, sheet_name = 'ByDepart')
        ResultData3.to_excel(writer, sheet_name = 'ByPortfolio')
        writer.save()
        writer.close()
        print("##############\n####산출완료#####\n##############\n")
        MainFlag2 = input("종료하시겠습니까? (Y/N)")
        if str(MainFlag2).lower() == 'y' or len(str(MainFlag2)) == 0:
            print("\n#########################\n### 프로그램을 종료합니다.###\n#########################")
            break
    elif MainFlag in [1,'1'] :                     
        YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata') 
        print("\nPricer를 선택하시오 : 1. 채권 2. IRS\n")
        n = int(input())
        if n == 1 : 
            MainFlag2 = PricingBondProgram(YYYYMMDD, Name, Data)
        else : 
            MainFlag2 = PricingIRSProgram(YYYYMMDD, Name, Data)            
        if str(MainFlag2).lower() == 'y' or len(str(MainFlag2)) == 0:
            print("\n#########################\n### 프로그램을 종료합니다.###\n#########################")
            break
    elif MainFlag in [3,'3'] : 
        print("\n#########################\n### 커브제너레이터 아직 미완성이므로 종료합니다.###\n#########################")
        break
        


# %%
